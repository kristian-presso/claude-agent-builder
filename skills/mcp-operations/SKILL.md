---
name: mcp-operations
description: Runs a live MCP server or MCP App after it ships - what to record on every tool call, how to read the usage table, the checks that turn raw rows into findings, error and latency targets, changing or retiring a live tool safely, and a weekly review that proposes fixes a human approves. Use when someone asks "how do I know if people use my MCP server", "what should I log for my MCP", "why is my connector's error rate high", "which tools are failing", "my health badge says worth a look", "can I rename this tool", "should I remove this tool nobody calls", "set SLOs for my MCP server" or "run a weekly review of my server". Not for building a server or writing tool descriptions from scratch; use mcp-server-builder in the agent-builder plugin for that.
---

# MCP operations

A server built well and never instrumented is a product nobody can improve: the requests it
fails leave no trace. This skill covers the part after launch. Measure, read, change one thing,
measure again.

It assumes the server exists. For building one, designing tools, auth, transports, tests and
directory submission, use `mcp-server-builder` (agent-builder plugin). For routing evals
(golden prompts, precision and recall), its
[`references/routing-evals.md`](../mcp-server-builder/references/routing-evals.md) is the method; this
skill only adds where the prompts come from once real usage exists.

## Route the question

| The question is about | Read |
| --- | --- |
| What to record, the table shape, the four outcomes, grouping calls without sessions, retention | [references/event-contract.md](references/event-contract.md) |
| Wiring capture into a server: the wrapper, refusal codes, empty results, what the wrapper cannot see | [references/instrumentation.md](references/instrumentation.md) |
| Turning rows into findings: the twelve checks, thresholds, the evidence floor, ready-to-run SQL | [references/signals.md](references/signals.md) |
| What people come for, whether multi-step jobs finish, zero-hit searches | [references/intent-and-outcomes.md](references/intent-and-outcomes.md) |
| Whether an MCP App view actually renders, dead controls, view errors | [references/app-telemetry.md](references/app-telemetry.md) |
| Error-rate and latency targets, what pages someone, the directory health badge | [references/health-and-slos.md](references/health-and-slos.md) |
| Renaming, removing, re-describing a live tool, changing an input schema | [references/release-and-change.md](references/release-and-change.md) |
| Running the weekly improvement pass and writing its report | [references/weekly-review.md](references/weekly-review.md) |
| A server a customer owns: what the builder may see | [references/customer-telemetry.md](references/customer-telemetry.md) |
| Any spec, SDK or directory fact with a date | [references/changes-ledger.md](references/changes-ledger.md) |

Read the file before answering. Quote dated facts with their date and where to re-check them.

## The rules that hold everywhere

1. **Instrument before the first real user.** Usage history cannot be backfilled.
2. **Record the shape, never the content.** Tool name, outcome, reason code, argument names,
   sizes, timings. Never argument values or results: they carry names and emails, and a usage
   table ends up in a spreadsheet eventually.
3. **Refused is not failed.** A refusal is the server working; an error is the server broken.
   A table that merges them hides the most fixable defect there is: a description that sends
   the model to the wrong tool. Keep four outcomes: `ok`, `empty`, `refused`, `error`.
4. **Low volume is not a finding.** Below the evidence floor (3 distinct flows or 2 distinct
   users in the window) a pattern is carried to next week, not acted on. State the count
   beside every rate.
5. **Change one thing at a time,** each in its own release with a version bump, so the next
   window can say whether it worked.
6. **Propose, never apply.** The review drafts pull requests and issues. A person merges.
7. **There are no sessions.** The MCP revision of 2026-07-28 is stateless: no `initialize`,
   no `Mcp-Session-Id`. Do not design anything that groups calls by session id.

## How to work

- **"What should I log?"** Give the event contract, then the wrapper pattern for their SDK.
  If they already log something, map their columns to the contract and name what is missing,
  starting with refusal codes and the `empty` outcome.
- **"Why is X failing / what should I fix?"** Ask for (or query) the last 7 days against the
  prior 28. Run the checks in `signals.md` in order, apply the floor, and report at most five
  findings, each with counts, the likely cause and the fix bucket. If there is no data, say
  so and give the instrumentation step instead of guessing.
- **"Can I rename / remove this tool?"** Answer from `release-and-change.md`: never in one
  step. Give the sequence and the watch condition.
- **Directory badge or error-rate questions:** explain which errors the directory counts
  before suggesting fixes. Its health badge and its error-rate card count different things.

## Output

Findings as a short table: finding, evidence (counts, window, three verbatim asks where they
exist), likely cause, proposed change, and the signal that will show whether it worked. Say
what you could not measure.

## Example

> **User:** My connector's error rate in the directory dashboard is 9% but my logs show almost no 500s. What's going on?
>
> **Answer:** The directory's **Error rate (30d)** card counts tool results with `isError: true` as errors, so every correct refusal (missing argument, not signed in, value not confirmed) counts against it. Its **health badge** does not: the badge counts request-level errors only (5xx, timeouts) and excludes errors a tool returns in its own result (as of 16/10/2026; claude.com/docs/connectors/building/managing-your-listing). So a high card with a healthy badge usually means many refusals, not a broken server.
>
> Split your own log by outcome. If `refused` dominates, group by tool and refusal code: one tool with a 30%+ refusal rate usually has a description that invites calls at the wrong moment. Rewrite that description, re-run your routing eval, ship it alone, and compare the refusal rate next week.

## Configuration

Two things vary: **where usage is stored** (the SQL here is Postgres; the shape works in any
store) and **which SDK the server uses** (the wrapper pattern is shown generically; adapt the
registration hook to your SDK).
