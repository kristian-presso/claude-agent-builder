# Authorisation at the boundary

Two boundaries, and they are not the same one. The **transport** boundary decides whether a
request may reach the server at all. The **call** boundary decides whether this principal
may run this tool with these arguments. A server that does only the first has authenticated
a connection and authorised nothing.

## Verify at the HTTP boundary, gate inside every tool

The HTTP layer verifies the credential and produces a principal: a verified token, its
claims, nothing else. Each tool then resolves that principal to what it actually needs (an
account, a customer, a workspace) and refuses if it cannot.

Keep the gate a single function every tool calls, and give it the awkward parameters rather
than letting each tool improvise:

- **`allow_degraded`** for read-only tools, so a lapsed-but-not-cancelled account keeps
  read access during a grace period while writes stop. Without it every tool re-invents the
  policy and they disagree.
- **A required role or scope**, checked in the same place, so authorisation is not
  scattered across thirty call sites.
- **An escape hatch for the recovery path.** Whatever tool restores access must not be
  gated by the thing it clears, or the only way out is closed.

**Fail closed, every time.** No token means refuse, not "treat as anonymous". An unknown
token means refuse. An exception inside the gate means refuse.

A useful shape for rate limiting: raise a `RateLimited` error that **subclasses** the
authorisation error. Every existing consumer keeps failing closed without being taught a new
exception, and anything that wants to tell "slow down" from "not allowed" still can.

## The 401 that starts sign-in

An MCP client starts its OAuth flow from an HTTP `401` whose `WWW-Authenticate` header
points at the server's protected-resource metadata. That is a transport response, not a
tool error. A server that offers some anonymous tools must still send that challenge where a
signed-in call is needed, or the client never offers the user a sign-in.

As of the `2026-07-28` spec, Dynamic Client Registration is deprecated in favour of Client
ID Metadata Documents, clients must validate the `iss` parameter, and client credentials are
bound to the issuer that minted them. Check the current authorisation section of the spec
before building the OAuth side (checked 16/10/2026).

## The listing is a separate seam from the call

Whatever `tools/list` shows, the gate runs on the call. Curating the list is presentation;
see [listing-and-visibility.md](listing-and-visibility.md).

## Just-in-time provisioning is an authorisation decision

If a verified external identity is provisioned into an account on first sight, that is a
write performed for someone not yet authorised for anything. Decide explicitly what a
first-seen identity gets. If every new account is an admin of its own space, "admin" no
longer separates your staff from your customers, and any visibility rule keyed on that role
is wrong from day one.

## Shared credentials

If the product is sold per person, the credential will be shared. Track the device or
session behind a verified identity and, above a soft threshold, require a step-up rather
than a block: a block on a false positive costs a customer, a step-up costs them a minute.
Exempt your own automation's principal type, or your scheduled jobs get challenged by a
mechanism designed for humans.

## Prompts have no auth context

An MCP prompt is served with no authenticated principal attached. It may greet and point at
a gated tool. It may not contain anything an unentitled caller should not see. Treat it as
public copy, because it is.
