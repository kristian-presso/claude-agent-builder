# The starter scaffold

## Contents

- What it gives you
- The tree
- package.json, tsconfig.json, vite.config.ts, wrangler.toml, .gitignore
- src/index.ts, src/mcp/server.ts, src/apps/uris.ts, src/apps/resources.ts
- scripts/build-apps.ts
- app/index.html, app/main.ts, app/styles.css
- After writing it out
- The lean-client question

A complete, working MCP App project, small enough to write out file by file into the user's
own project. Every file below is the whole file. Nothing is fetched or cloned: you write it
into their repo the way you would write any other code for them.

An MCP App belongs **inside the user's own project**, beside the business it serves, not in
a scratch directory. Replace `my-mcp-app` with the project's slug, and rename `sample` to
whatever the first view actually is.

## What it gives you

A Cloudflare Worker serving one MCP tool paired with one `ui://` HTML view, a build step
that inlines each view into a single committed module, and a typecheck. It is deliberately
the shape that survives the two things that break most MCP App projects: **no filesystem at
request time** and **no long-lived server object**. See
[serverless-deployment.md](serverless-deployment.md) for why both matter, and
[sdk-versions-and-corrections.md](sdk-versions-and-corrections.md) before copying any
snippet from upstream docs.

Every non-obvious line carries a comment saying why. Keep the comments: they stop the next
person reintroducing the defect.

**Tested** on 16/10/2026: written out exactly as below, `npm install`, `npm run build:apps`,
`npm run typecheck` and `wrangler deploy --dry-run` all succeed with `ext-apps` 1.7.5 and
`@modelcontextprotocol/sdk` 1.32.1. Under `wrangler dev`, `tools/list` returns the tool with
its annotations and `_meta.ui.resourceUri`, `tools/call` returns both `content` and
`structuredContent`, `resources/read` returns `text/html;profile=mcp-app` beginning
`<!doctype html>`, and `GET /mcp` answers 405.

The package uses Cloudflare Workers and Hono. The same shape works on any serverless
runtime: swap the entry file, keep the rest.

## The tree

```text
<project>/
  package.json
  tsconfig.json
  vite.config.ts
  wrangler.toml
  .gitignore
  src/
    index.ts              the Worker: CORS, health, stateless /mcp
    mcp/server.ts         the MCP server: tools, registered unconditionally
    apps/uris.ts          every ui:// URI, in one place
    apps/resources.ts     the resource registration and its read callback
    apps/generated/       build output, committed, never hand-edited
  app/
    index.html
    main.ts
    styles.css
  scripts/build-apps.ts   builds each view to one committed .ts module
```

## `package.json`

```json
{
  "name": "my-mcp-app",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "scripts": {
    "build:apps": "tsx scripts/build-apps.ts",
    "check:apps": "npm run build:apps && git diff --exit-code src/apps/generated",
    "typecheck": "tsc --noEmit",
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "size": "wrangler deploy --dry-run --outdir .wrangler/bundled"
  },
  "dependencies": {
    "@modelcontextprotocol/ext-apps": "^1.7.5",
    "@modelcontextprotocol/sdk": "^1.29.0",
    "hono": "^4.0.0",
    "zod": "^4.4.3"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^5.20260903.1",
    "@types/node": "^22.0.0",
    "tsx": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^7.0.0",
    "vite-plugin-singlefile": "^2.0.0",
    "wrangler": "^4.0.0"
  }
}
```

`check:apps` is the drift gate: rebuild the views, then fail if the committed output moved.
Wire it into whatever gate the project already runs, so a hand-edited generated module
cannot ship.

## `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "types": ["@cloudflare/workers-types", "node"],
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  },
  "include": ["src", "app", "scripts"]
}
```

## `vite.config.ts`

```ts
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

// One entry per app. viteSingleFile inlines JS and CSS into the HTML, which is what
// makes a view work with no same-origin server and a deny-by-default CSP.
//
// One entry per app rather than one shared bundle: a shared bundle would ship every
// view's code to a host that asked for one.
export default defineConfig({
  plugins: [viteSingleFile()],
  build: {
    outDir: "dist",
    emptyOutDir: false,
    rollupOptions: { input: process.env.INPUT },
  },
});
```

## `wrangler.toml`

```toml
name = "my-mcp-app"
main = "src/index.ts"
compatibility_date = "2026-09-01"

[observability]
enabled = true
```

## `.gitignore`

```text
node_modules/
dist/
.wrangler/
package-lock.json
```

`src/apps/generated/` is **committed**, not ignored. That is what makes the drift gate
possible and what lets every toolchain read the same artefact.

## `src/index.ts`

```ts
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { Hono } from "hono";
import { cors } from "hono/cors";
import { buildMcpServer } from "./mcp/server";

