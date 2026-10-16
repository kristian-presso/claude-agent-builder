# Acceptance criteria that can fail

Discuss ends in criteria, not intentions. Goal-backward verification is only as good as the
goal it runs against, and a goal written as prose gives a verifier nothing to run.

## The test

**Could a wrong build pass it?** If yes, it is not a criterion. "The export works" is passed
by a build that compiles and does the wrong thing. "Exporting a report with a comma in a
field and re-importing it yields an identical row" is not.

## Write them before the build

Criteria written after the fact describe the artefact rather than the goal, and pass by
construction. Deciding the goal and deciding how you would know are the same act; do them
together.

## Three ways a criterion fails to be one

- **It cannot fail.** The most common: it asserts something the build does trivially, or
  restates the task rather than its outcome.
- **It cannot run.** Rarer and more expensive: a malformed command, mangled quoting or an
  unmet precondition exits non-zero and is read as "the build is broken". If a criterion is
  executable, check it runs before trusting a red result.
- **Its target is regenerated.** A criterion that inspects an artefact a later step rebuilds
  passes on the rebuilt copy whatever the earlier step did.

## Five shapes that passed review and still shipped broken

Each shares one shape: the assertion claimed more than its check could observe.

1. **A grep proving a string exists proves nothing about "every".** "Every handler returns a
   text block" checked with `grep -q` passed with three occurrences after one was broken.
   When a criterion says every, count them or call them.
2. **Two calls in one process cannot tell a durable store from a variable.** State in a
   module-scoped map passed every count check, because both calls landed in the same process.
   After a restart the writes were gone. Wherever the work records something a person did (a
   payment, an admission, a vote), owe a criterion that writes, **restarts**, and reads back.
3. **Where one fact appears twice, assert the two agree.** One place said "12:39" (UTC),
   another "13:39" (local). Every criterion checked the value was present; none that it meant
   anything. Pin the copies to each other.
4. **A criterion that stops a process must stop only its own.** Killing by name or port takes
   a colleague's process with it, and the damage looks like their bug. Keep the PID you
   started, or bind a port the run chose.
5. **A gate the repo has and nothing calls is not a gate.** A project shipped a script proving
   a generated file was fresh, and no criterion ran it. Read the project's own task
   definitions while writing the spec and account for every check: each one is owed a
   criterion or a deletion.

## Unmeasured is not a pass

Every criterion reports **pass**, **fail** or **unmeasured**. An unattended process that
treats "could not tell" as "fine" ships broken work by default, silently.

If you use a harness, give it three exit outcomes: all ran and passed; something failed;
nothing failed but something was unmeasured. The third blocks a ship exactly as the second.
A criterion whose precondition is unmet reports unmeasured, never failed: a server that is not
running is not broken code.
