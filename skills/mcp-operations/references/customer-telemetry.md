# Customer telemetry

A server you build for a customer ships the same instrumentation, writing to the customer's own
database. You see nothing by default. With written opt-in, only daily rollups leave: counts per
tool and outcome, latency percentiles and zero-hit query counts, never query text, gap wording,
feedback text or account identifiers. The customer gets their own weekly report.

This is reference, not legal advice. Have the data-use clause reviewed.

## How to

1. **Same contract, their store.** The usage, gap and feedback tables live in the customer's
   database, so their data never depends on your uptime or policy.
2. **Give them the report.** Ship the operator report ([signals.md](signals.md)) on their
   server. A support plan can include running the weekly review for them against it.
3. **Opt-in rollups only.** A scheduled job on their side sends one row per day per tool and
   outcome. No free text crosses. The job is off until they switch it on.
4. **Separate telemetry from metering.** If the plan is usage-billed, the meter is a
   contractual count that cannot be opted out of; telemetry can. Keep them in separate tables
   so switching one off cannot break the other.
5. **Retention is theirs to set.** A sensible default: 90 days for raw usage rows, 365 for gap
   and feedback text, rollups kept.
6. **Name the columns in the contract.** A short clause listing exactly what is recorded and
   what leaves turns telemetry from a worry into a feature: "you will see which tools your team
   uses and what they asked for that you do not have yet".

## Don't

- **Don't pull raw rows to yourself "to help".** Gap asks and queries can contain names, which
  makes them personal data under UK and EU data protection law.
- **Don't let a credential scrub stand in for a privacy review.** It catches key shapes, not
  names, addresses or health details.
- **Don't default the export to on.** An opt-out default for data leaving the customer's estate
  fails most procurement reviews.

## Check

On a fresh customer install the rollup job is disabled, your store has no rows from that
customer, and the customer's own report returns their signals.
