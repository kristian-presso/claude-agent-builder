# Agent builder skills for Claude

**Build MCP servers, MCP Apps and agents that actually work, and prove it before you ship.**

```bash
/plugin marketplace add kristian-presso/claude-agent-builder
/plugin install agent-builder@claude-agent-builder
```

One department of [claude-skills](https://github.com/kristian-presso/claude-skills), where all departments live in one place. Free, MIT licensed, no sign-up.

Six skills for people building things with Claude: MCP servers, the apps that sit on them and running them once they are live, agents that are safe to give real access to, shipping multi-step work with coding agents, and turning a process you do by hand into a skill. They share one conviction: **the expensive failure is not code that breaks; it is work that reports success and is wrong.** Each skill is built around the check that catches its version of that.

## Skills

| Skill | Use it when |
| --- | --- |
| [mcp-server-builder](skills/mcp-server-builder/SKILL.md) | Building or auditing an MCP server: outcome-shaped tools, auth at the boundary, tests, deployment and directory listing. Includes a tested Python starter. |
| [mcp-operations](skills/mcp-operations/SKILL.md) | Your MCP server is live and you want to know what to record on every call, why the directory says your error rate is high, which tools are failing people, how to rename or retire a tool safely, or how to run a weekly improvement pass. Includes tested SQL. |
| [mcp-app-builder](skills/mcp-app-builder/SKILL.md) | Building an MCP App (interactive UI inside the chat) and proving it works before you ship it. |
| [agent-security](skills/agent-security/SKILL.md) | Giving an agent a new tool, credentials or untrusted input. Checks for the lethal trifecta and removes a leg rather than adding warnings. |
| [ship-with-agents](skills/ship-with-agents/SKILL.md) | Running real work through coding agents: discuss, plan, execute, verify blind, ship. |
| [skill-builder](skills/skill-builder/SKILL.md) | Turning a process you do by hand into a reusable skill, with a validator. |

## Tested, not just written

Every skill is evaluated with Claude Code's built-in `claude plugin eval`: each case is run three times with the skill and three times without, graded by a separate model (Sonnet), and a skill ships only if Claude does better with it than without it. Every skill has three cases it should handle and two near-misses it must leave alone. The three skills where plain Claude already did well (agent-security, skill-builder, mcp-server-builder) also have harder cases where an expert answer differs from a generalist one: a recipient allowlist that still leaks other customers' data, an approval step that shows the model's own summary, a summariser sub-agent that launders injection, a server generated one tool per endpoint, JWTs decoded without verifying them, nginx forwarding the wrong Host, drafts lost across instances, a skill that loses its trigger to a sibling, one skill doing three jobs, a live key in a reference file.

| Skill | Cases | Score with | Without | Gain | Before, 16/10/2026 (5 cases): with / without / gain |
| --- | --- | --- | --- | --- | --- |
| mcp-server-builder | 9 | 0.87 | 0.76 | +0.11 | 0.95 / 0.86 / +0.09 |
| mcp-operations | 5 | 1.00 | 0.65 | +0.35 | new in 0.3.0 |
| mcp-app-builder | 5 | 0.96 | 0.71 | +0.25 | unchanged |
| agent-security | 9 | 0.99 | 0.88 | +0.11 | 1.00 / 0.96 / +0.04 |
| ship-with-agents | 5 | 0.93 | 0.64 | +0.29 | unchanged |
| skill-builder | 8 | 0.93 | 0.69 | +0.24 | 0.93 / 0.86 / +0.07 |

New results from 16/10/2026. On the same nine, nine and eight cases, the 0.1.0 skills scored 0.82 / 0.76 (mcp-server-builder), 0.91 / 0.88 (agent-security) and 0.89 / 0.74 (skill-builder), so the gains come from the skills improving, not only from harder cases. The scores on the original five cases are kept for comparison. mcp-server-builder scored 0.90 / 0.76 in 0.2.0 and 0.87 / 0.76 once mcp-operations sat beside it in 0.3.0; the difference is runs where neither skill was invoked, within the run-to-run spread seen across rounds. mcp-operations fired on all 9 runs it should have and on none of the 6 near-misses.

## Install

### Claude Code

On its own, from this repository:

```bash
/plugin marketplace add kristian-presso/claude-agent-builder
/plugin install agent-builder@claude-agent-builder
```

Or with every other department, from the hub:

```bash
/plugin marketplace add kristian-presso/claude-skills
/plugin install agent-builder@claude-skills
```

Use one or the other, not both, or the skills load twice.

### Claude app

On claude.ai or the Claude desktop app, download this repository as a zip (Code, then Download ZIP), take the folder of the skill you want from `skills/` (the one containing `SKILL.md`), zip that folder on its own and upload it in your skills settings. Each skill works on its own.

## What "tested" means here

Both starters were written out from their reference files exactly as published and run on
16 October 2026:

- **mcp-server-builder**: the Python server installs and its 9 tests (in-process and over
  stdio) pass on `mcp` 2.3.0, and on 1.30.0 (the newest 1.x release, 07/09/2026,
  per PyPI) with the one-line import change the reference describes. The Host-allowlist and Content-Type behaviour described in its deployment notes
  was checked by sending real HTTP requests.
- **mcp-app-builder**: the Worker project installs, builds its view, typechecks and bundles,
  and under a local dev server answers `tools/list`, `tools/call` and `resources/read` as the
  verification tiers require.
- **mcp-operations**: every SQL block in its event contract and signal references runs
  against seeded data in a real PostgreSQL 16, locally and in CI, and the signal queries
  return the findings the seed was built to produce.
- **skill-builder**: the validator script needs only Python 3 and was run against every
  skill in this plugin and against deliberately broken ones.

The MCP ecosystem moves fast. Every fact that can change carries the date it was checked and
where to re-check it, and the SDK notes say exactly which version each claim was read from.

## Configuration

Each skill ends with a short **Configuration** section naming the one or two things that
vary: the SDK and runtime you build on, where your specs and test prompts live, which agent
runtime you secure, where your skills are saved. None needs a particular directory layout or
service to work.

## Re-run the evals and tests

The eval cases live in `evals/`, one folder per skill. From the repository root:

```bash
claude plugin eval . --trust-plugin --scaffold --ablation with-without --runs 3 -j 4 \
  --judge-model sonnet --allow-tools Write Edit Bash --no-publish
```

Every push runs the same checks as CI: each skill through the validator, the manifests through `claude plugin validate`, and the unit tests for the bundled scripts:

```bash
for d in skills/*/; do python3 skills/skill-builder/scripts/validate_skill.py "$d"; done
claude plugin validate .
python3 -m unittest discover -s tests -v
```

Tests are standard-library Python, so they need no installs.

## Feedback

Two minutes on [this form](https://tally.so/r/7XlJbL?source=agent-builder) tells me what worked, what broke and what to build next. Every answer gets read. Bugs with steps to reproduce are best as a GitHub issue: if a skill fired when it should not have, did not fire when it should, or produced the wrong thing, tell me what you typed and what happened.

## More departments

This is one of five. [claude-skills](https://github.com/kristian-presso/claude-skills) has all departments in one place: operator discipline, building with Claude, go-to-market, marketing and UK business, installable together or one at a time.

## All of it in one install

These skills also run inside [Corey](https://getcorey.ai), alongside the rest of the library I use to run my business: one install that already knows your business, remembers it between chats and keeps itself up to date. It is free for individuals.

## Licence

[MIT](LICENSE). Take them, fork them, strip the parts you disagree with.

How these were built, and why, is written up at [kristianpapadakis.com/guides](https://kristianpapadakis.com/guides).
