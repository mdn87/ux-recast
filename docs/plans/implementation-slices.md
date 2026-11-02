# Implementation slices

Status: planning deliverable, prepared 2026-11-02. Breaks each phase of [the initial implementation plan](initial-implementation-plan.md) into vertical slices an agent can take one at a time. Every slice names its outcome, what it touches, and the proof that closes it. Sizes are advisory (S: under an hour, M: a few hours, L: a day); they guide sequencing and never gate work.

A slice is done when its proof exists and is recorded. Slices inside a phase run in order unless marked parallel. Nothing here is authorized to start; AGENTS.md requires a separate instruction.

## Phase 0: Repository foundations

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S0.1 | License chosen and committed | `LICENSE`, `NOTICE`, README license line | Done 2026-11-02: Apache-2.0 text from GitHub's canonical copy, `NOTICE` present, D-01 marked confirmed in the plan | S (done) |
| S0.2 | Package skeleton installs | `pyproject.toml`, `src/ux_recast/__init__.py`, `tests/test_smoke.py` | `pip install -e .` and `python -m pytest` pass on Windows and Linux | S |
| S0.3 | CI green on an empty suite | `.github/workflows/ci.yml` (ubuntu-latest, Python 3.11 and 3.13) | One green run linked from the decision log | S |
| S0.4 | Decision log seeded | `docs/decisions/0001-license.md` through `0012-react-grab.md` from plan section 4 | Files present, linked from README | S (parallel with S0.2) |

## Phase 1: Standalone core and the independence fixture

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S1.1 | Controller ported | `src/ux_recast/cycle/{state.py,budget.py,checkpoint.py}`, `cli.py` verbs `status`, `mode`, `checkpoint`, `phase`, `finish` | `SKILL/tests/test_control.py` copied to `tests/lugos_compat/` passes with only the import line changed (27 tests) | M |
| S1.2 | Rubric and reviewer prompt relocated and versioned | `src/ux_recast/rubric/{rubric.md,autowork-reviewer.md,VERSION}` | `rubric_sha256` of the relocated file equals the Lugos file's at the pinned commit; a `ux-recast rubric --version` command prints it | S |
| S1.3 | Contracts defined and validated against real artifacts | `src/ux_recast/contracts/*.py`, `schemas/*.json` | The 2026-10-24 `packet.json`, state file and receipt from `.lugos-audit/ux-review-promotion-20261024/` validate; a mutated copy fails with a named field | M |
| S1.4 | Local-agent provider | `src/ux_recast/providers/{base.py,local_agent.py}` | `ux-recast review --provider local` writes `packet.json` and a `findings.template.json`; `ux-recast record` accepts a filled findings file and refuses a malformed one | M |
| S1.5 | Independence fixture copied with provenance | `fixtures/contact-request/{task.json,index.before.html,index.html,test_flow.py,PROVENANCE.md}` | `PROVENANCE.md` names the Lugos commit and path; `python fixtures/contact-request/test_flow.py` passes 7 tests in a clean venv with only `playwright` | S |
| S1.6 | First end-to-end cycle without Lugos | `docs/evidence/fixture-cycle-001/` | Recorded run: checkpoint, review (local agent), repair (swap in `index.html`), verify; outcome lists 7 passing acceptance checks; no Lugos, Autowork or Dias path imported (assert via `sys.modules` in the test) | M |

## Phase 2: Project design context and retained knowledge

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S2.1 | Context records read and write Impeccable-compatible files | `src/ux_recast/records/context.py` | Round-trips a `PRODUCT.md` and `DESIGN.md` from an Impeccable-initialized sample project without changing their headings; writes them only when absent | M |
| S2.2 | Decisions and outcomes are append-only | `records/decisions.py`, `.ux-recast/decisions.jsonl` writer with no-clobber semantics | Two concurrent writers produce two intact lines; a rewrite attempt is refused | S |
| S2.3 | Lessons in two tiers with promotion rule | `records/lessons.py`, `cli.py` verb `lessons promote` | Promotion refused with the reason "no supporting outcome from a second project"; accepted once a second outcome is linked | M |
| S2.4 | Fixture run yields a linked lesson | `docs/evidence/fixture-cycle-002/` | The project-tier lesson record links finding, diff, before and after screenshots and the passing test | S |

## Phase 3: Lugos entry point and staged migration

Work in this phase lands in the Lugos repository; ux-recast tags a release for it to pin.

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S3.0 | Windows encoding defect fixed upstream (B-07) | `SKILL/scripts/autowork_review.py:379`, mirror copy | `SKILL/tests` gives 61 passed on Windows with no `PYTHONIOENCODING` override | S |
| S3.1 | Dependency pinned | `plugins/lugos-toolset/requirements-ux-review.txt`, ux-recast tag `v0.1.0` | `pip install -r` resolves on the self-hosted Linux runner | S |
| S3.2 | `control.py` shim with legacy switch | `SKILL/scripts/control.py`, `SKILL/scripts/_legacy/control.py`, mirror | 27 controller tests pass with `UX_REVIEW_IMPL` unset and with `legacy`; `test_distribution.py` extended to cover the shim | M |
| S3.3 | `autowork_review.py` shim | `SKILL/scripts/autowork_review.py`, `_legacy/`, mirror | 25 prepare, claim, submit, record and consume tests pass under both values; packet `schema_version` still `1` | M |
| S3.4 | Caller replay | none (verification) | `scripts/coordination_trials.py` runs clean against the shim; `lugos_catalog.py --check` exits 0; CI green on Linux | S |
| S3.5 | First live submit (B-04) | `docs/evidence/ux-review-live-submit-001/` in Lugos | A text-only packet submitted through the real `lugos.models delegate`; receipt `accepted: true`; `task_sha256` matches | M |
| S3.6 | Documentation corrected | `lugos/docs/ux-review.md:49,87-90` | Lines state that `submit` starts the MCP server and that image review is opted in for `review` | S |
| S3.7 | Rollback drill recorded | `docs/evidence/ux-review-rollback-drill/` | With `UX_REVIEW_IMPL=legacy`, a run started on the shim is read and finished by the legacy code | S |
| S3.8 | Legacy removal | `_legacy/` deleted, switch removed | Only after S5.6; tests still pass | S |

