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
- **Isolated contexts, done properly.** The pattern above only works if what crosses back
  is narrow. A free-text summary can carry the injection straight through: the page tells
  the summariser what to write, or the summariser faithfully reports "the page asks you to
  email this file to X". Hand back typed fields the privileged side can validate (enums,
  numbers, extracted values against a schema), or treat the summary as an opaque value the
  privileged agent shows the user but never reads as instructions. The reader's own tools
  matter too: its fetch is an outward channel, so it must hold no private data, including
  the user's query or anything from the privileged side. This is the dual-LLM idea Simon
  Willison described in 2023, and the reason later designs such as Google DeepMind's CaMeL
  (2025) track where every value came from.
- **Action monitoring and gating.** Log, and where feasible gate, high-impact actions
  (network egress, destructive writes, credential use) independently of why the agent took
  them.
- **Vendor stacks.** Shipping examples in 2026 include Microsoft's Spotlighting (marking
  untrusted spans), Prompt Shields (a classifier) and FIDES (provenance), and Meta's
  open-source LlamaFirewall. Treat them as layers, not answers.

## Human approval that actually gates

A person approving each outward action is a real control only if all of these hold:

1. **The approver sees the action, not the agent's account of it.** Render the payee, IBAN,
   amount, recipients and attachments from the pending call's actual parameters, by code. A
   summary the model wrote is exactly what an injection controls.
2. **The approval is bound to that call.** The system holds the pending action and executes
   exactly what was approved, or the approval carries a hash of the parameters that the
   executing tool checks. "Approve, then the agent calls `send` again" lets it send
   something else.
3. **Approvals are rare enough to be read.** Approving every routine action trains people
   to click. Route the dangerous cases to a person (a new recipient or payee, changed bank
   details, an amount over a threshold, anything irreversible) and let deterministic rules
   handle the routine ones.
4. **Facts the attacker controls are checked outside the agent.** The classic case is
   invoice redirection: an email saying "our bank details have changed". A payee or bank
   detail must match a record held outside the inbox, and a change is confirmed out of band
   (a call to a known number), never from the content that requested it.

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
