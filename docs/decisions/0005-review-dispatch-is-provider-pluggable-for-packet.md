# D-05: Review dispatch is provider-pluggable for packet fulfilment only (`lugos_autowork`, `local

- Status: accepted (plan decision log, roundtable review 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-05

## Decision

Review dispatch is provider-pluggable for packet fulfilment only (`lugos_autowork`, `local_agent`); the Lugos provider is a port, byte-compatible on the inner request.

## Why

Standalone use (concept C-28) without breaking Lugos; linters are not providers (roundtable I-7).

## Cost to reverse

Moderate.
