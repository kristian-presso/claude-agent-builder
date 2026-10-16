---
name: ship-with-agents
description: Runs multi-step software work with coding agents through a five-step loop (Discuss, Plan, Execute, Verify, Ship), each ending in an artefact on disk, with acceptance criteria written before the build that can actually fail, blind verification by an agent that never saw the plan, named gates and escalation, and context-budget checkpoints. Use when a task spans more than one phase, file area or repository, will take more than a couple of hours, is being split across subagents, or when someone asks "plan this build", "how do I know the agent actually finished", "verify this properly", or "set up a workflow for shipping with Claude Code".
---

# Ship with agents

How a piece of work moves from idea to merged when an agent is doing the building. Five
steps, each ending in an artefact written to disk:

**Discuss, Plan, Execute, Verify, Ship.**

State lives in those artefacts, never in the conversation. If the work cannot be resumed by a
fresh session after the context is cleared, it is not finished.

The step that gets skipped is **Verify**. A run that completes every task and misses the
point reports success in the same words as one that succeeded. Two things make Verify real:
criteria written in Discuss that **can fail**, and a verifier that works **blind**.

## When to use the loop

Any one of these means start at Discuss:

- more than one distinct phase;
- more than one repository or layer touched;
- the file list is not obvious up front;
- more than one decision to lock before building;
- more than roughly two hours of focused work.

Below that bar, a mechanical single-file change goes straight to Execute. Say which mode is
in play when it is not obvious.

## The loop

| Step | Ends in | Done means |
| --- | --- | --- |
| **Discuss** | a spec with acceptance criteria | what is built, and what is explicitly out of scope, are written down |
| **Plan** | a task list | each task names the files it touches and how it will be verified |
| **Execute** | one commit per task | the work is committed, not sitting in a working tree |
| **Verify** | a verification report | did it achieve the outcome, not just complete the tasks |
| **Ship** | a merged pull request | landed, branch cleaned up |

Detail and the reasons behind each step: [references/the-loop.md](references/the-loop.md).

### 1. Discuss

- **First, check whether someone is already doing this.** Open pull requests, issues, remote
  branches, other working trees. Agents share no memory, and from inside a session the job
  always looks unclaimed.
- Write the goal, the out-of-scope list, and the **acceptance criteria**. Apply one test to
  each criterion: **could a wrong build pass it?** If yes, rewrite it. Read
  [references/acceptance-criteria.md](references/acceptance-criteria.md).
- Name the gates now, not when something goes wrong: see step 4 below.

### 2. Plan

A task list where every task names its files and its check. If you cannot name the check, the
task is not understood yet.

### 3. Execute

One commit per task. Delegate reading-heavy work to subagents and keep the deciding context
small: see [references/orchestration.md](references/orchestration.md). Every dispatched agent
gets a declared completion signal and a declared artefact, and must say so explicitly if it
cannot finish.

Watch the context budget. Past about half, economise. Past about seventy per cent, write the
checkpoint artefact now. See [references/context-budget.md](references/context-budget.md).

### 4. Gates, named up front

| Gate | Fires when | Recovery |
| --- | --- | --- |
| Pre-flight | a precondition is missing | block entry before any partial work exists |
| Revision | output wrong, approach right | loop back with specific feedback, **at most three times**; escalate early if the issue count stops falling |
| Escalation | the decision is not yours | hand over a finding, one recommendation and the action taken or one labelled question |
| Abort | continuing would do damage | stop, leave state resumable, say what would need to change |

Escalate on **access** (a signature, a credential only a person holds, a decision that binds
someone's name), not on hesitation. See
[references/gates-and-escalation.md](references/gates-and-escalation.md).

### 5. Verify, blind

Dispatch a fresh agent with the **acceptance criteria and the diff only**: not the plan, not
the execute summaries, not this conversation. An agent that read the plan verifies the plan.
See [references/blind-verification.md](references/blind-verification.md).

Every criterion reports **pass**, **fail** or **unmeasured**. Unmeasured blocks a ship
exactly as fail does. Before trusting a green result, read
[references/what-a-check-proves.md](references/what-a-check-proves.md): a check proves only
what it exercised.

### 6. Ship

Merge, or say plainly why it is held. Green, reviewed work in an unmerged branch decays.

## Rules

- A subagent's report is a claim. Files, tests and gates are the evidence. Never mark
  delegated work done on the report alone.
- A blocked step must declare the block. Plausible prose from a blocked step is the most
  expensive failure in the whole model, because the work routes onward as if it succeeded.
- The builder does not verify its own work.
- "Verified" is not a report. "Static and protocol checks passed, the rendered check did not
  run" is.

## Example

> "Add CSV export to the reports page and the API."

Discuss: two layers, so loop. Check for open pull requests touching export. Out of scope:
Excel format. Criteria include "an export of a report with zero rows returns a header-only
CSV and a 200, not a 500 or an empty body" and "a field containing a comma round-trips through
export and re-import unchanged". Plan: three tasks, each with its test. Execute: three
commits. Verify: a fresh agent gets the criteria and the diff, and reports "5 pass, 1
unmeasured: the large-export timeout needs a dataset the repo does not have". That
unmeasured item blocks the merge until a fixture exists.

## Configuration

Two things vary: **where the artefacts live** (a `docs/specs/` folder, issue descriptions,
or pull request bodies all work if they persist), and **how verification is dispatched**
(a subagent in your agent harness, a second session, or a colleague).
