# Verify blind

The verifier gets the acceptance criteria and the diff. **Not** the plan, not the execute
summaries, not the conversation that produced them.

## Why withholding is the mechanism

An agent that read the plan verifies the plan. It inherits the builder's assumptions and
confirms the work matches its own intention rather than that it achieves the goal. The result
reads like a verification and is worth nothing, because the two minds agreeing were the same
mind.

Withholding the context is not a formality around the check. It **is** the check.

That is also why the builder should not verify its own work even when it is the cheapest
option. It is blind to exactly the assumptions that produced the defect.

## How to dispatch it

In Claude Code, start a subagent (or a fresh session) whose prompt contains only:

1. the acceptance criteria, verbatim;
2. the diff, or the branch name to diff against main;
3. the instruction to report each criterion as pass, fail or unmeasured, with the evidence
   (command and output, file and line), and to say which criteria it could not run and why.

Do not paste the plan "for context". If a criterion genuinely cannot be settled without it,
the verifier marks it unmeasured and says why.

## When the plan arrives anyway

Ignore it. Reaching for it converts an honest gap into a false pass, and the false pass is
not recoverable later because nothing records that it happened.

## When blind verification is impossible

Say so. Some work cannot be verified from a fresh context: a judgement about tone, a change
whose correctness depends on a conversation with a person. Presenting that as independently
verified misstates the strength of the evidence.

The honest report names what ran, what did not, and why. "Static and protocol checks
passed, the rendered check did not run" is useful. "Verified" is not.

## Standing checks come first

A spec's own criteria are additional to the checks every artefact of its kind owes (tests
pass, types check, the linter is clean, the thing builds). A build that satisfies its spec
and fails the standing checks has been asked the wrong questions.
