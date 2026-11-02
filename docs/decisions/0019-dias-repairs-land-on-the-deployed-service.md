# D-19: Dias pilot repairs land on the deployed service (B-09)

- Status: accepted (user decision 2026-11-02; deploy mechanism corrected the same day: staged release, not continuous deploy)
- Source: `docs/plans/initial-implementation-plan.md`, user decision B-09 and decision log row D-19; plan section 5c

## Decision

The Phase 5c repairs (S5.8 sessions page and `app.js`, S5.9 question page, S5.10 approval page) land directly on Lugos master in `lugos-node/services/lugos-host-ops`, which is the deployed phone client. There is no pilot branch and no fork of the phone pages. The plan's recommended option, a host-ops branch gated by the pilot Decision, was put to the user and not chosen.

## What this changes

- The S5.11 Decision becomes accept-or-revert rather than merge-or-discard: rejecting the repair means `git revert` of the repair commits on master and a new staged release, not dropping a branch.
- Reaching the phone is a separate, operator-run step: host-ops production deploys are staged releases pinned to a commit (`deploy/deploy-to-lugos-host.ps1 -Operation Stage -Commit <sha>`, then `Activate`; rollback through the controller's `Rollback`), documented in `lugos-host-ops/deploy/MOBILE-SNAPSHOTS.md`. Master is the source of the release, not a continuous deploy. The three repair slices therefore reach the phone together, at the commit the operator stages.
- The after-run (S5.11) still runs the frozen scripts against the fixture at the pinned post-repair revision, exactly as the before-run did at `efbc9a7d`; the device observation after half runs against production as the installed PWA, which is now the same code.
- The before evidence stays valid: nothing in `tests/pilot/before/` or `thresholds.json` changes (`freeze.py --check` must still print "frozen scripts unchanged").

## Why

The phone client is the operator's own tool behind Cloudflare Access with one user, the repairs are bounded by the accepted `DESIGN.md` (D-18) and the frozen before-run, and every production release is already a staged, pinned, rollback-capable operation. A gated branch would add a merge step in front of that same release without reducing what the single operator is exposed to. The user made the call (plan P-10: where repairs land is the user's decision).

## Cost to reverse

Medium. Before a release is activated: a revert on Lugos master, nothing on the host. After activation: the controller's `Rollback` to the previous release, or a revert plus a new staged release; the device observation after half has to be repeated if the repair is later reinstated.
