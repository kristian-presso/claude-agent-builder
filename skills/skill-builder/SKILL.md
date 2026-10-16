---
name: skill-builder
description: Turns a process someone already does by hand into a reusable Claude skill - a folder with a SKILL.md (name and description frontmatter), optional references/ for depth and scripts/ for deterministic steps. Interviews one step at a time, writes the trigger description, keeps the body lean, writes three test prompts, validates the folder with a bundled script and packages it for Claude Code or claude.ai. Use when someone says "make this a skill", "build a skill", "turn this into a skill", "write a SKILL.md", "why isn't my skill triggering", or describes a task they keep explaining to Claude from scratch.
---

# Skill builder

A skill is a folder Claude loads when a request matches its description: a `SKILL.md` with
`name` and `description` frontmatter, plus optional `references/` (read only when needed)
and `scripts/` (run, not read). This skill captures a process the person already does by
hand and writes that folder.

The description decides whether the skill is ever used. The body decides whether it is used
well. Most of the work is those two things, plus a test.

## Step 1 - interview, one question at a time

Ask each in turn and reflect the answer back. Keep it tight: this is a build interview, not
a business review. Skip any question the conversation has already answered.

1. **The job.** In one sentence, what does the skill do and what does it produce?
2. **The triggers.** What would they actually type when they want this? Collect three to six
   real phrasings, including the vague ones ("can you tidy up this week's numbers").
3. **The walk-through.** Have them walk the manual process step by step, with a real example
   if they have one. Ask what they check before calling it done.
4. **The judgement calls.** Where do they decide something rather than follow a rule? What
   goes wrong when a newcomer does it?
5. **The material.** Is there anything Claude should look up rather than know: a style guide,
   a checklist, an API's two or three endpoints, example inputs and outputs? That becomes
   `references/`. Is there a step that must be exact every time (a calculation, a format
   conversion, a validation)? That becomes a script.
6. **The limits.** What must it never do? Does it write to anything or send anything outward?
   If so, which steps need a person to approve first?
7. **What varies.** Which one or two things differ between people or projects (an output
   folder, a house style, an account)? Everything else is fixed in the skill.

## Step 2 - write the description first

The description is loaded for every skill on every request, and it is what Claude matches
against. Get it right before the body. Read
[references/writing-the-description.md](references/writing-the-description.md). In short:

- Third person: "Builds ...", "Reviews ...", never "I can ..." or "You can ...".
- What it does, then **when to use it**, with the concrete phrases from question 2.
- Name the inputs and outputs a request would mention (file types, tools, nouns).
- Under 1,024 characters for Claude Code and the API. claude.ai's upload form shows a
  shorter limit (200 characters as of October 2026): if they will upload it there, keep the
  first 200 characters self-sufficient. Verify current limits at
  support.claude.com and platform.claude.com/docs.
- No XML tags such as `<example>`. A lone `<` or `>` is allowed.

## Step 3 - write the folder

Use the templates in [templates/](templates/):

- [templates/skill-template.md](templates/skill-template.md) for the SKILL.md body;
- [templates/reference.md](templates/reference.md) for a reference file;
- [templates/evals.md](templates/evals.md) for the test prompts.

The rules for the body, from [references/structure.md](references/structure.md):

- **Name** the folder and `name:` the same: lowercase letters, digits and hyphens, at most 64
  characters, no "claude" or "anthropic". Prefer a verb or gerund (`reviewing-contracts`,
  `invoice-chaser`), never `helper` or `utils`.
- **Under 500 lines**, and well under where possible. Claude is already capable: write what
  it would not know, not what it would.
- **Numbered steps** for anything with an order. Concrete examples over abstract advice.
- **Depth goes in `references/`**, one level deep, each linked from SKILL.md with when to
  read it: "Read references/pricing.md when the quote includes discounts."
- **Exact steps go in `scripts/`**, and SKILL.md says whether to run or read each one.
  Scripts handle their own errors and explain every constant.
- **Nothing private.** No real customer names, keys, account ids or internal URLs. Use
  placeholders, and list what varies in a short Configuration section at the end.
- **No dates that will rot** in the main instructions. If a fact changes (a rate, a limit,
  an API version), put it in a reference with "as of" and where to verify it.

Write the folder into the person's project (`.claude/skills/<name>/` for one repo) or their
personal skills folder (`~/.claude/skills/<name>/` for every project), unless they name
another place.

## Step 4 - test it

Write at least three test prompts in `evals.md` beside the skill: two that should trigger it
(one plain, one vague) and one near miss that should not. For each, note what a good result
contains. See [references/testing-a-skill.md](references/testing-a-skill.md).

Then validate the folder:

```bash
python3 scripts/validate_skill.py path/to/the-skill --check-text "Client Name" "internal.example"
```

Run the script from this skill's folder (it needs only Python 3). `--check-text` takes any
names that must not have leaked in. Fix every FAIL. Then, if the person can, try the test
prompts in a fresh session and adjust the description until the triggers fire and the near
miss does not.

## Step 5 - hand over

- **Claude Code**: the folder in `.claude/skills/` or `~/.claude/skills/` is live in the next
  session. It can also ship inside a plugin's `skills/` folder.
- **claude.ai**: zip the folder so the zip contains the folder itself at its root, then
  upload it under Customize, Skills. Requires code execution to be enabled.

Tell them where the skill lives, the three test prompts, and the one or two Configuration
items they should fill in.

## Rules

- Never invent the process. If a step is unclear, ask; a skill that encodes a guess teaches
  Claude the guess.
- Never put a credential, a real person's details or an internal URL in a skill.
- Never ship a skill whose validator run has a FAIL.
- One job per skill. Two unrelated jobs make two skills, which compose better than one big
  one.

## Example

> "Every Monday I pull last week's sales from the CSV export, compare to the week before,
> and write three bullet points for the team. Make that a skill."

Interview: triggers include "weekly sales summary" and "how did we do last week"; the
judgement call is which change is worth a bullet (they use anything over 10 per cent); the
exact step is the week-on-week calculation, so it becomes `scripts/compare_weeks.py`. The
description: "Summarises a weekly sales CSV export into three bullet points comparing the
week with the one before, flagging changes over 10 per cent. Use when someone asks for the
weekly sales summary, how last week went, or shares a sales export and wants the headline."
Evals: "weekly sales summary please" with a CSV (trigger), "how did we do last week?" (vague
trigger), "summarise this sales contract" (near miss). The validator passes, then the folder
goes to `~/.claude/skills/weekly-sales-summary/`.

## Configuration

One thing varies: **where skills are saved** (a project's `.claude/skills/`, the personal
`~/.claude/skills/`, a plugin's `skills/` folder, or a zip for claude.ai).
