# Writing the description

The `description` is the only part of a skill Claude sees until the skill is chosen. It sits
in context alongside every other installed skill's description on every request, and Claude
picks a skill by matching the request against it. A good body behind a vague description is a
skill that never runs.

## The shape

```text
<What it does, third person, one sentence.> <Its inputs and outputs, named.>
Use when <the situations and phrasings that should trigger it>.
```

Example:

> Reviews a supplier contract against a checklist of payment terms, liability caps,
> termination and data-protection clauses, and returns a table of issues with suggested
> wording. Use when someone shares a contract, MSA or terms of business and asks whether to
> sign, what to push back on, or for a contract review.

## Rules

- **Third person.** The description is injected into the system prompt. "Reviews ..." works;
  "I can help you ..." and "You can use this to ..." read oddly and match worse.
- **Say when, not only what.** The "Use when" clause is what matching runs on. List the
  phrasings people actually use, including vague ones.
- **Name concrete nouns.** File types (CSV, PDF, `.docx`), tools (Stripe, GitHub), artefacts
  (invoice, pull request). Requests mention these.
- **Say what it is not for**, when there is a close neighbour: "Not for drafting new
  contracts; use contract-drafter."
- **No XML tags** (`<example>`, `</b>`). A lone `<` or `>` in prose is allowed, but plain words
  ("under", "over", "then") usually read better anyway.
- **Length**: at most 1,024 characters for Claude Code and the API (checked October 2026 at
  platform.claude.com/docs). claude.ai's upload form documented a 200-character limit on the
  same date, so for skills that will be uploaded there, make the first 200 characters carry
  the what and the main trigger.

## Diagnosing a skill that does not trigger

1. Ask Claude, in a fresh session, the exact phrase the person used. Does the description
   contain any of its words or its intent?
2. Add the missing phrasing to the "Use when" clause. Prefer real phrasings over synonyms.
3. If two skills compete, sharpen both with a "not for" clause.
4. If it triggers too often, the description is too broad: name the specific inputs it needs.

Change one thing at a time and re-test with the three prompts in `evals.md`.
