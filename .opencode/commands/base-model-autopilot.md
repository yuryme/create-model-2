---
description: Legacy single-agent base model workflow from approved design to metadata implementation; use metadata-autopilot for new reusable runs
agent: build
---

Run the autonomous BaSYS base model workflow end-to-end. This is the historical task-specific single-agent command; for new medium metadata tasks prefer `.opencode/commands/metadata-autopilot.md`.

Input design:
@project/docs/specs/base-model-design.md

Project process references:
@project/docs/workflow.md
@PROJECT_CONTEXT.md
@OPEN_QUESTIONS.md
@project/docs/decisions.md
@project/docs/glossary.md
@project/docs/patterns/metadata-workflow.md

Important authorization:
This command is an explicit PM authorization for this autonomous run.
Do not ask the PM for intermediate approvals during this command.
You may create and edit files required by this workflow, including:
- project/docs/specs/base-model.md
- project/docs/specs/base-model-plan.md
- project/metadata/**
- companion import notes or implementation reports under project/docs/specs/

Do not commit or push.

Role protocol:
You must simulate the required project roles strictly:
1. Analyst writes the full specification from the design.
2. PM Assistant reviews the specification.
3. If the specification has critical defects that would make the future system non-functional, non-importable, or directly contradict the approved design, return it to Analyst and fix it.
4. If the specification has only non-critical methodology gaps or improvement opportunities, record them as notes and approve the specification.
5. Engineer writes the implementation plan.
6. PM Assistant reviews the implementation plan using the same criticality rule.
7. If the plan has critical defects that would make implementation fail or contradict the approved specification, return it to Engineer and fix it.
8. If the plan has only non-critical methodology gaps or improvement opportunities, record them as notes and approve the plan.
9. Engineer implements the metadata in project/metadata/.
10. PM Assistant reviews the implementation diff.
11. Critical implementation defects must be fixed autonomously.
12. Non-critical methodology gaps may be recorded as notes and must not block completion.

Artifact discipline:
Do not create persisted review/audit files for this single-agent run. Keep implementation reports and import notes concise, and extract durable lessons into `project/docs/patterns/`, ADR, workflow, or skills rather than preserving full experiment traces.

Critical defect definition:
A defect is critical only if it would likely cause one of the following:
- BaSYS metadata import failure.
- Broken references, invalid UIDs, invalid schemas, invalid JSON, or missing required standard columns.
- Operation records cannot be created according to the approved specification.
- The resulting model cannot execute the basic acceptance scenarios from the specification.
- The implementation contradicts an explicit approved design decision.
- The implementation edits forbidden locations such as reference/, basys-docs/, basys-cursor-rules/, or generated BaSYS skills.

Non-critical defects:
Do not block completion for these unless they accumulate into a functional failure:
- imperfect naming that is still valid and understandable;
- missing nice-to-have fields;
- report/dashboard omissions not required for acceptance;
- methodology improvements that can be handled in a later block;
- UX/form improvements not required for basic operation.

Mandatory constraints:
- Follow AGENTS.md and project/docs/workflow.md except that this command replaces intermediate human PM approvals for this autonomous run.
- Use the basys-metadata skill before editing project/metadata/.
- Do not edit basys-docs/.
- Do not edit basys-cursor-rules/.
- Do not edit reference/.
- Do not edit generated BaSYS skills.
- Use project/metadata/system/ as the only source of kind/type UIDs.
- New object and column Name values must be Latin snake_case.
- Keep Memo concise and Russian.
- Before implementation, inspect current project/metadata/ and respect the actual current baseline.
- Current intended first version excludes cash desk, currencies, cost of goods sold, gross profit, income/expense register, and opening balances.

Expected workflow outputs:
1. Create or update project/docs/specs/base-model.md with status approved after autonomous review.
2. Create or update project/docs/specs/base-model-plan.md with status approved after autonomous review.
3. Implement approved metadata under project/metadata/.
4. Provide import instructions, either in the final response or in a companion file if non-trivial.
5. Provide final report with:
   - files created/changed;
   - review notes accepted as non-critical;
   - critical defects found and fixed;
   - verification performed;
   - remaining risks;
   - import sequence.

Execution discipline:
- Work until the workflow is complete or blocked.
- If blocked by missing platform facts, read basys-docs/ and local schemas first.
- Ask the PM only if there is a genuine architectural contradiction that cannot be resolved from the approved design and current metadata.
- Do not stop after writing the specification; continue to plan and metadata implementation.
