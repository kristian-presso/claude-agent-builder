# A check proves only what it exercised

Five habits. Each looks like paranoia until it costs a day.

## A gate proves its own scope, not the tree

When one change dirties several artefacts made by several programs, one generator's gate
going green says nothing about the others. Ask what else the change touched before believing
a pass. The failure looks like success: the gate you ran was right about what it examined,
and nothing reports the artefact nobody checked.

## A check through the wrong channel proves nothing about the real consumer

An endpoint can answer `curl` perfectly and be unreachable from the browser meant to call it:
a cross-origin preflight, a header the CLI does not send, a redirect the real client will not
follow. Test through the path the real consumer uses, or record that you did not. This one
survives being written down precisely because the wrong-channel test works, which reads as
evidence.

## Reading the artefact is not watching it behave

Grep a script for its error message and you learn the message exists, not that it ever
prints. Find the state the requirement names, and cause it:

- **A failure**: make the dependency fail, then read what the user is shown.
- **A rerun**: run it twice and compare.
- **An empty result**: feed it nothing and look at the output.
- **A refusal**: ask for the forbidden thing and check the answer, not only its shape.
- **An environment**: start it under that environment, or a faithful stand-in.

Then look where the consumer looks: the exit code, the response body, the painted screen,
the table afterwards.

Checks drift towards states that already exist (the warm machine, the happy path) because
those cost nothing to reach. The states a requirement most needs checked are the ones someone
has to build. If one truly cannot be built, record it as unmeasured.

## A check that has never gone red has not been tested

Break the thing on purpose, in the way the criterion names, and require it to fail. Two
failures this catches that reading never does:

- **An exit-code collision**: a harness reads a tool's real error code as "could not tell"
  and turns a failure into a shrug. `tsc`, `grep` and `diff` all exit 2 on real errors.
- **A regenerated target**: a later step rebuilds what the check inspects, so the defect is
  erased first.

If the deliberate break could not be applied, that is evidence of nothing.

## A mechanism working is not a number being right

Something can pass every structural check and display a wrong figure. This matters more the
more authoritative the presentation: "roughly 400, though that includes bot traffic" invites
doubt; the same number in a dashboard tile reads as fact and gets quoted to a customer.

1. Name each displayed figure's provenance: measured, derived or estimated.
2. Assert against a known fixture, not whatever the system returned.
3. Check that anything inflated, sampled or partial is labelled on the surface.
4. Escalate any figure nobody can source to a person.

Report this as unmeasured unless a data assertion or a person actually ran it.
