# D-06: Reclassified as user decision B-09

- Status: accepted (plan decision log, roundtable review 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-06

## Decision

Reclassified as user decision B-09. The plan's recommendation: pilot runs on `mobile_browser_fixture.py`; repairs land on a host-ops branch gated by the Decision, not directly on the deployed service.

## Why

The phone client lives in host-ops and production sits behind Cloudflare Access, but committing an experimental toolset's repairs to a live operator service is the user's call (roundtable P-10).

## Cost to reverse

n/a
