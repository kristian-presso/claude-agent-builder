# Gates before, not regret after

Name each checkpoint **before** the work starts, because the type of gate sets the recovery.
A checkpoint improvised when something goes wrong is chosen under pressure by whoever is
already committed to the work.

| Gate | Fires when | Recovery |
| --- | --- | --- |
| **Pre-flight** | a precondition is missing | block entry, before any partial work exists |
| **Revision** | the output is wrong but the approach is right | loop back to the producer with specific feedback |
| **Escalation** | the decision is not yours to make | hand it over as finding, recommendation, action |
| **Abort** | continuing would do damage or waste | stop, preserving state so it can resume |

## Pre-flight blocks entry

The value is entirely in the timing. A missing precondition caught before work starts costs
nothing. Caught halfway, it leaves partial work someone has to decide whether to keep, and
partial work is almost always kept because discarding it feels wasteful.

## Revision is capped

Three iterations. Escalate early if the issue count stops falling between them. An uncapped
revision loop becomes a slow failure nobody declares, because each lap looks like progress.
The count not falling means the feedback is not landing, and another lap will not change that.

## Escalation hands over a decision, not a problem

The shape: **the finding, one recommended path with its reason, and the action already taken
or one labelled question.** Not a menu, and not a description of the difficulty.

An escalation presenting balanced options is usually avoiding the recommendation. The person
you escalate to has less context than you, so a neutral menu hands the hardest judgement to
the person least equipped for it. Recommend, then let them overrule you.

Escalate on **access**: a signature, a credential only a person holds, a console with no API,
a decision that binds someone's name. Not because the judgement feels hard.

## Abort preserves state

Stopping is legitimate and must not be destructive. Leave the work resumable, say what was
and was not done, and say what would need to change for it to continue.

## The failure all four exist to prevent

A blocked agent that returns plausible prose instead of declaring the block. The work routes
onward as though it succeeded, every downstream step compounds it, and by the time it
surfaces the evidence of where it started has been overwritten.
