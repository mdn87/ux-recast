# Implementation slices

Status: planning deliverable, prepared 2026-11-02 and amended the same day after the roundtable review (plan section 7). Breaks each phase of [the initial implementation plan](initial-implementation-plan.md) into vertical slices an agent can take one at a time. Every slice names its outcome, what it touches, and the proof that closes it. Sizes are advisory (S: under an hour, M: a few hours, L: a day); they guide sequencing and never gate work.

A slice is done when its proof exists and is recorded. Slices inside a phase run in order unless marked parallel. Nothing here is authorized to start; AGENTS.md requires a separate instruction.

## Phase 0: Foundations and the Lugos baseline

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S0.1 | Bootstrap: package skeleton, CI, decision log seeded | `pyproject.toml` with package data, `src/ux_recast/__init__.py`, `tests/test_smoke.py`, `.github/workflows/ci.yml` (ubuntu-latest, 3.11 and 3.13), `docs/decisions/0001` to `0016` from plan section 4 | `pip install -e .` and pytest pass on Windows and Linux; one green CI run; decision files present and linked from README (license S0.1 of the first draft is already done) | M |
| S0.2 | Wheel verification | `pyproject.toml` package-data, `tests/test_package_data.py` | `pip install .` from a built wheel in a clean venv; `importlib.resources` loads `rubric/`, `schemas/`, `docs/templates/` | S |
| S0.3 | Line endings pinned on both sides | ux-recast `.gitattributes` (already LF for md, json, yaml); Lugos `SKILL/` attributes checked | A test that `rubric.md` bytes hash identically on a Windows and a Linux checkout | S |
| S0.4 | Lugos Windows encoding fix (B-07) | `SKILL/scripts/autowork_review.py:379`, mirror copy | Lugos suite passes on Windows with no `PYTHONIOENCODING` override; recorded with Python version | S |
| S0.5 | Lugos test inventory by id | `lugos/docs/evidence/ux-review-test-inventory-2026-11.md` | Every test id listed, with which run env vars (`DEMO_EVIDENCE_DIR`, `DIAS_MOBILE_BROWSER_TESTS`) each needs | S |
| S0.6 | Baseline live submits on legacy (B-04) | `lugos/docs/evidence/ux-review-live-submit-baseline/` | Two receipts with `accepted: true` through the real `lugos.models delegate`: one text-only, one with an image; one recorded rejection or timeout path | M |

## Phase 1: Standalone core, both scripts ported, and the independence fixture

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S1.1 | Controller ported | `src/ux_recast/cycle/{state.py,budget.py,checkpoint.py}`, `cli.py` verbs `status`, `mode`, `checkpoint`, `phase`, `finish` | `SKILL/tests/test_control.py` copied to `tests/lugos_compat/` passes with only imports changed; if any test shells out, the harness adaptation is recorded | M |
| S1.2 | Packet helper ported as the Lugos Autowork provider | `src/ux_recast/providers/{base.py,lugos_autowork.py}`, `cli.py` verbs `prepare`, `claim`, `submit`, `record`, `consume` | `test_autowork.py` and `test_submit.py` (with the fixture MCP server) pass in `tests/lugos_compat/`; the inner delegate request is byte-identical to legacy for the same inputs | L |
| S1.3 | Rubric and reviewer prompt relocated, bytes frozen | `src/ux_recast/rubric/{rubric.md,autowork-reviewer.md,VERSION}`, `tests/test_rubric_bytes.py` | SHA-256 of each packaged file equals the Lugos file's at the pinned commit; the test also reads the two Lugos copies when the checkout is present | S |
| S1.4 | Contracts defined and validated against real artifacts | `src/ux_recast/contracts/*.py`, `schemas/*.json` | The 2026-10-24 packet, state and receipt and the S0.6 live-submit packets validate; a mutated copy fails naming the field; new fields are shown to be outer-envelope only | M |
| S1.5 | Local-agent provider | `src/ux_recast/providers/local_agent.py` | `ux-recast review --provider local` writes `packet.json` and `findings.template.json`; `record` accepts a filled file and refuses a malformed one | M |
| S1.6 | Differential harness and frozen corpus | `tests/differential/{corpus/*.json,run.py}` | Corpus covers valid, malformed contract, out-of-scope flow, double claim, stale consume, over-cap result; the runner diffs stdout bytes, exit code and `.ux-review/` tree between two implementations; baseline recorded against ux-recast | M |
| S1.7 | Independence fixture copied with provenance | `fixtures/contact-request/{task.json,index.before.html,index.html,test_flow.py,PROVENANCE.md}` | `PROVENANCE.md` names the Lugos commit and path; the seven tests pass in a clean venv with `playwright` and `playwright install chromium` | S |
| S1.8 | First end-to-end cycle without Lugos, findings-driven | `docs/evidence/fixture-cycle-001/` | Checkpoint, review through `local_agent`, repair written from the findings (the corrected `index.html` is the oracle, compared after), verify; seven passing checks; run on a host with no Lugos checkout; subprocess and file access logged and free of Lugos paths | M |

