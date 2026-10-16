# SDK versions and corrections to the upstream docs

## Contents

- Which version to pin, and why
- Seven corrections to the upstream documentation
- Re-checking

Everything here describes someone else's software. Each item carries the date it was checked
and how to re-check it. A correction that no longer applies is worse than none: it sends you
round a problem that is not there.

## Which version to pin, and why

Checked 16/10/2026 against the npm registry:

- `@modelcontextprotocol/ext-apps` `latest` is **2.0.3**. The 1.x line ends at **1.7.5**.
- `@modelcontextprotocol/sdk` (the monolithic server SDK) is at **1.32.1**, with no 2.x.
- The v2 server SDK lives in separate packages: `@modelcontextprotocol/core`, `/client`
  and `/server` (`/server` at 2.3.1).

**The ext-apps 2.x major is a dependency event, not an App API change.** ext-apps 2.0.3
peers on `@modelcontextprotocol/core`, `/client` and `/server` at `^2.0.0` and zod
`^4.2.0`, where 1.7.5 peers on the monolithic `@modelcontextprotocol/sdk` `^1.29.0`. The
App surface (extension id, `ui://` scheme, MIME type, `registerAppResource`'s signature,
the CSP nesting) is the same in both: verified by comparing the declaration files of 1.7.5
and 2.0.3.

So:

- **Server on the monolithic `@modelcontextprotocol/sdk` 1.x** (as the starter is): pin
  `ext-apps` to `^1.7.5`. A fresh `npm install @modelcontextprotocol/ext-apps` with no
  version takes 2.x and fails to resolve peers against an SDK 1.x server.
- **Server already on the v2 package trio**: take `ext-apps` 2.x. Handler registration
  changes form in v2 (`setRequestHandler("method", ...)` replaces the schema-object form),
  so re-read any example written for 1.x.

Adopting ext-apps 2.x does not buy anything for the App itself. Migrate when the server moves
to the v2 packages for its own reasons.

## Seven corrections to the upstream documentation

Found by reading the package's type declarations rather than the prose docs. In the published
npm package the declarations are under `dist/src/` (`server/index.d.ts`, `spec.types.d.ts`);
the upstream repository has the same content under `types/`. Anchor on symbol names, not line
numbers.

### 1. `registerAppResource` takes five positional arguments

An upstream skill teaches an object form that does not compile. The real signature (checked
in 1.7.5 and 2.0.3):

```ts
registerAppResource(server, name, uri, config, readCallback)
```

It wraps `McpServer.registerResource(name, uri, config, readCallback)`, which is why name
comes before uri. Re-check: `grep -A2 "export declare function registerAppResource" dist/src/server/index.d.ts`.

### 2. CSP domains nest under `csp`, on the content item

Upstream examples show the domain keys flat, in the resource config. They nest under
`_meta.ui.csp` (`connectDomains`, `resourceDomains`, `frameDomains`, `baseUriDomains`) and
belong in the `contents[]` objects returned by the **read callback**. The tool meta types
`csp` as `never`: hosts read CSP from `resources/read` and nowhere else. Omitted means no
network access, which is usually right. Re-check: search `spec.types.d.ts` for
`McpUiResourceMeta` and `csp?: never`.

### 3. The documented plugin install id

Upstream docs give `mcp-apps@modelcontextprotocol-ext-apps`. The marketplace manifest
declares the marketplace name `mcp-apps`, so the id is `mcp-apps@mcp-apps` after
`/plugin marketplace add modelcontextprotocol/ext-apps` (manifest checked 16/10/2026).

### 4. Capability-conditional registration cannot work on a stateless server

The docs prescribe registering the app tool only if the client's UI capability says so,
inside `oninitialized`. That assumes one server object spanning `initialize` and
`tools/list`. A stateless server builds a fresh object per request, so the object answering
`tools/list` has never seen a capability and always takes the fallback branch. No error, no
warning: just a server that never offers UI. Since the `2026-07-28` core spec removed the
handshake entirely, this is now the common case. **Register app tools unconditionally** and
degrade in what the result contains.

### 5. The reference host does not start from a clean checkout

`basic-host` (in the upstream repository, not the npm package) failed on 1.7.5 for three
reasons: `cross-env` used but not declared, `bun` required but not mentioned, and
`@types/cors` missing so the typecheck gating the build fails and the server answers
`Cannot GET /index.html`. Install the missing pieces in one `npm install --no-save` command
(a second `--no-save` install prunes the first), or run the server with `npx tsx serve.ts`.
Re-check against the tag you vendor.

### 6. A browser-based host needs CORS on the MCP endpoint

`basic-host` fetches the MCP endpoint cross-origin. Without CORS the preflight gets a 404
and the host reports only "Failed to connect to any servers", while `curl` against the same
endpoint works. The starter includes CORS for this reason.

### 7. `basic-host` 404s its own sandbox under a dotted directory

It serves `sandbox.html` with an absolute path and no `root`, and `send` ignores dotfiles by
default, so any dotted directory anywhere above the file (`.runs/`, `.cache/`) makes the
sandbox 404 while the host page loads fine. The view then never renders and the failure
points at your app. Keep the path free of dotted segments, or patch the call to
`res.sendFile("sandbox.html", { root: DIRECTORY })`.

## Re-checking

On any version bump, re-run the three checks that can be settled from the package (1, 2 and
the peer dependencies) by extracting the tarball:

```bash
npm pack @modelcontextprotocol/ext-apps@<version> && tar xzf modelcontextprotocol-ext-apps-*.tgz
grep -A2 "export declare function registerAppResource" package/dist/src/server/index.d.ts
grep -n "csp?: never" package/dist/src/spec.types.d.ts
node -e "console.log(require('./package/package.json').peerDependencies)"
```
