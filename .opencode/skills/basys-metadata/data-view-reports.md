# Data View Reports

Открывать при обычных отчетах, дашбордах, таблицах, графиках, KPI и `data_view`.

## Источники

- `basys-docs/ru/reporting/dataView.md`.
- `basys-docs/ru/reporting/introduction.md`.
- Паттерны: `reference/INDEX-data_view.md`.

## Правила

- `data_view` использовать по умолчанию для интерактивных таблиц, графиков и панелей.
- Источник данных может быть QueryBuilder или `.bjs` рядом с объектом.
- Для сложной агрегации сверяться с `basys-docs/ru/calculations/queryBuilder.md` и `dataTable.md`.
- UID и типы брать только из `project/metadata/system/`.

## Чек-лист

- У отчета понятный `Title` и `Memo`.
- Источник данных возвращает стабильный контракт колонок.
- Фильтры и параметры описаны в ТЗ или плане.
- Пункт меню для отчета добавлен только если это указано в ТЗ.