## Phase 2: Project design context and retained knowledge

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S2.1 | Context records: read as text, write only when absent | `src/ux_recast/records/context.py` | Existing `PRODUCT.md` and `DESIGN.md` are never modified; starter templates are created with `O_CREAT | O_EXCL`; a race to create yields exactly one file | S |
| S2.2 | Decisions append-only with the cycle lock | `records/decisions.py` | 200 iterations of two concurrent writers on Windows and POSIX with lines above 4 KiB produce intact JSONL; a stale `.lock` from a killed process is recovered and logged | M |
| S2.3 | Evidence archive | `records/evidence_archive.py` | Recording a Decision copies the cited packet, receipt and screenshots into `.ux-recast/evidence/<run>/`; links resolve on a clean checkout | S |
| S2.4 | Lessons in two tiers with project identity | `records/lessons.py`, `cli.py` verb `lessons promote` | Identity is git remote plus root hash; promotion refused and logged with "no supporting outcome from a second project identity"; the explicit-user-instruction bypass is logged; a copy of the same project at a new path does not count | M |
| S2.5 | Fixture run yields a linked lesson | `docs/evidence/fixture-cycle-002/` | The project-tier lesson links finding, diff, archived before and after screenshots and the passing test | S |
| S2.6 | Comparison record and lesson states | `records/comparisons.py`, `records/lessons.py`, `contracts/`, `schemas/comparison.schema.json`, `schemas/lesson.schema.json` | A `product` comparison for fixture-cycle-002 records frozen criteria, cited evidence, limitations, effort fields filled from the cycle log and a decision from the six allowed values; a lesson moved to `rejected` without a reason is refused; the lesson `status` enum is exactly candidate, project, shared, rejected, superseded (concept C-55, C-58, C-59, C-60) | S |

## Phase 3: Lugos entry point and staged migration

Work in this phase lands in the Lugos repository; ux-recast tags a release for it to pin.

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S3.1 | Dependency pinned | `plugins/lugos-toolset/requirements-ux-review.txt`, ux-recast tag | `pip install -r` resolves on the self-hosted Linux runner and on Windows | S |
| S3.2 | Legacy siblings and shims | `SKILL/scripts/{control.py,autowork_review.py}` as shims; `control_legacy.py`, `autowork_review_legacy.py` as siblings; mirror | Shims re-export the legacy module surface; `UX_REVIEW_IMPL` checked before importing `ux_recast`; absence of `ux_recast` without legacy selected fails closed with a message (tested); `test_distribution.py` extended and passing | M |
| S3.3 | Test-id parity on both implementations, both platforms | none (verification) | Every id in the S0.5 inventory passes under `legacy` and under the shim on Windows (recorded, Python version named) and on the Linux runner | M |
| S3.4 | Differential corpus parity | none (verification) | S1.6 corpus run under both; stdout bytes, exit codes and `.ux-review/` trees match, with the S0.4 encoding change the only documented difference | S |
| S3.5 | Importing callers replayed with expected output | `scripts/coordination_trials.py`, MyDocs forwarder `control.py` | Both run under the shim with a stated expected output recorded; `lugos_catalog.py --check` exits 0 | S |
| S3.6 | Live submits on the shim compared to baseline | `lugos/docs/evidence/ux-review-live-submit-shim/` | Text and image receipts `accepted: true`; compared field by field to S0.6; one rejection or timeout path exercised | M |
| S3.7 | Rollback drills in both directions | `docs/evidence/ux-review-rollback-drill/` | Shim to legacy and legacy to shim, including a crossover while `dispatch.lock` is held; legacy tolerates a `deferred` status and unknown outer-envelope keys | M |
| S3.8 | Documentation corrected | `lugos/docs/ux-review.md:49,87-90` | Lines state that `submit` starts the MCP server and that image review is opted in for `review` | S |
| S3.9 | Legacy removal | siblings deleted, switch removed | Only after the Phase 5 Decision is `accepted` and S3.7 passed; tests still pass | S |

