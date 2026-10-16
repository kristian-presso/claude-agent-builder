# Transports, sessions and what stateless forbids

Two choices, and they are not independent: how the client reaches the server, and whether
the server remembers anything between requests.

## stdio against streamable HTTP

**stdio** is a subprocess the client launches and talks to over pipes. It is the right
default for anything the user runs on their own machine: no port, no origin, no
certificate, and the operating system's process boundary is the security model. Its limits
follow from the same fact: one client per process, no remote access, and the client's
environment is the server's environment. That is why a server that works in a terminal can
fail when launched from a desktop app that does not inherit the shell's `PATH`.

**Streamable HTTP** is a real HTTP endpoint. Choose it when the server is shared, hosted or
reached by more than one client. Everything below applies only to it.

## The protocol went stateless in 2026

As of the `2026-07-28` MCP specification, the `initialize` handshake and the
`Mcp-Session-Id` header are gone from the core. Each request carries its protocol version,
client info and client capabilities in `_meta`, so any request can land on any instance.
Streamable HTTP requests also carry `Mcp-Method` and `Mcp-Name` headers, so a gateway can
route and rate-limit without parsing the body. Older protocol versions are still negotiated
by older clients.

Verify the current revision at modelcontextprotocol.io/specification before relying on any
detail here (checked 16/10/2026).

## What a stateless server cannot do

A stateless server builds a fresh transport per request and tracks no session. Each of
these is a real failure rather than a degradation:

- **No server-initiated messages that outlive the request.** Progress, logging and
  sampling requests belong to a live connection. The 2026 spec replaces the held-open
  stream with multi round-trip requests: the server answers `input_required` and the client
  retries with the answer attached.
- **No in-memory state between calls.** This is the one that bites, because it does not
  fail: it works on one instance and quietly stops working when there are two, or after a
  restart. Anything that must survive a call goes to a store outside the process. A dict at
  module scope is not one.
- **Capability negotiation is per request.** Anything you register conditionally, based on
  what a client said it supports, is decided again on every request from whatever that
  request said. Register unconditionally and degrade in what the result contains.

Application state is still fine. Return an explicit id ("deploymentId") and let the model
pass it back; the protocol is stateless, the product need not be.

## Draft, then confirm, across instances

The two-step pattern for anything that reaches a person (prepare a draft and show it, then
confirm to send) needs the draft to survive between two requests that may land on
different instances. The symptom of keeping it in a module-level dict is a fraction of
confirms failing with "not found", in proportion to how many instances are running, and
never locally.

- **Store the draft outside the process**: a database, Redis, Firestore, or the downstream
  system's own draft object, keyed by an unguessable id and with an expiry. Or make the
  draft self-contained: a signed token carrying its content, verified on confirm.
- **Bind the draft to what the person saw.** It is immutable once shown, bound to the
  caller who created it, and confirm sends exactly that content (check the total or a hash
  if anything could change it). A confirm must not be able to send a different draft or
  someone else's.
- **Consume it once, atomically** (get-and-delete, or a status change in a transaction), so
  two confirms cannot both send.
- **Refuse clearly when it is gone**: "That draft has expired or does not exist. Call
  `draft_invoice` again and show the person the new preview before confirming." That is a
  refusal, not a failure, so the model re-drafts instead of retrying or reporting success.

Sticky sessions or a single instance hide the bug rather than fix it: a restart or a deploy
still loses every pending draft.

## Python SDK knobs

In the Python SDK (`mcp`), streamable HTTP takes `stateless_http` and `json_response`.
On 1.29.1, passing `session_idle_timeout` with stateless mode raises at start-up;
on 1.30.0 and 2.3.0 (checked on 1.30.0, 16/10/2026)
the timeout is simply unused in stateless mode. Check your installed version's
`server/streamable_http_manager.py` rather than trusting either sentence.

## The version you cannot assume

Whatever the transport, the client's declared protocol version is data. A server that
assumes the newest version because it implements it will break older clients silently: the
reply is well-formed and a field the client does not understand is dropped on its side with
no error anywhere.
