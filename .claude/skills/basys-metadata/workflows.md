# Процессы (Workflows)

**Supporting-файл скилла `basys-metadata`.** Открывать при работе с процессами (видом `workflow`). Основной файл скилла — `SKILL.md`.

**Первоисточник:** `basys-docs/ru/workflows/`.

## Что такое workflow

**Workflow** в BaSYS — серверный pipeline из последовательных шагов, автоматизирующий обработку данных, интеграции и нотификации. Исполняется на сервере (движок ClearScript). Запускается:

- вручную из UI,
- по расписанию,
- по триггеру (на создание/изменение/удаление объекта),
- из клиентского кода через `runWorkflow(...)`.

## Размещение файлов

- У вида `workflow` флаги `StoreData = false` и `IsReference = false` → settings-файл валидируется по `system/schemas/workflowSettings.schema.json` (в `$schema` — обычно `../../system/schemas/workflowSettings.schema.json`). Запись в `system/dataTypes.json` **не нужна**.
- Settings-файл: `project/metadata/workflow/{name}/workflow.{name}.json`.
- Тела JS-шагов — **отдельные `.bjs`-файлы** в той же папке: `workflow.{name}.step.{stepName}.bjs`.
- Верхний уровень JSON: `$schema`, `Uid`, `Name`, `Title`, `Memo`, `IsActive`, `Version`, `Steps` (массив шагов).
- У вида нет `StandardColumns` — у процессов нет `Header`/`DetailTables`/`Commands`/`RecordsSettings`.

## Обзор шагов

Шаги исполняются **последовательно**. Общие поля каждого шага:

| Поле | Описание |
|---|---|
| `Uid` | Свежий UUID v4. |
| `PreviousStepUid` | `Uid` предыдущего шага (пустая строка `""` для первого). |
| `KindUid` | Фиксированный UUID типа шага (см. таблицу ниже). |
| `KindName` | Машинное имя типа шага. |
| `Title` | Человекочитаемая метка. |
| `Name` | Технический идентификатор (`snake_case` латиницей). **Уникален в пределах процесса.** |
| `Memo` | Короткое описание (по-русски). |
| `IsActive` | `true` для исполнения; `false` — пропустить. |

### Цепочка исполнения

Шаги формируют **односвязный список** через `PreviousStepUid`. У первого шага — `PreviousStepUid = ""`. Каждый последующий указывает на `Uid` шага, который должен завершиться перед ним. Шаг `if` ветвится через `TrueStepUid` / `FalseStepUid`.

### Передача данных между шагами

Каждый шаг, возвращающий результат, складывает его под своим `Name` в общий словарь `_data`. Последующие шаги обращаются через `_data.<stepName>`. Внутри шаблонных выражений `{{...}}` (используются в SMTP и message-шагах) — синтаксис `{{stepName.fieldName}}`.

## Виды шагов

| KindName | KindUid | Назначение |
|---|---|---|
| `java_script` | `dff616ce-0f40-4e44-a82b-14aa5ee2e4d6` | Исполнить JS-скрипт (`.bjs`-файл). |
| `if` | `9a3a0dc1-b4ed-4679-9f72-0667b7dcfa53` | Условное ветвление. |
| `iterator` | `07e698af-d11b-454b-a7f4-577a0439e92c` | Цикл по строкам DataTable / массива. |
| `iterator_stop` | `ac090927-e291-4421-b9aa-351b8fa51770` | Конец тела цикла. |
| `data_object_loader` | `a7edd0be-6f12-4fac-b88a-4f83acc7dacb` | Создать/обновить объекты данных из источника. |
| `read_file` | `800c9045-1c1c-46d0-a15f-968a43220d1a` | Прочитать файл (интерактивно или прикреплённый). |
| `excel_mapping` | `762db492-58b2-4e7e-86ca-0b80b0e3aaae` | Распарсить Excel в DataTable. |
| `http_connector` | `bb368829-007d-4b8e-87ce-1dadee75c7c3` | HTTP-запрос. |
| `smtp_send` | `df48f1ed-2bcf-4b1d-b45c-1305b55ce1f6` | Отправить почту по SMTP. |
| `message` | `e192c288-154e-4778-b92c-64da27279796` | Залогировать сообщение. |
| `sleep` | `2a5aca6d-2c41-4bd2-9e03-b35df7dab23e` | Пауза. |

