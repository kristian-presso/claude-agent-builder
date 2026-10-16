# Acceptance criteria for an MCP App

## Contents

- The test: could a wrong build pass it?
- Worked examples
- Seven shapes that passed review and shipped broken
- Reporting

## The test: could a wrong build pass it?

If yes, it is not a criterion. Write criteria before the build, while deciding the goal and
deciding how you would know are the same act. Criteria written afterwards describe the
artefact and pass by construction.

## Worked examples

| Not a criterion | A criterion |
| --- | --- |
| The app works | `resources/read` returns `text/html;profile=mcp-app` with a body beginning `<!doctype html>` |
| The view renders | The iframe paints a box of non-zero width and height, with no console errors |
| It talks to the server | Clicking refresh calls back through `callServerTool` and the view shows a value the first result did not |
| Degradation works | With the UI capability withheld, the same call returns usable text |
| Every tool returns text | Call each app tool and inspect its result for a non-empty text block |
| State persists | Mutate, **restart the server**, read back: the mutation is still there |

Name the channel when more than one exists. A server can answer `curl` perfectly and be
unreachable from the browser-based host meant to call it.

## Seven shapes that passed review and shipped broken

Each shares one shape: the assertion claimed more than its check could observe.

**1. A grep proving a string exists proves nothing about "every".** "Every app tool returns
text" checked with `grep -q 'type: "text"'` passed a file with three occurrences after one
was broken. When a criterion says every, count them or call them.

**2. A criterion that never opens the view cannot speak for what a person sees.** Three real
builds passed 68 criteria between them and covered one of nine stated requirements, because
the criteria called the server and grepped the source. A list view "with a text filter"
passed with **no text input at all**, because the filter was checked through the tool's
query parameter. Where a requirement is about what a person sees or does, drive the view
into that state and read what it paints. See [testing-and-hosts.md](testing-and-hosts.md).

**3. Two calls in one process cannot tell a store from a variable.** Check-in state lived in
a module-scoped map in a per-request Worker. Every count criterion passed; after a recycle
the admissions reverted, and a person already inside read as still expected. Wherever the
app records something a person did (an admission, a payment, a vote), the criteria owe one
that mutates, restarts and reads back.

**4. An empty result is a state the app has, whether or not you specified it.** A dashboard
passed 23 criteria; none covered "no rows", and the fixture always had data. A new user saw
a blank box and reported a bug against working code. Where the app renders a collection,
owe a criterion that drives it to empty (a window before the data starts, a filter that
matches nothing) and checks that both the view and the text say so in words ("No sales in
this window yet" beats "0").

**5. Where one fact is rendered twice, assert the two agree.** The text said an arrival was
"at 12:39" (UTC) and the view said "13:39" (browser time). Every criterion checked the name
was present; none checked the time meant anything. Pin the two to each other. Relative time
("four minutes ago") avoids the problem by construction.

**6. What the view asks the host for, the host can refuse.** A floor-plan viewer never asked
for fullscreen, and nothing checked, because the reference host grants every request. For
every request a view makes of the host (display mode, opening a link, sending a message),
one criterion drives the yes and one drives the no. A link is a control, not a string: click
it and assert the popup, rather than checking the `href`.

**7. A gate the repo has and nothing calls is not a gate.** The project defined a drift check
for its generated view modules, and no criterion ran it. Where the repo commits a derived
artefact and ships a script proving it fresh, a criterion runs that script.

Also: **a criterion that stops a server must stop only its own.** Kill by the PID you
started, never by process name or port, or the criterion takes a colleague's server with it.

## Reporting

Every criterion reports **pass**, **fail** or **unmeasured**. A criterion whose precondition
is unmet (the server is not running) reports unmeasured, never fail: calling it a failure
sends someone to fix code that was never wrong. Unmeasured still blocks a ship.

A grep of the source is admissible only for what is genuinely static. It is never the sole
evidence for a behaviour a person experiences.
