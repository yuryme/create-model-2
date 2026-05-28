---
sp-id: base-model
title: Базовая учетная модель для малого бизнеса
status: approved
author: analyst
created: 2026-05-26
updated: 2026-05-26
depends-on: [base-model-design.md]
---

# ТЗ base-model — Базовая учетная модель для малого бизнеса

## 1. Контекст

Нужно создать минимальное универсальное ядро учета для малого бизнеса на BaSYS. Ядро должно использоваться как стартовая модель для разных предпринимателей и как основа для будущих блоков: розница, услуги, склад, производство, CRM, проекты и управленческий учет.

Первая версия intentionally простая: она показывает товары, деньги и взаиморасчеты, но не рассчитывает себестоимость, валовую прибыль, доходы/расходы, валюты и начальные остатки.

## 2. Состав задачи

### В составе

- Справочники: организации, контрагенты, номенклатура, группы номенклатуры, единицы измерения, склады, банки, расчетные счета, договоры, статьи ДДС.
- Операции: поступление товаров, поступление услуг, реализация товаров, реализация услуг, поступление денег, списание денег.
- Регистры записей: товары на складах, расчеты с контрагентами, деньги на счетах.
- Простое меню с разделами справочников, операций и регистров.
- Автоформы BaSYS: `ListFormUid` и `ItemFormUid` не задаются.

### НЕ в составе

- Касса, валюты, НДС, налоги, план счетов и регламентированная бухгалтерия.
- Себестоимость реализации, валовая прибыль, доходы/расходы и отдельный регистр доходов/расходов.
- Начальные остатки товаров, денег и задолженности.
- Производство, CRM, сотрудники, проекты, подразделения, цены, прайс-листы и интеграции.

## 3. Сводка изменений в метаданных

| Действие | Вид | Name | Title | Назначение |
|---|---|---|---|---|
| CREATE | catalog | company | Организация | Собственные юрлица/ИП. |
| CREATE | catalog | counterparty | Контрагент | Покупатели, поставщики и партнеры. |
| CREATE | catalog | product_group | Группа номенклатуры | Классификация номенклатуры. |
| CREATE | catalog | unit | Единица измерения | Меры количества. |
| CREATE | catalog | product | Номенклатура | Товары, услуги, работы и материалы. |
| CREATE | catalog | warehouse | Склад | Места хранения товаров. |
| CREATE | catalog | bank | Банк | Банки для реквизитов. |
| CREATE | catalog | bank_account | Расчетный счет | Банковские счета. |
| CREATE | catalog | contract | Договор | Необязательная аналитика расчетов. |
| CREATE | catalog | cash_flow_item | Статья ДДС | Классификация платежей. |
| CREATE | records | stock_records | Товары на складах | Движения товаров. |
| CREATE | records | settlement_records | Расчеты с контрагентами | Долги покупателей/поставщиков. |
| CREATE | records | money_records | Деньги на счетах | Движения денег. |
| CREATE | operation | goods_receipt | Поступление товаров | Покупка товаров. |
| CREATE | operation | service_receipt | Поступление услуг | Получение услуг. |
| CREATE | operation | goods_sale | Реализация товаров | Продажа товаров. |
| CREATE | operation | service_sale | Реализация услуг | Оказание услуг. |
| CREATE | operation | money_receipt | Поступление денег | Получение денег на расчетный счет. |
| CREATE | operation | money_payment | Списание денег | Оплата с расчетного счета. |
| CREATE | menu | main | Главное меню | Навигация по базовой модели. |

## 4. Детали по метаобъектам

### 4.1. Общие правила

- Все новые `Name` — латиница `snake_case`, не длиннее 30 символов.
- Все новые объекты активны: `IsActive: true`.
- Стандартные колонки каждого вида Инженер копирует из `project/metadata/system/kinds/kind.<kind>.json`.
- `OrderByExpression` для справочников: `title`; для операций: `number desc, date desc`; для регистров: `period, id`.
- `DisplayExpression` для справочников: `title`; для операций оставить дефолт вида или использовать `Operation #{{number}} from {{date}}`.
- Пользовательские формы не создаются; используются автоформы.

