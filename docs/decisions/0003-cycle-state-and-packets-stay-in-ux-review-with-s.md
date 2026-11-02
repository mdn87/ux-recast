# D-03: Cycle state and packets stay in `.ux-review/` with `schema_version: 1` for every project; 

- Status: accepted (plan decision log, roundtable review 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-03

## Decision

Cycle state and packets stay in `.ux-review/` with `schema_version: 1` for every project; ux-recast durable records go to `PRODUCT.md`, `DESIGN.md` and `.ux-recast/`, with cited evidence archived under `.ux-recast/evidence/`.

## Why

Preserves callers and recorded runs; one location for state; durable records must not link into a gitignored folder (roundtable I-8).

## Cost to reverse

Easy until Phase 3 Stage C.
