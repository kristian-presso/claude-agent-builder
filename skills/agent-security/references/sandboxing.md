# Sandboxing and isolation

## Contents

- Why isolation matters even with permission prompts
- Technology comparison
- Both layers: filesystem and network
- A hardened container baseline
- What isolation does not solve

Last researched August 2026. Flag names and settings drift; re-check against your runtime's
current documentation before applying them.

## Why isolation matters even with permission prompts

A permission system decides **whether** an action runs, and is only as good as the model's
honesty about what a command will do. A sandbox constrains what a running process can
**reach**, enforced by the operating system whatever the command claimed. They are
complementary: a successfully injected agent that talked its way past a permission check is
still contained.

## Technology comparison

| Technology | Isolation | Overhead | Setup |
| --- | --- | --- | --- |
| OS sandbox runtime (bubblewrap, macOS Seatbelt) | Good, secure defaults | Very low | Low |
| Containers (default config) | Depends on setup | Low | Medium |
| gVisor (user-space syscall interception) | Excellent if configured well | Medium to high; heavy file I/O can slow 10 to 200 times | Medium |
| microVMs (Firecracker, QEMU) | Excellent if configured well | Higher | Medium to high |

- Sandbox runtimes and containers **share the host kernel**. Fine for many developer and CI
  uses, but not kernel-level isolation, and should not be described as such.
- microVMs give each agent its own kernel and boot fast, but still depend on hypervisor
  quality. "It is a VM" is not automatically stronger than well-configured gVisor.
- In every credible design the agent runs **inside** the boundary.

## Both layers: filesystem and network

Every credible implementation treats these as required together:

> Without network isolation, a compromised agent can exfiltrate SSH keys even if writes are
> locked down. Without filesystem isolation, it can plant something in a cron job, a shell
> start-up file or a binary on `PATH` to gain network access later.

Filesystem: mount code read-only where the agent only analyses it; exclude credential files
even from read-only mounts (see [credentials.md](credentials.md)); use `tmpfs` for scratch;
use an overlay when changes need review before they persist.

Network: default-deny with an explicit **allowlist** (an allowlist bounds risk to what you
named; a denylist only to what you thought of), and route traffic through a proxy outside
the boundary, which is also where credentials get injected.

## A hardened container baseline

Illustrative, to show what each control is for. Adapt to your runtime.

```bash
docker run \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --network none \
  --memory 2g \
  --pids-limit 100 \
  --user 1000:1000 \
  -v /path/to/code:/workspace:ro \
  -v /var/run/proxy.sock:/var/run/proxy.sock:ro \
  your-agent-image
```

- `--cap-drop ALL`, `no-new-privileges` (plus a seccomp profile): fewer escalation paths.
- `--read-only` with a scoped `tmpfs`: nothing persists into the image; scratch is wiped.
- **`--network none` plus a mounted socket to a host-side proxy**: the container has no
  network interface, so the only way out is the proxy you control, which decides what is
  reachable and logs every request. This is the pattern to internalise above the flags.
- `--memory`, `--pids-limit`: a runaway process cannot take down the host.
- `--user 1000:1000`: an escape does not start as root.
- Code mounted `:ro`: the agent can read but not change it.

## What isolation does not solve

- **The TLS blind spot.** A proxy allowlisting by hostname without terminating TLS cannot
  see inside traffic, and domain-fronting-style tricks may reach a different host. Strong
  guarantees need a TLS-terminating proxy, with its certificate complexity, and any tool
  that ignores proxy settings bypasses it. As of August 2026 at least one vendor described
  TLS-aware sandbox networking as still in development.
- **Escape hatches.** A "retry outside the sandbox on failure" option is a deliberate hole.
  Where you need a hard guarantee, disable it outright.
- **Broad default reads.** Sandboxes often allow reading the whole filesystem except denied
  paths, which includes credential files unless you denied them. "Sandboxed" does not mean
  "credentials protected".
- **Side doors.** Write access to `PATH` directories, shell start-up files or config
  directories lets a sandboxed process plant something a less-isolated process later runs.
- **Narrow scope.** Isolation often wraps only the shell tool. File-edit tools, browser or
  desktop control may be governed by the permission system alone.
