# Instrumentation

## Contents

- The wrapper
- Sketch (TypeScript, any SDK with a `registerTool`-style call)
- What the wrapper cannot see
- Don't
- Check


Wrap tool registration once, before any tool is registered, so every tool is recorded without
a line of code in the tool itself. Never await the write and never let a failed write fail the
call. Tools add meaning through a handful of small helpers.

## The wrapper

1. **Decorate, don't sprinkle.** Replace the SDK's tool-registration call with a wrapper that
   times the handler, inspects the result and hands a row to a recorder. A per-tool `record()`
   call is one chance per tool to forget, and the one forgotten is always the newest.
2. **Fire and forget.** Start the insert during the call and do not await it. On a serverless
   runtime, hand the promise to the platform's keep-alive (for example `waitUntil` on Workers)
   so the write survives the response. Catch and drop any recorder error.
3. **Classify the outcome from the result:**
   - result with `isError: true` built by `refuse(code, text)` → `refused`
   - result with `isError: true` built by `fail(text)` (a failure the tool caught: a
     dependency down, a write that did not land) → `error`
   - thrown exception → `error`, rethrown untouched
   - result the tool marked with `markEmpty(result)` → `empty`
   - anything else → `ok`
4. **Code every refusal.** `refuse("price_not_confirmed", "...")` keeps the code in a side map
   keyed by the result object (a `WeakMap` in TypeScript, a `WeakKeyDictionary` or an
   attribute in Python), so the wire response is unchanged. A refusal built without the helper
   logs as `uncoded`, which gives the review a list of tools still to fix.
5. **Mark empties.** A search or list that finds nothing returns normally and calls
   `markEmpty`. Without it "nothing matched" and "matched" look identical.
6. **Log queries from search tools only.** Lower-case, collapse whitespace, truncate to about
   120 characters, and drop the query entirely if it looks like a credential, an email
   address or a phone number.
7. **Tag app-initiated calls.** A tool registered as app-only (MCP Apps visibility
   `["app"]`) records `initiator = app`. There is no standard per-call marker for a view
   calling a model-visible tool, so a tool that must be told apart has to be app-only.
8. **Read the caller from `_meta`.** Client name and version from
   `io.modelcontextprotocol/clientInfo`, else `User-Agent`; trace id from `traceparent`.
   Record `access` from the tool's `readOnlyHint` at registration, so an unannotated tool
   counts as a write rather than passing as a read.
9. **Cross-check at the edge.** Streamable HTTP requests on the 2026-07-28 revision carry
   `Mcp-Method` and `Mcp-Name` headers, so an edge or proxy log can count calls per tool
   without parsing bodies. Compare it with the table weekly.

Argument names are stored only when identifier-shaped, at most 32. With an open schema the
caller chooses key names, so anything else is counted as `+N`, not stored.

## Sketch (TypeScript, any SDK with a `registerTool`-style call)

```ts
const codes = new WeakMap<object, string>();
const empties = new WeakSet<object>();
const failures = new WeakSet<object>();

export const refuse = (code: string, text: string) => {
  const r = { isError: true, content: [{ type: "text", text }] };
  codes.set(r, code);
  return r;
};
export const fail = (text: string) => {
  const r = { isError: true, content: [{ type: "text", text }] };
  failures.add(r);
  return r;
};
export const markEmpty = <T extends object>(r: T) => (empties.add(r), r);

export function instrument(server: { registerTool: Function }, record: (row: object) => void, version: string) {
  const original = server.registerTool.bind(server);
  server.registerTool = (name: string, config: any, handler: Function) => {
    const access = config?.annotations?.readOnlyHint === true ? "read" : "write";
    const initiator = config?._meta?.ui?.visibility?.includes?.("app") &&
      !config._meta.ui.visibility.includes("model") ? "app" : "model";
    return original(name, config, async (args: any, extra: any) => {
      const t0 = Date.now();
      const base = { name, access, initiator, server_version: version,
        arg_keys: Object.keys(args ?? {}).filter(k => /^[A-Za-z_][\w-]{0,63}$/.test(k)).sort().slice(0, 32).join(",") };
      try {
        const res = await handler(args, extra);
        const outcome = res?.isError ? (failures.has(res) ? "error" : "refused")
          : empties.has(res) ? "empty" : "ok";
        safe(() => record({ ...base, outcome,
          refusal_code: outcome === "refused" ? codes.get(res) ?? "uncoded" : null,
          result_bytes: JSON.stringify(res).length, duration_ms: Date.now() - t0 }));
        return res;
      } catch (e) {
        safe(() => record({ ...base, outcome: "error", duration_ms: Date.now() - t0 }));
        throw e;
      }
    });
  };
}
const safe = (f: () => void) => { try { f(); } catch { /* never fail the call */ } };
```

The recorder adds `product`, `account_id`, `client` and `trace_id` from the request context.
Check your SDK's handler signature: where `_meta` and headers arrive differs between SDK major
versions (see [changes-ledger.md](changes-ledger.md)).

## What the wrapper cannot see

- Arguments that fail input-schema validation never reach the handler, so there is no row.
  Only edge logs show that mis-routing.
- A result rejected by the tool's `outputSchema` after the handler is logged `ok`.
- Tools registered some other way are not wrapped.
- `arg_keys` are read after schema defaults, so a defaulted key counts as present.

## Don't

- **Don't await the recorder.** Analytics that slow the product get switched off.
- **Don't catch and convert errors in the wrapper.** It observes; it must not change behaviour.
- **Don't put the refusal code in a custom result field or `_meta` key.** Strict clients may
  reject unknown fields, and it changes the wire contract for a logging need.
- **Don't register tools before the wrapper is installed.** They are invisible.
- **Don't copy a result after a helper annotated it.** `{ ...refuse(...) }` is a new object
  with no annotation and logs as `uncoded`.

## Check

A test that connects a real client over an in-memory transport and asserts: one row per
outcome, the refusal code, the app initiator, that an argument **value** never appears in a
recorded row, and that a recorder that throws leaves the call successful.
