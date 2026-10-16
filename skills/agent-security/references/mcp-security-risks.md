# MCP and tool-server risks

Giving an agent third-party tool servers moves part of the trust boundary into
infrastructure the operator configured once, rather than content the agent happens to read.
Last researched August 2026; incident details re-checked 16/10/2026.

## Attack classes

- **Tool poisoning.** A malicious or compromised server puts adversarial instructions in a
  tool's description, parameter schema or response. Agents treat tool metadata as trusted
  operating context, so a poisoned description can redirect behaviour with nothing visible
  to the user.
- **Rug-pull updates.** A server that was clean when vetted ships an update adding poisoned
  descriptions or behaviour. If the host reloads metadata without re-asking for trust, a
  server that passed review yesterday is hostile today with no signal.
- **Injection through tool output.** A tool's return value carries instructions that hijack
  the agent mid-task. Mechanically the same as indirect injection from a web page, but
  through a channel the agent is primed to trust more.
- **Supply-chain impersonation.** The documented case: in September 2025 an npm package
  called `postmark-mcp`, published by someone with no connection to the email provider
  Postmark, built trust over fifteen clean versions and then added a line that BCC'd every
  sent email to the attacker (reported by Koi Security; Postmark confirmed it was not
  theirs). The package was removed. The lesson is about who may publish under a trusted
  name, which general supply-chain security already has words for. Sources:
  postmarkapp.com/blog and snyk.io/blog, September 2025.

## Secrets leaking into tool results

A server's error path is usually its least reviewed code, and its output goes straight into
the model's context. Common leaks:

- **An exception's text.** An HTTP client's error often includes the request URL, so a key
  passed in a query string comes back in `str(exc)`. Keep keys out of URLs (headers, or a
  proxy that injects them) because URLs are also written to access and proxy logs.
- **Tracebacks and debug fields** returned "so the model can retry sensibly", which can
  include request headers and with them a bearer token.
- **Raw upstream errors** forwarded as they came.

Return a fixed, actionable message to the model and log the detail server-side, redacted.
Do not try to scrub secrets out of exception text after the fact; you will miss a format.
Once a secret is in the context, an agent that also reads untrusted content can be told to
send it anywhere it can reach, and it also lands in transcripts and logs.

## Token passthrough

A server that forwards the caller's bearer token to a different API (a "confused deputy")
lets any token the client holds act on systems it was never issued for, and removes the
downstream service's ability to tell the server and the user apart. The MCP authorization
specification's security guidance forbids it: a server accepts only tokens issued for
itself, and calls downstream with its own credential, scoped to what the tool needs (or a
token obtained by an explicit exchange). Checked 16/10/2026; re-check the current
authorization section at modelcontextprotocol.io before citing it.

## No protocol-level detection

As of the sources reviewed, MCP has no built-in mechanism to detect tool poisoning and no
package-signing scheme to lean on. Mitigation sits with the host application and the
operator's choice of servers.

## Practical mitigation

- Write your own servers where practical, or use servers only from providers you actually
  trust. A directory **listing** a connector is weaker than a vendor **auditing** it; check
  which one a directory claims to do.
- Install from the provider's own documentation, not a package that merely carries their
  name.
- Pin versions, and treat an update as needing the same scrutiny as first use.
- Require explicit trust on first use of a server.
- Keep server configuration in version control so changes to what is trusted are reviewed,
  not a runtime toggle a compromised process could flip.
- Treat descriptions and outputs from third-party servers as untrusted content, which brings
  them under the trifecta analysis in [lethal-trifecta.md](lethal-trifecta.md).