const app = new Hono();

// CORS on /mcp is required for any browser-based host, including the reference
// basic-host used for local testing: it fetches this endpoint cross-origin, and
// without a preflight response the connection fails before a single tool is
// listed. Easy to omit, because a curl against the same endpoint works fine.
//
// Tighten the origin before production. "*" is right for a template and wrong
// for a deployment.
app.use("/mcp", cors({
  origin: "*",
  allowHeaders: ["content-type", "authorization", "mcp-protocol-version"],
  allowMethods: ["POST", "GET", "OPTIONS"],
}));

app.get("/health", (c) => c.text("ok"));

// Stateless Streamable HTTP: a fresh server per request, closed when the response
// is written. This is the shape the 2026-07-28 core spec made standard, and the
// reason capability-based conditional registration cannot work here.
//
// Streamable HTTP defines GET on the MCP endpoint for server-initiated messages.
// A stateless server has no stream to offer, and the honest answer is 405: this
// endpoint exists and does not do that. Without this Hono falls through to 404,
// which tells a probing host the endpoint is absent rather than that the method
// is unsupported, and the host logs a hard error for what is a normal negotiation.
app.get("/mcp", (c) => c.text("Method Not Allowed", 405, { allow: "POST, OPTIONS" }));

app.post("/mcp", async (c) => {
  const mcp = buildMcpServer();
  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });
  await mcp.connect(transport);
  const response = await transport.handleRequest(c.req.raw);
  await mcp.close();
  return response;
});

export default app;
```

## `src/mcp/server.ts`

```ts
import { registerAppTool } from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerAppResources } from "../apps/resources";
import { UI } from "../apps/uris";

