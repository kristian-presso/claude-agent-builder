# Host context, patterns and security

## Contents

- Theming from host context
- Display modes are requests
- Patterns: app-only tools, polling, chunking, streaming input, model context, view state
- A view makes a number look true
- Security: sandbox, CSP, auth, open questions

## Theming from host context

The host sends `McpUiHostContext` in the `ui/initialize` reply and on every
`host-context-changed`: `theme`, `styles.variables`, `styles.css.fonts`, `displayMode` and
`availableDisplayModes`, `containerDimensions`, `locale`, `timeZone`, `platform`,
`deviceCapabilities` and `safeAreaInsets`.

```ts
app.onhostcontextchanged = (ctx) => {
  if (ctx.theme) applyDocumentTheme(ctx.theme);
  if (ctx.styles?.variables) applyHostStyleVariables(ctx.styles.variables);
  if (ctx.styles?.css?.fonts) applyHostFonts(ctx.styles.css.fonts);
};
```

Style from the variables (`--color-background-*`, `--color-text-*`, `--color-border-*`,
`--font-sans`, `--border-radius-*` and so on), always with a fallback because a host may omit
one: `background: var(--color-background-primary, Canvas);`.

The test that catches theming bugs: switching `theme` must produce a **different computed
background**. Hardcoded colours survive a light-mode screenshot and fail a real user in dark
mode. Respect `safeAreaInsets` on mobile hosts; it is always zero on a desktop test, which is
why it gets skipped.

## Display modes are requests

```ts
const { mode } = await app.requestDisplayMode({ mode: "fullscreen" });
```

Offer the control only when `availableDisplayModes` includes the mode, and lay out by the
mode the host **returned**, not the one you asked for. Anything bigger than the inline frame
(a document, a map, a floor plan, a long table) owes a way out of it. Test both answers: the
host says yes, and the host says `inline`. A reference host that always says yes cannot show
you the no.

## Patterns

- **App-only tools.** `visibility: ["app"]` keeps polling, pagination and chunk loaders out
  of the model's list. They are still network endpoints: authenticate them fully.
- **Polling.** Clear the interval in `onteardown` and pause while offscreen with an
  `IntersectionObserver`. Otherwise every dashboard opened in a session polls forever.
- **Chunked reads.** Hosts cap response size. Return offset-and-count slices with a
  `hasMore` flag and let the view loop.
- **Streaming input.** `ontoolinputpartial` delivers healed but incomplete arguments while
  the model is still generating. Render a preview, never act on it. The cheapest large
  improvement to perceived latency.
- **Errors.** Validation failures go in the tool result as `isError: true` with text the
  model can act on. A failure inside a live view is invisible to the model, so say so with
  `updateModelContext`, or the model will describe data nobody can see.
- **Keeping the model informed.** Send a short `updateModelContext` summary on meaningful
  interaction (a filter applied, rows selected), not every keystroke. Without it the model's
  next answer contradicts the screen. `ui/message` is different: it speaks as the user and
  starts a turn.
- **View state.** Presentation state (page, sort, map position) can go in `localStorage`
  keyed by the view's id, wrapped in try/catch because it can be empty or throw. Anything
  the user put effort into goes to the server through a tool.

## A view makes a number look true

A sentence can carry its caveat ("roughly 400 views, though that includes automated
fetches"). A large number in a tile reads as measured fact, and the tile is what gets quoted.
Anything inflated, sampled, partial or estimated must say so **on the surface**, not in a
tooltip. Where a metric has a sibling that cannot be inflated (paid conversions rather than
raw views), lead with the sibling.

## Security

**The sandbox.** The view runs in a sandboxed iframe: no access to the parent DOM, cookies
or storage, no parent navigation. The host, not the server, decides what a view may do.
Design for refusal.

**CSP is deny by default**, including localhost. A view that talks only through
`callServerTool` needs none, because that is postMessage. Keep it that way where you can: it
keeps credentials server-side and the data path auditable.

**CORS and stable origins.** CSP governs what the browser allows; CORS governs what an API
allows. The sandbox origin is unpredictable by default, so an API that allowlists origins
needs `_meta.ui.domain`, whose format is host-specific. Consult the host's docs rather than
guessing, and skip it unless something genuinely needs allowlisting.

**Authorisation stays at the HTTP boundary.** An unauthorised request gets HTTP `401` with
`WWW-Authenticate`; the host runs OAuth and retries. The view never holds a token. That
enables step-up sign-in: a public tool renders the view with public data, and the host runs
OAuth only when the user does something that calls a protected tool.

**Open questions the spec does not settle.** Treat them as risks: whether a host stops a
scrolled-away view from calling app-only tools (re-check scope in every handler), what
happens when a token expires while a view is polling (render a recoverable error, not a
blank pane), and how actions inside a view are attributed under an impersonated session.
