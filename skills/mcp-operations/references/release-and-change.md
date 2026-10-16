# Release and change

A live tool's name, input schema and description are a contract with every client, every saved
workflow and every prompt that learned to call it. Add freely; change descriptions behind an
eval; never rename or remove in one step. Every release bumps `server_version`, so the usage
table can show what the change did.

## Every release

1. Bump the version the recorder writes to `server_version`.
2. Add a changelog entry: what changed per tool, the routing eval score before and after,
   and which signal or proposal the change answers, so next week's review can measure it.
3. Keep `tools/list` order deterministic. The 2026-07-28 revision asks servers to (it helps
   client caching), and a stable order keeps diffs of the listed surface readable.

## Changing a description

Run the routing eval before and after (method: `mcp-server-builder` in agent-builder,
[`references/routing-evals.md`](../../mcp-server-builder/references/routing-evals.md)). Ship only if negatives did not get worse and the holdout did
not drop. Once real usage exists, add indirect prompts from real gap asks and zero-hit queries,
paraphrased so no personal data enters the set: they are what people actually say.

## Renaming a tool

1. Add the new name as a separate tool calling the same function.
2. Mark the old one deprecated in its description ("Deprecated: use `new_name`") and keep it
   working.
3. Watch the usage table until the old name has had no calls for two full weeks.
4. Remove it in its own release. On a directory-listed server, tool names shown on the listing
   are edited from the developer dashboard and go through review.

## Removing a tool

Only after two consecutive weekly reviews agree it is unused (signal 8 in
[signals.md](signals.md)), and after checking gap reports for asks that name it. Removal ships
alone so its effect is visible.

## Changing an input schema

Adding an optional parameter is safe. Making a parameter required, renaming it, or narrowing
its type breaks callers that learned the old shape: treat it as a rename (new tool, deprecate,
watch, remove), or accept both shapes for a deprecation window.

## Don't

- **Don't reuse a removed tool's name for different behaviour.** Clients and prompts that
  learned the old meaning will call it confidently.
- **Don't batch a description rewrite with a behaviour change.** Neither can then be measured.
- **Don't ship a destructive tool without `destructiveHint: true`.** Hosts use it to decide
  when to ask the person first.

## Check

The changelog has one entry per `server_version` seen in the usage table, and every entry that
changed a description carries two eval scores.
