# D-11: Impeccable is used through its agent commands where a project already has it installed, an

- Status: accepted (plan decision log, roundtable review 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-11

## Decision

Impeccable is used through its agent commands where a project already has it installed, and through `detect` as an evidence pre-pass when the binary is on PATH. ux-recast installs nothing and never auto-installs through `npx`.

## Why

Preserves the concept's active design role (roundtable P-2) without violating the AGENTS.md overlap rule; installation per project is a user decision (B-10).

## Cost to reverse

Easy.