> ⚠️ UID-ы шагов **взяты из чужой выгрузки** (Cursor-rules). Перед использованием **обязательно свериться** с нашей `project/metadata/system/kinds/kind.workflow.json` — UID-ы видов шагов могут отличаться между инсталляциями.

## JS-шаг (`java_script`)

Самый частый. Запускает BaSYS.FX-скрипт на сервере.

Специфическое поле: `Expression` — **имя файла** `.bjs` (например, `"workflow.my_proc.step.load_data.bjs"`).

Шаблон имени: `workflow.{workflowName}.step.{stepName}.bjs`.

Скрипт **обязан `return`-ить** значение; оно становится доступным следующим шагам как `_data.<stepName>`. Для БД — **QueryBuilder** (`from('kind.name')...query()`).

```json
{
  "Expression": "workflow.fill_calendar.step.data.bjs",
  "Uid": "...",
  "PreviousStepUid": "...",
  "KindUid": "dff616ce-0f40-4e44-a82b-14aa5ee2e4d6",
  "KindName": "java_script",
  "Title": "Data",
  "Name": "data",
  "Memo": "Загрузка данных для заполнения календаря",
  "IsActive": true
}
```

### QueryBuilder: имена PK у разных видов и фильтр табличных частей по шапке

В табличных частях операций (и других видов с табличными частями) каждая строка имеет колонку **`object_uid`** — техническая ссылка на PrimaryKey шапки. **Имя PK не универсально — оно зависит от вида.** Таблица соответствий (источник — `project/metadata/system/kinds/kind.*.json`, колонка с `PrimaryKey: true`):

| Вид | Имя PK у шапки | Тип PK |
|---|---|---|
| `catalog` | `id` | Int32 |
| `enum` | `name` | String 20 |
| `operation` | `number` | Int32 |

Имя `id` есть **только** у `catalog`. У `operation` PK называется **`number`**; у `enum` — **`name`** (строковый). Использование `headerRow.id` / `header.id` в скрипте при работе с шапкой `operation` или `enum` приводит к `undefined` в фильтре — запрос **молча возвращает 0 строк, без серверной ошибки**. Эту ловушку легко проглядеть при ревью.

**Правило.** В QueryBuilder, когда нужно отфильтровать строки табличной части по конкретной шапке, использовать имя PK **в соответствии с видом**:

```javascript
// operation/loan — фильтруем строки табличной части books по конкретной выдаче
const rows = await from("operation.loan.books")
  .where("object_uid = @ouid and is_returned = @notReturned")
  .parameter("ouid", headerRow.number, 11)        // ← number, не id, для operation
  .parameter("notReturned", false, 3)
  .query();

// catalog/<name> — для шапки catalog был бы id (DbType 11)
//   .parameter("ouid", headerRow.id, 11)

// enum/<name> — для шапки enum было бы name (DbType 16 — System.String)
//   .parameter("ouid", headerRow.name, 16)
```

**Перед написанием скрипта**, обращающегося к табличной части через `object_uid`, открывай соответствующий `kind.*.json` в `project/metadata/system/kinds/` и проверяй, какая стандартная колонка помечена `PrimaryKey: true`. Не полагайся на «по аналогии с другим видом».

> Эмпирика добыта на реализации `sandbox-04` (2026-05-17): первый запуск workflow `overdue_loans` отдавал пустой результат, потому что в фильтре стояло `headerRow.id` вместо `headerRow.number`. Сервер не падал — `object_uid = undefined` молча отсекало все строки.

