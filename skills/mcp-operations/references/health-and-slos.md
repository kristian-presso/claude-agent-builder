# Health and SLOs

Hold every production server to three numbers to start with: server error rate under 1%, p95
tool latency under 2 seconds for reads and 5 for writes, and p95 result size under 25,000
bytes. Page on errors; review everything else weekly. These are starting points; tighten them
per product once you have a month of data.

| Measure | Target | Alert when | Source |
| --- | --- | --- | --- |
| Error rate (`outcome = error`) | under 1% of calls, 7 days | over 5% in any hour with 20+ calls | your table |
| p95 duration, read tools | under 2,000 ms | doubled against the 4-week median | your table |
| p95 duration, write tools | under 5,000 ms | doubled against the 4-week median | your table |
| p95 result size | under 25,000 bytes | any tool over for a week | your table |
| Recorder health | rows written in the last hour when calls were served | zero rows while the edge log shows calls | edge log against table |
| Directory badge | Healthy | leaves Healthy | directory dashboard |

Only errors page someone, through your existing error tracker. Refusal rates, latency drift
and size go to the weekly review, because none of them get worse in an hour.

## The Claude directory's two error figures

For a server listed in the Claude connector directory, the developer dashboard shows two
different error measures. Checked 16/10/2026 at claude.com/docs/connectors/building/managing-your-listing:

- **Health badge** (30 days): Healthy at 2% or less request errors, "Worth a look" above 2%,
  Degraded above 5%. Request errors **exclude errors a tool returns in its own result**
  (`isError: true`) and include calls rejected for authentication problems.
- **Error rate (30d) card**: counts both request-level failures (5xx, timeouts) **and** tool
  results with `isError: true`. Auth rejections are not counted as errors but are in the total.

So a server whose tools refuse correctly and often can show a high error-rate card with a
Healthy badge. That is not a broken server, but it is still worth fixing: most avoidable
refusals come from a description that invites the call at the wrong moment, which a routing
eval addresses (`mcp-server-builder`, agent-builder plugin, [`references/routing-evals.md`](../../mcp-server-builder/references/routing-evals.md)).

Other things the dashboard docs say (same date): metrics are computed daily and can lag up to
24 hours; time windows and per-tool rows under 5 calls, and per-product rows under 50 calls,
are hidden; only traffic from Claude surfaces is counted; per-tool rows cover the top 15 tools.
Treat the dashboard as a cross-check on your own table, not a replacement.

## Don't

- **Don't alert on refusals.** A refusal spike is a description problem, found weekly.
- **Don't set targets from a cold-start-dominated first week.**
- **Don't treat a silent recorder as "no usage".** A table that stopped filling looks exactly
  like a quiet week. Compare with the edge or request log.
- **Don't copy the directory thresholds into your SLOs unexamined.** Its card includes correct
  refusals.

## Check

Your operator report returns error rate, p50, p95 and p95 size per tool for the window, and
the alert rule exists in the error tracker with the threshold above.
