# D-21: Redesign-first method adopted, with walkthrough mode, prompt hand-off and comparison record

- Status: accepted (user instruction 2026-11-02 to port the firm copy's method back into ux-recast)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-21; [plans/redesign-first.md](../plans/redesign-first.md); lifted from bwa-ux-recast (its commits `c248549`, `74b8d39`, `e653fba`); proven in `mdn87/email-automation` PR #35

## Decision

"Improve the UX/UI of this project" means the five-stage redesign-first method on one selected task: brief, current and proposed flows, a complete visual design, a fresh-context walkthrough with functional verification, and a before-and-after comparison record. The bounded defect-and-repair cycle stays, as a tool inside stage 4 and as the "Fix" shape of the ask, not as the whole job.

ux-recast gains four things for it:

- `rubric/walkthrough.md`, a fresh-evaluator cognitive-walkthrough assignment, selected with `review --mode walkthrough` or `packet prepare --mode walkthrough`.
- `packet prompt [--out]`, which hands a separate agent context the claimed packet's exact task text and nothing else; its findings come back through `findings`.
- The `comparison` contract (`ux-recast/comparison@1`, `schemas/comparison.schema.json`): same content and conditions, improvements labelled `observed` or `judgement`, every finding's disposition, verification, assumptions, and a person's decision. A score field is refused.
- The playbook (`docs/playbook-improve-ux.md`), the `skills/improve-ux` skill, and the brief, flows and comparison templates.

## Constraints kept

- **D-15.** `rubric.md` and `autowork-reviewer.md` are byte-for-byte unchanged, and `rubric_version` stays 1: the version bump belongs to Phase 4 (S4.4). `walkthrough.md` is additive; `VERSION` records its digest.
- **Lugos parity (D-05, D-14, S3.4).** A review-mode packet is byte-identical to the legacy one; only a walkthrough-mode packet records `review_mode` and `rubric_version`, in the outer packet. The differential corpus shows no differences against the Lugos legacy scripts, and the Lugos ux-review tests, shim tests included, pass against the package (66 on Windows, 2026-11-02; the Playwright demo test was not run).
- **D-09.** The comparison carries evidence and a decision, never a score.

## Why

The bounded cycle finds defects and polishes screens but never requires a better workflow, so an awkward organization survives every cycle. The firm copy built the method on the cycle's own foundations (task contract, plan-stage checkpoint, read-only reviewer) and the first real run redesigned the email-automation intake companion's request-to-letter task end to end: a plan walkthrough whose five findings revised the flow before anything was built, two build walkthroughs, a 24-check verification and a comparison record left `pending` for the owner. The lessons from that run are in the playbook.

## What it leaves open

- Slice S2.6 planned `schemas/comparison.schema.json` for Phase 2's comparison record (`product` and `method` kinds, effort accounting, six decision values including `keep_baseline`). S2.6 now extends this record, as a new schema version, rather than adding a second one.
- Whether a walkthrough packet should also be submittable through the Lugos Autowork lane as a matter of course. It can be today (the inner request is unchanged); the method only requires a fresh context.

## Cost to reverse

Easy. The new mode, verb and contract are additive; removing them leaves review-mode packets and the frozen rubric exactly as they were.
