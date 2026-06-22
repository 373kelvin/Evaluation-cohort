# A2 Worktree Execute Agent — Prompt

You are the **A2 Worktree Execute Agent** for Evaluation 2.0.

## Goal (90 min)
Create two parallel worktrees, make independent changes, reconcile cleanly.

## Output: `outputs/a2-worktrees/EXECUTION.md`

## Steps
1. Follow the plan from `outputs/a1-parallel-plan/PLAN.md` (or create one inline)
2. Document every command:
   ```bash
   git worktree add ../wt-lane-a -b feat/lane-a
   git worktree add ../wt-lane-b -b feat/lane-b
   ```
3. Record separate outputs from each lane (files changed, test results)
4. Merge or rebase steps with conflict notes
5. Final test run after merge

## EXECUTION.md sections
- Commands used to create worktrees
- Branch / worktree names
- Lane A output (changes + test result)
- Lane B output (changes + test result)
- Merge / reconcile steps
- Final test result
- Conflict notes (or "none")

## Acceptance criteria
- [ ] Two worktrees actually created (or documented why not)
- [ ] Independent changes in each lane
- [ ] Clean merge with passing tests
