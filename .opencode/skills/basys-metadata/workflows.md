# Workflows

Открывать при создании или изменении `workflow`, шагов процесса, импорте Excel через workflow, параметрах workflow и вызовах `runWorkflow(...)`.

## Источники

- `basys-docs/ru/workflows/index.md` и страницы конкретных шагов.
- `basys-docs/ru/calculations/workflowParameter.md`.
- Паттерны: `reference/INDEX-workflow.md`.

## Базовые шаги

- `java_script` - произвольная JS-логика, обычно `.bjs` в папке workflow.
- `if` - ветвление.
- `iterator` / `iterator_stop` - цикл.
- `read_file` - чтение файла из файлового хранилища.
- `excel_mapping` - Excel -> DataTable.
- `data_object_loader` - создание/обновление объектов данных.
- `http_connector` - HTTP-интеграции.
- `smtp_send` - отправка почты.

## PK и object_uid

У разных видов разные primary key:

- `catalog` обычно `id`.
- `enum` обычно `name`.
- `operation` обычно `number`.

Перед фильтром по `object_uid` сверять PK в `project/metadata/system/kinds/kind.<kind>.json`, не угадывать.

## Чек-лист

- Параметры workflow явно описаны.
- `.bjs`-файлы лежат рядом с JSON workflow и корректно указаны в `Expression`.
- Возвращаемый контракт workflow понятен вызывающей команде.
- При вызове из команды проверить формат `runWorkflow(...)` на актуальном примере или документации.
