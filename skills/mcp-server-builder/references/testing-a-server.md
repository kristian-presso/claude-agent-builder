# Testing a server

Three levels, each proving something the one below cannot. Skipping a level is fine as long
as you say which claim you gave up.

## Level 1: in-process

Build the application object and call into it directly. Fast, and enough for most of the
work: tool logic, gate behaviour, refusal wording, schema shapes.

Three assertions worth writing once and keeping forever:

- **The listed tool set, as an exact set.** A tool that silently disappears in a refactor
  then fails a test rather than a customer. The cheapest test in the suite.
- **Every tool declares its class**: `readOnlyHint` and `destructiveHint` both present and
  never both true, plus a title. That catches a tool registered with no annotation, which
  would otherwise pass as a read while clients treat it as destructive.
- **The destructive set, by name.**

Read annotations by their wire names (`model_dump(by_alias=True)`), not by attribute: the
Python SDK renamed the attributes to snake case in 2.x while the wire names stayed the same.
The scaffold's tests do this and pass on both 1.29.1 and 2.3.0 (re-run 16/10/2026).

## Level 2: over the protocol

Run the server over stdio and drive it with a real client session. This proves the
handshake, the framing and the serialisation, none of which level 1 touches because level 1
never encodes anything. It is also where a changed return annotation shows up as a changed
wire shape.

## Level 3: over the wire

Start the HTTP server and talk to it as a client would, with a real token. Only this level
exercises the auth layer, the Host and Origin middleware and the proxy in front, each of
which fails totally when it fails. Assert:

- An unauthenticated call is **refused with the exact wording** from
  [errors-and-refusals.md](errors-and-refusals.md). Assert the words, not only the status.
- A gated tool refuses a caller without the role, and the refusal does not disclose whether
  the target exists.
- A tool an ordinary customer must reach **is reachable** to one. This catches the hiding
  mistake in [listing-and-visibility.md](listing-and-visibility.md), and nobody writes it
  because the tool works fine for the author.

## What a local pass does not prove

- **That a real client renders it.** Clients disagree about which title field they read,
  about name punctuation and about how much description they show.
- **That the proxy passes the headers.** Level 3 against `localhost` sends `Host:
  localhost`. Production sends the public name, which is exactly what a wrong allowlist
  rejects. See [deployment.md](deployment.md).
- **That a second instance behaves like the first.** In-memory state works perfectly on one
  process.
- **That the deployed revision is the one you tested.** Check the running revision after a
  release.

## Verify against the goal, not the task list

Every test passing means every test passed. After a change, ask what a user can now do that
they could not before, and check that through the surface they use. A catalogue listing a
tool proves reachability; only calling it proves usability.

If you can, hand this step to someone or something that did not build the server: give it
the spec and the diff, not your notes. A reviewer who read the plan verifies the plan.