### 4.2. Справочники

| catalog | Дополнительные колонки шапки |
|---|---|
| company | `full_name` string(200), `inn` string(12), `phone` string(50), `email` string(100) |
| counterparty | `full_name` string(200), `inn` string(12), `phone` string(50), `email` string(100) |
| product_group | дополнительных колонок нет |
| unit | `code` string(10) required unique |
| product | `product_type` string(20) required, `product_group` ref product_group, `unit` ref unit required, `sku` string(50) |
| warehouse | `code` string(20) |
| bank | `bic` string(20) |
| bank_account | `bank` ref bank required, `company` ref company, `counterparty` ref counterparty, `account_number` string(34) required, `is_own` boolean default true |
| contract | `company` ref company required, `counterparty` ref counterparty required, `contract_number` string(50), `contract_date` Date&Time |
| cash_flow_item | `flow_kind` string(20) required; values by convention: `in`, `out` |

Связи `bank_account.company` и `bank_account.counterparty` взаимоисключающие методически, но в первой версии это не валидируется скриптом. Договор создается в ядре, но все операции должны работать без договора.

### 4.3. Регистры записей

#### `records/stock_records` — Товары на складах

Пользовательские колонки шапки:

| Name | Title | DataType | Обязательно | Memo |
|---|---|---|---|---|
| company | Организация | ref company | да | Организация учета. |
| warehouse | Склад | ref warehouse | да | Склад движения. |
| product | Номенклатура | ref product | да | Товарная позиция. |
| quantity | Количество | Decimal | да | Количество товара. |
| amount | Сумма | Decimal | нет | Сумма поступления; для реализации без себестоимости может быть 0. |

#### `records/settlement_records` — Расчеты с контрагентами

Знак суммы: положительное значение означает, что контрагент должен организации; отрицательное — организация должна контрагенту.

| Name | Title | DataType | Обязательно | Memo |
|---|---|---|---|---|
| company | Организация | ref company | да | Организация учета. |
| counterparty | Контрагент | ref counterparty | да | Участник расчетов. |
| contract | Договор | ref contract | нет | Необязательная аналитика договора. |
| amount | Сумма | Decimal | да | Изменение задолженности. |

#### `records/money_records` — Деньги на счетах

| Name | Title | DataType | Обязательно | Memo |
|---|---|---|---|---|
| company | Организация | ref company | да | Организация учета. |
| bank_account | Расчетный счет | ref bank_account | да | Счет движения денег. |
| cash_flow_item | Статья ДДС | ref cash_flow_item | да | Смысл платежа. |
| amount | Сумма | Decimal | да | Изменение остатка денег. |

### 4.4. Операции

Общие колонки шапки для закупок и продаж: `company`, `counterparty`, `contract`, `total_amount`. Договор необязателен. `total_amount` хранится пользователем/автоформой вручную в первой версии; автоматический расчет итогов и UX-улучшения не входят в scope.

Табличная часть `items` для товарных операций:

| Name | Title | DataType | Обязательно | Memo |
|---|---|---|---|---|
| product | Номенклатура | ref product | да | Товарная позиция. |
| unit | Единица | ref unit | да | Единица строки. |
| quantity | Количество | Decimal | да | Количество товара. |
| price | Цена | Decimal | нет | Цена за единицу. |
| amount | Сумма | Decimal | да | Сумма строки. |

Табличная часть `items` для сервисных операций:

| Name | Title | DataType | Обязательно | Memo |
|---|---|---|---|---|
| product | Номенклатура | ref product | да | Услуга или работа. |
| unit | Единица | ref unit | да | Единица строки. |
| quantity | Количество | Decimal | да | Количество услуг. |
| price | Цена | Decimal | нет | Цена за единицу. |
| amount | Сумма | Decimal | да | Сумма строки. |

Денежные операции имеют колонки шапки: `company`, `counterparty`, `contract`, `bank_account`, `cash_flow_item`, `amount`. Контрагент обязателен в первой версии, чтобы операция одновременно закрывала взаиморасчеты.

### 4.5. Проведение операций

