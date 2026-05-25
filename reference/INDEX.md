# INDEX — карта референсного корпуса

Карта экспорта действующей системы BaSYS, лежащего в `reference/metadata/`.
Используется как навигация: смотри сводку ниже, открывай нужный `INDEX-<kind>.md` для подробного списка объектов вида.

**Версия и дата выгрузки:** см. `reference/README.md`.

## Сводка по видам

| Вид | Объектов | Подробный список |
|---|---|---|
| Справочники (`catalog/`) | 91 | [INDEX-catalog.md](INDEX-catalog.md) |
| Кастомные отчёты (`customreport/`) | 3 | [INDEX-customreport.md](INDEX-customreport.md) |
| Кастомные представления (`customview/`) | 2 | [INDEX-customview.md](INDEX-customview.md) |
| Панели данных (`data_view/`) | 7 | [INDEX-data_view.md](INDEX-data_view.md) |
| Перечисления (`enum/`) | 12 | [INDEX-enum.md](INDEX-enum.md) |
| Отчёты Excel (`excel_report/`) | 2 | [INDEX-excel_report.md](INDEX-excel_report.md) |
| Меню (`menu/`) | 4 | [INDEX-menu.md](INDEX-menu.md) |
| Операции (документы) (`operation/`) | 29 | [INDEX-operation.md](INDEX-operation.md) |
| Регистры записей (`records/`) | 57 | [INDEX-records.md](INDEX-records.md) |
| Регистры (`register/`) | 12 | [INDEX-register.md](INDEX-register.md) |
| Системные объекты (`system/`) | 1 | [INDEX-system.md](INDEX-system.md) |
| Процессы (Workflows) (`workflow/`) | 115 | [INDEX-workflow.md](INDEX-workflow.md) |
| **ВСЕГО** | **335** | |

## Как пользоваться

- При генерации нового объекта: открой карту нужного вида (`INDEX-catalog.md`, `INDEX-operation.md` и т.д.) и найди аналогичный по `Title`/`Memo`.
- Найден паттерн → открой конкретный файл `reference/metadata/<kind>/<name>/<kind>.<name>.json` через `Read` для полного содержимого.
- `MetaObjectKindUid`, `DataTypeUid` и подобные UID видов/типов брать из этих файлов. **UID самих объектов не копировать в новые** — каждый новый объект получает свой при импорте в BaSYS.

