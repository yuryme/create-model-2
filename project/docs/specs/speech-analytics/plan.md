---
sp-id: speech-analytics
title: План реализации модуля учета минут распознавания
kind: implementation-plan
status: approved
author: pm-chat
created: 2026-05-27
updated: 2026-05-27
source-spec: project/docs/specs/speech-analytics/spec.md
---

# План реализации

## 1. Объекты

1. Создать регистр `records/recognition_minutes` со стандартными колонками records и аналитиками: организация, клиент, пакет, тариф, минуты, сумма, перерасход.
2. Создать операцию `operation/recognition_package` с расчетом тарифа и минут пакета, провести ее плюсом в регистр.
3. Создать операцию `operation/recognition_usage` с табличными частями `items` и `write_offs`, провести `write_offs` минусом в регистр.
4. Создать workflow `workflow/load_rec_usage_excel` для чтения прикрепленного Excel.
5. Добавить команды `load_from_file` и `calculate_fifo` в `recognition_usage`.
6. Добавить новые operation-типы в `system/dataTypes.json`.

## 2. Проверки

- JSON parse всех новых файлов.
- Уникальность UID в новых файлах и отсутствие пересечений с существующими UID проекта.
- Проверка `$schema` и `MetaObjectKindUid`.
- Проверка, что `DataTypeUid` ссылаются на существующие типы.
- Проверка, что `.bjs` файлы совпадают с `Expression` в JSON.
- `git diff --check`.

## 3. Риски

- Команда FIFO использует query builder в клиентском command script; финальное подтверждение возможно только на стенде BaSYS.
- Excel mapping reference-поля клиента может потребовать уточнения формата файла после первого импорта.
- Печатный акт сознательно отложен до проверки учетного ядра модуля.
