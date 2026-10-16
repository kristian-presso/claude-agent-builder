# Tool design

## Contents

- The description is the routing surface
- Names: two rules the SDK will not enforce
- Titles and annotations (the three classes)
- Structured output is inferred from your return annotation
- Schemas: make the refusal impossible

A tool is not an API endpoint with a different envelope. Its caller is a model choosing
between thirty of them from their metadata alone, so the metadata is the product.

## The description is the routing surface

Before a tool is ever invoked, the model reads its name, title, description and input
schema and decides whether this is the one. A description that documents the
implementation ("wraps the internal ledger query") tells the model nothing about when to
choose it. One that names the question it answers ("what this customer has been charged
this month, and whether anything failed") does.

Write for a reader who is deciding, not one who has already decided:

- What it answers, and what it will not.
- What the caller must have ready.
- When two tools are close enough to be confused, which one to prefer and when. That
  sentence is cheaper than the wrong call.

Do not put instructions to the model in a description ("always call this first"). Hosts
treat descriptions from untrusted servers as untrusted, and directory reviews reject
injection-shaped descriptions.

## Names: two rules the SDK will not enforce

The specification allows 1 to 128 characters of `A-Z a-z 0-9 _ - .`, case-sensitive. The
Python SDK has that as a regex, but **validation never blocks registration**: it logs a
warning and registers the tool anyway (checked against `mcp` 1.29.1 and 2.3.0, 16/10/2026). A name with a space in it starts cleanly and fails later at whichever client is
stricter, where it looks like a client bug.

1. **Validate names yourself, in a test.** Assert every registered name against the regex.
   A log warning nobody reads is not a control.
2. **Assume clients are stricter than 128.** Short, lowercase, underscore-separated and
   verb-first survives everywhere. Prefer `create_event` over `calendar.create_event`.

## Titles and annotations

Directory reviews ask for a human-readable `title` on every tool plus the applicable hints
(see [directory-listing.md](directory-listing.md)). Registering those by hand across thirty
tools invites drift, so declare intent once and derive the rest:

```python
from mcp.types import ToolAnnotations

def _tool(title, *, read_only, destructive, idempotent, open_world):
    return {
        "title": title,
        "annotations": ToolAnnotations(
            title=title, readOnlyHint=read_only, destructiveHint=destructive,
            idempotentHint=idempotent, openWorldHint=open_world,
        ),
    }

def read_only(title, *, open_world=False):
    """Only reads: changes nothing, so calling it twice is free."""
    return _tool(title, read_only=True, destructive=False, idempotent=True, open_world=open_world)

def write(title, *, idempotent=False, open_world=False):
    """Changes state, but nothing the user cannot take back: create, add, record."""
    return _tool(title, read_only=False, destructive=False, idempotent=idempotent, open_world=open_world)

def destructive(title, *, idempotent=False, open_world=False):
    """Can do something irreversible in any mode: delete, overwrite, send, refund, revoke."""
    return _tool(title, read_only=False, destructive=True, idempotent=idempotent, open_world=open_world)
```

Then `@app.tool(**read_only("List orders"))`, `@app.tool(**write("Create draft"))` or
`@app.tool(**destructive("Refund order"))` at each site.

| Class | `readOnlyHint` | `destructiveHint` | Use for |
| --- | --- | --- | --- |
| read-only | true | false | Lists, lookups, quotes, previews |
| write | false | false | Additive or easily undone changes: create a draft, add an item, record feedback |
| destructive | false | true | Deletes, overwrites, refunds, sends, publishes, revokes |

Edge cases that catch people:

- A tool that **returns a plan the client will execute** is not read-only, even though it
  only returns JSON. Nor is a tool that only writes a log or queues a job: any state change
  counts.
- **Do not mark everything destructive to be safe.** Hosts ask the user to approve
  destructive calls, so over-marking turns every harmless create into a prompt, and reviews
  reject hints that do not match behaviour.
- **Split merged tools.** A tool whose default lists things but which can also delete is
  destructive as a whole. Make it a read-only tool and a destructive tool.
- **Write the title in both places**: the tool's `title` and `annotations.title`. Clients
  differ in which one they render.
- **Set every hint explicitly.** The specification defaults an omitted `destructiveHint` to
  true on a tool that is not read-only.
- **Pin the destructive set in a test**, by name, so a refund tool quietly re-registered as
  a write fails the build.

`openWorldHint` is about reach, not danger: true for the public internet or open-ended
external entities (web search, posting publicly, messaging outside recipients); false for a
bounded private account, even one hosted by a third party.

## Structured output is inferred from your return annotation

In the Python SDK, `@app.tool()` takes `structured_output=None`, and `None` means "infer
from the function's return type annotation". Changing a tool's return annotation therefore
changes its wire shape (whether an output schema is published and whether results carry
`structuredContent`) with no edit to the decorator and no warning. Treat the return
annotation as part of the public contract and changelog it like a renamed field.

## Schemas: make the refusal impossible

Every input you accept you must validate, and every input you validate a caller can get
wrong. Prefer a schema that cannot express the invalid state:

- an enum over a free string;
- a required field over an optional one with a fallback;
- one tool per mode rather than a `mode` parameter that changes what the others mean.

Give every parameter a description and an example. Where a value cannot be validated by the
schema (a path, an id from another system), validate it in the body and refuse in the shape
[errors-and-refusals.md](errors-and-refusals.md) describes.
