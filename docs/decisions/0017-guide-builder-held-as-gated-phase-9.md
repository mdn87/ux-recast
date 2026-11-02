# D-17: Guide Builder held as a gated Phase 9

- Status: accepted (user decision 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-17; concept `docs/concepts/improvement-loop-and-guide-builder.md`

## Decision

The 2026-11-02 additive concept is accepted as a record. Its Improvement Loop content is folded into Phases 2 and 8 now (lesson states, comparison record with effort accounting, method comparisons on held-out cases). The Guide Builder becomes Phase 9, gated on Phase 3 shims landing, the Dias pre-pilot checkpoint, and user decisions B-13 (first process and reader), B-14 (capture mode and output toolchain) and B-15 (authority for an agent demonstration). No Guide Builder code, dependency or slice before then.

## Why

Phase 2's record shapes are the next batch and are exactly where the loop content changes shapes; retrofitting statuses and a comparison record later is the costly part. The Guide Builder is a new capture-and-document workstream that cannot be scoped without a first process, a capture mode and an authority model, and starting it now would pull effort off the Lugos critical path.

## Cost to reverse

None. Nothing is built. Lifting the gate is a plan edit.
