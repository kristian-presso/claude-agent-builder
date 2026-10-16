# Directory listing

## Contents

- Sources and dates
- Build once, list twice
- What both reviews read
- Being chosen
- The anonymous first call

A remote server people can reach only by pasting its URL is one most people never find. The
assistant directories are where a user finds a tool from inside the chat and installs it in
one click. Design for the listing from the first commit: retrofitting means renaming tools,
re-annotating each one and rewriting the privacy policy after users depend on the old
shapes.

**Review rules on both sides change often. Re-fetch the sources below before any submission.**
Every claim here carries its source key and was checked on the date shown.

## Sources

| Key | Page | Checked |
| --- | --- | --- |
| C1 | claude.com/docs/connectors/building/submission | 16/10/2026 |
| C2 | claude.com/docs/plugins/submit | 11/10/2026 |
| O1 | developers.openai.com/plugins/deploy/app-review | 16/10/2026 |
| O2 | developers.openai.com/plugins/guides/submit-claude-plugin | 11/10/2026 |
| O3 | developers.openai.com/plugins/guides/optimize-metadata | 11/10/2026 |

## Build once, list twice

The same remote server can be listed on both sides. Only the paperwork differs.

| | Claude | ChatGPT and Codex |
| --- | --- | --- |
| What is listed | The server as an MCP connector, optionally with a plugin of skills that points at it [C1, C2] | One plugin: skills alone, or skills with a remote MCP server [O2] |
| Who can submit | Anyone on a paid Claude plan [C1] | An identity-verified individual or business, with the `api.apps.write` permission; EU data residency projects cannot yet submit MCP plugins [O1] |
| Auth | OAuth (dynamic client registration, client ID metadata documents, or provider-held credentials), user-supplied credentials, or none [C1] | OAuth for private data or actions, with a UserInfo endpoint returning a verified email [O2] |
| After submission | Automatic scan, then listed as Community by default; some get a human review [C1] | Automated or manual review, approval by email, then a separate publish step [O1] |
| Local servers | Not accepted as connectors; ship them inside a plugin [C1] | Not accepted [O2] |

## What both reviews read

1. **Every tool's annotations are true.** A `title` and the applicable hints [C1]. OpenAI
   spells out the semantics and rejects mismatches [O1]: `readOnlyHint` only when nothing
   changes, including logs and queued jobs; `destructiveHint` when any mode or default can
   do something irreversible; `openWorldHint` only for the public internet or open-ended
   external entities. See [tool-design.md](tool-design.md) for the three classes.
2. **Destructive tools name their safeguards**, such as a confirmation step or a dry run
   [O1].
3. **Responses carry only what the request needs.** OpenAI asks for internal identifiers
   (session, trace or request ids, internal account ids), telemetry and auth secrets to be
   removed, and rejects returning user data the privacy policy does not disclose [O1].
4. **A reviewer can get in.** Claude asks for credentials to a fully populated account [C1].
   OpenAI rejects credentials that need MFA, SMS or any other verification step [O1].
5. **The listing is complete.** Claude: name up to 100 characters, one-liner up to 200,
   description up to 2,000, one to five categories, documentation and privacy URLs, a
   support contact and an icon [C1].
6. **UI views are declared.** Claude wants 3 to 5 PNG screenshots at least 1,000px wide,
   cropped to the app's response, each with its prompt supplied separately, and no video or
   GIF [C1]. OpenAI wants a content security policy listing exactly the domains the view
   fetches from [O1].

## Being chosen

The model picks a tool from its metadata alone [O3]. Name it for the user's job; start the
description with "Use this when..." and say what it is not for; give every parameter a
description and an example, and make constrained values enums [O3].

Test with a golden prompt set of direct, indirect and negative prompts, scored for precision
and recall, negatives first. See [routing-evals.md](routing-evals.md).

## The anonymous first call

A client starts OAuth from an HTTP `401` with a `WWW-Authenticate` header pointing at the
protected-resource metadata. A server with some anonymous tools must still send that
challenge where sign-in is needed, or the client never offers it. And a refusal must name a
step the caller can actually take. Test both against the live server, not the code. See
[auth-at-the-boundary.md](auth-at-the-boundary.md).
