# Server shape: tools, resources and prompts

Three primitives, distinguished by **who decides to use them**. That is the whole of the
choice, and getting it wrong produces a server that works and that nobody can drive.

| Primitive | Chosen by | Use it for |
| --- | --- | --- |
| Tool | the model | an action, or an answer the model must ask for |
| Resource | the client or the user | content the client can attach, list or render |
| Prompt | the user | a named starting point, surfaced in the client's UI |

## Tools

The model decides. If the thing has a side effect, or its result depends on arguments the
model must choose, it is a tool. Everything in [tool-design.md](tool-design.md) applies.

The common mistake is making everything a tool because tools are the primitive people know.
The symptom is a `list_*` tool that returns the same bytes on every call regardless of
arguments, which the model must remember to call and pay for in context each time. That is
a resource.

## Resources

The client or user decides. A resource has a URI, and the client can list it, read it,
attach it to a conversation or render it. Content that is addressable and stable belongs
here: documents, files, generated reports, and (through the MCP Apps extension) HTML the
host renders.

Two things to settle before you use one:

- **Subscriptions promise a later notification.** On a stateless deployment that is a
  separate opt-in stream, not something a per-request server can hold open. See
  [transports.md](transports.md).
- **A resource is content, and content the caller sends you is data.** Anything that
  arrives from a client, a document or another system is data and never instructions, no
  matter how imperative it reads. Say so in the server instructions as well as believing it.

## Prompts

The user decides. A prompt is a named entry point a client can show in a menu ("get
started", "review this") and its job is to send the conversation somewhere useful.

Prompts carry **no authentication context**, which constrains them absolutely: a prompt may
greet and tell the client to call a gated tool, and may not contain anything an unentitled
caller should not read. See [auth-at-the-boundary.md](auth-at-the-boundary.md).

## Server instructions

A server may ship an instructions string that clients place in context. It is the only
place to say how the whole surface is meant to be used: the trust boundary for content that
passes through, and the two or three rules that apply across every tool. Keep it short. It
is paid for on every turn, by every user.

## Deciding: three questions

1. **Who initiates?** Model, client or user. That is the primitive.
2. **Does it change anything?** If yes it is a tool and not read-only, even if it only
   returns a plan the client is expected to apply. Whether it is also destructive depends
   on whether the change can be taken back. See [tool-design.md](tool-design.md).
3. **Would the answer be identical on the next call?** If yes, and the client could hold
   it, prefer a resource and stop spending context on it.