## Phase 4: Cycle with provider adapters

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S4.1 | Autowork provider ported behind the protocol | `providers/lugos_autowork.py` | S3.3's tests pass through the provider; `image_input`, `image` modality and `visual_inputs` are declared together or not at all | M |
| S4.2 | Impeccable detect provider | `providers/impeccable_detect.py` | With `impeccable@4.8.0` on PATH, findings carry rule ids and `kind: implementation`; without it the run records `unavailable` and completes | M |
| S4.3 | Five-finding cap enforced on record | `cycle/budget.py` | A seven-finding result records five actionable and two `deferred`; the controller test added for it passes | S |
| S4.4 | Capability pass names in the reviewer prompt | `rubric/autowork-reviewer.md` | Prompt lists `critique`, `adapt`, `harden`, `polish` as pass names; rubric version bumped; S1.2 test updated | S |

## Phase 5: Dias mobile pilot

Prerequisite: B-03 resolved and a host-ops revision pinned.

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S5.1 | Phone-client context recorded as observed | `lugos-host-ops/PRODUCT.md`, `DESIGN.md` (`basis: observed`) | The three inline palettes appear as literals with file and line provenance; no new colours introduced | S |
| S5.2 | Pilot task contracts written | `lugos-host-ops/.ux-review/tasks/{needs-you,request-detail,response-status}.json` | Each validates against the Task schema; acceptance lists match plan section 3, Phase 5 table | S |
| S5.3 | Before evidence captured on the fixture | `docs/evidence/dias-pilot/before/` | Screenshots at 390×844 and 375×812 for every table row; `*-proof.json` with taps and scroll counts; fixture revision recorded | M |
| S5.4 | Review pass with images through Autowork | packet under `.ux-review/packets/` | Receipt `accepted: true`; at most five actionable findings; `consume` reports `findings: current` | M |
| S5.5 | One repair batch in host-ops | affected pages only (`remote_sessions.py`, `input_page.py`, `approval_http.py`, `app.js`) | Existing host-ops pytest passes; the opt-in browser suite passes; diff limited to the affected flows | L |
| S5.6 | Verification and user decision | `docs/evidence/dias-pilot/after/`, a Decision record | After evidence for every row; the comparison table; the user's accept or reject recorded; the real-device keyboard observation requested (B-02) | M |
| S5.7 | Dias-specific decisions filed | `dias-mobile/docs/` note and the phone client's `DESIGN.md` | Decisions reference the pilot run id; no Dias colour or status meaning written into the shared rubric | S |

## Phase 6: Style guide and component sheets

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S6.1 | Documentation request contract | `contracts/documentation.py`, `cli.py` verb `document` | Flags `guide`, `sheets`, `motion` independent; `motion` without `sheets` refused with a message | S |
| S6.2 | Guide template | `docs/templates/guide.md` | Renders with any subset of the concept's sections; an empty subset renders only the header and `basis` | S |
| S6.3 | Sheet template adapted with notice | `docs/templates/sheet.html`, header with MIT notice and `5c457437c8c8` | Opens standalone; variable table and `[TBD]` slots render; notice present | M |
| S6.4 | Variable table schema and validator | `docs/variables.py` | A sheet with an unlabeled numeric value fails; `source` enumerations enforced; formula inputs resolved | M |
| S6.5 | Rendered measurement input | `evidence/measure.py` (Playwright, optional extra) | Measures the sessions card's padding, border width and radius on the fixture at 390 px and records `source: rendered` with revision and viewport | M |
| S6.6 | First Dias sheet and guide | `lugos-host-ops/docs/design/{guide.md,sheets/sessions-card.html}` | A second agent traces every non-`[TBD]` value to source or measurement; "content behavior" section present; user accepts usefulness | L |

## Phase 7: Motion presentation (gated)

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S7.0 | Entry gate | none | S6.6 accepted; Chromium available on the implementing host | n/a |
| S7.1 | Renderer defects fixed in a local copy or upstream | `docs/motion/render.mjs` or upstream PR | ffmpeg non-zero exit fails the export; video output directory created | S |
| S7.2 | One real export verified | `docs/evidence/motion-001/` | An mp4 of the sessions-card sheet plays; frame count matches the scene; the static sheet is unchanged | M |

## Phase 8: Second-project validation

| Slice | Outcome | Touches | Proof | Size |
| --- | --- | --- | --- | --- |
| S8.1 | Second project chosen and context recorded | that project's `PRODUCT.md`, `DESIGN.md` | Written with `basis: observed`; user names the project (B-08) | S |
| S8.2 | Full cycle through the local agent | that project's `.ux-recast/` | Decision and Outcome recorded; no Lugos path imported | M |
| S8.3 | One lesson promoted to shared | `src/ux_recast/lessons/shared/*.md`, rubric version bump | Promotion accepted with two `supported_by` links; the next packet's rubric section shows the lesson | S |

## Suggested first batch

If implementation is authorized, the smallest coherent batch that proves the architecture is S0.2, S0.3, S1.1, S1.2, S1.3, S1.5 and S1.6: a package that passes the existing controller tests and runs one full cycle on the fixture with nothing from Lugos imported. S3.0 can go in parallel in the Lugos repository because it is a one-line fix with its own test proof.
