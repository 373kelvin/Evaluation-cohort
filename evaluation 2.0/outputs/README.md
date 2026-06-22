# Agent outputs

Each evaluation agent writes deliverables here. Regenerate with the scripts
in `scripts/` or by running the agent prompts in `agents/`.

| Task | Output folder | How to generate |
|------|---------------|-----------------|
| B1 | `b1-artifact-inventory/` | `python Project-based-entity-diagrams/inventory.py ..` |
| B2 | `b2-endpoint-map/` | `python Project-based-entity-diagrams/analyze.py ../fastapi_transactions -o b2-endpoint-map/...` |
| B3 | `b3-test-results/` | `./scripts/run_all_tests.sh` |
| A1 | `a1-parallel-plan/` | Fill via agent prompt in `agents/a1-parallel-plan/` |
| A2 | `a2-worktrees/` | Fill via agent prompt in `agents/a2-worktrees/` |
| A4 | `a4-modernization/` | Fill via agent prompt in `agents/a4-modernization/` |
| A5 | `a5-code-review/` | Fill via agent prompt in `agents/a5-code-review/` |
| A6 | `a6-performance/` | Fill via agent prompt in `agents/a6-performance/` |
