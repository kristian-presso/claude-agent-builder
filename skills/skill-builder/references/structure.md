# Skill structure

Limits and guidance checked on 16/10/2026 against platform.claude.com/docs (Agent Skills
overview and best practices) and support.claude.com. Verify there before relying on a
number.

## The folder

```text
my-skill/
  SKILL.md            required: frontmatter plus instructions
  references/         optional: depth Claude reads only when SKILL.md says to
    topic.md
  scripts/            optional: code Claude runs; only its output enters context
    do_thing.py
  templates/          optional: files Claude copies and fills in
  evals.md            recommended: the test prompts
```

## Frontmatter

```yaml
---
name: my-skill
description: Does X for Y. Use when ...
---
```

| Field | Rules |
| --- | --- |
| `name` | At most 64 characters; lowercase letters, digits and hyphens; no XML tags; no "anthropic" or "claude"; same as the folder name |
| `description` | Non-empty; at most 1,024 characters; no XML tags (such as `<example>` or `</b>`); third person; says what and when |

The rule is no XML tags, not no angle brackets: a lone `<` or `>` in prose ("under 5 MB", "3 > 2", an arrow `->`) is allowed. Checked 16/10/2026 against the Agent Skills overview at platform.claude.com/docs/en/agents-and-tools/agent-skills/overview, which says both fields "cannot contain XML tags".

claude.ai also accepts an optional `dependencies` field (for example
`python>=3.8, pandas>=1.5.0`) listing packages a skill needs.

## How Claude loads it (progressive disclosure)

1. **Always**: `name` and `description`, about a hundred tokens per skill.
2. **When triggered**: the SKILL.md body. Keep it under about 5,000 tokens and under 500
   lines.
3. **When needed**: a reference file is read when SKILL.md points at it and the task needs
   it. A script is run, and only its output costs context.

So the body says what to do and **when to read which reference**; the references carry the
depth.

## Body guidance

- **Assume Claude is capable.** Write what it would not otherwise know: the person's process,
  their judgement calls, their limits. Cut explanations of general knowledge.
- **Match freedom to fragility.** Where many approaches are fine, give principles. Where a
  pattern is preferred, give a template. Where an operation is fragile or order-critical,
  give an exact script and say not to vary it.
- **Workflows as numbered steps**, with a checklist for long ones.
- **Feedback loops** for quality-critical work: run the validator, fix, run again.
- **One term per concept.** If it is "invoice" in step 2 it is not "bill" in step 5.
- **Concrete examples** beat abstract descriptions. One realistic worked example at the end
  is worth a page of advice.

## References

- **One level deep.** Every reference is linked directly from SKILL.md. A reference that
  links to another reference may only be partly read.
- **Contents list** at the top of any reference over 100 lines.
- **Forward slashes** in paths, always.
- **Dated facts live here**, not in SKILL.md, each with "as of" and where to verify it.

## Scripts

- Say whether Claude should **run** it ("Run `scripts/check.py`") or **read** it ("See
  `scripts/check.py` for the algorithm").
- Handle errors in the script and print a specific message ("Column 'amount' not found.
  Columns are: date, total, customer"), rather than leaving Claude to interpret a traceback.
- No unexplained constants: a comment says why each value is what it is.
- List dependencies, and prefer the standard library. claude.ai can install packages from
  PyPI and npm; the API's code execution environment cannot install at runtime.
- When using MCP tools, name them fully: `ServerName:tool_name`.

## Privacy and portability

A skill may be shared, zipped or published. Before that:

- no credentials, tokens or keys;
- no real customer, employee or supplier names;
- no internal URLs, account ids or repository names;
- no absolute paths from one machine.

Put anything that varies in a short **Configuration** section and have the skill ask for it.
