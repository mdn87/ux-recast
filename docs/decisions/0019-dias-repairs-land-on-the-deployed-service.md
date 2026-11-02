# D-19: Dias pilot repairs land on the deployed service (B-09)

- Status: accepted (user decision 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, user decision B-09 and decision log row D-19; plan section 5c

## Decision

The Phase 5c repairs (S5.8 sessions page and `app.js`, S5.9 question page, S5.10 approval page) land directly on Lugos master in `lugos-node/services/lugos-host-ops`, which is the deployed phone client. There is no pilot branch and no fork of the phone pages. The plan's recommended option, a host-ops branch gated by the pilot Decision, was put to the user and not chosen.

## What this changes

- The S5.11 Decision becomes accept-or-revert rather than merge-or-discard: rejecting the repair means `git revert` of the repair commits on master and a redeploy, not dropping a branch.
- The production phone client changes as each repair slice lands, so the operator sees intermediate states between S5.8 and S5.10. Each slice still stays inside its flow and ships with passing host-ops pytest and browser checks.
- The after-run (S5.11) still runs the frozen scripts against the fixture at the pinned post-repair revision, exactly as the before-run did at `efbc9a7d`; the device observation after half runs against production as the installed PWA, which is now the same code.
- The before evidence stays valid: nothing in `tests/pilot/before/` or `thresholds.json` changes (`freeze.py --check` must still print "frozen scripts unchanged").

## Why

The phone client is the operator's own tool behind Cloudflare Access with one user, the repairs are bounded by the accepted `DESIGN.md` (D-18) and the frozen before-run, and master already deploys continuously to the host. A gated branch would add a merge step and a second deploy without reducing what the single operator is exposed to. The user made the call (plan P-10: where repairs land is the user's decision).

## Cost to reverse

Medium. Before S5.8 lands: a line in this note and the plan. After: a revert of the repair commits on Lugos master plus redeploy, and the device observation after half has to be repeated if the repair is later reinstated.