| Операция | Регистр | Направление | Источник | Колонки регистра ← выражения |
|---|---|---|---|---|
| goods_receipt | stock_records | Plus | items | `period ← $h.date`, `company ← $h.company`, `warehouse ← $h.warehouse`, `product ← $r.product`, `quantity ← $r.quantity`, `amount ← $r.amount` |
| goods_receipt | settlement_records | Minus | items | `period ← $h.date`, `company ← $h.company`, `counterparty ← $h.counterparty`, `contract ← $h.contract`, `amount ← $r.amount` |
| service_receipt | settlement_records | Minus | items | `period ← $h.date`, `company ← $h.company`, `counterparty ← $h.counterparty`, `contract ← $h.contract`, `amount ← $r.amount` |
| goods_sale | stock_records | Minus | items | `period ← $h.date`, `company ← $h.company`, `warehouse ← $h.warehouse`, `product ← $r.product`, `quantity ← $r.quantity`, `amount ← 0` |
| goods_sale | settlement_records | Plus | items | `period ← $h.date`, `company ← $h.company`, `counterparty ← $h.counterparty`, `contract ← $h.contract`, `amount ← $r.amount` |
| service_sale | settlement_records | Plus | items | `period ← $h.date`, `company ← $h.company`, `counterparty ← $h.counterparty`, `contract ← $h.contract`, `amount ← $r.amount` |
| money_receipt | money_records | Plus | header | `period ← $h.date`, `company ← $h.company`, `bank_account ← $h.bank_account`, `cash_flow_item ← $h.cash_flow_item`, `amount ← $h.amount` |
| money_receipt | settlement_records | Minus | header | `period ← $h.date`, `company ← $h.company`, `counterparty ← $h.counterparty`, `contract ← $h.contract`, `amount ← $h.amount` |
| money_payment | money_records | Minus | header | `period ← $h.date`, `company ← $h.company`, `bank_account ← $h.bank_account`, `cash_flow_item ← $h.cash_flow_item`, `amount ← $h.amount` |
| money_payment | settlement_records | Plus | header | `period ← $h.date`, `company ← $h.company`, `counterparty ← $h.counterparty`, `contract ← $h.contract`, `amount ← $h.amount` |

## 5. Меню

Создать `menu/main` с тремя группами: **Справочники**, **Операции**, **Регистры**. В каждую группу добавить ссылки на соответствующие объекты по URL `/app#/data-objects/<kind>/<name>`.

## 6. Зависимости и порядок реализации

1. Создать справочники без ссылок: `company`, `counterparty`, `product_group`, `unit`, `warehouse`, `bank`, `cash_flow_item`.
2. Создать справочники со ссылками: `product`, `bank_account`, `contract`.
3. Создать регистры записей.
4. Создать операции и правила проведения.
5. Создать меню.

## 7. Чек-лист приемки

### A. Файловая самопроверка

- [ ] Все объекты из раздела 3 созданы.
- [ ] Все JSON синтаксически валидны.
- [ ] Все `Name` соответствуют латинице `snake_case` и длине ≤30.
- [ ] Все ссылки на виды и типы берутся из `project/metadata/system/`.
- [ ] В `system/dataTypes.json` добавлены типы для всех catalog и operation объектов.
- [ ] `Memo` заполнены у объектов и пользовательских колонок.

### B. Декларативные проверки

- [ ] Операции имеют `RecordsSettings` согласно разделу 4.5.
- [ ] `goods_sale` пишет `amount ← 0` в `stock_records` и не рассчитывает себестоимость.
- [ ] Денежные операции используют только `bank_account`, без кассы.
- [ ] `income_expense_records`, currency и opening-balance объекты отсутствуют.

### C. Функциональные проверки на стенде BaSYS

- [ ] Можно создать организацию, контрагента, номенклатуру, склад, банк и расчетный счет.
- [ ] Поступление товаров создает приход товара и задолженность перед поставщиком.
- [ ] Реализация товаров создает расход товара и задолженность покупателя без себестоимости.
- [ ] Поступление/списание денег двигает деньги на расчетном счете и взаиморасчеты.