## Шаг `if`

Вычисляет boolean-выражение `Condition`. Поля `TrueStepUid` (куда прыгнуть при true) и `FalseStepUid` (при false). Любое можно оставить `""` чтобы продолжить обычной цепочкой.

В `Condition` доступен `_data.<stepName>`.

```json
{
  "Condition": "_data.messages != null",
  "TrueStepUid": "<uid целевого шага>",
  "FalseStepUid": "",
  "Uid": "...", "PreviousStepUid": "...",
  "KindUid": "9a3a0dc1-b4ed-4679-9f72-0667b7dcfa53",
  "KindName": "if",
  "Title": "Check data", "Name": "check_data",
  "Memo": "Проверка наличия данных",
  "IsActive": true
}
```

## Итератор (`iterator` + `iterator_stop`)

Цикл по строкам DataTable, возвращённого предыдущим шагом. Все шаги между `iterator` и `iterator_stop` исполняются раз на строку.

Поля `iterator`:
- `SourcePath` — `Name` шага, чей результат итерировать (например, `"mail_list"`).
- `ItemName` — имя переменной текущей строки (например, `"item"`). Доступно внутри как `_data.<iteratorStepName>` или в `{{...}}`-шаблонах как `{{itemName.field}}`.

У `iterator_stop` нет специфических полей. Его `PreviousStepUid` указывает на последний шаг тела цикла.

## Загрузчик объекта данных (`data_object_loader`)

Создаёт/обновляет объекты данных из источника. Поля:

| Поле | Описание |
|---|---|
| `MetaObjectKindUid` | Uid вида-приёмника. |
| `MetaObjectUid` | Uid метаобъекта-приёмника. |
| `SaveRegime` | `0` = CreateUpdate, `1` = только Create, `2` = только Update. |
| `SearchBy` | Поле для поиска существующих объектов (для Update/CreateUpdate). |
| `SourcePath` | `Name` шага, чей результат даёт строки данных. |
| `Condition` | Опциональный JS-boolean для фильтрации строк. |
| `CreateRecords` | `true` — после сохранения запустить проведение. |
| `HeaderMapping` | Массив `FieldMappingRow` — маппинг полей источника на колонки шапки. |
| `TableMapping` | Массив `DetailsTableLoadSettings` — маппинг на колонки табличных частей. |

`FieldMappingRow`: `Uid`, `SourceFieldName`, `DestinationFieldName`, `DefaultValue`, `SearchBy` (для ссылочных), `DataTypeUid`, `CreateIfNotExist`.

`DetailsTableLoadSettings`: `TableUid` (целевая табличная часть), `SourcePath` (поле на строке источника с дочерними строками), `Mapping` (массив `FieldMappingRow`).

## Чтение файла (`read_file`)

Читает файл для последующей обработки (обычно с последующим `excel_mapping`).

| Поле | Описание |
|---|---|
| `Regime` | `0` = Interactive (пользователь загружает из браузера), `1` = AttachedFile (читать прикреплённый файл объекта). |
| `OutputFormat` | `0` = Binary, `1` = Text. |
| `AttachedFileUidExpression` | Выражение или UUID прикреплённого файла (для `Regime = 1`). |

## Excel-маппинг (`excel_mapping`)

Парсит Excel-файл из предыдущего `read_file` в DataTable.

| Поле | Описание |
|---|---|
| `SourcePath` | `Name` шага `read_file`. |
| `SheetName` | Имя листа. |
| `StartRow` | 0-based индекс первой строки данных (после заголовка). Обычно `1`. |
| `EndRow` | 0-based индекс последней строки. `0` = читать все. |
| `Mapping` | Массив `ExcelMappingRow` (`Uid`, `SourceFieldName` = заголовок колонки Excel, `DestinationFieldName` = имя колонки на выходе, `DataTypeUid`). |

## HTTP Connector (`http_connector`)

