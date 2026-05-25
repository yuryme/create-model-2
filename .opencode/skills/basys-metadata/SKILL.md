---
name: basys-metadata
description: Правила генерации JSON-метаданных BaSYS: справочники, документы, регистры, data_view, Excel-отчеты, workflow, меню, команды и проведение. Использовать при просьбах создать/изменить метаобъект или при работе с project/metadata/.
---

# Генерация метаданных BaSYS

## Источники правды

- Официальная документация: `basys-docs/ru/` + карта `basys-docs-index.md`.
- Собственный system целевой инсталляции: `project/metadata/system/`.
- Референс: `reference/metadata/` + `reference/INDEX*.md` только как банк структурных паттернов.

## Главное правило UID

UID видов, типов, стандартных колонок и схем брать только из `project/metadata/system/`. UID из `reference/metadata/system/` не использовать, потому что это другая инсталляция BaSYS.

## Поток работы

1. Понять задачу и вид метаобъекта.
2. Проверить ТЗ и текущее состояние `project/metadata/`.
3. Найти похожий паттерн в `reference/INDEX-<kind>.md`, если это полезно.
4. Проверить синтаксис по `basys-docs/ru/...`, если есть сомнения.
5. Создать или изменить JSON и связанные `.bjs`.
6. Проверить `dataTypes.json`, схемы, UID, имена, `Memo`, JSON-синтаксис.
7. Подготовить инструкцию импорта с учетом ADR-003.

## Типы файлов

- `*.json` - декларативные настройки метаобъектов.
- `*.bjs` - серверные скрипты команд, источников данных, проведения и workflow.
- `*.vue` - программируемые UI-компоненты, используются редко.

## Что не редактировать

- `reference/` - read-only.
- `basys-docs/` - read-only, кроме явного обновления документации.
- `project/metadata/system/kinds/` и `project/metadata/system/schemas/` - не редактировать.
- `project/metadata/system/dataTypes.json` - только дописывать новые reference-kind типы, не менять существующие.

## Имена и тексты

- Новые `Name` - латиница, нижний регистр, `snake_case`, цифры и `_`, длина имени объекта до 30 символов.
- `Title` и `Memo` - обычно по-русски.
- JS-переменные - `camelCase`, классы - `PascalCase`, константы - `UPPER_SNAKE_CASE`.
- `Memo` обязателен для новых объектов, колонок и таблиц, максимум 300 символов.

## Stored, Virtual и Formula

- По умолчанию новые колонки `Kind = 0` (`Stored`).
- `Kind = 1` (`Virtual`) только если явно требуется не хранить значение.
- `Formula` не означает автоматически Virtual: Stored-колонка с Formula сохраняет вычисленное значение.

## Создание нового метаобъекта

1. Определить вид по `project/metadata/system/kinds/kind.*.json`.
2. Создать папку `project/metadata/<kind>/<name>/` при необходимости.
3. Создать файл `project/metadata/<kind>/<name>/<kind>.<name>.json`.
4. Выбрать `$schema` из `project/metadata/system/schemas/`.
5. Установить `MetaObjectKindUid` из собственного `kind.*.json`.
6. Скопировать стандартные колонки вида, если они есть: `StandardColumnUid` из kind, новый свежий `Uid` для самой колонки.
7. Подобрать `DataTypeUid` из `project/metadata/system/dataTypes.json`.
8. Сгенерировать свежие UUID v4 для нового объекта и всех новых вложенных сущностей.
9. Заполнить `Title`, `Memo`, `Header`, колонки, табличные части, команды и настройки.
10. Если вид `IsReference = true`, дописать запись в `project/metadata/system/dataTypes.json` с `uid` равным `Uid` нового объекта.

## Чек-лист перед завершением

- `Name` объекта и колонок соответствуют ADR-001.
- `Title` и `Memo` заполнены и не превышают лимиты.
- Все новые `Uid` свежие и уникальные.
- Все платформенные UID взяты из `project/metadata/system/`.
- `Header.Name = "header"`.
- Стандартные колонки имеют `IsStandard = true` и корректный `StandardColumnUid`.
- `$schema` относительный и указывает на существующую схему.
- JSON синтаксически валиден.
- `.bjs` не требует npm-зависимостей.

## Supporting Files

В этой OpenCode-миграции supporting-файлы лежат рядом:

- `commands.md` - команды формы и `.bjs`.
- `records-creation.md` - проведение по регистрам.
- `workflows.md` - workflow и шаги процессов.
- `data-view-reports.md` - отчеты `data_view`.
- `excel-reports.md` - Excel-отчеты.
- `menu.md` - меню.

Открывать supporting-файл только когда тема релевантна.
