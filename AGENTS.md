# BaSYS-AI Workspace For OpenCode

Read these files at the beginning of every project session:

- `Claude_Context.md` - current project state: where we are, what is done, what is next.
- `OPEN_QUESTIONS.md` - open questions and accepted decisions.

Without these two files, recommendations about the project are likely to be stale.

## Roles

The workspace uses three assistant roles in separate chats:

- `/analyst` - Analyst: designs specifications in `project/docs/specs/`.
- `/engineer` - Engineer: implements approved specifications and maintains infrastructure.
- PM assistant - this chat: helps the human PM coordinate roles, review artifacts, and maintain workspace documentation.

The human PM approves designs, specifications, implementation plans, and final implementations.

## Path Convention

OpenCode is launched from the workspace root `create-model-2/`. Paths in project instructions are relative to this root.

Exception: `$schema` paths inside BaSYS metadata JSON files are relative to the JSON file itself.

## Workspace Structure

- `project/` - Git repository with project metadata, specifications, ADRs, and documentation.
- `basys-docs/` - local clone of official BaSYS documentation, treated as read-only.
- `basys-docs-index.md` - local map of `basys-docs/ru/`.
- `reference/` - read-only reference export from another BaSYS installation; use for patterns, not UID values.
- `inbox/` - incoming materials for analysis.
- `Claude_Context.md`, `OPEN_QUESTIONS.md`, `RETROSPECTIVE.md` - workspace-level working documents.

## Safety Rules

- Do not edit `reference/` unless explicitly asked.
- Do not edit `basys-docs/` except explicit documentation update operations.
- Before creating, editing, or deleting files, provide a concise action plan and wait for explicit PM approval.
- Do not remove legacy `.claude/` files until the OpenCode replacement is verified and the PM approves cleanup.