| Поле | Описание |
|---|---|
| `Url` | URL запроса. Поддерживает `{{stepName.field}}`-шаблоны. |
| `Method` | `0` GET, `1` POST, `2` PUT, `3` PATCH, `4` DELETE. |
| `BodyKind` | `0` Undefined, `1` JSON, `2` FormData, `3` XWWWFormUrlEncoded, `4` XML. |
| `BodyEncoding` | `0` UTF8, `-1` None. |
| `Body` | Тело запроса. Поддерживает `{{...}}`. |
| `Timeout` | Таймаут в секундах. |
| `LogResponse` | Логировать ответ. |
| `AutoParse` | Парсить JSON-ответ в объект. |
| `BypassSslCertificate` | Пропустить проверку SSL. |
| `ReturnResponseInfo` | Вернуть полный info (status, headers) вместо тела. |
| `AllowSetCookieFromHeaders` | Передавать cookies между шагами. |
| `Headers`, `Parameters`, `FormData` | Массивы `NameValueDescriptionRow`. |

## SMTP Send (`smtp_send`)

Отправляет email. Все строковые поля поддерживают `{{stepName.field}}`-подстановку.

Поля: `Host`, `User`, `Password`, `Port`, `TimeoutSeconds`, `EnableSsl`, `From`, `To`, `CC`, `BCC`, `Subject`, `Body`, `IsBodyHtml`.

## Message (`message`)

Логирует текст. Поле: `Message` (поддерживает `{{...}}`).

## Sleep (`sleep`)

Пауза. Поле: `Delay` (строка, например `"00:00:05"` для 5 секунд).

## Создание нового процесса

1. **Создать папку** `project/metadata/workflow/{name}/` (snake_case латиницей, ≤30 символов).
2. **Создать settings-файл** `workflow.{name}.json` с `$schema`, `Uid`, `Name`, `Title`, `Memo`, `IsActive = true`, `Version = 1`, `Steps = [...]`.
3. **Спроектировать цепочку шагов.** У первого `PreviousStepUid = ""`. У каждого следующего `PreviousStepUid` = `Uid` предыдущего.
4. **Для каждого `java_script`-шага** — создать рядом `.bjs`-файл `workflow.{name}.step.{stepName}.bjs`. В `Expression` шага — это имя файла.
5. **Свежие `Uid`** для процесса и каждого шага.
6. **Заполнить `Memo`** на процессе и каждом шаге.
7. У вида `workflow` `IsReference = false` — запись в `system/dataTypes.json` **не добавлять**.

## Правка существующего процесса

- При добавлении шагов — вставлять в массив `Steps` и обновлять `PreviousStepUid`-связки.
- При удалении шага — обновить `PreviousStepUid` следующего шага так, чтобы он указывал на шаг перед удалённым.
- При правке `java_script`-шага — обновлять **оба места**: запись в JSON **и** `.bjs`-файл.
- Существующие имена шагов/процессов/файлов (включая кириллические в `reference/`) **не переименовывать**.

## Типичные паттерны

### Script → Iterator → Action → Iterator Stop

Подготовить DataTable в `java_script`, проитерироваться по строкам, выполнить действие (`smtp_send`, `data_object_loader`) на каждой.

### Read File → Excel Mapping → Data Object Loader

Импорт данных из Excel в метаобъект. См. отдельный скилл-рецепт `excel-import-to-detail` для готового шаблона импорта в табличную часть операции.

### Script chain + If

Несколько `java_script`-шагов готовят данные, шаг `if` проверяет условие и разветвляет на разные продолжения.

## Гигиена

- Имя `.bjs`-файла **точно** совпадает с `Expression` в JSON.
- `Name` шага уникален в пределах процесса.
- В `.bjs`-скриптах предпочитать QueryBuilder и `DataTable`-хелперы.
- **Никаких сторонних npm-зависимостей.**
- Комментарии в `.bjs` — на языке окружающих файлов (обычно русский).
- Примеры — в `reference/metadata/workflow/`.
