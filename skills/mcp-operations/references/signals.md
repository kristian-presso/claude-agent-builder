# Signals

## Contents

- The evidence floor
- The twelve checks
- Reading the numbers honestly
- SQL (Postgres)

Twelve checks over the usage table, the gap table and the feedback table turn raw rows into
findings. Each points at one kind of fix.

## The evidence floor

Default window: the last 7 days, compared with the median of the 4 weeks before. A pattern
counts only if it appears in **at least 3 distinct flows or 2 distinct accounts** in the
window. Below that, list it under "watching" and carry it forward.

## The twelve checks

| # | Signal | Detected by | Usually means | Fix bucket |
| --- | --- | --- | --- | --- |
| 1 | Refusal loop | same tool refused 2+ times in one flow, or refusal rate over 30% | the description sends the model at the wrong time | Rewrite description or refusal text |
| 2 | Refusal then gap | a `refused` row followed by a gap report in the same flow | the tool nearly covers the job | Widen the tool or add a sibling |
| 3 | Zero-hit search | `outcome = empty` with a `query` | missing content, or content without the words people use | Add content or retrieval keys |
| 4 | Repeat ask | the same normalised query or gap ask from 3+ flows | a real feature request | Add, with the verbatim asks attached |
| 5 | Unknown name | a refusal code such as `unknown_name` from a lookup-by-name tool | the model guesses a name that does not exist | Alias it, or build it |
| 6 | Read, then nothing | a document served, then no further call in the flow | the document does not answer what it is routed for | Rewrite it |
| 7 | Read in pairs | two documents read together in over 70% of flows that read either | one concept split in two | Merge or cross-link |
| 8 | Never used | a tool or document with zero rows in 60 days | undiscoverable, or not needed | Check routing first, then remove |
| 9 | Error spike | error rate above twice the 4-week median, or any rise right after a `server_version` change | a regression | Fix, naming the version |
| 10 | Slow tool | p95 duration up 50% week on week | a performance regression | Fix |
| 11 | Heavy result | p95 `result_bytes` over 25,000 | the model pays tokens for detail it rarely needs | Paginate or add a concise mode |
| 12 | Long path | median calls per flow before the first `ok` write, over 5 | a common job takes too many steps | Add a composite tool or a skill that sequences them |

MCP App views add their own checks ([app-telemetry.md](app-telemetry.md)); goals and job
outcomes add theirs ([intent-and-outcomes.md](intent-and-outcomes.md)).

**Uncoded refusals** are a standing item: any tool with `refusal_code = 'uncoded'` stays on the
list until fixed, because every other refusal signal is blind to it.

Two reads the checks cannot replace:

- **Feedback is quoted, never counted.** Put verbatim feedback beside the signal it relates
  to. "Confusing" on a tool with a high refusal rate is one finding seen from two sides.
- **Gaps are clustered, then quoted.** Group gap asks by the tool attempted, then by wording,
  and carry three verbatim asks into any proposal.

## Reading the numbers honestly

- Two calls with one refusal is a 50% rate that says nothing. State the count beside every
  rate.
- Report p50 and p95, never a mean: one cold start drags a mean.
- Never collapse refused and error into one failure rate. They send you to opposite fixes.
- Don't propose from one account's behaviour unless it is the whole customer base.
- **Don't remove a tool on signal 8 alone.** New, seasonal and undiscoverable tools all show
  zero calls. Check its description with a routing eval, and remove only after a second window
  agrees ([release-and-change.md](release-and-change.md)).

## SQL (Postgres)

Tested on PostgreSQL 16 against the table in [event-contract.md](event-contract.md).

**Flows** (account + client + 30-minute inactivity gap, or trace id when present):

```sql
create or replace view mcp_flows as
with ordered as (
  select e.*,
         lag(created_at) over (partition by coalesce(trace_id, account_id || '|' || coalesce(client, ''))
                               order by created_at) as prev_at
  from mcp_events e
)
select ordered.*,
       coalesce(trace_id, account_id || '|' || coalesce(client, '')) || '#' ||
       sum(case when prev_at is null or created_at - prev_at > interval '30 minutes' then 1 else 0 end)
         over (partition by coalesce(trace_id, account_id || '|' || coalesce(client, ''))
               order by created_at rows unbounded preceding) as flow_id
from ordered;
```

**Per-tool health, this week** (counts beside every rate):

```sql
select name,
       count(*)                                                        as calls,
       count(*) filter (where outcome = 'refused')                     as refused,
       round(100.0 * count(*) filter (where outcome = 'refused') / count(*), 1) as refused_pct,
       count(*) filter (where outcome = 'error')                       as errors,
       count(*) filter (where outcome = 'empty')                       as empty,
       percentile_cont(0.5)  within group (order by duration_ms)       as p50_ms,
       percentile_cont(0.95) within group (order by duration_ms)       as p95_ms,
       percentile_cont(0.95) within group (order by result_bytes)      as p95_bytes,
       count(distinct account_id)                                      as accounts
from mcp_events
where kind = 'tool' and created_at > now() - interval '7 days'
group by name order by calls desc;
```

**Signal 1, refusal loops** (above the floor):

```sql
select name, count(*) as flows_with_loop
from (select flow_id, name from mcp_flows
      where outcome = 'refused' and created_at > now() - interval '7 days'
      group by flow_id, name having count(*) >= 2) t
group by name having count(*) >= 3
order by flows_with_loop desc;
```

**Signal 3 and 4, zero-hit and repeated queries:**

```sql
select query, count(distinct flow_id) as flows, count(distinct account_id) as accounts
from mcp_flows
where outcome = 'empty' and query is not null and created_at > now() - interval '7 days'
group by query
having count(distinct flow_id) >= 3 or count(distinct account_id) >= 2
order by flows desc;
```

**Signal 9, errors by server version:**

```sql
select server_version, min(created_at) as first_seen, count(*) as calls,
       round(100.0 * count(*) filter (where outcome = 'error') / count(*), 2) as error_pct
from mcp_events where created_at > now() - interval '35 days'
group by server_version order by first_seen;
```

**Signal 12, long paths** (calls before the first successful write in each flow):

```sql
with firsts as (
  select flow_id, min(created_at) as first_write
  from mcp_flows where access = 'write' and outcome = 'ok'
    and created_at > now() - interval '7 days'
  group by flow_id
)
select percentile_cont(0.5) within group (order by n) as median_calls_before_write,
       count(*) as flows
from (select f.flow_id, count(*) as n
      from mcp_flows m join firsts f on m.flow_id = f.flow_id and m.created_at <= f.first_write
      group by f.flow_id) t;
```

**Uncoded refusals:**

```sql
select name, count(*) from mcp_events
where refusal_code = 'uncoded' and created_at > now() - interval '28 days'
group by name order by 2 desc;
```
