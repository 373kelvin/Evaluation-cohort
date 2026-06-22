# AI Agent Directory — Evaluation 2.0

Use this file to pick the right agent for each evaluation task.

## Basic tasks (B1–B4)

### B1 — Repo Inventory Agent
- **Skill:** `.cursor/skills/b1-repo-inventory/SKILL.md`
- **Prompt:** `agents/b1-repo-inventory/PROMPT.md`
- **Action:** Run `python Project-based-entity-diagrams/inventory.py <target>` and save to `outputs/b1-artifact-inventory/`
- **Finds:** classes, models, services, configs, utilities, entry points

### B2 — API Endpoint Agent
- **Skill:** `.cursor/skills/b2-api-endpoints/SKILL.md`
- **Prompt:** `agents/b2-api-endpoints/PROMPT.md`
- **Action:** Run analyzer on each service; produce route map with file:line citations
- **Output:** `outputs/b2-endpoint-map/`

### B3 — Test Discovery Agent
- **Skill:** `.cursor/skills/b3-test-discovery/SKILL.md`
- **Prompt:** `agents/b3-test-discovery/PROMPT.md`
- **Action:** Run `./scripts/run_all_tests.sh`; document framework, files, commands, results
- **Output:** `outputs/b3-test-results/RESULTS.md`

### B4 — FastAPI Greenfield Agent
- **Skill:** `.cursor/skills/b4-fastapi-greenfield/SKILL.md`
- **Prompt:** `agents/b4-fastapi-greenfield/PROMPT.md`
- **Project:** `fastapi_transactions/`
- **Must deliver:** POST/GET `/transactions`, GET `/balance`, validation, ≥3 tests, README

---

## Advanced tasks (A1–A6)

### A1 — Parallel Worktree Plan Agent
- **Skill:** `.cursor/skills/a1-parallel-plan/SKILL.md`
- **Prompt:** `agents/a1-parallel-plan/PROMPT.md`
- **Output template:** `outputs/a1-parallel-plan/PLAN.md`
- **Deliver:** task decomposition, branch names, agent prompts per lane, merge order

### A2 — Worktree Execute Agent
- **Skill:** `.cursor/skills/a2-execute-worktrees/SKILL.md`
- **Prompt:** `agents/a2-execute-worktrees/PROMPT.md`
- **Output template:** `outputs/a2-worktrees/EXECUTION.md`
- **Deliver:** git worktree commands, lane outputs, merge steps, test results

### A3 — Polyglot System Agent
- **Skill:** `.cursor/skills/a3-polyglot-system/SKILL.md`
- **Prompt:** `agents/a3-polyglot-system/PROMPT.md`
- **Project:** `fraud-score-system/`
- **Must deliver:** FastAPI + Node worker + Rust CLI, data contract, tests, `./run.sh`

### A4 — Modernization Agent
- **Skill:** `.cursor/skills/a4-modernization/SKILL.md`
- **Prompt:** `agents/a4-modernization/PROMPT.md`
- **Output template:** `outputs/a4-modernization/PLAN.md`
- **Deliver:** findings with evidence, prioritized plan, one implemented step

### A5 — Code Review Agent
- **Skill:** `.cursor/skills/a5-code-review/SKILL.md`
- **Prompt:** `agents/a5-code-review/PROMPT.md`
- **Output template:** `outputs/a5-code-review/REVIEW.md`
- **Deliver:** issue list, severity, fixes, verification steps

### A6 — Performance Agent
- **Skill:** `.cursor/skills/a6-performance/SKILL.md`
- **Prompt:** `agents/a6-performance/PROMPT.md`
- **Output template:** `outputs/a6-performance/PROFILE.md`
- **Deliver:** baseline numbers, profile, targeted fix, after numbers

---

## Agent invocation examples

```
# In Cursor Agent chat (with evaluation 2.0 as workspace root):

"Run the B1 Repo Inventory Agent on fraud-score-system and save output."

"Execute B3 Test Discovery Agent — run all tests and write RESULTS.md."

"Use A3 Polyglot System Agent to verify fraud-score-system end-to-end."
```

Each skill contains full acceptance criteria so the agent knows when the task is done.
