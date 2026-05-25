# BaSYS-AI Workspace For OpenCode

Read these files at the beginning of every project session:

- `PROJECT_CONTEXT.md` - current project state: where we are, what is done, what is next.
- `OPEN_QUESTIONS.md` - open questions and accepted decisions.

Without these two files, recommendations about the project are likely to be stale.

## Agents

The workspace uses specialized OpenCode agents in separate chats:

- `analyst` - designs solution methodologies and specifications in `project/docs/specs/`.
- `engineer` - implements approved specifications and maintains project infrastructure.
- PM assistant - the coordinating chat: helps the human PM coordinate agents, review artifacts, and maintain workspace documentation.

The human PM approves designs, specifications, implementation plans, and final implementations.

## OpenCode Infrastructure

Before changing `opencode.json`, `.opencode/agent/`, `.opencode/skills/`, plugins, MCP, providers, commands, or permission rules, use the user-level skill `opencode-docs` and verify exact config shapes against `https://opencode.ai/config.json`.

## Path Convention

OpenCode is launched from the workspace root `create-model-2/`. Paths in project instructions are relative to this root.

Exception: `$schema` paths inside BaSYS metadata JSON files are relative to the JSON file itself.

## Workspace Structure

- `project/` - Git repository with project metadata, specifications, ADRs, and documentation.
- `basys-docs/` - local clone of official BaSYS documentation, treated as read-only.
- `basys-docs-index.md` - local map of `basys-docs/ru/`.
- `reference/` - read-only reference export from another BaSYS installation; use for patterns, not UID values.
- `inbox/` - incoming materials for analysis.
- `PROJECT_CONTEXT.md`, `OPEN_QUESTIONS.md` - workspace-level working documents.

## Safety Rules

- Do not edit `reference/` unless explicitly asked.
- Do not edit `basys-docs/` except explicit documentation update operations.
- Before creating, editing, or deleting files, provide a concise action plan and wait for explicit PM approval.
- Legacy Claude Code project files have been removed; use `.opencode/agent/`, `.opencode/skills/`, and `opencode.json` for project instructions.
