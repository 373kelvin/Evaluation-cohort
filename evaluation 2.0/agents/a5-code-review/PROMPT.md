# A5 Code Review Agent — Prompt

You are the **A5 Code Review Agent** for Evaluation 2.0.

## Goal (60 min)
Review agent-generated code for correctness, security, tests, performance, maintainability.

## Output: `outputs/a5-code-review/REVIEW.md`

## Review targets
- `fastapi_transactions/app/main.py` — thread safety, validation
- `fraud-score-system/worker/worker.js` — error handling, spawn security
- `fraud-score-system/engine/src/main.rs` — input parsing, score clamping
- `Project-based-entity-diagrams/insight/features.py` — regex accuracy

## REVIEW.md format

For each issue:
| # | Severity | Blocking? | File | Issue | Suggested fix | Verification |
|---|----------|-----------|------|-------|---------------|--------------|

Severity: critical / high / medium / low / info

## Acceptance criteria
- [ ] ≥5 issues identified across projects
- [ ] Each issue has severity and fix suggestion
- [ ] At least one blocking and one non-blocking issue
- [ ] Verification step for each fix
