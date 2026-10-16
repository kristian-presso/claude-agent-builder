# The lethal trifecta

Simon Willison's framing (June 2025, simonwillison.net), still the reference model in
practitioner writing in 2026, for when an AI agent becomes exploitable by design rather than
by bug. Three capabilities, each harmless alone, are dangerous together:

1. **Access to private data**: files, email, databases or credentials that matter.
2. **Exposure to untrusted content**: input the agent did not fully choose, such as web
   pages, documents, tool responses, issue comments or email.
3. **An exfiltration vector**: any way to communicate outward, such as HTTP requests,
   messages, an image that triggers a fetch, or an API call.

With all three present, one piece of poisoned content can make the agent leak private data
or take an unauthorised action, with no conventional vulnerability anywhere in the stack.

## Why it is structural

Instructions and untrusted data arrive as natural-language tokens in the same context
window. There is no syntactic boundary a model is guaranteed to respect between "what I was
told to do" and "what I just read". Better training and prompt hardening reduce the risk
but cannot close it, so the defences have to live in the application, permission and
network layers around the model.

## Why the model is useful

It replaces an unanswerable question with an answerable one. Removing any single leg closes
the exploit even if the other two remain:

- No private data: nothing worth stealing, however badly the agent is fooled.
- No untrusted content: nothing can inject instructions.
- No outward channel: nothing the agent decides can leave the boundary.

Every other defence in this skill (sandboxing, proxy-injected credentials, isolated contexts
for fetched content) is best understood as removing or narrowing one leg for a particular
deployment, not as a general "make it safer" setting.

## Easy-to-miss legs

- **Exfiltration through rendering.** A markdown image whose URL carries data leaks it the
  moment a client renders it. So does a link preview.
- **Untrusted content through tools.** A third-party MCP server's descriptions and outputs
  are content the agent did not choose, even if it never browses the web. See
  [mcp-security-risks.md](mcp-security-risks.md).
- **Private data through memory.** Long-term memory or notes written from earlier untrusted
  input carry that input into later sessions.
