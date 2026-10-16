# Credentials: keep them out, let the agent use them anyway

## Contents

- Two different problems
- Prevention: secret hygiene
- Use without exposure: proxy injection
- The target shape: ephemeral, scoped credentials

Last researched August 2026. Tool recommendations move; re-check every six to twelve months.

## Two different problems

Keeping secrets out of an agent's context and out of version control is a different problem
from letting an agent **use** a secret it genuinely needs. Treating them as one produces a
solution to neither: either the agent is denied credentials it needs to do useful work, or a
credential is handed over in the clear "because it needs to authenticate somehow".

## Prevention: secret hygiene

**Scanning.** The established pairing in 2026:

- **Gitleaks** at pre-commit and on every pull request: regex-based, no network, fast
  enough that nobody disables it.
- **TruffleHog** on a scheduled sweep of full history: slower because it verifies whether a
  found credential is live against its provider, which cuts false positives.
- **detect-secrets** where a legacy codebase needs a maintained baseline.

Agentic coding ships more code per hour with less human review per line, so scanning that
was good enough before may not be now.

**Deny before the agent reads, not just before commit.** Explicitly deny read access to
credential paths and unset credential environment variables before the agent starts. Read
access alone is enough to leak them:

| Path | Holds |
| --- | --- |
| `.env`, `.env.local` | API keys, database passwords |
| `~/.git-credentials` | Git tokens in plaintext |
| `~/.aws/credentials` | AWS keys |
| Cloud CLI config (`~/.config/gcloud`, `~/.azure/`) | Cloud tokens |
| `~/.docker/config.json` | Registry auth |
| `~/.kube/config` | Cluster credentials |
| `.npmrc`, `.pypirc` | Package registry tokens |
| `*-service-account.json`, `*.pem`, `*.key` | Service account and private keys |

**Build-time filtering.** Use `.dockerignore`-style exclusion when building any image or
mount an agent uses, so credential files are never copied in. A misconfigured mount later
cannot leak a file that was never there.

## Use without exposure: proxy injection

Run a proxy **outside** the agent's security boundary. The agent sends the request without
credentials; the proxy adds the real one and forwards it.

Why this is the load-bearing pattern:

- The plaintext never enters the agent's process, logs or context, so even a fully
  successful injection has nothing to steal.
- The proxy enforces which endpoints a credential may ever be sent to.
- Every credentialed request is logged in one place.
- Credentials live in one place, which makes rotation simple.

Two implementations:

- **Plaintext proxy** for one API (for example, an LLM API reached via a base-URL override):
  simple, but covers only that API.
- **TLS-terminating proxy** for arbitrary HTTPS services: handles anything, but the agent's
  environment must trust the proxy's CA, and some tools and runtimes ignore standard proxy
  environment variables and silently bypass it.

**Credential masking** goes further: the agent holds a structurally valid placeholder, so
"is a token present" checks still pass, and the proxy swaps in the real value only on the
hosts that credential may reach.

## The target shape: ephemeral, scoped credentials

For any credential an agent does hold:

1. **Workload identity**: the agent proves what it is, not which person it acts for.
2. **Scoped to the task**: read-only on one table, not a standing database role.
3. **Short-lived and just-in-time**: minutes to hours, expiring on its own.

An agent makes non-deterministic decisions about what to touch, so a credential that outlives
its task is a standing liability. Combined with proxy injection, the blast radius of a fully
compromised environment is capped twice: by scope, and by a clock already running down.
Ephemeral scope substitutes for detection speed you may not have.
