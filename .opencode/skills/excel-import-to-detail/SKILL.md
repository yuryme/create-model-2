---
name: excel-import-to-detail
description: Рецепт BaSYS «Excel -> табличная часть операции»: workflow find_file/read_file/excel_mapping плюс программируемая команда, вызывающая workflow через runWorkflow. Использовать при просьбах загрузить табличную часть из Excel.
---

# Excel -> Табличная Часть Операции

Использовать, когда нужна кнопка на операции, которая берет прикрепленный Excel-файл и заполняет табличную часть.

## Типовая архитектура

1. Пользователь прикрепляет Excel-файл к операции.
2. Команда на форме операции вызывает workflow через `runWorkflow(...)`.
3. Workflow находит файл, читает его, применяет `excel_mapping` и возвращает строки.
4. Команда очищает или дополняет табличную часть через `$t.<table>.load(...)`.

## Что создать

- `workflow/<name>/workflow.<name>.json`.
- `.bjs`-шаги workflow, если нужны.
- Команду в JSON операции.
- `operation.<name>.command.<command>.bjs` рядом с JSON операции.

## Supporting Files

- Общие правила workflow: `.opencode/skills/basys-metadata/workflows.md`.
- Общие правила команд: `.opencode/skills/basys-metadata/commands.md`.
- Общие правила метаданных: `.opencode/skills/basys-metadata/SKILL.md`.

## Чек-лист

- Контракт колонок Excel явно сопоставлен с колонками табличной части.
- Для ссылочных колонок команда передает и значение, и display-поле при необходимости.
- После `load()` критичные Stored-Formula значения заполнены явно, если runtime их не пересчитывает.
- Ошибки показываются через `throw new Error(...)` с понятным сообщением.
