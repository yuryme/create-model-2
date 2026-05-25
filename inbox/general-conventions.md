---
description: General conventions for working with BaSYS metadata settings
alwaysApply: true
---

# Project Overview

This repository contains metadata settings for the **BaSYS** LowCode platform for building business applications on top of a metadata layer.

Platform documentation: https://basysteam.github.io/BaSys.Docs/ru/ (Russian)

# Workflow

1. Settings are **exported** from the BaSYS system into this repository.
2. The agent **edits** settings locally on user request.
3. Changes are **imported** back into the system, fully or partially.
4. The system periodically pushes updates to `manifest.json` and the data types under `system/`.

# Do Not Edit

The agent **must never modify** the following — they are owned by the system and regenerated automatically:

- `manifest.json` at the repository root
- anything under `system/` (including `system/dataTypes.json`, `system/kinds/`, `system/schemas/`)

These files **may be read** to understand available data types and JSON schemas for settings, but never written. In particular:

- `system/dataTypes.json` — catalog of all data types (`Uid`, `Title`, `TypeName`). Use it to look up a `DataTypeUid` when defining a column's `DataSettings`.
- `system/schemas/` — JSON schemas to validate settings files against.
- `system/kinds/` — definitions of metadata kinds (catalog, register, operation, etc.).

**Exception — `system/dataTypes.json`:** when the agent creates a new metaobject of a kind with `IsReference = true`, it **must** append a corresponding entry to `system/dataTypes.json` (see step 11 in "Adding a New Metaobject"). Without this entry the new type cannot be referenced from other objects in the same editing session. After the changes are imported back, the system regenerates `system/dataTypes.json`, so the locally added entry will be replaced by the server's authoritative version. **Do not modify or delete existing entries** in `system/dataTypes.json` — only append new ones for reference-kind objects you have just created.

# Settings File Types

Settings are stored in three kinds of files:

- `*.json` — declarative metaobject settings (catalogs, registers, operations, etc.). Must validate against the schemas in `system/schemas/`.
- `*.bjs` — standalone server- or client-side scripts, as well as data source scripts for `data_view` objects (see the **`data-view-reports`** rule for the naming convention).
- `*.vue` — standalone UI components.

# Logic in JavaScript

Logic in BaSYS is written in **JavaScript**. For domain tasks the platform provides the **BaSYS.FX** library, which covers:

- working with tabular data,
- executing database queries,
- working with dates and other utilities.

Library documentation: https://basysteam.github.io/BaSys.Docs/ru/calculations/

Rules:

- In `.bjs` and `.vue` files, **prefer `BaSYS.FX` functions** over plain JS for tabular data, queries and date manipulation when an equivalent exists.
- Do not introduce third-party npm dependencies — the runtime is provided by the platform.
- Verify any unfamiliar `BaSYS.FX` function against the documentation before use.

# Naming

In metadata, the technical identifier of an object or table column is the `Name` field; the human-readable label is the `Title` field. They are independent: `Title` may be Russian (Cyrillic) while `Name` should still be a meaningful English identifier.

Rules for **new** objects, columns and variables:

- `Name` must be in English, lowercase, `snake_case`, and meaningful (e.g. `delivery_address`, not `field1`).
- `Title` may be in any language and is what users see in the UI.
- Object `Name` length is limited to **30 characters**. Column and JS variable names have no length limit, but keep them reasonable.
- JS variable, function and parameter names follow standard JS conventions: `camelCase` for variables/functions, `PascalCase` for classes/components, `UPPER_SNAKE_CASE` for constants.

Rules for **existing** identifiers:

- Cyrillic `Name` values, folder names and file names already present in the model must **not** be renamed — they are referenced by the system.
- When extending an existing object with new fields, still apply the new-name rules above to the added fields.

# Memo Field

Most metaobjects, columns and nested items expose a `Memo` field for free-form notes.

- Whenever you create a new object, column or nested entity, fill `Memo` with a short description of its purpose (in Russian, matching the project language).
- When editing an existing entity, update `Memo` if the original description is empty or no longer accurate.
- Keep it concise — one sentence is usually enough.

