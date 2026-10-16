# Routing evals

A tool description is the routing surface, so it gets a test like code does. Keep a golden
prompt set per server, run it against a real model on every description change, and score
precision and recall of tool selection.

## Write the prompts, three kinds per tool

- **Direct**: names the job plainly ("refund order 1042").
- **Indirect**: the job in a person's words ("the customer wants their money back").
- **Negative**: close to the tool's job but belonging to another tool or to none ("what is
  our refund policy?" must not call `refund_order`).

Start with about five of each per tool. Once real usage exists, take indirect prompts from
what people actually typed, paraphrased so no personal data enters the set.

## Store them beside the server

One JSON object per line, for example `evals/golden-prompts.jsonl`:

```json
{"id": "refund-direct-1", "prompt": "refund order 1042", "expected_tool": "refund_order", "split": "train"}
{"id": "refund-neg-1", "prompt": "what is our refund policy?", "expected_tool": null, "split": "holdout"}
```

`null` means no tool from this server should be called. An optional `accept` list covers a
lookup that must legitimately come first. Keep a baseline score file next to it.

## Run and score

1. Fetch the tool list the server **actually serves** (`tools/list` against a running
   instance), not a copy from the source.
2. Send each prompt to a model with that tool list and no other context, and record the
   first tool it calls. Any agent harness that exposes tool calls will do, including the
   Claude Code CLI with the server connected.
3. Score per tool: **precision** (of calls to it, the share that were right) and **recall**
   (of prompts expecting it, the share that called it). Overall: the share of negatives that
   called nothing.
4. **Negatives first.** Any negative that calls a tool fails the run, whatever recall says.
5. Record the model and server version with the score.

## Change one thing at a time

One description, one title or one parameter description per run. Two changes at once cannot
be credited or blamed. Check the **holdout last**: a rewrite that lifts train and drops
holdout has been fitted to the prompts, not improved.

For multi-step jobs, keep a second, smaller set scored on whether the outcome was right,
plus calls taken and errors.

## Do not

- Write the eval after the description. It will test what you wrote.
- Accept a gain measured on one model as universal. Recheck on the others your users run.
- Put instructions to the model in a description to win the eval ("always call this
  first"). Directory reviews reject it and hosts treat it as untrusted.

A contract test (does `tools/list` return what we expect) is useful in CI but does not
measure routing.