## Phase 4: Cycle hardening and evidence helpers

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S4.1 | Five-finding cap with ordering, dispatch count | `cycle/budget.py` | A seven-finding result records five actionable and two `deferred`, ordered by severity then input order, deterministically | S |
| S4.2 | Image-policy preflight | `providers/lugos_autowork.py`, `tests/test_image_preflight.py` | A contract test that an image packet is accepted by the installed policy; rejection fails with a message and never falls back to text silently | S |
| S4.3 | Impeccable detect as an evidence pre-pass | `evidence/impeccable_detect.py` | Runs only when `impeccable` is on PATH (no `npx` install); exit 2 is findings, other non-zero is error; missing binary or browser reports `unavailable`; findings carry rule ids and `kind: implementation` | M |
| S4.4 | Impeccable command passes where installed | `rubric/autowork-reviewer.md`, `cycle/` pass runner | With the skill present in a project, `critique`, `adapt`, `harden`, `polish` are invoked by name; without it the prompt carries the vocabulary; rubric `VERSION` bumped once here with S1.3's byte test updated | M |
| S4.5 | Tap-to-target capture | `evidence/tap_to_target.py` (Playwright extra) | A tap coordinate on the fixture page yields the deepest element's selector and `data-*` state; the finding schema accepts it | S |

## Phase 5: Dias mobile pilot

Pre-pilot slice S5.0 can start right after Phase 0. The rest needs B-03, B-09 and a pinned host-ops revision.

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S5.0 | Pre-pilot: Dias checkpoint 2 on the existing Lugos skill | `lugos-host-ops/.ux-review/`, `docs/evidence/dias-pre-pilot/` | One review pass with screenshots on the fixture at 390×844; findings recorded; nothing repaired | M |
| S5.1 | Browser coverage for the two untested pages | `lugos-host-ops/tests/test_input_page_browser.py`, `test_approval_page_browser.py` | Both pages have a passing Playwright check under `DIAS_MOBILE_BROWSER_TESTS=1` before any repair | M |
| S5.2 | Harness gains 375×812 and a WebKit project, engine recorded | `lugos-host-ops/tests/fixtures/*.cjs`, Playwright config | Proof JSON names engine and version; both viewports produce screenshots | S |
| S5.3 | Phone-client context recorded as observed | `lugos-host-ops/PRODUCT.md`, `DESIGN.md` (`basis: observed`) | Three inline palettes as literals with file and line provenance; build id recorded | S |
| S5.4 | Pilot task contracts and frozen before scripts | `.ux-review/tasks/{needs-you,request-detail,response-status}.json`; `tests/pilot/before/*.py` with a recorded hash | Contracts validate; each packet's rows are listed and fit the five-screenshot and 64 KiB caps; scripts hashed before any repair | M |
| S5.5 | Before evidence, fixture and device | `docs/evidence/dias-pilot/before/` | Screenshots at both viewports for every row; taps and scroll counts; fixture server received-message counts; the user's phone observation with model and OS (B-02) | M |
| S5.6 | Review passes with images through Autowork | three packets under `.ux-review/packets/` | Each receipt `accepted: true`; at most five actionable findings each; `consume` reports current | M |
| S5.7 | Accepted design direction (B-12) | `lugos-host-ops/DESIGN.md` (`basis: proposed` then `accepted`) | One palette, type scale, status vocabulary and layout rhythm for the three pages, with contrast figures; the user's acceptance recorded as a Decision | M |
| S5.8 | Repair: sessions page and `app.js` | `remote_sessions.py`, `mobile_static/app.js`, landing per B-09 | Host-ops pytest and the browser suite pass; diff limited to the flow | L |
| S5.9 | Repair: question page | `input_page.py` | Same, with S5.1 coverage | M |
| S5.10 | Repair: approval page | `approval_http.py` | Same, with S5.1 coverage; receipt-row exclusion stated | M |
| S5.11 | Verification and user Decision | `docs/evidence/dias-pilot/after/`, a Decision record | Frozen scripts rerun unchanged; device observation after; comparison table including visual criteria; the fixture-vs-production non-coverage list; the user's accept or reject | M |
| S5.12 | Dias-specific decisions filed | `dias-mobile/docs/` note and the phone client's `DESIGN.md` | Decisions reference the pilot run ids; no Dias colour or status meaning in the shared rubric | S |

