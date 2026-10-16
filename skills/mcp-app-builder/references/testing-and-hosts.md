# Testing, and which hosts render

## The reference host (`basic-host`)

The MCP Apps project ships a reference host, `basic-host`, that shows tool input, tool
result, messages to the model and model-context updates in four panels. Point it at a running
server:

```bash
SERVERS='["http://localhost:3001/mcp"]' npm start
```

then open `http://localhost:8080`.

**It is not in the npm package.** The `@modelcontextprotocol/ext-apps` tarball contains only
`dist/`, `LICENSE`, `package.json` and `README.md` (checked 09/09/2026 on 1.7.5). Take
`basic-host/` from the upstream repository at the tag matching your pinned version and commit
it inside the project, recording the tag. Its known start-up defects are in
[sdk-versions-and-corrections.md](sdk-versions-and-corrections.md) (items 5 to 7).

If you cannot run it, the protocol tier still has to be answered: drive `tools/list`,
`tools/call` and `resources/read` over the wire with any MCP client and assert on the
responses. Rendering needs a real host regardless. Report anything you could not run as
unmeasured.

If the server requires OAuth, `basic-host` is not an OAuth client. Expose an unauthenticated
development route or use a direct-token mechanism the server already supports.

## Driving the view in a browser

For anything a person sees or does, drive the view in a browser rather than calling the tool.
With Playwright against `basic-host`, the app's document sits two frames deep because the host
wraps it in a sandbox frame:

```js
const view = page.frameLocator("iframe").frameLocator("iframe").last();
await view.getByRole("textbox").fill("smi");
await expect(view.getByRole("listitem")).toHaveCount(1);
```

To test a host saying **no** to a display-mode request without modifying the host, add an
init script that rewrites the host's reply to `{ mode: "inline" }` in the sandbox frame, then
assert on the view's own layout and controls (the host page's panel will still expand).

## What the reference host does not prove

- that a production host renders the view the same way;
- that theming works, since real hosts supply richer style variables;
- anything about mobile, safe areas or touch;
- that the text fallback is reachable, unless you test it deliberately.

Test in at least one real client before believing it works.

## Reaching a real client

A hosted client cannot see localhost, so tunnel:

```bash
npx cloudflared tunnel --url http://localhost:3001
```

Add the URL plus the MCP path as a custom connector. The tunnel URL changes on every
restart: fine for a spike, not for anything durable.

## Client support

The official client matrix at modelcontextprotocol.io lists, as of 04/09/2026: Claude web,
Claude Desktop, ChatGPT, Cursor, VS Code GitHub Copilot, Microsoft 365 Copilot, Goose,
Postman, MCPJam and others. **It is community-maintained.** Treat each row as a claim to
probe, and remember support varies by feature within a client: "supports MCP Apps" does not
mean every `ui/*` method works.

## Assertions that never fail are not assertions

Break the build on purpose, in the way one named assertion should catch, and require that
assertion to go red. Two things this finds that review does not:

1. **Exit-code collisions.** A harness that reads exit code 2 as "could not tell" disarms
   every check built on `tsc`, `grep` or `diff`, which all exit 2 on real errors.
2. **A break the build erases.** Breaking a generated file proves nothing when the next step
   regenerates it. Break the generator instead.

If the deliberate break could not be applied because its target text was not there, that is
evidence of nothing, not evidence the check works.
