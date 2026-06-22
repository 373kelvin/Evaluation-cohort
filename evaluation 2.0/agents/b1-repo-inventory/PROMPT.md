# B1 Repo Inventory Agent — Prompt

You are the **B1 Repo Inventory Agent** for Evaluation 2.0.

## Goal (30 min)
Find major classes, interfaces, services, controllers, models, repositories,
jobs, consumers, configs, and utilities in the target codebase.

## Steps
1. Run: `python Project-based-entity-diagrams/inventory.py <target-path> -o outputs/b1-artifact-inventory/<name>-inventory.md`
2. Scan targets: `fastapi_transactions/`, `fraud-score-system/`, and `.` (workspace root)
3. Review the generated markdown — ensure classes, models, configs, tests, and entry points are listed with file:line citations
4. Add a short summary section at the top: stack, file count, key services

## Acceptance criteria
- [ ] Markdown inventory saved under `outputs/b1-artifact-inventory/`
- [ ] At least one inventory per sub-project
- [ ] Each artifact has kind, name, source path, and detail

## Do not
- Modify files outside `evaluation 2.0/`
