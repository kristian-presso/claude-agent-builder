# Event contract

## Contents

- Columns
- The four outcomes
- Grouping calls without a session
- Retention
- OpenTelemetry
- Don't
- Check


One table, one row per tool call, the same columns on every server you run. The shape is what
lets one review read every product. It holds what happened and why, never what was said.

## Columns

| Column | Holds | Null? |
| --- | --- | --- |
| `product` | which server wrote the row | no |
| `account_id` | pseudonymous key for the caller's account or organisation, as the server already knows it | yes, for anonymous calls |
| `kind` | `tool`; `view` for MCP App view events ([app-telemetry.md](app-telemetry.md)); `goal` and `outcome` ([intent-and-outcomes.md](intent-and-outcomes.md)); optionally `knowledge_read` per document a tool served | no |
| `name` | tool name; `<view>/<event>/<detail>` for a view event; a document id for a knowledge read | no |
| `outcome` | `ok`, `empty`, `refused`, `error` | no |
| `refusal_code` | stable snake_case reason; `uncoded` when a refusal was built without one | only when not refused |
| `arg_keys` | sorted argument names present, comma-joined; identifier-shaped only, at most 32 | yes |
| `query` | normalised, credential-scrubbed search text, from search tools only | yes |
| `result_bytes` | serialised result size | yes |
| `duration_ms` | handler time | no |
| `initiator` | `model`, or `app` for a tool only an MCP App view can call | no |
| `access` | `read` when the tool's `readOnlyHint` is true, otherwise `write` | no |
| `client` | self-reported client name and version, else the HTTP `User-Agent` | yes |
| `trace_id` | from a W3C `traceparent` the client sent in `_meta` | yes |
| `server_version` | the build that served it | no |
| `created_at` | timestamp with time zone | no |

```sql
create table mcp_events (
  id             bigserial primary key,
  product        text not null,
  account_id     text,
  kind           text not null default 'tool',
  name           text not null,
  outcome        text not null check (outcome in ('ok','empty','refused','error')),
  refusal_code   text,
  arg_keys       text,
  query          text,
  result_bytes   integer,
  duration_ms    integer not null,
  initiator      text not null default 'model',
  access         text not null default 'write',
  client         text,
  trace_id       text,
  server_version text not null,
  created_at     timestamptz not null default now()
);
create index on mcp_events (product, created_at);
```

Two companion tables are worth having from day one, because they are the only channels for
what the tool list cannot see: `tool_gaps` (a `report_gap` tool the model calls when nothing
fits, storing the ask verbatim and the tool it tried) and `feedback` (a `feedback` tool for
the person's own words). Both hold free text, so treat them as personal data.

## The four outcomes

- `ok` - the tool did its job and returned something.
- `empty` - the tool did its job and found nothing. Not a failure; the best gap signal.
- `refused` - the tool correctly said no, with a code saying why.
- `error` - the server failed.

The value of the table rests on keeping these apart.

## Grouping calls without a session

The 2026-07-28 revision removed protocol sessions: no `initialize`, no `Mcp-Session-Id`.
Group calls into a "flow" in this order of preference:

1. `trace_id`, when the client propagates trace context in `_meta`.
2. `account_id` + `client` + a 30-minute inactivity gap, computed in SQL at read time (see
   [signals.md](signals.md)). Clients on the 2026-07-28 revision send
   `io.modelcontextprotocol/clientInfo` in each request's `_meta`; older clients name
   themselves only in `initialize`, which a stateless server never sees on a tool call, so
   fall back to the HTTP `User-Agent`.
3. A server-minted handle that a tool returns and later takes as an argument, for multi-step
   jobs that genuinely need state. This is also what the spec recommends for cross-call state.

Older clients may still send a session header. Do not build on it: the series breaks when
they upgrade.

## Retention

A daily job rolls finished days into `mcp_events_daily` (product, kind, name, outcome, calls,
distinct accounts, p50, p95), then deletes raw rows older than 90 days. Rollups hold no free
text and no account id, and are kept. Gap and feedback text is deleted after 365 days, or
sooner if your privacy notice says so.

## OpenTelemetry

If the server also emits spans, map `name` to `gen_ai.tool.name`, the method to
`mcp.method.name`, an error to `error.type`. The MCP semantic conventions were at Development
status when checked (see [changes-ledger.md](changes-ledger.md)), so keep the table as the
source of truth.

## Don't

- **Don't store argument values or results,** even "just for debugging".
- **Don't add a product-specific column.** Put product detail in its own table keyed by the
  event id; a renamed column drops that product out of every cross-product query.
- **Don't treat `client` as identity.** It is self-reported.

## Check

```sql
select outcome, count(*) from mcp_events
where created_at > now() - interval '1 day' group by 1;
```

returns only the four outcomes, and a test call to each refusal path shows a non-null
`refusal_code`.
