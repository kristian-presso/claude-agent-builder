# SDK versions and known source-level gotchas

Facts in this file describe someone else's software and will move. Each carries the date it
was checked and the command to re-check it. Re-check before relying on one: a workaround for
a defect that has since been fixed sends you round a problem that is not there.

## The Python SDK (`mcp` on PyPI)

Checked 16/10/2026 on PyPI (pypi.org/project/mcp/#history): `latest` is **2.3.0** (released
02/10/2026). The 1.x line is still maintained alongside 2.x: its newest release is
**1.30.0** (07/09/2026), after 2.0.0 shipped on 28/07/2026. Do not assume 1.x has ended;
ask the index.

```bash
pip index versions mcp
python -c "import mcp, pathlib; print(pathlib.Path(mcp.__file__).parent)"   # where to read the source
```

What the 2.x major changed, for anyone porting a 1.x server (verified by running the same
server on both; the 1.x column was first checked on 1.27.2 and re-checked on 1.30.0 on
16/10/2026):

| | 1.30.0 | 2.3.0 |
| --- | --- | --- |
| Server class | `from mcp.server.fastmcp import FastMCP` | `from mcp.server.mcpserver import MCPServer` (the old import raises with a pointer to the migration guide) |
| Annotation attributes | `ann.readOnlyHint` | `ann.read_only_hint` (wire names unchanged) |
| Transport security | passed to the constructor | passed to `run()` / `streamable_http_app()` |
| Types | in the package | separate `mcp-types` package, pinned exactly |
| HTTP client | `httpx` | `httpx2`, a different distribution |
| Tracing | none | `opentelemetry-api` is a hard dependency |

Pin the version deliberately in `pyproject.toml` and record why. If something else in the
project depends on `mcp-types` or `httpx`, check the resolver before taking the bump.

## Gotchas that hold on both 1.30.0 and 2.3.0

Each was re-checked by reading the installed source on 16/10/2026 (first found on 1.27.2).

1. **Tool-name validation cannot fail.** The tool factory calls `validate_and_warn_tool_name`
   and discards the result, so an invalid name registers with only a log line. Re-check:
   `grep -n validate_and_warn_tool_name <sdk>/server/*/tools/base.py`. Assert names in a
   test.
2. **DNS-rebinding protection: the middleware default is off, the field default says on.**
   Re-check: compare the field default with the constructor fallback in
   `<sdk>/server/transport_security.py`.
3. **Enabled with an empty `allowed_hosts`, it 421s every request.** Same file,
   `_validate_host`.
4. **The Content-Type check runs even with protection disabled.** Same file: the
   content-type branch in `validate_request` sits above the early return.
5. **Hiding a tool by overriding `list_tools` does not stop a direct call.** See
   [listing-and-visibility.md](listing-and-visibility.md).

Detail and symptoms for 2 to 4 are in [deployment.md](deployment.md).

## The specification

The core protocol revision current at the time of writing is `2026-07-28` (stateless core,
no handshake, `Mcp-Method` and `Mcp-Name` headers, cacheable list results; Roots, Sampling,
Logging and the legacy HTTP+SSE transport deprecated with at least twelve months' notice).
Verify at modelcontextprotocol.io/specification.
