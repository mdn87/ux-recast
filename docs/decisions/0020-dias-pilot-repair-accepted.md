# D-20: Dias pilot repair accepted (S5.11)

- Status: accepted (user decision 2026-11-03)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-20; plan Phase 5, step 5d; slice S5.11

## Decision

The operator accepted the Phase 5c repair of the three phone pages as it stands on Lugos master at `842ebd67`. It is live as release `hops-0bf9e79e5332-559318e60ab3`, build `mobile-navigation-20261102-2`. Nothing is reverted.

## What it was decided on

- The frozen before scripts reran unchanged against the repaired pages (`freeze.py --check` printed "frozen scripts unchanged"). The run was at Lugos `0bf9e79e`, on Chromium 149 and WebKit 26.5, at 390x844 and 375x812. The evidence is in Lugos `docs/evidence/dias-pilot/after/` (commit `18075d66`), compared with `before/` by `lugos-host-ops/tests/pilot/compare.py`.
- After the repair, no observation fails a threshold on either engine. Before, out of 30 observations per engine, these failed: 18 on buttons under 48 px, 4 on the fold rule, 4 on tap targets, 4 on banned words, 4 on receipt wording, 2 on base font and 2 on the connection line.
- A first after-run, at `814cbd7a`, found two sessions-page rules the repair had missed: the connection line still said "Connected" over an expired status report, and there was no closing sentence. Both were fixed in `0bf9e79e` before the run this Decision rests on.
- B-02 after half, on the operator's iPhone 16e (Lugos `docs/evidence/dias-pilot/after/device/`, commit `842ebd67`): the installed PWA runs build 20261102.2. The question page keeps its last field and Send answer visible with the keyboard open, and recovers when the keyboard closes.

## What it leaves open

- Composer with the keyboard open. In the after capture the iOS keyboard accessory bar covered the field and Send stayed under the keyboard; in the before capture both were visible. One capture on each side does not show whether the repair or the tap position caused it. This is not a revert reason, because reverting does not change how iOS scrolls a focused field. A fix that keeps Send in view after focus needs one confirming phone capture.
- When preparing an answer fails unexpectedly, the question page shows the raw exception text. Recorded only.
- The send path cannot be observed on the phone through the LAN fixture. Plain HTTP on a LAN address is not a secure context, so `crypto.randomUUID` is undefined there. The send and refusal paths are covered by the browser tests on `127.0.0.1`.
- Still not covered by the fixture, as the after README lists:
  - a push-notification tap into the PWA;
  - the Access 401 and redirect;
  - 200 percent zoom;
  - screen-reader announcements;
  - approvals-first ordering;
  - the Received, Resumed, Failed, Rejected and Delivery unknown receipt stages (Queued was seen in production);
  - a 1024-unit output;
  - more than one host.

## Why

The plan made S5.11 an accept-or-revert Decision (D-19), and the operator made the call after the comparison and the device notes. On that evidence:

- every threshold is met on both engines;
- the two rules the first after-run caught were fixed and re-verified before the Decision;
- the device check found no regression shown to come from the repair.

## Cost to reverse

Medium. A full revert means `git revert` of the 5c commits on Lugos master and a new staged release. The controller's Rollback returns to an earlier release, and the one before this, `hops-814cbd7a20cd-9a7ec5c1ab88`, already carries most of 5c. The before evidence stays valid either way.
