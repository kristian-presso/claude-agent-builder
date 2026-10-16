# Deploying an HTTP server

Everything here concerns the streamable HTTP surface. A stdio server has none of these
problems and none of these controls.

## The Host allowlist that 421s everything

The Python SDK ships DNS-rebinding protection in `mcp/server/transport_security.py`. These
facts were re-checked against both `mcp` 1.30.0 and 2.3.0 on 16/10/2026, by reading the
source and by sending real requests:

1. **The middleware's own default is off.** Constructed with no settings it falls back to
   `enable_dns_rebinding_protection=False` "for backwards compatibility", even though the
   settings model declares the field `default=True`. Reading the model alone tells you the
   opposite of what you get.
2. **The app builder switches it on for local binds.** When the HTTP app is built with
   `host` set to `127.0.0.1`, `localhost` or `::1` (the default) and no explicit settings,
   the SDK enables protection with only localhost names allowed. Deploy that behind a proxy
   and every request carrying the public `Host` gets `421 Invalid Host header`, while a
   direct request to the container still works.
3. **Enabling protection with an empty `allowed_hosts` rejects every request** with 421.
4. **Matching is exact**, apart from a trailing `:*` port wildcard. `example.test` does not
   match `example.test:443`; list the form the proxy actually sends.
5. **Origin**: a missing `Origin` is allowed (treated as same-origin); a present but
   unlisted one gets `403`.
6. **Content-Type is checked even with protection off.** Any POST whose `Content-Type` does
   not start with `application/json` gets `400 Invalid Content-Type header`, before the
   protection flag is consulted. Turning protection off to isolate a problem will not make
   this one go away.

Decide the allowlist from the deployment, not the code: which `Host` does the proxy forward,
and which origins does a browser-based client present? Pass it explicitly. Re-check the file
in your installed version before trusting any line above.

## Health, readiness and the deploy gate

An authenticated MCP endpoint answers `401` to an anonymous caller, which makes it a poor
liveness probe: a process that started but cannot reach its database answers `401` just as
convincingly as a healthy one. Serve a separate unauthenticated `/health` route.

After a release, poll until the health route, any public page and the MCP endpoint all
answer what they should, including the `401` from the MCP endpoint, which proves the auth
layer is loaded rather than bypassed.

A deploy that aborts silently is worse than one that fails. If the pipeline can refuse a
release, make the refusal loud and make the running revision inspectable. Otherwise
production quietly stops tracking main while every dashboard says green.

## Generated artefacts are part of the deploy

If the server serves anything generated (a catalogue, a registry, a reference document),
regenerate all of them in the same change and add a check that fails when they disagree with
their sources. Two changes that each regenerate a different artefact merge cleanly and leave
the result inconsistent, and no test catches it because each side was consistent alone.
