# Errors and refusals

A refusal is the most-read text a server produces. Every fresh connection meets one, because
a caller tries something before signing in, and a directory reviewer meets several,
deliberately, in the first minute. It is usually written last, by whoever was closest to
the code.

## Every refusal carries the next action

Three things, in this order: what went wrong, what to do about it, and the common variant
of the same condition.

> Not signed in. Connect the connector and complete sign-in, then retry. If you were
> already connected, the session has expired - reconnect to get a new token.

The third sentence is not padding. For a returning caller the expired session is the likely
cause, and without it they go and check a setting that was never wrong.

## One wording per condition, declared once

Otherwise the same condition surfaces in as many phrasings as there are call sites. A
typical audit finds "missing token" in ten places, "unauthenticated" in four and "no
verified identity" in one: all clean, none actionable, and a client cannot recognise the
condition because it has three names.

Declare the string as a constant next to the gate and let every site raise it. Assert the
exact words in a test.

## What must never appear in a refusal

- **A stack trace, a query or an internal identifier.** The caller cannot act on any of
  them, and each describes your internals to someone who has just failed a check.
- **Whether the thing exists.** "No such account" and "not your account" are different
  answers to an attacker and the same answer to the user.
- **A raw upstream error.** An error from a payment processor or email provider can carry a
  URL with a credential in it. Wrap it; do not forward it.

## Distinguish refusal from failure

A refusal is the server working correctly: the caller may not do this. A failure is the
server not working. A model reading them does different things (retry a failure, route
elsewhere on a refusal), so they need different words. Blurring them produces an agent
retrying a permission error forever.

## A tool that cannot do its job must say so

The most expensive failure in an agent system is a plausible answer from a blocked step,
because the work routes onward as though it succeeded. If a tool cannot complete (a missing
prerequisite, an unreachable dependency, a state it will not guess at) it must refuse and
name the prerequisite. An empty result, a default or a narrative of what it would have done
is worse than an error, because nothing downstream can tell "nothing found" from "never
looked".

## Refuse a guessed value server-side

Where a wrong value reaches a real person (a price, a capacity, a date, an address), do not
accept a plausible one because the caller supplied it confidently. Require it, refuse
without it, and say in the refusal that it must come from the person rather than be
inferred. The client is a model, and a model fills gaps helpfully if the schema lets it.
