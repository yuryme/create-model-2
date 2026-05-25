# Контекст проекта

> **Назначение.** Снимок текущего состояния workspace для быстрой пересборки картины в новой сессии или после компрессии контекста.
> **Не дублировать:** обсуждения и очередь вопросов → `OPEN_QUESTIONS.md`; формальные архитектурные решения → `project/docs/decisions.md`.
> **Поддерживает AI-ассистент** — обновляет в конце смысловой главы работы.

**Последнее обновление:** 2026-05-25 — Аналитик и Инженер переведены из role-skills в OpenCode agents; workspace очищен от legacy Claude Code infrastructure и старых тестовых результатов.

---

## Где мы сейчас

Проект разворачивает рабочий процесс совместной разработки человек-ИИ для автоматизации учётных задач на платформе BaSYS. Прикладная конфигурация описывается JSON-метаданными: справочники, документы, регистры, отчёты, меню, workflow и серверные `.bjs`-скрипты.

Workspace работает в OpenCode из корня `create-model-2/`. Все пути в инструкциях относительны этому корню. Исключение: `$schema` внутри JSON-метаданных относителен самому JSON-файлу.

## Агенты

- **analyst**: OpenCode agent для проектирования методик и ТЗ в `project/docs/specs/`; не правит `project/metadata/`.
- **engineer**: OpenCode agent для реализации approved-ТЗ, планов реализации, изменений `project/metadata/` и инструкций импорта.
- **Ассистент PM**: текущий координационный чат; ведёт контекст, ревьюит артефакты, помогает PM принимать этапы.
- **PM**: пользователь; утверждает методики, ТЗ, планы и реализации.

## Что построено

- `opencode.json` — проектная конфигурация OpenCode, подключает `AGENTS.md` и `.opencode/skills/`.
- `AGENTS.md` — постоянная инструкция workspace для OpenCode.
- `.opencode/agent/` — OpenCode agents: `analyst`, `engineer`.
- `.opencode/skills/` — OpenCode skills. BaSYS metadata skills are generated from `BaSYS.CursorRules`; operational/project skills are maintained locally.
- `basys-cursor-rules/` — локальный read-only clone `https://github.com/BaSysTeam/BaSYS.CursorRules`, branch `main`, source of truth для generated BaSYS skills.
- User-level `opencode-docs` skill — справочник по актуальной документации OpenCode; использовать перед изменениями OpenCode-инфраструктуры.
- `project/metadata/` — чистая стартовая BaSYS-модель: `system/`, `catalog/product_group`, `menu/main`.
- `project/docs/` — ADR, словарь, шаблоны, будущие ТЗ, методики, планы и материалы интервью.
- `basys-docs-index.md` — карта локальной документации BaSYS.
- `reference/` — read-only корпус примеров из другой BaSYS-инсталляции; использовать только как банк паттернов, не как источник UID.
- `inbox/` — зона входящих материалов.

## Git

- Новый репозиторий инициализирован в корне `create-model-2/`.
- Remote: `https://github.com/yuryme/create-model-2.git`.
- Ветка: `main`, initial commit `e65e9f6` уже запушен.
- Старый репозиторий `create-model-1` не используется и не должен изменяться в рамках этого workspace.
- `basys-docs/` исключён из репозитория.

## Важные правила

- Перед созданием, редактированием или удалением файлов ассистент даёт краткий план и ждёт явного одобрения PM.
- `reference/` не редактировать без явного запроса.
- `basys-docs/` не редактировать, кроме явного обновления документации.
- `basys-cursor-rules/` не редактировать; обновлять только через `git pull --ff-only`.
- Generated BaSYS skills не редактировать вручную; синхронизировать только через `basys-cursor-rules-sync`.
- UID видов, типов, стандартных колонок и схем брать только из `project/metadata/system/`.
- Новые `Name` объектов и колонок — латиница `snake_case`, максимум 30 символов.
- При любой реализации Инженер обязан дать инструкцию импорта в BaSYS.

## Что следующее

1. Проверить diff после очистки.
2. По одобрению PM сделать commit и push cleanup-изменений.
3. После перезапуска OpenCode проверить agents `analyst` и `engineer`.
4. Определить боевую предметную область проекта.
