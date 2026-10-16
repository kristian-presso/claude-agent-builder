# App telemetry

The tool log sees that a tool with a view was called. It cannot see whether the view painted,
what the person did in it, whether the host granted the display mode it asked for, or whether
it crashed. A view makes no network requests of its own, so the only way back is a tool call:
one app-only tool, `record_view_event`, called by the view at four named moments with
enum-only fields. The number that matters most is the render rate.

## Server side

Register `record_view_event` only on servers that serve a view, as app-only
(`_meta.ui.visibility: ["app"]`), so a host that implements MCP Apps keeps it out of the
model's tool list. Each call becomes one usage row with `kind = view`, `initiator = app`,
named `<view>/<event>/<detail>`. Set both `readOnlyHint` and `destructiveHint` false: it
appends a record and changes nothing the person owns.

| Event | When the view sends it | Row name |
| --- | --- | --- |
| `rendered` | once per view instance, after the first result has painted, with time to paint | `<view>/rendered/<mode>` |
| `interaction` | a declared control was used; at most once per control per 30 seconds | `<view>/interaction/<control>` |
| `display_mode` | after requesting a display mode, with what was asked and what the host returned | `<view>/display_mode/<asked>_to_<got>` |
| `view_error` | render, a tool call or a malformed result failed inside the view | `<view>/view_error/<kind>` |

The input schema accepts only enums and numbers. Controls are ids the view declares; errors
are kinds.

## View side

Fire and forget, never in the render path, never with free text:

```ts
const VIEW = "revenue_chart";            // the tool this view renders
const lastSent = new Map<string, number>();

export function report(app: { callServerTool: Function }, e: Record<string, string | number>) {
  if (e.event === "interaction") {
    const now = Date.now();
    if (now - (lastSent.get(String(e.control)) ?? 0) < 30_000) return;
    lastSent.set(String(e.control), now);
  }
  app.callServerTool({ name: "record_view_event", arguments: { view: VIEW, ...e } })
    .catch(() => {});                    // a lost report must never break the view
}
```

Take a timestamp before connecting, and report `rendered` inside a `requestAnimationFrame`
callback after the first result paints, so the time is to paint rather than to data. Wrap the
render and every server call in a try/catch that reports `view_error`. Report `display_mode`
with the mode the host returned, not the one requested.

## Reading it

| Check | How | Starting threshold | Usually means |
| --- | --- | --- | --- |
| Render rate | `rendered` rows over model calls to the view's tool, per client, among clients that rendered at least once | under 90% | the view fails or paints too late in that host |
| Text-only share | calls to view tools from clients that never rendered | tracked | how many people only see the text fallback; invest in that text |
| View errors | `view_error` over `rendered` | over 2% | a render path the tests do not reach |
| Mode refused | `display_mode` rows where asked and got differ | tracked | the inline layout is what they see; test it as the main layout |
| Dead control | a declared control with no `interaction` over 50+ renders in 60 days | zero | remove it, or it is in the wrong place |
| Slow first paint | p50 of `rendered` durations | over 1,000 ms | bundle weight |

## Don't

- **Don't infer "rendered" from a successful tool call.** A green tool row with a blank view
  is precisely the failure people report as "it's broken".
- **Don't report every keystroke or scroll.** Each report is a round trip through the host.
- **Don't await the report before painting.**

## Check

One test drives the view in a reference host and asserts a `<view>/rendered/...` row arrives;
another sends free text and asserts it is refused with no row written. For building and
verifying the view itself, use [`mcp-app-builder`](../../mcp-app-builder/SKILL.md) (agent-builder plugin).
