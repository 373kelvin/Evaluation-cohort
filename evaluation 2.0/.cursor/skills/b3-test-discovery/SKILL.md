---
name: b3-test-discovery
description: B3 evaluation task — discover tests, run them, save results. Use when asked about B3, test discovery, or test execution in evaluation 2.0.
---

# B3 Test Discovery Agent

## Command
```bash
./scripts/run_all_tests.sh
```

## Output
- `outputs/b3-test-results/RESULTS.md` — framework, files, commands, interpretation
- `outputs/b3-test-results/test-run.log` — raw terminal output

## Projects
| Project | Framework | Tests |
|---------|-----------|-------|
| fastapi_transactions | pytest | 8 |
| fraud-score-system/service | pytest | 4 |
| fraud-score-system/engine | cargo test | 4 |
| integration | pytest | 1 e2e |

Prompt: `agents/b3-test-discovery/PROMPT.md`
