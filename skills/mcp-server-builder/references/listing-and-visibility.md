# Listing and visibility

A server usually has tools not every caller should see: back-office operations, an admin
surface, a provisioning path one internal job uses. Curating the list is worth doing.
Confusing it with a permission is how you take a feature away from the person who needs it.

## Registration is once; listing is per request

Tools are registered when the application object is built, at start-up, with no request in
scope, so registration cannot depend on who is asking. The per-request seam is the
**listing**.

In the Python SDK, subclassing the server and overriding `list_tools` is enough, because
the low-level handler calls `self.list_tools` (checked on `mcp` 1.30.0 and 2.3.0, 16/10/2026):

```python
class RoleFilteredMCP(MCPServer):  # FastMCP on SDK 1.x
    async def list_tools(self):
        return [t for t in await super().list_tools() if t.name not in OPERATOR_ONLY]
```

Everything stays registered and every call-time gate is untouched.

## Hiding is not a permission

A hidden tool is still callable by anyone who knows its name. Tested on `mcp` 2.3.0: a tool
filtered out of `tools/list` this way still answered a direct `tools/call`. If the only thing
stopping a caller is that they cannot see the tool, nothing is stopping them.

- **Gate at call time, always**, whether or not the tool is listed.
- **Hide only what your own systems invoke.** The rule that survives reality is *who calls
  it*: a tool belongs in the hidden set when your code calls it, never when the user must.

Getting that wrong fails silently and completely. A customer-facing tool hidden because its
name resembled a family of internal ones (say, `apply_invite` sitting beside the internal
`issue_invite` and `revoke_invite`) is simply unavailable: the user has a valid reason to call
it, the client says it does not exist, and no log says anything is wrong.

Pin the rule with a test that asserts membership by the property that decides it, not by
restating the list of names. A test that repeats the set only proves you typed it twice.

## Do not key visibility off a role you grant everyone

If provisioning gives every customer an admin seat, "is admin" will never separate an
operator from a customer. Key on a property that actually holds: an internal account with
no external identity behind it, or an explicit allowlist of internal callers. A boundary
that is true by construction beats one that is true by convention.

## What an unauthenticated caller sees

A caller who has not signed in is not an edge case; it is the first thing that happens on
every fresh connection. Decide deliberately what `tools/list` returns to them. Listing tools
that then refuse is fine and often right, because it shows the user what connecting would
give them. Listing nothing is also defensible. Listing a tool whose refusal does not say
that signing in is the fix is not. And a refusal that tells an anonymous caller to "call
`get_started`" when `get_started` is hidden from them is a dead end.
