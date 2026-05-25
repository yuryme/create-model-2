---
name: excel-import-to-detail
description: Готовый рецепт «загрузка табличной части операции из прикреплённого Excel-файла». Создаёт workflow (find_file → read_file → excel_mapping → optional result) плюс программируемую команду на табличной части операции, вызывающую workflow через runWorkflow. Триггерится при просьбах «импортируй из Excel», «заполни табличную часть из файла», «добавь кнопку "загрузить из файла"», или при создании workflow вида «excel → детали операции».
when_to_use: Конкретный рецепт связки workflow + команды для загрузки данных в табличную часть операции из прикреплённого Excel. Для общих правил workflow и команд — открывать вместо этого `basys-metadata/workflows.md` и `basys-metadata/commands.md`.
---

# Excel → табличная часть операции

Готовый шаблон для частой задачи: загрузить данные из прикреплённого к операции Excel-файла в одну из её табличных частей по кнопке.

## Что нужно уточнить у пользователя

Перед созданием — выясни (если не очевидно из контекста):

1. **Целевая операция** — какая операция получает данные? (её `Name`).
2. **Табличная часть** — в какую запись `DetailTables`? (её `Name`).
3. **Структура Excel-файла**: имя листа, заголовки колонок и сопоставление с полями таблицы:
   - `SheetName` (по умолчанию `"Лист1"`).
   - `SourceFieldName` — точный текст заголовка колонки в Excel.
   - `DestinationFieldName` — имя колонки в целевой табличной части.
   - `DataTypeUid` для каждой строки маппинга — искать в `project/metadata/system/dataTypes.json`.
4. **Колонки с формулами в целевой табличной части.** Проверить колонки на наличие непустого поля `Formula`. **Их значения нужно вычислять явно в workflow** — формулы НЕ срабатывают автоматически при `$t.load(source)`. Если такие колонки есть — шаг `result` обязателен.
5. **Пост-обработка** — нужны ли join, фильтрация, очистка? Если нет и нет колонок с формулами — результат шага `mapping` возвращается напрямую.

## Структура решения — две части

### A. Workflow (серверная сторона)

Последовательность шагов:

| # | Имя шага | KindName | Назначение |
|---|---|---|---|
| 1 | `find_file` | `java_script` | Найти прикреплённый файл по id документа |
| 2 | `read_file` | `read_file` | Прочитать найденный файл |
| 3 | `mapping` | `excel_mapping` | Маппинг Excel-колонок → DataTable |
| 4 | *(опционально)* `result` | `java_script` | Пост-обработка (join, фильтр, формульные колонки) |

### B. Команда в операции

Программируемая команда (`Kind = 0`), привязанная к **целевой табличной части**, вызывающая workflow через `runWorkflow(...)`.

## Шаг 1. Создать workflow

### Имя и расположение

- `Name`: `load_excel_{operation_name}` (или другое осмысленное, ≤30 символов).
- Папка: `project/metadata/workflow/{name}/`.
- Settings: `workflow/{name}/workflow.{name}.json`.

### Шаблон JSON

```json
{
  "$schema": "../../system/schemas/workflowSettings.schema.json",
  "Uid": "<new-uuid>",
  "Name": "<workflow_name>",
  "Title": "<Human-readable title>",
  "Memo": "Загрузка табличной части операции из прикреплённого Excel-файла",
  "IsActive": true,
  "Version": 1,
  "Steps": [
    {
      "Expression": "workflow.<name>.step.find_file.bjs",
      "Uid": "<step1-uuid>",
      "PreviousStepUid": "",
      "KindUid": "dff616ce-0f40-4e44-a82b-14aa5ee2e4d6",
      "KindName": "java_script",
      "Title": "Find file",
      "Name": "find_file",
      "Memo": "Поиск прикреплённого файла операции",
      "IsActive": true
    },
    {
      "Regime": 1,
      "OutputFormat": 0,
      "AttachedFileUidExpression": "_data.find_file.rows[0].uid",
      "Uid": "<step2-uuid>",
      "PreviousStepUid": "<step1-uuid>",
      "KindUid": "800c9045-1c1c-46d0-a15f-968a43220d1a",
      "KindName": "read_file",
      "Title": "Read file",
      "Name": "read_file",
      "Memo": "Чтение прикреплённого файла",
      "IsActive": true
    },
    {
      "SourcePath": "read_file",
      "SheetName": "<sheet_name>",
      "StartRow": 1,
      "EndRow": 0,
      "Mapping": [
        {
          "Uid": "<mapping-row-uuid>",
          "SourceFieldName": "<Excel column header>",
          "DestinationFieldName": "<target_field_name>",
          "DataTypeUid": "<uuid из system/dataTypes.json>"
        }
      ],
      "Uid": "<step3-uuid>",
      "PreviousStepUid": "<step2-uuid>",
      "KindUid": "762db492-58b2-4e7e-86ca-0b80b0e3aaae",
      "KindName": "excel_mapping",
      "Title": "Mapping",
      "Name": "mapping",
      "Memo": "Маппинг колонок Excel в таблицу данных",
      "IsActive": true
    }
  ]
}
```

