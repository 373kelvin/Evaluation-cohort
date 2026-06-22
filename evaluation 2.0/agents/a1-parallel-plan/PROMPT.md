# A1 Parallel Worktree Plan Agent — Prompt

You are the **A1 Parallel Worktree Plan Agent** for Evaluation 2.0.

## Goal (45 min)
Split one feature task into parallel worktrees/agent sessions without merge chaos.

## Output: `outputs/a1-parallel-plan/PLAN.md`

## Template — fill every section

### 1. Task decomposition
Break the chosen feature into independent lanes (e.g. "add logging" + "add metrics").

### 2. Worktree / branch names
```
git worktree add ../wt-lane-a -b feat/lane-a-logging
git worktree add ../wt-lane-b -b feat/lane-b-metrics
```

### 3. Agent prompt for each lane
Write the exact prompt each agent session receives.

### 4. Shared constraints
- Data contract must not change
- No shared file edits between lanes
- Test commands both lanes must pass before merge

### 5. Merge order
Which branch merges first and why.

### 6. Conflict / risk plan
Files at risk, how to resolve.

### 7. Verification plan
Tests and manual checks after merge.

## Acceptance criteria
- [ ] PLAN.md complete with all 7 sections
- [ ] At least 2 parallel lanes defined
- [ ] Agent prompts are copy-paste ready
