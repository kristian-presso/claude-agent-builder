# Verification tiers

## Contents

- What the verifier receives
- Tier 1: static conformance
- Tier 2: protocol
- Tier 3: rendered
- Tier 4: meaning
- Tier 5: budget
- Scorecard

These are the standing checks every MCP App owes, whatever its own spec says. A spec's
criteria are additional, never a substitute.

## What the verifier receives

The acceptance criteria and the diff. **Not** the plan, the build notes or the conversation.
An agent that reads the plan verifies the plan: it inherits the builder's assumptions and
checks the same things the builder thought to check. If a criterion cannot be settled without
that context, mark it unmeasured and say why rather than reaching for the plan.

Where you have no script for a tier, run it by hand and report the same three results. Never
downgrade a check you could not automate to a pass.

## Tier 1: static conformance

No server needed. All must pass.

1. Every tool's `_meta.ui.resourceUri` resolves to a registered resource.
2. Every UI resource is referenced by at least one tool. Orphans either way are silent bugs.
3. Every resource reads back with `text/html;profile=mcp-app` and non-empty HTML.
4. **Every app tool returns a non-empty text `content` block.** The most commonly missing.
5. View handlers are registered before `connect()`. Check the order in the source.
6. No tool declares `_meta.ui.csp`.
7. Any `csp` or `domain` sits in the read callback's `contents[]`.
8. No capability branching decides which tools get registered.
9. Every tool has a title and explicit `readOnlyHint` and `destructiveHint`.
10. Generated view modules match a fresh build: rebuild, diff, fail on a difference.

## Tier 2: protocol

Run the server and drive it with the reference host or any MCP client.

1. `tools/list` includes the app tools.
2. `tools/call` returns both `content` and `structuredContent`.
3. `resources/read` returns the HTML.
4. The view's `ui/initialize` completes and `ui/notifications/initialized` follows.
5. The tool result reaches the view.
6. A view-initiated `callServerTool` round-trips.
7. `size-changed` reports a non-zero, bounded size where the container is flexible.
8. **With the UI capability withheld, the same call still gives a usable text answer.** The
   check everyone skips, guarding the property most relied on.

If the server needs OAuth and the host cannot do it, mark the tier unmeasured and say so.

## Tier 3: rendered

The only tier that proves a person sees something. Drive a real client or browser automation
against one.

1. The iframe is present and paints a non-zero box.
2. No console errors and no CSP violations. Separate the host's own errors (for example its
   `GET /mcp` probe getting 405) from the app's.
3. **Switching theme changes the computed background.**
4. Safe-area insets are respected where supplied.
5. Each requirement about what a person sees or does is driven to its state: type into the
   filter, empty the data, fail the dependency, decline the display mode.

## Tier 4: meaning

Every check above proves the mechanism. None proves the number is true. A view can pass all
of them while showing a wrong figure, and a rendered tile lends that figure authority prose
does not.

1. Name each displayed figure's provenance: measured, derived or estimated.
2. Assert against a known fixture, not whatever the server returned.
3. Check that anything inflated, sampled or partial is labelled on the surface.
4. Escalate any figure nobody can source to a person.

Report this tier as unmeasured unless a data assertion or a person actually ran it. It is
the tier most often skipped, because the screenshot looks convincing.

## Tier 5: budget

Bundle size per view and for the server, raw and gzipped, against the last recorded figure.
Size is rarely the limit; cold-start parse time is.

## Scorecard

| Tier | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | text fallback on every app tool | pass | called 3 of 3 tools, each returned text |
| 3 | theme switch changes background | fail | `rgb(255,255,255)` in both themes |
| 4 | figures match fixture | unmeasured | no fixture in repo |

Every fail carries observed against expected. Every unmeasured carries the reason. Exit as a
gate: all ran and passed; something failed; nothing failed but something was unmeasured. The
last blocks a ship exactly as a failure does.
