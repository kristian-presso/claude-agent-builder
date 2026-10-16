# Protocol, `_meta.ui` and the view lifecycle

## Contents

- The extension and the resource contract
- The text fallback is mandatory
- The two `_meta.ui` objects
- The `ui/*` messages
- Lifecycle and the handlers-before-connect rule

## The extension and the resource contract

An MCP App is two ordinary MCP primitives wired together: a **tool** the model calls and a
**resource** holding the HTML that renders its result. The extension id is
`io.modelcontextprotocol/ui`; both sides declare it in `capabilities.extensions`, so a
server can never force a UI on a host that does not want one.

- The resource URI **must** use the `ui://` scheme, e.g. `ui://revenue/dashboard.html`.
- The MIME type **must** be `text/html;profile=mcp-app`. Use the SDK's
  `RESOURCE_MIME_TYPE` constant rather than typing it.
- The content is a complete HTML5 document. There is no same-origin server behind it, so
  every asset must be inlined or explicitly permitted. Bundle to a single file.
- The tool points at the resource through `_meta.ui.resourceUri`. Several tools may share
  one resource, and the host may fetch it before the tool is called.

Order of events: the model calls the tool; the host fetches the resource (possibly ahead of
time) and renders it in a sandboxed iframe; the view and host complete `ui/initialize`; the
host pushes tool input, then the result; from then on the view may call tools, send
messages or update the model's context.

## The text fallback is mandatory

```ts
return {
  content: [{ type: "text", text: `Gross ${gross}, net ${net}.` }],
  structuredContent: { gross, net, daily },
};
```

A host without the extension treats `_meta.ui.resourceUri` as inert and shows the text. A
host with it shows the view. The same registration serves both, which is why conditional
registration is unnecessary as well as unreliable. Strict conformance for
`structuredContent` wants a declared `outputSchema`; budget for it.

## The two `_meta.ui` objects

Putting a field in the wrong one is the most common MCP Apps mistake, and it is silent.

**On the tool** (registration config):

| Field | Meaning |
| --- | --- |
| `resourceUri` | The `ui://` resource that renders this tool's result |
| `visibility` | `["model", "app"]` by default. `["app"]` hides the tool from the model while the view can still call it: right for polling and pagination helpers |

**On the resource content item** (returned by the read callback, not the config):

| Field | Meaning |
| --- | --- |
| `csp` | `{ connectDomains, resourceDomains, frameDomains, baseUriDomains }`. Omitted means no network |
| `permissions` | Requests camera, microphone, geolocation or clipboard write |
| `domain` | A stable sandbox origin, only for an API that allowlists origins. Host-specific format |
| `prefersBorder` | A rendering hint, not a guarantee |

```ts
registerAppResource(
  server,
  "Revenue dashboard",              // name
  "ui://revenue/dashboard.html",    // uri
  { mimeType: RESOURCE_MIME_TYPE }, // config: no csp, no domain here
  async () => ({
    contents: [{
      uri: "ui://revenue/dashboard.html",
      mimeType: RESOURCE_MIME_TYPE,
      text: html,
      _meta: { ui: { csp: { connectDomains: [] } } },  // here
    }],
  }),
);
```

## The `ui/*` messages

JSON-RPC 2.0 over `postMessage`.

| Direction | Message | Purpose |
| --- | --- | --- |
| view to host | `ui/initialize` | Takes `appInfo`, `appCapabilities`, `protocolVersion` (not the core `clientInfo`/`capabilities` pair) |
| view to host | `ui/notifications/initialized` | Ready for data |
| host to view | `ui/notifications/tool-input` / `tool-input-partial` | Arguments, complete or still streaming |
| host to view | `ui/notifications/tool-result` | The result. Usually the main render |
| host to view | `ui/notifications/tool-cancelled` | Stop work and say so |
| host to view | `ui/notifications/host-context-changed` | Theme, display mode or size changed |
| host to view | `ui/resource-teardown` | Shut down cleanly |
| view to host | `tools/call` | Call a server tool over the host's authenticated connection |
| view to host | `ui/message` | Speak as the user and start a new turn |
| view to host | `ui/update-model-context` | Silently tell the model what the user sees or did. A **request**, not a notification: send it fire-and-forget with no id and the host drops it |
| view to host | `ui/open-link` | Open a URL, host-mediated |
| view to host | `ui/request-display-mode` | Ask for `inline`, `fullscreen` or `pip`. The host may refuse |
| view to host | `ui/notifications/size-changed` | Report content size when the container is flexible |

Report a **bounded** height in `size-changed`. Report the raw height of a fifty-row list and
the host grows the iframe, moving the scrolling to the host page. Report nothing and the host
clips to its default.

## Lifecycle and the handlers-before-connect rule

```ts
const app = new App({ name: "Revenue", version: "1.0.0" });
app.ontoolinput = (params) => { /* ... */ };
app.ontoolinputpartial = (params) => { /* preview only, never act */ };
app.ontoolresult = (result) => { /* main render */ };
app.onhostcontextchanged = (ctx) => { /* theme, size */ };
app.onteardown = async () => ({});   // stop timers, observers, requests
await app.connect();                  // last, always
```

`connect()` completes the handshake and the host may push the result immediately. A handler
attached one line later misses it; locally the round trip hides the bug. In React the
`useApp` hook handles the ordering.

Every `callServerTool` is a full round trip through the host: render something immediately,
show that a refresh is in flight, and never block first paint on a call you could avoid.
`app.sendLog({ level, data })` logs to the host, which is easier to reach than the iframe
console in most clients.