# Column Kind: Stored vs Virtual

Every column (on `Header.Columns` and on nested table columns) has a `Kind` field of type `DataObjectColumnKinds`:

- `0` — `Stored`: the column is persisted in the database.
- `1` — `Virtual`: the column is **not** persisted and exists only as a runtime-computed value.

Rules for **new** columns:

- **Default to stored.** Always set `Kind = 0` unless the user **explicitly** asks for a virtual (non-stored) column. If the requirement is ambiguous, ask the user instead of guessing.
- The `Formula` field is **independent** of `Kind`. A stored column (`Kind = 0`) may also have a `Formula`: in that case the value is computed by the formula and then saved to the database. Presence of a `Formula` is **not** a reason to set `Kind = 1`.
- Set `Kind = 1` only when the user clearly states the column must not be stored (e.g. "виртуальная колонка", "не сохраняется в БД", "только для отображения").

# Adding a New Metaobject

When the user asks to add a new object:

1. **Determine the metadata kind.** Inspect `system/kinds/kind.*.json` to find which kind the object belongs to (e.g. `kind.catalog.json`, `kind.register.json`, `kind.operation.json`). If the kind is not obvious from the request, **ask the user explicitly** before creating anything.
2. **Locate the kind folder** in the repository root (named after the kind's `Name`, e.g. `catalog/`, `register/`).
3. **Create the object folder** inside the kind folder, named after the new object's `Name` (snake_case English, ≤30 chars). Use the **singular form** for both `Name` and `Title` (e.g. `product` / `Товар`, **not** `products` / `Товары`).
4. **Create the settings file** inside that folder, named `{kind.Name}.{object.Name}.json` (example: `catalog/city/catalog.city.json`).
5. **Choose the schema** based on the kind's `StoreData` flag:
   - `StoreData = true` → file must conform to `system/schemas/metaObjectStorableSettings.schema.json` (set `$schema` accordingly with the correct relative path).
   - `StoreData = false` → use the schema applicable to that kind, if present in `system/schemas/`.
6. **Set `MetaObjectKindUid`** on the new object to the `Uid` of the chosen kind.
7. **Copy standard columns.** If the kind has a `StandardColumns` collection, replicate each entry as a column on the new object's `Header.Columns` with:
   - `StandardColumnUid` = `Uid` of the standard column,
   - `IsStandard` = `true`,
   - `Name`, `Title`, `DataSettings`, `RenderSettings` copied from the standard column,
   - a freshly generated `Uid` for the column itself (do **not** reuse the standard column's `Uid`).
8. **Pick `DataTypeUid` for custom columns** from `system/dataTypes.json` (match by `Title` or `TypeName`). Never invent a `DataTypeUid`.
9. **Generate fresh `Uid` values** (UUID v4, lowercase, hyphenated) for the new object and for every new column or nested item. Each `Uid` in the file must be unique across the project.
10. **Fill `Memo`** on the new object and on each new column with a short description of its purpose.
11. **Register the type in `system/dataTypes.json`** — but **only if** the kind has `IsReference = true` (e.g. `catalog`, `enum`, `operation`). Skip this step for non-reference kinds. Append a new entry to the array with these fields:
    - `uid` — same value as the new object's `Uid` (do **not** generate a separate UID).
    - `kind` — the kind's `Name` (e.g. `"catalog"`, `"enum"`, `"operation"`).
    - `name` — the new object's `Name`.
    - `title` — `"{Kind.Title}.{Object.Title}"` (e.g. `"Справочник.Город"`, `"Перечисление.Тип дня"`).
    - `isPrimitive` — `false`.
    - `dbType` — copy from any existing entry in `dataTypes.json` that has the same `kind` value (all objects of one kind share the same `dbType`; e.g. catalogs use `11`, enums use `16`). If no entry of this kind exists yet, derive it by looking up the `DataTypeUid` of the kind's primary-key standard column (`PrimaryKey = true`, usually `id`) in `dataTypes.json` and copying its `dbType`.
    - `objectKindUid` — the kind's `Uid` (same value as `MetaObjectKindUid` on the new object).
    - `typeName` — `null`.

    This entry will be overwritten by the server on the next sync, but it is required so that the new type can be selected as a `DataTypeUid` in other settings files during the current editing session.

After creating the file, mentally validate it against the chosen schema before finishing.

# Reports and Data Views

For building reports, dashboards, charts, tables, KPIs, gauges and pivot tables, use the `data_view` (Панель данных) metaobject kind by default. Detailed conventions (file layout, data source scripts as separate `.bjs` files, `_filters` / `_data` variables, supported indicator types, 12-column layout grid, singular-report and single-indicator-title rules) live in the separate **`data-view-reports`** rule. Consult that rule whenever the user asks for any kind of report, dashboard or visualization, or when editing files under `data_view/`.

# Excel Reports (Отчёт Excel)

For reports that must be rendered into a pre-designed `.xlsx` layout — regulated forms, printable documents (счета, накладные, акты, договоры), or heavily-formatted summary reports with multi-level headers, merged cells and corporate styling — use the `excel_report` metaobject kind. An Excel report consists of three artefacts that live side by side in the metaobject folder: the JSON settings (`excel_report/{name}/excel_report.{name}.json`, validated against `system/schemas/excelReportSettings.schema.json`), one `.bjs` script per data source (named `excel_report.{name}.data_source.{sourceName}.bjs` and referenced from the JSON via the `Expression` field), and **the template as a separate binary file** `excel_report.{name}.template.xlsx` (the filename is mandatory — that's how the import pipeline picks the template up; the agent must never generate or modify `.xlsx` content itself, only instruct the user to prepare it in Excel and place it in the folder). Data sources are evaluated sequentially in declaration order; each script returns a scalar, object, typed collection or `DataTable`, and the result is exposed in the template under the source `Name` (markers `{{source}}`, `{{source.property}}`, or `{{item.Property}}` / `{{item["ColumnName"]}}` inside a same-named Excel named range). Filters mirror the `data_view` filter schema and are passed to query builders via `_filters` + `.withFilters(_filters)`. Kind `excel_report` has `StoreData = false` and `IsReference = false` — no entry in `system/dataTypes.json` is required, no `Header` / `DetailTables` / `Commands` / `Forms` are configured, and `HasTemplate` is set by the server when the template file is imported. Prefer `data_view` whenever the task does not actually require the pre-designed Excel layout — building `.xlsx` is significantly heavier and the in-app preview is limited (single sheet, no charts/pivots/conditional formatting, `<<sum>>`-style template totals are not shown). Detailed conventions (file layout, marker syntax, named-range hygiene, totals strategy, filter fields, building checklist) live in the separate **`excel-reports`** rule. Consult that rule whenever the user asks to create, modify or debug an Excel report (отчёт Excel, печатная форма, регламентированная отчётность по макету), or when editing files under `excel_report/`. Real examples live under `excel_report/`.

# Commands

Commands (buttons, menu items, fill / pick-up actions) on metaobject forms are declared in the `Commands` collection of the metaobject's JSON, and the body of every command is stored as a separate `.bjs` script file referenced by filename via the `Expression` field. **Default to programmable commands (`Kind = 0`)** — even for fill and pick-up scenarios — over the simplified `Fill` / `PickUp` kinds. Detailed conventions (file naming `{kind}.{name}.command.{cmdName}.bjs`, `Commands` entry shape, `TableUid` for header- vs detail-bound commands, execution context with `$h` / `$t` / `$r` and form-control functions like `openPickUp`, `runWorkflow`, `save`, `setIsWaiting`) live in the separate **`commands`** rule. Consult that rule whenever the user asks to add a button, action, fill or pick-up to a metaobject form, or when editing `*.command.*.bjs` files. Many real examples live under `operation/`.

# Records Creation (Проведение по регистрам)

For metaobject kinds with `CanCreateRecords = true` (typically `operation`), records posting into registers is configured by two collections in the metaobject's JSON: `RecordsSettings` (rules per destination register, with `SourceUid`, `Direction`, `Condition` and per-column `Expression`s) and `RecordsSources` (**источники записей** — custom JavaScript sources that return a `DataTable`). The body of every records source / источника записей is stored as a **separate `.bjs` script file** in the same folder as the metaobject JSON, referenced by filename through the `Expression` field of the `RecordsSources` entry — exactly like commands and data-view data sources. Detailed conventions (the three source kinds — header / detail table / records source; engine-managed service columns; `Direction = Plus | Minus`; `$h` / `$t` / `$r` inside expressions and scripts; file naming `{kind}.{name}.records_source.{sourceName}.bjs`; the `create_records` flag) live in the separate **`records-creation`** rule. Consult that rule whenever the user asks to set up or edit "Записи" / проведение / registry posting on an operation, to create or add a "источник записей" / records source, or when editing `*.records_source.*.bjs` files. Many real examples live under `operation/`.

# Workflows (Процессы)

Workflows (`workflow` kind) are server-side pipelines of sequential steps that automate data processing, integrations and notifications. A workflow is a flat `Steps` array — no Header, DetailTables, Commands or RecordsSettings. Each step has a `KindName` identifying its type: `java_script` (BaSYS.FX script in a separate `.bjs` file), `if` (conditional branching), `iterator` / `iterator_stop` (loop over a DataTable), `data_object_loader` (create / update data objects), `read_file` + `excel_mapping` (Excel import), `http_connector` (HTTP request), `smtp_send` (email), `message` (log), `sleep` (pause). Steps are chained via `PreviousStepUid` and exchange data through a shared `_data` dictionary keyed by step `Name`. JavaScript step bodies are stored as separate `.bjs` files named `workflow.{name}.step.{stepName}.bjs`. Kind `workflow` has `IsReference = false` — no entry in `system/dataTypes.json` is required. Detailed conventions (step kinds and their fields, file naming, step chaining, common patterns) live in the separate **`workflows`** rule. Consult that rule whenever the user asks to create, modify or debug a workflow (процесс), or when editing files under `workflow/` or `*.step.*.bjs` files. Many real examples live under `workflow/`.

# Menus (Меню)

Menus (`menu` kind) describe the navigation tree rendered in the application's side panel by the PrimeVue MegaMenu component (vertical orientation). A `menu` metaobject stores no user data and has no Header / DetailTables / Commands / Forms — only a hierarchical `Items` array. The hierarchy has four levels: root groups (`MenuSettingsGroupItem`, with `Kind = 1` Link / `2` Separator / `3` Group) → columns (`MenuSettingsColumn`) → sub-items / column headings (`MenuSettingsSubItem`) → final links and separators (`MenuSettingsLinkItem`, with `Kind = 1` Link / `2` Separator). A root group can be filled either **manually** (curated subtree) or **automatically** (`AutoFill = true` + `MetaObjectKindUid` — the server lists all active objects of the chosen kind and lays them out into columns of `ItemsPerColumn` items). Several active `menu` metaobjects coexist: the server merges visible groups from all of them, filtered by the current user's access rights. Settings files live at `menu/{name}/menu.{name}.json` and validate against `system/schemas/menuSettings.schema.json`. Kind `menu` has `StoreData = false` and `IsReference = false` — no entry in `system/dataTypes.json` is required, and there are no companion `.bjs` / `.vue` files. Detailed conventions (field reference for each hierarchy level, manual vs auto-fill mode, URL conventions like `/app#/data-objects/{kindName}/{objectName}`, PrimeIcons usage, `MetaObjectKindUidParsed`) live in the separate **`menu`** rule. Consult that rule whenever the user asks to create, modify or debug a menu (меню, навигация, боковое меню, sidebar), to add a link / group / column / separator, to set up auto-fill of a group, or when editing files under `menu/`. Many real examples live under `menu/`.

# Communication and Comments

- Communicate with the user in the language they use in chat (typically Russian).
- Code comments must follow the language already used in the file (typically Russian).
