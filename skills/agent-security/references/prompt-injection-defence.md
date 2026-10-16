# Prompt injection defence

Last researched August 2026. Vendor product names change; re-check before citing.

## Direct and indirect

- **Direct injection**: a user types instructions meant to override the system prompt. The
  user is at least an identifiable, semi-trusted party.
- **Indirect injection**: instructions hidden in content the agent retrieves and treats as
  data (a web page, PDF, email, issue comment or tool response). The operator never sees the
  text before the agent acts. Concealment includes white-on-white text, zero-width characters
  and Unicode tag characters that render invisibly to people but are read by the model.

## Why there is no model-layer fix

Trusted instructions and untrusted data share one context window with no guaranteed
separator. Training measurably reduces susceptibility; no model reviewed is immune. Defence is
layered around the model.

## Layered defences

- **Governed context.** Restrict what content the agent may treat as instruction-bearing. A
  smaller, curated retrieval set is a smaller attack surface.
- **Least privilege.** An agent that structurally cannot reach a capability cannot be talked
  into misusing it.
- **Isolated contexts for untrusted fetches.** Process web or tool content in a separate
  context and summarise before merging back, rather than piping raw content into the context
  that holds the tools and the private data. At least one coding agent applies this to both
  web search and page fetches.
- **Action monitoring and gating.** Log, and where feasible gate, high-impact actions
  (network egress, destructive writes, credential use) independently of why the agent took
  them.
- **Vendor stacks.** Shipping examples in 2026 include Microsoft's Spotlighting (marking
  untrusted spans), Prompt Shields (a classifier) and FIDES (provenance), and Meta's
  open-source LlamaFirewall. Treat them as layers, not answers.

## Concrete controls worth copying

A well-documented coding agent's controls are useful because each is an inspectable
mechanism rather than a principle:

- A permission check runs before any tool executes, independent of the model's stated
  intent.
- Shell commands are parsed and matched against rules; unparseable commands and high-risk
  constructs always need approval. This is a permission gate, not a sandbox: it reads the
  command text, not its effects.
- Network-fetching commands are not auto-approved by default.
- New codebases and newly configured MCP servers need explicit trust on first use.
- Unmatched commands fail closed.

Operating practice for untrusted content: review suggested commands before approving; never
pipe untrusted content straight into an agent's context; verify changes to files that
matter; run anything touching external services inside a VM or other isolation boundary.

## The standing caveat

Every vendor source reviewed says these measures "significantly reduce" risk without claiming
to remove it. Treat prompt injection as a residual risk to manage and monitor, never a box
ticked.
