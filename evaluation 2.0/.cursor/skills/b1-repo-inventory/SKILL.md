---
name: b1-repo-inventory
description: B1 evaluation task — generate repo artifact inventory (classes, services, models, configs). Use when asked about B1, artifact inventory, or repo discovery in evaluation 2.0.
---

# B1 Repo Inventory Agent

Run from `evaluation 2.0/` workspace root.

## Command
```bash
python Project-based-entity-diagrams/inventory.py <target> -o outputs/b1-artifact-inventory/<name>-inventory.md
```

## Targets
- `fastapi_transactions`
- `fraud-score-system`
- `.` (full workspace)

## Done when
- Markdown saved under `outputs/b1-artifact-inventory/`
- Lists classes, functions, configs, models, tests, entry points with file:line

Prompt: `agents/b1-repo-inventory/PROMPT.md`
