# D-15: Rubric and reviewer-prompt bytes are frozen through Phase 3; vocabulary changes and the ve

- Status: accepted (plan decision log, roundtable review 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-15

## Decision

Rubric and reviewer-prompt bytes are frozen through Phase 3; vocabulary changes and the version bump land in Phase 4 after parity.

## Why

`rubric_sha256` and `task_sha256` must match between legacy and shim for the rollback drill to mean anything (roundtable I-6).

## Cost to reverse

Easy.
