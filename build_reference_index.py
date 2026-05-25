"""Однократный скрипт: генерирует reference/INDEX.md + reference/INDEX-<kind>.md
по содержимому reference/metadata/. Удаляется после использования."""

import json
from pathlib import Path

ROOT = Path("reference/metadata")
OUTPUT = Path("reference")

KIND_TITLES = {
    "catalog": "Справочники",
    "operation": "Операции (документы)",
    "register": "Регистры",
    "records": "Регистры записей",
    "enum": "Перечисления",
    "data_view": "Панели данных",
    "menu": "Меню",
    "workflow": "Процессы (Workflows)",
    "excel_report": "Отчёты Excel",
    "customreport": "Кастомные отчёты",
    "customview": "Кастомные представления",
    "system": "Системные объекты",
}

def extract_info(obj_dir: Path):
    """Найти главный JSON-файл объекта и вытащить Name/Title/Memo/IsActive."""
    # Кандидаты в порядке предпочтения
    for f in sorted(obj_dir.glob("*.json")):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
            data = json.loads(text)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
        # Берём только верхнеуровневые объекты с полем Name
        if not isinstance(data, dict) or "Name" not in data:
            continue
        return {
            "name": data.get("Name") or obj_dir.name,
            "title": (data.get("Title") or "").strip(),
            "memo": (data.get("Memo") or "").strip().replace("\n", " ").replace("\r", " "),
            "active": data.get("IsActive", True),
            "file_path": str(f.relative_to(OUTPUT)).replace("\\", "/"),
        }
    return None

def md_escape_cell(s: str) -> str:
    """Минимальное экранирование для markdown-таблиц: | заменить на \\|."""
    return s.replace("|", "\\|")

def truncate(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    return s[: n - 1].rstrip() + "…"

summary = []

for kind_dir in sorted(ROOT.iterdir()):
    if not kind_dir.is_dir():
        continue
    objects = []
    for obj_dir in sorted(kind_dir.iterdir()):
        if not obj_dir.is_dir():
            continue
        info = extract_info(obj_dir)
        if info:
            objects.append(info)

    if not objects:
        continue

    kind_title = KIND_TITLES.get(kind_dir.name, kind_dir.name)
    out_path = OUTPUT / f"INDEX-{kind_dir.name}.md"

    lines = [
        f"# INDEX — {kind_title}",
        "",
        f"Всего объектов: **{len(objects)}**",
        "",
        f"Источник: `reference/metadata/{kind_dir.name}/`. Сгенерирован автоматически из выгрузки BaSYS — см. `reference/README.md` (версия и дата).",
        "",
        "| Name | Title | Memo |",
        "|---|---|---|",
    ]
    for obj in objects:
        name = md_escape_cell(obj["name"])
        title = md_escape_cell(obj["title"]) or "—"
        memo = md_escape_cell(truncate(obj["memo"], 100)) or "—"
        marker = "" if obj["active"] else " ⚠️ inactive"
        lines.append(f"| `{name}`{marker} | {title} | {memo} |")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary.append((kind_dir.name, kind_title, len(objects)))
    print(f"Wrote {out_path} ({len(objects)} objects)")

# Top-level INDEX.md
top = [
    "# INDEX — карта референсного корпуса",
    "",
    "Карта экспорта действующей системы BaSYS, лежащего в `reference/metadata/`.",
    "Используется как навигация: смотри сводку ниже, открывай нужный `INDEX-<kind>.md` для подробного списка объектов вида.",
    "",
    "**Версия и дата выгрузки:** см. `reference/README.md`.",
    "",
    "## Сводка по видам",
    "",
    "| Вид | Объектов | Подробный список |",
    "|---|---|---|",
]
total = 0
for kind_name, kind_title, count in summary:
    top.append(f"| {kind_title} (`{kind_name}/`) | {count} | [INDEX-{kind_name}.md](INDEX-{kind_name}.md) |")
    total += count
top.extend([
    f"| **ВСЕГО** | **{total}** | |",
    "",
    "## Как пользоваться",
    "",
    "- При генерации нового объекта: открой карту нужного вида (`INDEX-catalog.md`, `INDEX-operation.md` и т.д.) и найди аналогичный по `Title`/`Memo`.",
    "- Найден паттерн → открой конкретный файл `reference/metadata/<kind>/<name>/<kind>.<name>.json` через `Read` для полного содержимого.",
    "- `MetaObjectKindUid`, `DataTypeUid` и подобные UID видов/типов брать из этих файлов. **UID самих объектов не копировать в новые** — каждый новый объект получает свой при импорте в BaSYS.",
    "",
])
(OUTPUT / "INDEX.md").write_text("\n".join(top) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT / 'INDEX.md'}")
print(f"Total: {total} objects across {len(summary)} kinds")
