# Changes ledger

Facts in this skill that move, each with the date checked and where to re-check it. Re-check
the source on the day you rely on one rather than quoting the value here.

| Checked | Fact | Re-check at |
| --- | --- | --- |
| 16/10/2026 | Current MCP revision is **2026-07-28**: protocol sessions and `Mcp-Session-Id` removed; `initialize` handshake removed; `server/discover` added; clients SHOULD send `io.modelcontextprotocol/clientInfo` in each request's `_meta` | modelcontextprotocol.io/specification/2026-07-28/changelog |
| 16/10/2026 | Streamable HTTP POST requests carry required `Mcp-Method` and `Mcp-Name` headers | same changelog, minor change 4 |
| 16/10/2026 | `_meta` keys `traceparent`, `tracestate` and `baggage` are the documented OpenTelemetry context convention | same changelog, minor change 2 |
| 16/10/2026 | Servers SHOULD return `tools/list` in a deterministic order | same changelog, minor change 3 |
| 16/10/2026 | Roots, Sampling and Logging are deprecated (minimum twelve-month window); the spec suggests stderr or OpenTelemetry instead of Logging | same changelog, Deprecated section |
| 16/10/2026 | Claude directory health badge: Healthy at 2% or less request errors over 30 days, "Worth a look" above 2%, Degraded above 5%; request errors exclude `isError` tool results | claude.com/docs/connectors/building/managing-your-listing |
| 16/10/2026 | Claude directory Error rate (30d) card counts request failures **and** `isError: true` tool results; auth rejections are in the total but not counted as errors | same page |
| 16/10/2026 | Directory metrics are computed daily, lag up to 24 hours, and hide windows or per-tool rows under 5 calls and per-product rows under 50 | same page |
| 29/09/2026 | OpenTelemetry MCP semantic conventions are at Development status in `open-telemetry/semantic-conventions-genai` | that repository, `docs/gen-ai/mcp.md` |
| 29/09/2026 | MCP Apps: no standard per-call marker says the view, not the model, made a `tools/call`; app-only visibility is the dependable way to tell | github.com/modelcontextprotocol/ext-apps |
| 07/10/2026 | SDKs lag the spec: TypeScript `@modelcontextprotocol/sdk` 1.x still reported `LATEST_PROTOCOL_VERSION` 2025-11-25, so its clients send `clientInfo` only in `initialize`, and `client` falls back to `User-Agent` | the SDK's `types.js`; `npm view @modelcontextprotocol/sdk version` |
| 07/10/2026 | The TypeScript SDK v2 line moves reserved `_meta` keys off the request onto the handler context; re-check where your wrapper reads `_meta` on any major upgrade | ts.sdk.modelcontextprotocol.io |

For Python SDK versions and their differences, see `mcp-server-builder` (agent-builder plugin),
[`references/sdk-versions.md`](../../mcp-server-builder/references/sdk-versions.md).

## Don't

- **Don't build on a session id.** It was removed on 2026-07-28; older clients may still send
  one until they upgrade, and the series breaks when they do.
- **Don't quote an SDK version from memory.** Ask the package manager.
