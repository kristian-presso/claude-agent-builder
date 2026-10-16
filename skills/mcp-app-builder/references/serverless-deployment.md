# Deploying MCP Apps on a serverless runtime

Most official examples assume a long-lived Node process with a filesystem. A serverless MCP
server has neither, and two of the resulting mismatches fail silently. Read this before
deploying to Workers, Lambda, Vercel functions or anything stateless.

"Serverless" here means the shape the `2026-07-28` core spec made standard: no session, a
fresh server object per HTTP request, closed when the response is written.

## Trap 1: capability detection cannot work, and does not complain

Registering the app tool only when the client's UI capability says so assumes one server
object spanning `initialize` and `tools/list`. Per request, those are two objects, and the
one answering `tools/list` never saw a capability. The fallback branch always wins, with no
exception and no warning.

**Register app tools unconditionally.** A host without the extension ignores
`_meta.ui.resourceUri`, so it costs nothing. Degrade in what the result contains: text for
every host, `structuredContent` for the view. As a bonus the tool list is identical across
clients.

## Trap 2: there is no filesystem

Examples read the HTML at request time with `fs.readFile`. No serverless runtime can.

| Approach | Verdict |
| --- | --- |
| Object storage or KV at runtime | Adds a fetch to every resource read and lets the bundle and the stored copy disagree with no symptom |
| A bundler-specific raw-text import | Works only if every toolchain (deploy, test, typecheck) uses the same bundler. Usually they do not |
| A runtime-specific text-module rule | Works in the runtime, breaks every other tool importing the module |
| **A build step emitting a committed `.ts` module** | **Recommended.** One artefact every toolchain reads identically |

Emit the bundled HTML with `JSON.stringify`, never a template literal: bundled JavaScript
contains backticks and `${`. Name the module `<name>-view.ts`, never `<name>.html.ts`: an
import specifier ending in `.html` is resolved differently by TypeScript (to the `.ts` file)
and esbuild (as raw text), so both are green and the resource serves TypeScript source.
Commit the generated file and add a drift check (rebuild, fail on a diff). The starter does
all three.

## Trap 3: the SDK is the bundle, not your framework

Measured 04/09/2026 with Vite and `vite-plugin-singlefile` on ext-apps 1.7.5, the same
trivial view:

| View client | Raw | Gzip |
| --- | --- | --- |
| SDK `App` class | 431 KB | 102 KB |
| Hand-rolled postMessage, same features | 2.21 KB | 1.16 KB |

The weight is protocol validation: `App` extends the MCP SDK's `Protocol` and pulls zod into
the browser to validate every `ui/*` message. Typing is not the trade-off: a hand-rolled
client can import the SDK's types for free, because types erase at build.

**Default to the SDK**: protocol correctness you did not write, and spec revisions absorbed
by a version bump. **Hand-roll when a measurement justifies it**: a view rendered many times
per conversation, a mobile host, a cold-start-sensitive worker. Startup binds before the size
limit does, because a large string module is parsed on every cold start. Keep one bundle per
view and measure the gzipped size in CI.

## What does not change

Authorisation, data access and tenancy. A view's tool call arrives over the host's
authenticated connection carrying the ordinary credential.
