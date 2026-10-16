# The orchestrator routes, it does not execute

Quality degrades as a context fills, and it degrades gradually: silent partial completion,
vague nouns where a filename belongs, protocol steps skipped. All of it well before any
warning fires. So keep the deciding context small and push consuming work to fresh
subagents.

The orchestrator decides what happens next and checks that it did. Any task that reads a lot
to produce a little belongs somewhere else.

## Keeping the deciding context small

- **Do not read a subagent's definition to brief it.** The definition is for the subagent;
  reading it spends your context to learn something you are about to delegate.
- **Pass paths, not pasted files.** The subagent can open it. You cannot un-read it.
- **Read summaries and headings rather than full bodies**, unless the body drives a decision
  you are about to make.

## The dispatch contract

Every dispatched agent gets, before it starts:

1. **A declared completion signal**, so completion is detected rather than inferred. Use
   structured output where the harness offers it.
2. **A declared artefact**, written to disk, so the result outlives the run.

It owes one thing back: **if it cannot finish, it says so explicitly.** A blocked agent
returning plausible prose is the most expensive failure in the model.

## Delegate, then verify on disk

A subagent's report is a **claim**. Files, tests and gates are the **evidence**. Never mark
delegated work done on the report alone. This is not distrust: the report is generated from
the same context that produced the work, so it carries the same blind spots, and the one
thing a report cannot tell you is what it failed to notice.

## Backgrounded work must leave something behind

Work dispatched to run in the background must write its result somewhere durable before it
exits. A result that existed only in a process that has ended did not happen, and the failure
is silent: a completed job with no output looks exactly like a job that produced nothing.
