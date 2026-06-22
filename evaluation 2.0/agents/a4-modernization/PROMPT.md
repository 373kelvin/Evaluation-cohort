# A4 Modernization Agent — Prompt

You are the **A4 Modernization Agent** for Evaluation 2.0.

## Goal (90 min)
Analyze the repo for modernization opportunities, prioritize, implement the highest-value lowest-risk first step.

## Output: `outputs/a4-modernization/PLAN.md`

## Sections

### 1. Findings (with file evidence)
Scan `fastapi_transactions/`, `fraud-score-system/`, `Project-based-entity-diagrams/` for:
- Missing CI/CD
- No pinned dependencies / lock files
- In-memory storage limitations
- Missing `.gitignore` entries
- Duplicate code between projects
- Security smells

Cite specific files and lines.

### 2. Prioritized plan
Rank findings by value vs risk.

### 3. First step implemented
Implement ONE small change (e.g. add `pyproject.toml`, add root `.gitignore` rule, pin deps).

### 4. Verification
Show build/test/lint output after the change.

### 5. Rollback notes
How to revert the first step.

## Acceptance criteria
- [ ] Findings cite real files
- [ ] One concrete change implemented in `evaluation 2.0/` only
- [ ] Tests still pass after change
