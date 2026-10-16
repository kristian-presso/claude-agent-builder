# The loop

Five steps. Each ends in an artefact on disk, and the artefact is the handover: the next step
reads it rather than remembering the conversation.

## Why an artefact per step

Because the alternative is a conversation, and a conversation is not state. Three things go
wrong when the loop runs in the chat:

- The session ends, is cleared or is compacted, and the plan is gone. What survives
  summarisation is never the specifics.
- Nobody else can pick the work up. A colleague, a fresh session or a subagent has nothing
  to read.
- Nothing can be checked. A criterion that exists only as something the model said cannot
  be run against the build.

The rule generalises: **if it cannot be resumed after the context is cleared, it is not
finished.** That applies to a decision as much as to code.

## Discuss is not a preamble

It is the step that decides whether Verify can work at all, because it is where acceptance
criteria are written. Criteria are cheap while the goal is still being decided and expensive
to reconstruct afterwards.

Out of scope is written down for the same reason. An agent given a goal and no boundary will
helpfully widen it, and the widening is invisible in the diff because every addition looks
reasonable.

## Discuss opens by asking who else is doing this

Where more than one agent works a repository, they share no memory, and each begins
convinced the job is unclaimed. The signals are cheap and external: open pull requests, open
issues, remote branches, other working trees on the machine.

Accept that early is not early enough: the first moment one agent's intent is visible to
another is usually a pull request, by which point the work exists. Still worth catching. A
duplicate found then costs a conversation; found at merge it costs a revert, or worse, two
copies of one concept that later disagree. Report rather than block: parallel work is normal.

## Plan names files and checks

Each task says which files it touches and how it will be verified. A task whose check cannot
be named is not understood yet.

## Execute commits per task

One commit per task, not one at the end. A single commit spanning a whole plan cannot be
reverted selectively, cannot be reviewed in pieces, hides the order things happened, and
loses the cheapest evidence of where a regression entered.

## Verify is goal-backward

Not "were the tasks done" but "is the outcome achieved". See
[blind-verification.md](blind-verification.md) and
[what-a-check-proves.md](what-a-check-proves.md).

## Ship is a step

Work that is green, gated and reviewed but unmerged is not shipped, and it decays: the base
moves, the context is lost, and someone has to reconstruct why it exists. Finish it or say
plainly why it is held.
