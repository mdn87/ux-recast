# D-14: Shims keep the Python module surface, check `UX_REVIEW_IMPL` before importing `ux_recast`,

- Status: accepted (plan decision log, roundtable review 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-14

## Decision

Shims keep the Python module surface, check `UX_REVIEW_IMPL` before importing `ux_recast`, and fail closed with a message when `ux_recast` is absent and legacy was not selected.

## Why

Importing callers exist (`coordination_trials.py`, the MyDocs forwarder); a silent fallback would hide a broken install (roundtable I-2, T-6).

## Cost to reverse

Easy.
