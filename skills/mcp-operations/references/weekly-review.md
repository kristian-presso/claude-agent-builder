# Weekly review

Once a week, one pass reads every server's signals, gaps and feedback, researches the strongest
findings, and writes at most ten proposals sorted into five buckets. It opens draft pull
requests and issues and changes nothing on its own. It starts by scoring last week's shipped
changes against the signal that triggered them.

## Inputs, per server

- The usage report: the current 7 days, the 28 before as baseline, and 60 days for the
  never-used check.
- New gap reports and feedback since the last run, verbatim.
- Goals, zero-hit and top queries, job outcomes ([intent-and-outcomes.md](intent-and-outcomes.md)).
- Error-tracker issues opened or regressed in the window.
- Last week's report and the rejected-proposals log.

## Steps

1. **Measure last week.** For each change shipped since the last run, compare its trigger
   signal before and after. Moved: close it. Did not move: reopen with the evidence.
2. **Compute the signals** in [signals.md](signals.md), apply the evidence floor, and carry
   sub-floor patterns forward as "watching".
3. **Pick the top five findings.** Sort by severity (error, then gap, then refusal, then cost),
   then by accounts affected.
4. **Research each.** Read the tool's code and description and any document it serves. Name
   the cause, not only the symptom.
5. **Write proposals** into the buckets below, each with evidence (counts and three verbatim
   asks where they exist), the proposed change, and the signal that will show it worked.
6. **Deliver.** Description and content edits as draft pull requests; tool and behaviour
   changes as issues; the report itself, one page, wherever the owner reads.

| Bucket | Holds |
| --- | --- |
| Add | new tools or content, each backed by asks or zero-hit queries |
| Rewrite | descriptions, refusal texts, content read without effect |
| Remove or merge | dead tools, documents always read together; flagged first, removed on the second agreeing week |
| Research | questions the data raises and cannot answer |
| Measure | last week's changes, moved or reopened |

## Guardrails

- At most ten proposals. More is a list nobody reads.
- Fix and remove before adding.
- A rejected proposal is logged with the reason and not proposed again without new evidence
  that answers that reason.
- Nothing merges without a person.
- An empty report is valid. Say when a week had too little data.

## Report shape

A one-sentence headline (the most important finding), one health line per server, the five
buckets, the "watching" list, and what last week's changes did. Each proposal links to its pull
request or issue.

## Running it on a schedule

Any scheduler that can run an agent with read access to the usage store and write access to
the repo works: a cron job calling Claude Code in print mode, a CI schedule, or a cloud
scheduled task. Give it read-only database credentials, permission to open draft pull requests
and issues, and no permission to merge.

## Don't

- **Don't propose from one week of low volume.** Carry it.
- **Don't summarise feedback.** Quote it.
- **Don't let the review edit content in place.** Draft pull requests only, so a person sees
  the diff.
- **Don't drop the Measure bucket when busy.** Without it the loop cannot tell good changes from
  noise.

## Check

Every proposal links to an open pull request or issue, and every item in last week's Add and
Rewrite buckets appears in this week's Measure bucket.
