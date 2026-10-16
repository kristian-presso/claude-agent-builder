# agent-builder

Five skills for people building things with Claude: MCP servers and the apps that sit on
them, agents that are safe to give real access to, shipping multi-step work with coding
agents, and turning a process you do by hand into a skill.

They share one conviction. **The expensive failure is not code that breaks; it is work that
reports success and is wrong.** A server that starts cleanly and is unreachable through the
proxy. A view that passes every check and shows a figure nobody can source. An agent that
completed every task and missed the point. A skill with a perfect body and a description
that never triggers. Each skill here is built around the check that catches its version of
that.

## Skills

| Skill | Use it when |
| --- | --- |
| **mcp-server-builder** | You are building an MCP server, adding tools to one, auditing one before release, or preparing it for the Claude or ChatGPT directory. Includes a tested Python starter. |
| **mcp-app-builder** | You want an MCP tool's result to render as an interactive view in the conversation, or need to prove an existing view actually works. Decides first whether it deserves a UI at all. Includes a tested serverless starter. |
| **agent-security** | You are designing or reviewing an agent, adding a tool or MCP server to it, giving it credentials, or letting it read the web or email. Maps the lethal trifecta and finds the one change that removes the most risk. |
| **ship-with-agents** | Work spans several phases, files or repositories, or is being split across subagents, and you need to know it is actually done. Criteria that can fail, verification by an agent that never saw the plan. |
| **skill-builder** | You keep explaining the same task to Claude from scratch, or a skill you wrote is not triggering. Interviews you, writes the skill, tests it, and validates it with a bundled script. |

## Install

In Claude Code:

```bash
/plugin marketplace add kristian-presso/claude-skills
/plugin install agent-builder@claude-skills
```

On claude.ai or the Claude desktop app, zip any skill folder (for example
`skills/agent-security/`) so the folder is at the root of the zip, and upload it under
Customize, Skills.

## What "tested" means here

Both starters were written out from their reference files exactly as published and run on
16 October 2026:

- **mcp-server-builder**: the Python server installs and its 8 tests (in-process and over
  stdio) pass on `mcp` 2.3.0, and on 1.29.1 (the newest 1.x release, 24/08/2026,
  per PyPI) with the one-line import change the reference describes. The Host-allowlist and Content-Type behaviour described in its deployment notes
  was checked by sending real HTTP requests.
- **mcp-app-builder**: the Worker project installs, builds its view, typechecks and bundles,
  and under a local dev server answers `tools/list`, `tools/call` and `resources/read` as the
  verification tiers require.
- **skill-builder**: the validator script needs only Python 3 and was run against every
  skill in this plugin and against deliberately broken ones.

The MCP ecosystem moves fast. Every fact that can change carries the date it was checked and
where to re-check it, and the SDK notes say exactly which version each claim was read from.

## Configuration

Each skill ends with a short **Configuration** section naming the one or two things that
vary: the SDK and runtime you build on, where your specs and test prompts live, which agent
runtime you secure, where your skills are saved. None needs a particular directory layout or
service to work.

## Licence

MIT.
