# OWASP Top 10 for Agentic Applications

Published by the OWASP GenAI Security Project in December 2025 as the 2026 edition. The ten
ids and names below were checked against the OWASP resource page on 21/09/2026 and against
independent write-ups on 16/10/2026. The OWASP page states no version history.

**Verify at genai.owasp.org before citing a category id in an audit or a decision.** The
framework is young and categorises a field moving faster than the document.

| ID | Risk | Note |
| --- | --- | --- |
| ASI01 | Agent Goal Hijack | The end state most other risks lead to |
| ASI02 | Tool Misuse and Exploitation | A path to goal hijack through tool calls |
| ASI03 | Agent Identity and Privilege Abuse | Over-broad or standing credentials |
| ASI04 | Agentic Supply Chain Compromise | Compromised tool servers, dependencies, models |
| ASI05 | Unexpected Code Execution | |
| ASI06 | Memory and Context Poisoning | The persistent-memory form of injection |
| ASI07 | Insecure Inter-Agent Communication | Once agents talk to agents |
| ASI08 | Cascading Agent Failures | One agent's error propagating through a system |
| ASI09 | Human-Agent Trust Exploitation | Social engineering through the agent, either way |
| ASI10 | Rogue Agents | Acting outside scope with no single injected trigger |

## Where prompt injection sits

Indirect prompt injection is not a category of its own here. It is an attack path into ASI01
and ASI02: in an agentic system the injected text is not the harm, what the agent then does
with its tools is.

## Mapping checklist findings

| Finding in the skill's checklist | Likely category |
| --- | --- |
| All three trifecta legs present | ASI01, ASI02 |
| Plaintext or long-lived credential in the agent | ASI03 |
| Unvetted or unpinned third-party MCP server | ASI04 |
| Shell access without sandbox | ASI05 |
| Memory written from untrusted input | ASI06 |
| Sub-agent output trusted without checks | ASI07, ASI08 |
| Agent asks a person to approve something it misdescribes | ASI09 |

The older OWASP Top 10 for LLM Applications (where prompt injection is LLM01) covers the
single-prompt level and remains useful alongside this one.
