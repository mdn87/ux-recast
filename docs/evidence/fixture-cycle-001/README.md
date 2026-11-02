# fixture-cycle-001: findings-driven cycle on the contact-request fixture

Plan slice S1.8. One bounded review -> repair -> verify cycle run by `scripts/fixture_cycle.py` on 2026-11-02 using only the installed `ux_recast` package, with the agent driving the script as the reviewer (`local-agent` provider). The point of the exercise is independence from the Lugos checkout and a repair that comes from recorded findings, not from the fixture's known answer.

## What happened

1. `baseline`: the fixture was copied to a scratch project with `index.before.html` installed as `index.html`. The fixture's seven Playwright flow tests ran against it: four failed (`empty_form_identifies_required_fields`, `invalid_email_preserves_work_and_can_complete`, `keyboard_validation_recovery`, `small_touch_viewport_recovery`), three passed. Their observation captures became `evidence.json` (10 observations, 5 screenshots, 6,780 bytes). The controller opened run `aeca78da6838` on an `implementation` snapshot checkpoint bound to `index.html`; the packet was prepared and claimed (`packet.json`, text plus image modalities, 14,550 request characters).
2. `record`: the reviewer read `evidence.json` and the screenshots and wrote `findings.json` (four findings: F1 entries wiped on a rejected submit, F2 no field identified, F3 focus left on the Send button, F4 an unresolved question about the 375px status line). The findings were validated against the contract, recorded through the ordinary packet lifecycle (`receipt.json`, accepted), consumed as `current`, and the controller granted the repair phase.
3. `repair`: the reviewer authored a change to the submit handler from F1 to F3 (`repair.diff`, `index.repaired.html`): per-field validation into the existing `*-error` slots, `aria-invalid`, no form reset, focus to the first invalid field, a status line that says the entries are kept. The controller sealed the repaired input and granted verification. The seven flow tests passed on the repaired page (`after-tests.txt`) and on the fixture's corrected `index.html` as the oracle (`oracle-tests.txt`).
4. `finish`: the run was finished as `verified` (the controller's own words: "Recorded agent report; not independent proof of verification"). Consuming the receipt after the repair reports the findings as `stale` with `index.html` changed, which is the intended Lugos semantics: findings guide one repair and never satisfy verification themselves.

## Independence

Every `open()` in the cycle process and in the test subprocesses was logged through `sys.addaudithook` (`access-log.txt`, 336 distinct paths). None is under the Lugos checkout (`cycle.json` -> `access.lugos_reads` is empty). The log is scrubbed: the repository is `<repo>`, the home directory is `~`.

## Caveats

- The reviewer and the repair author are the same agent, in the same session, working from the fixture's own test captures. This proves the mechanics and the independence of the code path, not the quality of an external review.
- The repair converges on the oracle because the defective page already carries the error slots and `aria-describedby` wiring; the diff shows the authored change rather than a copy.
- F4 is recorded as unresolved on purpose: a full-page screenshot cannot show whether the status line is in the 375px viewport.
- `task_sha256` values in `packet.json` and `receipt.json` are those of the unscrubbed request text; `request.workspace` was a local path and reads `<repo>/.work/fixture-cycle-001` after scrubbing.

Rerun: `python scripts/fixture_cycle.py baseline`, author findings from `.work/fixture-cycle-001/evidence.json`, then `record --findings`, `repair --page`, `finish`. Requires `playwright` with Chromium.