export function buildMcpServer(): McpServer {
  const mcp = new McpServer({ name: "my-mcp-app", version: "0.0.1" });

  // ---------------------------------------------------------------------------
  // Register app tools UNCONDITIONALLY.
  //
  // The upstream guidance is to branch on getUiCapability() inside
  // server.server.oninitialized. That assumes one long-lived server spanning
  // initialize and tools/list. This Worker builds a fresh McpServer per request
  // and closes it, so oninitialized fires on an object destroyed microseconds
  // later and tools/list would permanently take the fallback branch, with no
  // error and no warning.
  //
  // Degrade in what the RESULT CONTAINS instead: a text content block for every
  // host, structuredContent for the view. A host without the extension treats
  // _meta.ui.resourceUri as inert metadata, so this costs it nothing, and the
  // tool list stays identical across clients.
  // ---------------------------------------------------------------------------
  registerAppTool(
    mcp,
    "sample_reading",
    {
      title: "Sample reading",
      description: "Returns a sample reading, with an interactive view where supported.",
      inputSchema: {},
      // Every hint explicit: an omitted destructiveHint reads as true on a non-read tool.
      annotations: {
        title: "Sample reading",
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
      _meta: { ui: { resourceUri: UI.sample } },
    },
    async () => {
      const reading = { label: "Sample reading", value: Math.round(Math.random() * 100), unit: "units" };
      return {
        content: [{ type: "text", text: `${reading.label}: ${reading.value} ${reading.unit}` }],
        structuredContent: reading,
      };
    },
  );

  registerAppResources(mcp);
  return mcp;
}
```

## `src/apps/uris.ts`

```ts
/** The ui:// URIs, in one place, so a tool and its resource cannot drift apart. */
export const UI = {
  sample: "ui://sample/app.html",
} as const;
```

## `src/apps/resources.ts`

```ts
import { registerAppResource, RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
// Specifier must NOT end in .html - see the note in scripts/build-apps.ts.
import sampleHtml from "./generated/sample-view";
import { UI } from "./uris";

export function registerAppResources(mcp: McpServer): void {
  // Five POSITIONAL arguments: (server, name, uri, config, readCallback).
  // The upstream add-app-to-server skill teaches an object form that does not
  // compile; this wraps McpServer.registerResource, which is why name precedes uri.
  registerAppResource(
    mcp,
    "Sample view",
    UI.sample,
    { mimeType: RESOURCE_MIME_TYPE },
    async () => ({
      contents: [
        {
          uri: UI.sample,
          mimeType: RESOURCE_MIME_TYPE,
          text: sampleHtml,
          // _meta.ui.csp and _meta.ui.domain belong HERE, in the content item,
          // not in the config object above. Omitted entirely on purpose: this
          // view makes no network requests, because callServerTool is a
          // postMessage rather than a fetch and is unaffected by CSP. Declaring
          // nothing is the secure default and the correct one.
          //
          // If a view ever does need a direct call, the shape is:
          //   _meta: { ui: { csp: { connectDomains: ["https://api.example.com"] } } }
          // and, only for an API that allowlists origins, a host-specific
          // _meta.ui.domain alongside it.
        },
      ],
    }),
  );
}
```

## `scripts/build-apps.ts`

```ts
/**
 * Build each view to a single HTML file, then emit it as a committed TypeScript
 * module exporting the HTML as a string.
 *
 * WHY NOT read the file at request time. Every official MCP Apps example does:
 *
 *     const html = await fs.readFile(path.join(import.meta.dirname, "dist", "app.html"));
 *
 * There is no filesystem in a Worker, so that cannot run. The alternatives all
 * leak into other toolchains: a bundler-specific raw-text import only works if the
 * deploy bundler is also the test and typecheck bundler (it is not), and a
 * runtime-specific text-module rule works in the Worker while breaking every tool
 * that imports the same module outside it.
 *
 * A generated .ts module is the one artefact tsc, vitest, tsx and the deploy
 * bundler all read identically, with no configuration in any of them.
 *
 * NAMING IS LOAD-BEARING: the file is <name>-view.ts, never <name>.html.ts.
 * An import specifier ending in .html is resolved TWICE, differently. TypeScript
 * follows extension resolution to the .ts file and types it as string, so tsc
 * passes; esbuild sees the .html suffix and applies its TEXT loader, handing the
 * raw file bytes to the runtime instead of the module's evaluated export. The
 * resource then serves TypeScript source to the host. Both toolchains are green
 * and the artefact is wrong.
 */
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { gzipSync } from "node:zlib";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "src", "apps", "generated");

/** One entry per view. Add a line here and the rest follows. */
const APPS = [
  { name: "sample", entry: "app/index.html" },
];

mkdirSync(OUT, { recursive: true });

for (const { name, entry } of APPS) {
  execFileSync("npx", ["vite", "build"], {
    cwd: ROOT,
    stdio: "inherit",
    env: { ...process.env, INPUT: entry },
  });

  // Vite preserves the entry's directory under outDir, so app/index.html emits
  // to dist/app/index.html. Derive it rather than assuming dist/index.html.
  const html = readFileSync(join(ROOT, "dist", entry), "utf-8");

  // JSON.stringify, never a template literal. Bundled JavaScript routinely
  // contains backticks and ${, which would escape a template literal and
  // produce a file that either fails to parse or, worse, parses into
  // something else entirely.
  const module = `// GENERATED by scripts/build-apps.ts. Do not edit.\n` +
    `export default ${JSON.stringify(html)} as string;\n`;

  writeFileSync(join(OUT, `${name}-view.ts`), module, "utf-8");
  const kb = (Buffer.byteLength(html) / 1024).toFixed(1);
  const gz = (gzipSync(Buffer.from(html)).length / 1024).toFixed(1);
  console.log(`built ${name}: ${kb} KB raw, ${gz} KB gzip -> src/apps/generated/${name}-view.ts`);
}
```

## `app/index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sample MCP App</title>
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <main id="root">
      <p class="muted" id="status">Waiting for data...</p>
    </main>
    <script type="module" src="./main.ts"></script>
  </body>
</html>
```

## `app/main.ts`

```ts
import {
  App,
  applyDocumentTheme,
  applyHostFonts,
  applyHostStyleVariables,
} from "@modelcontextprotocol/ext-apps";

const root = document.getElementById("root") as HTMLElement;

type Reading = { label: string; value: number; unit: string };

function render(reading: Reading | null, busy = false): void {
  if (!reading) {
    root.innerHTML = `<p class="muted">Waiting for data...</p>`;
    return;
  }
  root.innerHTML = `
    <div class="card">
      <div class="row">
        <div>
          <div class="muted">${escapeHtml(reading.label)}</div>
          <strong>${reading.value} ${escapeHtml(reading.unit)}</strong>
        </div>
        <button id="refresh" ${busy ? "disabled" : ""}>
          ${busy ? "Refreshing..." : "Refresh"}
        </button>
      </div>
    </div>`;
  document.getElementById("refresh")?.addEventListener("click", refresh);
}

/** Never interpolate tool output into HTML unescaped: it is data, not markup. */
function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c] as string,
  );
}

const app = new App({ name: "Sample MCP App", version: "0.0.1" });

