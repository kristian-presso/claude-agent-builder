# Intent and outcomes

The tool log says what was called. It cannot say why, whether anything matched, whether the
job finished, or what kind of customer is asking. Capture a little more, all in closed
categories. Only the search query is free text.

A server never sees the conversation, only the arguments a model puts in a tool call. So
everything here arrives as an argument, and each must be an input the tool genuinely uses: the
Claude connector directory's review rejects servers that collect conversation data beyond what
the tool needs (check the current review criteria before submitting).

## What to capture

1. **Searches.** Every search or list tool records its query and marks empty results. The
   zero-hit query is the clearest demand signal there is.
2. **Goals.** Give entry tools (search, start a job) an optional `goal` argument from a closed
   list, and make the tool use it, for example to rank results from the matching area first.
   Record one `goal` row per call.
3. **Job outcomes.** List the server's multi-step jobs and register a small `report_job_outcome`
   tool that takes the job name and `finished | partial | abandoned | failed`. The server
   instructions ask the model to call it once when a job ends. Refuse job names the server
   does not ship.
4. **Customer profile,** only where customers build something on the product: one tool at the
   end of onboarding, called only after the person says yes, with about five closed fields
   (industry, business model, stage, size, country), replaced rather than appended, and a
   second tool that withdraws it as easily as it was given.

## Designing the closed lists

| Rule | Why |
| --- | --- |
| 8 to 15 values, plus `other` | a model picks reliably from a short list; `other` keeps it honest |
| Values from the product's own map of jobs | the counts then point straight at something to build |
| Never rename a value; add the new one and retire the old | a rename splits one series in two |
| `other` above 15% of rows means a value is missing | the list is wrong, not the people |

## What the review reads

| Check | Starting threshold | Usually means |
| --- | --- | --- |
| A goal with repeated zero-hit searches | any repeated query | build or research that capability |
| Abandoned or partial share per job | over 30% with 10+ reports | rewrite the job's steps or tool sequence |
| Reporting rate: outcomes over job starts | under 50% | the instruction to report is not landing |
| Top query whose top result is not what people then use | repeated | fix ranking or the result summary |

The evidence floor in [signals.md](signals.md) applies.

## Don't

- **Don't add a free-text "what is the person trying to do" field,** and don't ask the model
  to summarise the conversation into a tool call.
- **Don't infer a profile from what was said.** Ask, and store only what was agreed.
- **Don't read a missing outcome as abandoned.** Agents do not always report. Compute finish
  rates over reported outcomes and watch the reporting rate separately.
- **Drop a query outright** when it carries an email address or phone number.

## Check

A test pins one `goal` row and one `outcome` row from the closed lists, and shows a free-text
or unknown value refused with no row written.
