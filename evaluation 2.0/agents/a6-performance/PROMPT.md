# A6 Performance Agent — Prompt

You are the **A6 Performance Agent** for Evaluation 2.0.

## Goal (90 min)
Find a real bottleneck, make a measurable minimal improvement without broad rewrite.

## Target candidates
- `fastapi_transactions/app/main.py` — balance calculation on every GET
- `fraud-score-system/worker/worker.js` — polling interval, sequential scoring
- `Project-based-entity-diagrams/analyze.py` — file scan speed

## Output: `outputs/a6-performance/PROFILE.md`

## Sections

### 1. Baseline measurement
Method (timeit, pytest-benchmark, curl loop) and numbers.

### 2. Profiling approach
What tool (cProfile, console.time, hyperfine) and what it showed.

### 3. Bottleneck explanation
Short, evidence-based.

### 4. Targeted code change
Small focused diff in `evaluation 2.0/` only.

### 5. After measurement
Same method, show improvement percentage.

### 6. Behavior unchanged
Tests still pass.

## Acceptance criteria
- [ ] Before/after numbers with same methodology
- [ ] Change is <50 lines
- [ ] Tests pass after change