// ---------------------------------------------------------------------------
// Register EVERY handler before connect(). connect() completes the handshake and
// the host may push the tool result immediately after, so a handler attached one
// line later misses it. Locally the round trip hides this; over a real connection
// it does not.
// ---------------------------------------------------------------------------

app.ontoolresult = (result) => {
  render((result.structuredContent as Reading | undefined) ?? null);
};

app.onhostcontextchanged = (ctx) => {
  if (ctx.theme) applyDocumentTheme(ctx.theme);
  if (ctx.styles?.variables) applyHostStyleVariables(ctx.styles.variables);
  if (ctx.styles?.css?.fonts) applyHostFonts(ctx.styles.css.fonts);
  if (ctx.safeAreaInsets) {
    const { top, right, bottom, left } = ctx.safeAreaInsets;
    document.body.style.padding = `${top + 12}px ${right + 12}px ${bottom + 12}px ${left + 12}px`;
  }
};

app.onteardown = async () => {
  // Stop anything still running. Views are created and destroyed as the
  // conversation scrolls, so leaks accumulate across a session.
  return {};
};

async function refresh(): Promise<void> {
  render(null, true);
  try {
    const result = await app.callServerTool({ name: "sample_reading", arguments: {} });
    render((result.structuredContent as Reading | undefined) ?? null);
  } catch (err) {
    // The model cannot see the iframe, so tell it the view is degraded rather
    // than failing silently and letting it describe data nobody can see.
    root.innerHTML = `<p class="muted">Could not refresh. Try asking again.</p>`;
    await app.updateModelContext({
      content: [{ type: "text", text: `The sample view failed to refresh: ${String(err)}` }],
    });
  }
}

await app.connect();
```

## `app/styles.css`

```css
/* Style from the host's variables, never from literals: the same view runs in light
   and dark, in several hosts, at sizes you do not choose. Every var() carries a
   fallback because a host may omit one. */
:root {
  color-scheme: light dark;
}

body {
  margin: 0;
  padding: 12px;
  background: var(--color-background-primary, Canvas);
  color: var(--color-text-primary, CanvasText);
  font-family: var(--font-sans, system-ui, sans-serif);
  font-size: var(--font-text-md-size, 14px);
}

.card {
  background: var(--color-background-secondary, rgba(127, 127, 127, 0.08));
  border: var(--border-width-regular, 1px) solid var(--color-border-primary, rgba(127, 127, 127, 0.3));
  border-radius: var(--border-radius-md, 8px);
  padding: 12px;
}

.muted {
  color: var(--color-text-secondary, GrayText);
}

.row {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
}

button {
  font: inherit;
  color: var(--color-text-inverse, Canvas);
  background: var(--color-background-inverse, CanvasText);
  border: 0;
  border-radius: var(--border-radius-sm, 6px);
  padding: 6px 12px;
  cursor: pointer;
}

button[disabled] {
  opacity: 0.6;
  cursor: default;
}
```

## After writing it out

```bash
npm install
npm run build:apps     # writes src/apps/generated/sample-view.ts - commit it
npm run typecheck
npm run dev            # wrangler dev, then point a host at /mcp
```

Measured on 16/10/2026: the view builds to 438.7 KB raw / 106.8 KB gzip, `tsc --noEmit` is
clean, and the Worker bundles to 2,072 KiB / 376 KiB gzip, inside the free plan's 3 MB
compressed limit (verify current limits at developers.cloudflare.com/workers/platform/limits).
Re-run these after any dependency bump: the numbers are the fastest signal that something
regressed.

Then work through [verification-tiers.md](verification-tiers.md) before calling it done. A
green build is not evidence; only a render is evidence of a render.

## The lean-client question

The SDK's `App` class costs roughly 431 KB raw and 102 KB gzip for a trivial view, against
2.21 KB and 1.16 KB for a hand-rolled `postMessage` client at the same feature level. Those
figures were measured on 04/09/2026 and [serverless-deployment.md](serverless-deployment.md)
explains where the weight comes from; re-measure rather than trusting this paragraph.
The scaffold above uses `App`, which is the right default:
it is supported, it validates messages, and startup budget rather than size is usually what
binds.

Reach for a hand-rolled client only when a measurement says to. If you do, note that
`ui/initialize` takes `appInfo` / `appCapabilities` / `protocolVersion`, **not** the
`clientInfo` / `capabilities` pair an MCP core `initialize` takes. The two look
interchangeable and are not: a host validates this and answers a bare JSON-RPC error, after
which it never sends a tool result, so the view paints correctly and stays empty forever
with nothing in the server logs. Re-measure the figures above on any ext-apps or SDK bump.
