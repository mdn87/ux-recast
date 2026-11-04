# fixture-cycle-002: a fixture run that ends in a linked project lesson

Plan slices S2.5 and S2.6. The same contact-request fixture and the same `scripts/fixture_cycle.py` as [fixture-cycle-001](../fixture-cycle-001/README.md), run on 2026-11-04 with two new last phases that exercise the Phase 2 records. `lesson`: the Outcome goes to `decisions.jsonl` (S2.2), the evidence it rests on is archived into `.ux-recast/evidence/<run>/` (S2.3), and a project-tier lesson links all of it (S2.4). `compare` records the product comparison (S2.6).

## What happened

1. `baseline`, run `9da027be4b4b`: 4 of the 7 flow tests failed on the defective page; 10 observations and 5 screenshots became `evidence.json` (6,780 bytes); the packet was prepared and claimed (14,550 request characters, text and image).
2. `record`: the agent driving the cycle reviewed `evidence.json` and the screenshots and wrote three findings (`findings.json`): F1 a rejected submit wipes every entry, F2 no field is identified, F3 focus is left on Send. The receipt was accepted, the findings consumed as `current`, and the controller granted repair.
3. `repair`: the page applied is cycle 001's agent-authored `index.repaired.html`, unchanged, because these findings are the same F1 to F3 that page repaired. This run tests the records, not a new repair. All 7 flow tests passed after (`after-tests.txt`) and on the fixture's oracle page (`oracle-tests.txt`).
4. `finish`: finished as `verified` ("Recorded agent report; not independent proof of verification"); the receipt consumed after the repair reports the findings `stale`, as intended. 322 files were opened and none is under the Lugos checkout.
5. `lesson`: the scratch project was given its own git repository, so its identity is `#c043adbf1ff2…` (no remote, its root commit). Then:
   - Outcome `44a31b5f6ff3` was recorded through `evidence_archive.record`, which archived the packet, receipt, evidence JSON and the five before screenshots from the packet, plus the cited `findings.json`, `repair.diff`, `after-tests.txt` and the three after screenshots of the lesson's test.
   - Lesson `L-d8a44a04`, "A rejected submit keeps every entry and points at the field to fix", was written as a `candidate` with links to finding F1, the diff, the before and after screenshots of `test_invalid_email_preserves_work_and_can_complete` (failed before, passes after), that test's passing output, and the Outcome.
   - Both were committed and the project was cloned. In the clone, where `.ux-review/` does not exist, all 18 links from the lesson and the Outcome resolve, and every archived file matches its manifest digest (`cycle.json`, `lesson.clean_clone`).

6. `compare`: comparison `3a558aa1c2bf` ([`comparison.json`](comparison.json), `ux-recast/comparison@2`, kind `product`) was appended to the project's `.ux-recast/comparisons.jsonl`.
   - The criteria are the task's eight acceptance statements, frozen when the controller bound `task.json` at the checkpoint.
   - It cites the test outputs, findings, diff, a before screenshot, the archive manifest and the lesson.
   - Its effort comes from the cycle log: 1 review pass, 0 retries, 0 false findings, 0 user interventions, and 66.6 s of measured test runs. `effort.basis` says what that leaves out.
   - It states four limitations. The decision is `accept`, recorded by the fixture-cycle driver, because the fixture has no human owner. It is not a product owner's decision.

The project's `.ux-recast/` tree is exported here as [`ux-recast/`](ux-recast/); the lesson is [`ux-recast/lessons/project/L-d8a44a04.md`](ux-recast/lessons/project/L-d8a44a04.md).

## Caveats

- The exported text files are scrubbed of local paths (the repository is `<repo>`, the home directory `~`, the temp directory `<tmp>`). Four archived files therefore differ from their manifest digests here: `packet.json`, `receipt.json`, `cited/evidence/repair.diff` and `cited/evidence/after-tests.txt`. The digests were checked against the unscrubbed archive in the clone before export.
- The reviewer, the lesson author and the cycle driver are the same agent in one session, and the repair is reused from cycle 001. This proves the record mechanics, not the quality of an independent review.
- `supported_by` is empty: the lesson has support only from its own project. Promoting it to the shared tier was attempted after the run and refused with "no supporting outcome from a second project identity", logged in [`ux-recast/lessons/log.jsonl`](ux-recast/lessons/log.jsonl); it stays a `candidate` until a second project identity records an Outcome for it (Phase 8).

Rerun: `python scripts/fixture_cycle.py baseline --cycle fixture-cycle-002`, author findings with the new run's `task_sha256`, then `record --findings`, `repair --page`, `finish`, `lesson --lesson L.json` with `{title, body, finding, test}`, and `compare --comparison C.json` with the claims, dispositions, limitations and decision. Requires `playwright` with Chromium and `git`.