### Скрипт шага `find_file`

Файл: `workflow.{name}.step.find_file.bjs`

```javascript
var fileData = await from("operation.<operation_name>.attached_files")
  .select(['uid', 'filename'])
  .where("objectuid = @id")
  .parameter("id", _parameters.id, 11)
  .query();

return fileData;
```

Ключевые моменты:

- `operation.<operation_name>.attached_files` — таблица прикреплённых файлов целевой операции.
- `_parameters.id` — идентификатор документа, переданный из команды.
- Тип параметра `11` = `Int32`.

### Колонки с формулами — важно

Формулы колонок целевой табличной части (поле `Formula` колонки) **не срабатывают автоматически** при загрузке через `$t.load(source)`. Поэтому если в целевой таблице есть колонки с формулами, workflow **обязан** вычислить их явно и включить в возвращаемый `DataTable`.

Типичный подход:

1. Проверить колонки целевой табличной части на непустое `Formula`.
2. В шаге `result` (или в отдельном пост-шаге) пройтись по строкам и вычислить эти значения по той же логике, что и формула.
3. Включить вычисленные колонки в возвращаемый `DataTable`.

Шаг `result` **обязателен**, если у целевой табличной части есть формульные колонки — даже если другой пост-обработки не нужно.

### Опциональный шаг `result`

Добавлять при необходимости пост-обработки (join, удаление колонок, фильтрация, вычисление формульных колонок). Если результата `mapping` достаточно **и** у целевой таблицы нет формульных колонок — делать `mapping` последним шагом. Иначе добавлять `result`.

Файл: `workflow.{name}.step.result.bjs`

```javascript
// Пример 1: join данных маппинга с другой таблицей
return _data.some_table
  .innerJoin(_data.mapping, (pr, jr) => pr.field == jr.field)
  .deleteColumn('extra_column');
```

```javascript
// Пример 2: вычислить формульные колонки (amount = quantity * price)
var dt = _data.mapping;
for (var i = 0; i < dt.rows.length; i++) {
  var row = dt.rows[i];
  row.amount = (row.quantity || 0) * (row.price || 0);
}
return dt;
```

## Шаг 2. Создать команду в операции

### Запись `Commands` (в JSON операции)

```json
{
  "Uid": "<new-uuid>",
  "TableUid": "<Uid целевой табличной части>",
  "Kind": 0,
  "Title": "Заполнить из файла",
  "Name": "load_from_file",
  "Expression": "operation.<operation_name>.command.load_from_file.bjs",
  "Memo": "Загрузка данных из прикреплённого Excel-файла",
  "IsActive": true,
  "Parameters": [
    {
      "Name": "data_source",
      "Value": "",
      "DbType": 16
    },
    {
      "Name": "clear",
      "Value": "false",
      "DbType": 3
    }
  ]
}
```

### Тело команды (`.bjs`)

Файл: `operation.{operation_name}.command.load_from_file.bjs`

```javascript
setIsWaiting(true);
var source = await runWorkflow('<workflow_name>',
                               '<last_step_name>',
                               [{name: 'id',
                                 dataType: 'integer',
                                 value: $h.number}]);
setIsWaiting(false);
$t.<detail_table_name>.load(source);
setIsModified(true);
```

Подстановки:

- `<workflow_name>` — `Name` workflow-а.
- `<last_step_name>` — `Name` финального шага, чей результат — готовый `DataTable` (обычно `mapping` или `result`).
- `$h.number` — стандартная колонка `number` шапки операции, используется как идентификатор документа для поиска файла.
- `$t.<detail_table_name>.load(source)` — загрузка результата в табличную часть.

## Чек-лист

- [ ] Workflow JSON валидируется по `workflowSettings.schema.json`.
- [ ] Все `Uid` — свежие, уникальные UUID v4.
- [ ] `PreviousStepUid` формирует цепочку (у первого — `""`).
- [ ] `.bjs`-файлы соответствуют шаблону: `workflow.{name}.step.{stepName}.bjs`.
- [ ] `Expression` в JSON точно совпадает с именем файла.
- [ ] `find_file.bjs` ссылается на правильную операцию (`operation.<name>.attached_files`).
- [ ] `DataTypeUid` в `Mapping` взяты из `system/dataTypes.json`.
- [ ] Команда привязана к нужной табличной части (`TableUid`).
- [ ] Вызов `runWorkflow` ссылается на корректное имя workflow и последнего шага.
- [ ] Колонки целевой табличной части с `Formula` — вычислены явно в workflow.
- [ ] `Memo` заполнен (по-русски) на workflow, шагах и команде.

## Связанные правила (если нужны подробности)

- Общие правила workflow — `project/.claude/skills/basys-metadata/workflows.md` (полный список видов шагов, JSON-структура, чек-лист для других сценариев).
- Общие правила команд — `project/.claude/skills/basys-metadata/commands.md` (контекст команды, form-control функции, варианты Kind).
- Общие правила метаобъектов — `project/.claude/skills/basys-metadata/SKILL.md` (именование, UID, чек-лист сохранения).
