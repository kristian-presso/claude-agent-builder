# Checkpoint before the wall

Watch context usage and change behaviour as it climbs, rather than working normally until it
runs out.

| Past roughly | Do this |
| --- | --- |
| half | economise: read headings and summaries, inline less, and tell the person the budget is getting heavy |
| seventy per cent | write the durable checkpoint artefact **now** |

**A checkpoint the person has to ask for was left too late.**

## Why a warning is not enough

Degradation starts long before the limit and does not announce itself:

- **Silent partial completion.** Four of five things done, reported as done.
- **"Appropriate handling" in place of specifics.** Vague nouns where a filename belongs.
- **Skipped protocol steps.** The verify, the gate, the artefact.

None of those throw. They read as slightly less crisp work, which a reader attributes to the
task being hard rather than the context being full.

## The checkpoint is an artefact, not a message

"I am running low on context" is not a checkpoint. A checkpoint is written to disk: the spec,
the plan with its state, what is done and what remains. The test is the one that governs the
whole loop: can a fresh session resume from what is on disk?

Write it while there is budget left to write it well. An artefact produced at ninety-five per
cent is produced by exactly the degraded process this rule routes around.

## The same instinct elsewhere

Notice a resource getting scarce and change behaviour before it binds: a revision loop's
iteration cap, a session's wall-clock, a rate limit. Anywhere failure arrives as degradation
rather than as an error.
