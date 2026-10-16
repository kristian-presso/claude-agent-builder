---
name: mcp-app-builder
description: Builds and verifies an MCP App, the interactive HTML view an MCP server serves as a ui:// resource and a host such as Claude renders inside the conversation. Decides first whether the tool earns a UI at all, writes acceptance criteria that can fail, builds from a tested starter, then verifies in tiers (static, protocol, rendered, meaning) and reports a scorecard rather than an opinion. Use when someone says "build an MCP App", "add a UI to my MCP tool", "make this tool visual", "does my view actually render", "verify the MCP App", or wants an existing server's results to render rather than print.
---

# MCP App builder

An MCP App is an ordinary MCP tool paired with a `ui://` HTML resource. A host that
supports the extension renders the HTML in a sandboxed iframe and lets it call tools back.
A host that does not shows the tool's text result. This skill takes an idea to a verified
App, not to "it compiles".

The server underneath follows the `mcp-server-builder` skill. This skill covers the view
layer and how to prove it works.

## Step 1 - the gate: does this earn a UI?

Ask before building anything, and be willing to stop. A tool that does not need a view is
worse with one: more bundle, another failure surface, and detail hidden that a sentence
would have carried.

| Output | Verdict |
| --- | --- |
| Lists, tables, anything wanting search, sort or filter | Build it |
| Metrics over time | Build it |
| Media: maps, documents, images, floor plans | Build it |
| A multi-step workflow with state | Build it |
| A value that changes while the user watches (progress, a live count) | Build it, if polling is bounded and stops offscreen |
| Several interdependent fields validated before a costly action | Build it, if the entered values are echoed back to the model |
| A confirmation, or a single value that is final when produced | **Stop.** Text is better |
| A destructive action needing consent | **Stop.** A button is a weaker gate than a sentence the user must say |
| One or two scalars the model can gather by asking | **Stop.** Ask in conversation |

Emit the verdict as a decision, not prose, so it can be checked:

```json
{"decision": "refuse", "reason": "A button is a weaker consent gate than a sentence the user must say.", "alternative": "Keep the spoken confirmation: state what will happen, then require the words."}
```

A refusal with no reason is a shrug; one with no alternative is a dead end. If the verdict
is refuse, say so, give the alternative, and stop.

## Step 2 - decide the shape

1. **New server or existing?** Existing: keep every current tool working and add
   `_meta.ui.resourceUri` to the ones that earn a view. New: start from
   [references/starter-scaffold.md](references/starter-scaffold.md), written **into the
   user's own project**, never a temp directory.
2. **Which hosts?** Support varies per client and per feature. Probe rather than assume.
   See [references/testing-and-hosts.md](references/testing-and-hosts.md).
3. **Runtime.** If it is serverless or stateless, read
   [references/serverless-deployment.md](references/serverless-deployment.md) before
   writing code. Two of its three traps fail silently.
4. **SDK or hand-rolled view client?** Default to the SDK's `App` class. Hand-roll only with
   a measured reason (it is about 100 KB gzipped against about 1 KB hand-rolled).

## Step 3 - write acceptance criteria before the code

Cover: the tool and its input, what the view renders, which interactions call back, what
the text fallback says, and the criteria that settle whether it works. **Every criterion
must be capable of failing**: ask whether a wrong build could pass it.

Read [references/acceptance-criteria.md](references/acceptance-criteria.md). It lists the
shapes that have passed review and still shipped broken: a grep that proves a string exists
but not that every tool has it, a check that never opens the view, a state that only lives
in one process, an empty state nobody specified, and a host request whose "no" was never
tested.

## Step 4 - build

Follow the starter. The rules that are not optional:

- **Register app tools unconditionally.** Never branch on the client's UI capability. On a
  server built per request it silently never offers the UI.
- **Always return a text `content` block** alongside `structuredContent`. This is the whole
  degradation strategy.
- **Register every view handler before `connect()`.** A handler attached after misses the
  first tool result, and the bug hides locally.
- **Style from the host's CSS variables** with fallbacks, never from literal colours.
- **Declare no CSP** unless the view genuinely fetches something. `callServerTool` is a
  postMessage, not a network request.
- **`_meta.ui.csp` and `_meta.ui.domain` go in the read callback's `contents[]`**, not in
  the resource config and never on the tool.
- **Escape anything interpolated into HTML.** Tool output is data, not markup.
- **Clean up in `onteardown`.** Views outlive their moment as the conversation scrolls.
- **Never put a credential in the view.** The host proxies tool calls over its own
  authenticated connection.
- **Pin the SDK deliberately.** Read
  [references/sdk-versions-and-corrections.md](references/sdk-versions-and-corrections.md)
  before following any upstream snippet: several documented examples do not compile or are
  silently ignored.

Protocol detail, when needed: [references/protocol-and-meta.md](references/protocol-and-meta.md)
(resource contract, `_meta.ui` placement, the `ui/*` messages, lifecycle) and
[references/host-context-and-patterns.md](references/host-context-and-patterns.md) (theming,
display modes, polling, model-context updates, security).

## Step 5 - verify, blind, in tiers

Hand verification to a fresh agent or reviewer that gets the acceptance criteria and the
diff, and nothing else: not the plan, not the build notes. An agent that read the plan
verifies the plan. If you cannot dispatch one, run the tiers yourself and say so.

Run the tiers in [references/verification-tiers.md](references/verification-tiers.md):

1. **Static** - resource and tool links resolve, MIME type, text fallback on every app
   tool, handler order, CSP placement, no capability branching.
2. **Protocol** - `tools/list`, `tools/call` returns `content` and `structuredContent`,
   `resources/read` returns HTML, and the fallback path works with the UI withheld.
3. **Rendered** - a real host paints a non-zero box with no console or CSP errors, and
   switching theme changes the computed background.
4. **Meaning** - every displayed figure has a known provenance and matches a fixture. No
   browser can check this.
5. **Budget** - bundle size, raw and gzipped, against the last recorded figure.

Every check reports **pass**, **fail** or **unmeasured**. Unmeasured blocks a ship exactly
as a failure does. "Tiers 1 and 2 passed, tier 3 not run" is a useful report. "Verified" is
not.

## Step 6 - ship

If the App is meant for the public, run the directory checklist in the `mcp-server-builder`
skill: screenshots of this view are part of the Claude listing. Submitting is public and
stays the owner's decision.

## Rules

- Never claim a host renders it without having seen it render. A green build is not
  evidence; only a render is evidence of a render.
- Never remove a working text path to make room for a view.
- Never infer a pass from a related check. "The resource read" is not "the view rendered".
- Stop and say so when the honest answer is that a UI is the wrong tool.

## Example

> "Add a view to `list_orders` so store owners can search their orders."

Gate: a list wanting search, so build. Criteria include: typing a partial customer surname
into the view's filter narrows the visible rows to matches (driven in a browser, not checked
through the tool's query parameter); a store with no orders shows "No orders yet" in both
the view and the text fallback; the order time in the view and the text agree.
Build from the starter, then a fresh agent runs the tiers and returns a scorecard such as
"static 9/9 pass, protocol 8/8 pass, rendered 4/5 pass with dark-mode background
unchanged (fail), meaning unmeasured".

## Configuration

Two things vary: the **runtime** the server deploys to (the starter targets a serverless
Worker; a long-lived Node process removes two of the traps), and **which hosts** must
render the view, since support differs per client.
