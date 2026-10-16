# Testing a skill

A skill is tested on two separate questions: **does it trigger** when it should (and not when
it should not), and **does it do the job well** once triggered.

## Write the tests before polishing the body

The authoring guidance from the people who build the skills feature is to write evaluations
first: run representative tasks without the skill, note where Claude falls short, write at
least three prompts covering those gaps, and only then write the minimum instructions that
close them. Writing the tests after the skill tests what you wrote.

## The three prompts

Keep them in `evals.md` beside SKILL.md (template in
[../templates/evals.md](../templates/evals.md)):

1. **Plain trigger.** The obvious phrasing. Should trigger.
2. **Vague trigger.** How the person actually talks on a busy day. Should trigger.
3. **Near miss.** Shares words with the skill but is a different job. Should **not** trigger.

For each, write what a good result contains: specific, checkable items ("three bullets",
"flags the 12 per cent drop", "does not invent a figure the CSV lacks"), not "a good summary".

Add more over time from real requests that went wrong.

## Running them

In a fresh session with the skill installed:

1. Send each prompt. Check whether the skill loaded (in Claude Code it is named when it is
   used; in claude.ai, Claude's reasoning shows it reading the skill).
2. Check the output against the expected items.
3. Record pass or fail per prompt.

If triggering fails, change the description (see
[writing-the-description.md](writing-the-description.md)). If the output fails, change the
body. One change at a time, then re-run all three: a fix for one prompt can break another.

If you can, try it with a smaller and a larger model. A smaller model may need more explicit
steps; a larger one may be over-directed by the same text.

## Watch real use

After a week of use, look at what actually happened:

- references Claude never opens: delete them, or say more clearly when to read them;
- a reference Claude opens every time: its content belongs in SKILL.md;
- steps it skips: they are probably buried or vague;
- requests that should have triggered it and did not: add their phrasing to the description.