## Phase 6: Style guide and component sheets

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S6.1 | Documentation request contract and packet | `contracts/documentation.py`, `docs/packet.py`, `cli.py` verb `document` | Flags independent; `motion` without a sheet refused; a documentation packet is prepared for a provider and the returned artifact is validated before writing | M |
| S6.2 | Lugos skill entry point for documentation | `SKILL/SKILL.md`, shim verb | `$ux-review document ...` reaches `ux-recast document`; review mode untouched | S |
| S6.3 | Guide template | `docs/templates/guide.md` | Any subset of sections renders; content-behavior section is required only when a sheet uses slots (C-45) | S |
| S6.4 | Sheet template with notice | `docs/templates/sheet.html` with MIT notice and `5c457437c8c8` | Opens standalone; variable table and `[TBD]` render; notice present | M |
| S6.5 | Variable schema and validator corpus | `docs/variables.py`, `tests/docs/validator_corpus/` | Corpus covers `0`, unitless line-height, hex, z-index, percentages, SVG attributes; unlabeled numerics fail; `[TBD]` ratio reported | M |
| S6.6 | Rendered measurement input with full provenance | `evidence/measure.py` | Records value, CSS px, device pixel ratio, engine and version, font availability, revision and viewport for the sessions card at 390 px | M |
| S6.7 | Mechanical trace and seeded-mutation check | `docs/trace.py`, `tests/docs/test_trace_sensitivity.py` | Literals re-read, rendered values re-measured within tolerance, formulas recomputed; N seeded mutations all caught; the remainder checked by a blind agent from another family | M |
| S6.8 | First Dias sheet and guide | `lugos-host-ops/docs/design/{guide.md,sheets/sessions-card.html}` | Trace passes with zero unexplained deltas; host-ops code diff empty; a developer reproduces the card from the sheet and guide within tolerance | L |

## Phase 7: Motion presentation (gated; defect fix may run early)

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S7.1 | Renderer defects fixed in a local copy or upstream | `docs/motion/render.mjs` or upstream PR | Non-zero ffmpeg exit fails the export; video output directory created | S |
| S7.2 | Entry gate | none | S6.8 accepted; Chromium available on the implementing host | n/a |
| S7.3 | One real export verified mechanically | `docs/evidence/motion-001/` | `ffprobe` duration and frame count match the scene; the static sheet unchanged | M |

## Phase 8: Second-project validation

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S8.1 | Second project chosen and context recorded | that project's `PRODUCT.md`, `DESIGN.md` | `basis: observed`; its project identity differs from the fixture's and Dias's (B-08) | S |
| S8.2 | Full cycle through the local agent | that project's `.ux-review/` and `.ux-recast/` | Decision and Outcome recorded; no Lugos path accessed | M |
| S8.3 | One lesson promoted and shown to change a result | `src/ux_recast/lessons/shared/*.md`, rubric `VERSION` | Promotion accepted with two `supported_by` from two identities; a frozen input reviewed before and after promotion yields the predicted difference | M |
| S8.4 | Method comparison on a held-out case | `records/comparisons.py`, `docs/evidence/method-comparison-001/` | One `method` comparison names a case not used to develop the method, records effort, and reaches a decision; the fixture is refused as the held-out case for a method developed on it (concept C-55) | S |

## Phase 9: Guide Builder (gated by D-17; not scheduled)

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S9.0 | Entry gate | none | Phase 3 rollback drill recorded (S3.7); Dias pre-pilot checkpoint done (5a); B-13, B-14 and B-15 resolved in the plan's blocker table | n/a |
| S9.1 onward | Written when S9.0 passes | to be decided | Slices are cut from the Phase 9 shape in the plan at that time, not before | n/a |

## Suggested first batch

If implementation is authorized, the smallest coherent batch that proves the architecture is S0.4, S0.5, S0.6 in Lugos (green Windows baseline and live-submit receipts) in parallel with S0.1, S0.2, S1.1, S1.2, S1.3, S1.4, S1.7, S1.8 in ux-recast (both scripts ported, Lugos tests passing against the package, one findings-driven cycle on the fixture with nothing from Lugos on disk). S5.0 can run as soon as S0.4 lands if the user wants Dias findings early.
