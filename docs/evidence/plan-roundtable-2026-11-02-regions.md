# Plan review roundtable, 2026-11-02: participant regions

Verbatim copy of the CONTROL block and the three concerns regions from the Lugos roundtable session document `lugos/.roundtable/sessions/ux-recast-plan-review-20261102.md`, which Lugos does not track in git. The facilitator's clarify region (framing plus the captured plan at `db78c53`) and the reconcile artifact (the amended plan set) are omitted here because both are reproduced by this repository's own history; see [the evidence record](plan-roundtable-2026-11-02.md).

## CONTROL

```text
technique: three-amigos
seq: 5
round: 2
turn: 
phase: reconcile
status: converged
max_seq: 30
max_rounds: 2
clean_attacks: 0
converge_k: 2
lease_until: 
participants: facilitator:facilitator:<<facilitator/>>, product:product:<<product/>>, implementer:implementer:<<implementer/>>, tester:tester:<<tester/>>
submitted_round: 
topic: Review the ux-recast initial implementation plan set (docs/plans at db78c53): scope and acceptance (product), the shim-based Lugos migration and package boundary (implementer), and how each phase would actually be verified (tester). Planning review only; no implementation is authorized.
updated:
```


## REGION: product

[seq 2 | round 1 | phase concerns] # Product Concerns: Initial Implementation Plan (ux-recast db78c53)

## 1. Scope Distortions: Drops, Narrowings, and Unwarranted Mandates

- **[critical] "Looking sharper" is completely dropped from the Dias pilot (C-01 vs Phase 5, S5.1, S5.5, S5.7, Phase 6 Acceptance).**
  Matt's primary founding mandate was: *"improve the Dias mobile interface's user experience and make it look sharper"* (Turn 1, C-01). Section 1.2 establishes that the client has *"Three phone pages carry separate inline style blocks with different palettes; the approval page is light-themed while the others are dark. No framework, no build step, no design tokens."* Yet the plan systematically forbids fixing this:
  - S5.1 records the chaos as literal strings under `basis: observed` and explicitly commands *"no new colours introduced"*.
  - S5.5 restricts repairs to *"diff limited to the affected flows"* on structural bugs.
  - S5.7 commands *"no Dias colour or status meaning written into the shared rubric"*.
  - Phase 6 Acceptance explicitly boasts *"the product palette is untouched"*.
  Across 45 slices, not one slice harmonizes the inline palettes, unifies typography, or establishes visual hierarchy. The plan treats preserving ugly legacy inline styles as a virtue, completely dropping the aesthetic "make it look sharper" requirement.

- **[high] Impeccable's generative design improvement capability is quietly gutted into a passive linter (C-03, C-08, C-09 vs D-11, S4.2, S4.4).**
  In Turn 3, Impeccable was proposed as *"the main design-improvement capability"* (C-03) whose commands (`critique`, `adapt`, `harden`, `polish`) provide active design guidance. D-11 unilaterally reduces Impeccable to *"detect --json and record-file compatibility only"*, turning it into an automated syntax/rule linter (S4.2). S4.4 demotes its active capabilities to mere passive string labels in the reviewer prompt (*"pass names, not as new commands"*). The actual generative design intelligence that could make Dias look sharper was quietly abandoned without user consent.

- **[high] Interactive visual feedback (React Grab) dropped without a functional substitute (C-06 vs D-12, Table 2.2).**
  C-06 proposed React Grab so an operator could *"point at a Dias component and give source-linked feedback"*. D-12 dismisses it because *"No React tree in the phone client"*. While technically true, the *product need*—allowing a user to tap an element on screen to target a UX review finding—was quietly dropped. Table 2.2 falls back to `element (selector or data-* reference)`, forcing the operator back into inspecting raw HTML strings. If React Grab cannot be used, a DOM/Playwright coordinate click-to-selector alternative should have been scoped.

- **[medium] Mandatory "content behavior" section in style guide violates concept optionality (C-34, C-36 vs S6.6).**
  C-34 and C-36 mandate that style guide outputs be modular with *"every section optional, no default palette"*, and C-37 dictates *"The product determines which sections apply"*. Slice S6.6 violates this contract by decreeing: *"the guide's 'content behavior' section mandatory because the card uses slots"*. The planner should not promote optional sections to mandatory.

## 2. Sequencing and Value Realization: Style Guide (Phase 6) vs Dias Pilot (Phase 5)

- **[high] Inverted sequence: Running repair batches (Phase 5) before establishing design foundations (Phase 6).**
  In Phase 5, S5.5 executes a *"repair batch in host-ops"* against pages with three competing inline palettes. Against what visual standard is the agent repairing? None. It repairs against `DESIGN.md` initialized with `basis: observed` (the existing incoherent styling). Only in Phase 6 (S6.1-S6.6) does the plan extract component sheets and style guides. This is inverted: defining the style guide/tokens and component spec for the session card (Phase 6) provides the design contract that S5.5 should repair against. Doing Phase 5 first guarantees that S5.5 will only patch functional DOM leaks while leaving the visual design fractured.

- **[high] Heavy architectural scaffolding delays user value across 24 slices.**
  Phase 0 (Repo), Phase 1 (Standalone core), Phase 2 (Retained knowledge), Phase 3 (Lugos shim migration), and Phase 4 (Provider adapters) demand 24 vertical slices before the user sees a single improvement to Dias in Phase 5. The plan prioritizes building an abstract, multi-tier knowledge-promotion engine over solving the concrete product problem that motivated the repository.

## 3. Observability and Rigor of Acceptance Criteria

- **[high] Phase 5 acceptance measures plumbing and layout boundaries, not UX or visual quality.**
  In the Phase 5 table, acceptance criteria are purely mechanical checks: *"target card opened and scrolled... no horizontal overflow at 375 px... 409 surfaced... wrap, no clipping, Send reachable"*. A page can fulfill every single criterion while looking visually atrocious and illegible. There are zero observable acceptance criteria for visual polish, readability, contrast, or typographic hierarchy.

- **[medium] S6.6 acceptance criterion ("user accepts usefulness") is unobservable and ambiguous.**
  Slice S6.6 ends with *"user accepts usefulness (entry criterion for Phase 7)"*. What constitutes "useful"? Does it mean complete variable tables? Implementable by an engineer? Faithful rendering? Without defined acceptance gates, "usefulness" is an unobservable rubber-stamp that pushes ambiguity onto the user.

- **[medium] S8.3 acceptance conflates data promotion with learning efficacy.**
  In S8.3, acceptance is proven if *"The next packet's rubric section shows the lesson"*. Proving that a file was promoted from project to shared tier and injected as text proves string interpolation, not that the system improved design quality or prevented a recurring UX defect on a second project.

## 4. Decisions That Belonged to the Operator (Matt)

- **[critical] D-06: Landing pilot code repairs directly into production `lugos-host-ops`.**
  Section 1.2 notes the phone client is `lugos-host-ops`, a live service controlling host operations. D-06 unilaterally commits: *"The Dias pilot runs on mobile_browser_fixture.py, and repairs land in Lugos host-ops."* Authorizing an experimental agentic toolset to mutate host-ops code—especially when B-03 notes the `dias-mobile` worktree is a detached HEAD with uncommitted edits—is an operational risk that must be decided by Matt, not assumed by the planner.

- **[high] D-11: Gutting Impeccable into an audit-only CLI.**
  Matt specifically asked to explore Impeccable (C-03) to help Dias look sharper. The planner discarded its active styling skills in D-11 to maintain Lugos toolset purity. That trade-off belonged to Matt.

- **[medium] D-08: Deferring motion presentations without operator consultation.**
  Matt explicitly pointed at Dimensional Drawing's visual output (C-31). Deferring motion to Phase 7 due to two small headless renderer defects (`render.mjs:93` and missing `mkdirSync`) shelves one of Matt's primary visual interests without asking if he preferred fixing those two defects early.

## 5. Unassessed Aspects

- **Real-device usability (Blocker B-02):** Captured desktop Playwright runs at 390×844 cannot establish whether iOS Safari's dynamic URL bar and virtual keyboard obstruct form submission on Matt's actual phone.
- **Operational risk to host-ops (Blocker B-03):** Whether landing pilot edits in `lugos-host-ops` disrupts running operator sessions or conflicts with uncommitted detached-HEAD changes cannot be determined from plan text alone. <<product/>>


## REGION: implementer

[seq 4 | round 1 | phase concerns] # Implementer Concerns: Shim Migration, Package Boundary, Provider Protocol, and Slice Plan

## 1. Phase 3 Load-Bearing Claim & Migration Risks

- **[critical] Phase 3 / Phase 4 dependency inversion breaks `autowork_review.py` shim (`initial-implementation-plan.md` §3 Phases 3–4; `implementation-slices.md` S3.1, S3.3, S3.5 vs. S4.1; `reuse-and-license-map.md` "Packet helper" row)**: Phase 1 ports only `control.py` (`S1.1`) and implements only `providers/local_agent.py` (`S1.4`). Phase 3 then pins `ux-recast` tag `v0.1.0` (`S3.1`), replaces `autowork_review.py` with a shim calling `ux_recast.cli` (`S3.3`: *"25 prepare, claim, submit, record and consume tests pass under both values"*), and runs a live MCP `submit` (`S3.5`). However, `prepare`, `claim`, `submit`, `record`, and `consume` are not ported into `ux_recast` until Phase 4 (`S4.1`: *"Autowork provider ported behind the protocol | `providers/lugos_autowork.py` | S3.3's tests pass through the provider"*). `S3.3` and `S3.5` cannot execute against `ux_recast` before `S4.1` exists.
- **[high] Direct Python module imports vs. CLI-only shims (`initial-implementation-plan.md` §1.1, §3 Phase 3 Stage A; `implementation-slices.md` S3.2, S3.3, S3.4)**: §1.1 notes *"`scripts/coordination_trials.py:78-140` imports both scripts"* and `SKILL/tests/` imports them directly (`S1.1`: *"with only the import line changed"*). Yet Phase 3 Stage A states: *"Replace the bodies of `control.py` and `autowork_review.py` with shims that call `ux_recast.cli`, keeping argv, stdout JSON, exit codes, file paths and `schema_version: 1`."* A shim that only forwards CLI `argv` to `ux_recast.cli` will break callers and tests that import module-level functions, constants, or helpers from `control` and `autowork_review`. The shims must re-export the legacy Python module surface (or dispatch at the function level when `UX_REVIEW_IMPL=legacy`), not just wrap `sys.argv`.
- **[high] Relocating legacy scripts to `SKILL/scripts/_legacy/` breaks `__file__`-relative path resolution and doubles the manual mirror (`implementation-slices.md` S3.2, S3.3; `initial-implementation-plan.md` §1.1)**: `autowork_review.py` embeds `references/autowork-reviewer.md` and `references/rubric.md` (`§1.1:119-127`). Moving the legacy scripts one directory deeper into `SKILL/scripts/_legacy/` changes `Path(__file__).parent.parent` from `SKILL/` to `SKILL/scripts/`, breaking reference file lookup under `UX_REVIEW_IMPL=legacy` unless path resolution is patched. Furthermore, because `test_distribution.py` enforces byte-identity between `SKILL/` (minus `tests/`) and `.agents/skills/ux-review/` (`§1.1`), adding `_legacy/` inside `SKILL/scripts/` forces duplicating `_legacy/` into `.agents/skills/ux-review/scripts/_legacy/` by hand. Additionally, the shim must check `UX_REVIEW_IMPL == "legacy"` (and ideally catch `ModuleNotFoundError` when `ux_recast` is not installed in a caller's venv) *before* importing `ux_recast`, because `control.py` was previously zero-dependency stdlib Python.
- **[high] Additive contract fields in §2.2 risk breaking `autowork_review.py` strict validation and `task_sha256` (`initial-implementation-plan.md` §1.1, §2.2, §2.4)**: §1.1 notes that `autowork_review.py:62-66,104-116` allows *"keys `observations`, `screenshots`, `coverage`, `plan` only"* on evidence, and `autowork_adapter.py:615-636` validates `DispatchRequest` and `task_sha256`. §2.2 proposes adding `request_kind`, `provider`, and `rubric_version` to Review request, and adding a per-screenshot capture manifest (`revision`, `viewport`, `state`, `theme`, `captured_at`) to Evidence. If those fields are placed inside the inner Autowork `delegate` request payload or replace `screenshots: list[str]` with dicts, `lugos.models delegate` schema validation and `visual_inputs` construction will fail. The plan must specify that new metadata lives in the outer `packet.json` envelope (or an optional `capture_manifest` key after updating the allowed-keys check) while keeping the inner MCP `delegate` payload byte-identical.
- **[medium] Non-editable install packaging omission (`implementation-slices.md` S0.2 vs. S3.1)**: `S0.2` only proves `pip install -e .`, whereas `S3.1` pins `ux-recast` by git tag `v0.1.0` in `requirements-ux-review.txt`. Without explicit package-data configuration in `pyproject.toml` and `importlib.resources` loading, non-`.py` assets (`rubric.md`, `autowork-reviewer.md`, `VERSION`, `schemas/*.json`, `docs/templates/*`) will be omitted from built wheels.

## 2. Rubric Relocation (D-04) and Mirror Discipline

- **[medium] Moving the rubric to `ux-recast` creates a three-way sync trap and diverges `rubric_sha256` between shim and legacy (`initial-implementation-plan.md` §4 D-04; `implementation-slices.md` S1.2, S4.4, S8.3)**: D-04 states *"The rubric moves into ux-recast; the Lugos copy becomes a distributed artifact checked by `test_distribution.py`."* First, `SKILL/tests/test_distribution.py` only compares `SKILL/` against `.agents/skills/ux-review/` inside Lugos; it does not compare against the installed `ux_recast.rubric` package unless a new cross-package test is added. Second, `S1.2` asserts that `rubric_sha256` in `ux-recast` equals the Lugos file's hash, but `S4.4` (and later `S8.3`) modifies `rubric/autowork-reviewer.md` and bumps the rubric version. Once `S4.4` changes the prompt, either Lugos's two mirrored copies must be manually updated and re-pinned in lockstep, or `UX_REVIEW_IMPL=legacy` (reading `SKILL/references/`) will produce a different `rubric_sha256` and `task_sha256` than the default shim (reading `ux_recast.rubric`), breaking `S3.7` rollback parity.

## 3. Package Boundary (§2.1) and Provider Protocol (§3 Phase 4)

- **[high] `impeccable_detect` is a static/rendered linter, not a review dispatch `Provider` (`initial-implementation-plan.md` §2.1, §3 Phase 4; `implementation-slices.md` S4.2)**: `providers/lugos_autowork` and `providers/local_agent` implement a 5-step packet dispatch protocol (`prepare`, `claim`, `submit`, `record`, `consume`) that sends a task + rubric + evidence to an agent and records structured findings. By contrast, `npx impeccable detect --json` (`reuse-and-license-map.md`: *"gives machine-readable findings with exit code 2 on findings"*) is a deterministic CLI linter that does not consume `packet.json`, `rubric.md`, `claim`, or `consume`. Modeling `impeccable_detect` as a `Provider` forces a bogus abstraction where most protocol methods are no-ops and leaves ambiguous how `detect` runs *alongside* `lugos_autowork` or `local_agent` in the same checkpoint. It belongs in `evidence/` (or an audit pre-pass helper) that emits pre-populated `kind: implementation` findings or `observations[]`, leaving `Provider` strictly for review packet fulfillment (`local_agent` and `lugos_autowork`).
- **[high] Durable `.ux-recast/` records link to ephemeral gitignored `.ux-review/` artifacts (`initial-implementation-plan.md` §1.1, §2.2, §2.3, §4 D-03; `implementation-slices.md` S2.2, S2.4)**: §1.1 states `.ux-review/` is gitignored in Lugos (`.gitignore:96`), and D-03 keeps controller state and packets in `.ux-review/` while placing durable records in `.ux-recast/decisions.jsonl` and `.ux-recast/lessons/`. Yet §2.2 and Phase 2 state: *"Link every Decision to findings and a Revision; every Outcome to a run and its before/after evidence"* (`S2.4`). If committed records in `.ux-recast/` link by path or run ID to packets and screenshots stored only under gitignored `.ux-review/packets/`, every evidence link breaks on a clean checkout or another host. Also, D-03 does not specify whether standalone projects (Phase 1/8) use `.ux-review/` or `.ux-recast/` for cycle state.
- **[medium] Unspecified execution model for `request_kind: documentation` (`initial-implementation-plan.md` §2.1, §2.2, §3 Phase 6; `concept-traceability.md` Q-01; `implementation-slices.md` S6.1–S6.6)**: §2.2 adds `request_kind: review | documentation` to Review request, and `Q-01` states *"documentation outputs are a separate request kind to the core... The Lugos skill gains one additional invocation for it."* However, `S6.1`–`S6.6` only build `contracts/documentation.py`, static Jinja/Markdown/HTML templates (`guide.md`, `sheet.html`), a validator (`variables.py`), and `evidence/measure.py`. Nothing in Phase 6 specifies how source files, `measure.py` outputs, and `DESIGN.md` are synthesized into the filled component SVG/HTML sheet and prose guide (i.e., whether `ux-recast document` prepares a documentation packet for `Provider` dispatch and validates the returned artifact via `variables.py`), nor is there any slice adding the documentation invocation to the Lugos skill.

## 4. Slice Sizes, Cuts, Merges, Reordering, and Missing Slices

### Dishonest Slice Sizes
- **`S2.1` (marked `M`)**: Losslessly parsing and round-tripping arbitrary Markdown headings/prose in Impeccable `PRODUCT.md` and `DESIGN.md` with stdlib-only Python is a time sink if treated as AST manipulation, or `S` if treated as read-only context ingestion plus write-template-only-when-absent (which is all §2.3 actually requires: *"written only when absent"*).
- **`S2.2` (marked `S`)**: Proving *"Two concurrent writers produce two intact lines"* on `.ux-recast/decisions.jsonl` across Windows and Linux requires cross-platform lockfile coordination (since Windows file semantics differ from POSIX `O_APPEND`); it is only `S` if it directly reuses `cycle/`'s `.lock` context manager.
- **`S5.5` (marked `L`)**: Bundling all Dias host-ops UI repairs across three inline-styled Python HTML templates and a 686-line `app.js`—including net-new mobile keyboard/viewport handling, 375px overflow fixes for 8-question forms and JSON payloads, and potentially approval resumption receipts (`B-05` vs. Phase 5 table row 4)—into a single slice understates the scope.
- **`S6.5` + `S6.6` (marked `M` and `L`)**: Measuring live DOM box-model relationships in Playwright and producing a traceable HTML+SVG dimensional specification sheet for `sessions-card` with validated variable formulas is the most complex greenfield work in the plan.

### Slices to Reorder
1. **Execute `S3.0` first (before Phase 1)**: Fix the one-line `ensure_ascii=False` Windows bug in Lugos `autowork_review.py:379` immediately so the 61-test baseline passes natively on Windows before extracting code.
2. **Move `S4.1` (port `lugos_autowork`) and `S4.3` (five-finding cap) before `S3.1`–`S3.7`**: `ux-recast` must contain `providers/lugos_autowork.py` and pass the 25 packet-helper tests before tagging `v0.1.0` (`S3.1`) and shimming `autowork_review.py` (`S3.3`).

### Slices to Cut or Merge
- **Merge `S0.1`–`S0.4` into one foundation slice**: `S0.1` is already done; `pyproject.toml`, smoke test, CI workflow, and seeding the 12 decision files from §4 belong in a single bootstrap commit.
- **Merge `S1.2` and `S4.4`**: Add the capability pass names (`critique`, `adapt`, `harden`, `polish`) to `autowork-reviewer.md` once when establishing the versioned rubric in `ux-recast`, or explicitly defer prompt edits until after Phase 3 parity testing so `rubric_sha256` does not shift mid-migration.
- **Merge `S2.1` into `S2.2`/`S2.3` and drop Markdown round-trip mutation**: Read `PRODUCT.md`/`DESIGN.md` as plain text context and write starter templates only when absent (`O_CREAT | O_EXCL`).
- **Move `S4.2` (`impeccable_detect`) out of `providers/` and defer past Phase 5 (or re-scope as an `evidence/` helper)**: Neither Phase 3 migration nor the Phase 5 Dias pilot depends on `npx impeccable detect`.

### Missing Slices
1. **Wheel / non-editable package-data verification slice (Phase 0/1)**: Verify `pip install .` (non-editable wheel) in a clean venv includes `rubric/`, `schemas/`, and `docs/templates/` via `importlib.resources` before `S3.1` pins a git tag.
2. **Evidence promotion / archival slice (Phase 2)**: Copy or snapshot accepted packet evidence (`packet.json`, before/after screenshots, `receipt.json`) from ephemeral `.ux-review/packets/` into a tracked path when recording a `Decision` or `Lesson` (`S2.2`–`S2.4`).
3. **Documentation packet dispatch + Lugos skill entrypoint slice (Phase 6)**: Connect `ux-recast document` (`S6.1`) and `measure.py` (`S6.5`) to the provider workflow that populates `guide.md`/`sheet.html` before `variables.py` (`S6.4`) validates it, and add the Lugos skill invocation promised in `Q-01`.

## 5. What Could Not Be Assessed From the Captured Material Alone

- Which specific symbols `lugos/scripts/coordination_trials.py:78-140`, `SKILL/tests/test_control.py`, and `SKILL/tests/test_submit.py` import directly from `control.py` and `autowork_review.py` versus invoking via CLI subprocesses.
- How `control.py` and `autowork_review.py` currently resolve `SKILL/references/` paths and implement `.lock` files on Windows.
- Whether `autowork/src/autowork/campaign/dispatch_contract.py` uses `extra="forbid"` on `DispatchRequest`, which determines what fails if any new fields leak into the `lugos.models delegate` payload.
- The nature of the uncommitted edits and version drift (`20261031-4` vs `20261031.5`) in the `dias-mobile` / `lugos-host-ops` checkout (`B-03`). <<implementer/>>


## REGION: tester

[seq 3 | round 1 | phase concerns] # Tester concerns, round 1

Role: tester. For each phase I cover how its acceptance would actually be verified, what that proof leaves out, and which edge cases are missing. I could not read the test bodies, `coordination_trials.py`, the fixture server or the Playwright config, so every finding below rests only on the captured plan text. Section or slice ids are quoted for each finding. I am not proposing that implementation start.

## Phase 3: is 61 tests on 2 implementations x 2 platforms plus 1 live submit enough to call the migration safe? No.

- [critical] **The tests can only check what they already assert.** Plan 3 Stage A promises 'argv, stdout JSON, exit codes, file paths and `schema_version: 1`' unchanged. The 61 tests were written for the legacy code, and nothing captured shows they assert byte-level stdout, key order, every error-path exit code, or the exact files left on disk. The missing proof is a differential test: a frozen corpus of argv/stdin cases, including malformed contracts, an out-of-scope flow, a double claim, a stale consume and an over-cap result. Each case runs under `legacy` and under the shim in fresh project copies, and the run diffs stdout bytes, the exit code, and the resulting `.ux-review/` tree. Green unit tests are a weaker claim than that.
- [high] **The shim has to keep the Python API too, not just the CLI.** Reuse map: '`scripts/coordination_trials.py:78-140` imports both scripts'. An importing caller depends on module-level names and signatures, not argv. S3.4 says only 'runs clean', with no pass criterion. The same applies to the MyDocs forwarder, a '15-line `control.py` importing the canonical one by relative path' and marked out of scope. If the shim's `ux_recast` import resolves differently from that path, it breaks there. S3.4 needs both callers exercised with a stated expected output.
- [high] **The test counts don't reconcile.** S3.2 says '27 controller tests', S3.3 says '25 prepare, claim, submit, record and consume tests', and the reuse map says 'the 27 controller tests and 15 Autowork tests are the regression contract'. Facts give 51+10 = 61, and the seven demo tests need `DEMO_EVIDENCE_DIR`. Nobody can tell whether 61 includes the demo or `test_distribution`. Acceptance should name the test ids, not a count.
- [high] **The live submit is n=1 and attributes nothing.** S3.5 runs after S3.3, so a failure on the shim cannot be separated from a defect in a `submit` that has never run live (B-04). The first live submit should happen on legacy right after S3.0 as a baseline, then be repeated on the shim. It is also text-only, while Phase 5 depends on the image path ('image review is now permitted'). That leaves untested: an image submit, a rejection or timeout (`timeout_seconds:300`), a `task_sha256` mismatch, and a retry after the single-use claim has been spent.
- [high] **The rollback drill runs in one direction only, and 'no state or packet format changed' will not stay true.** S3.7 covers shim to legacy only. Untested: legacy to shim, and a crossover while `dispatch.lock` is held. Plan 2.4 and S4.3 then add a `deferred` finding status and a dispatch count. Nothing tests whether the legacy code tolerates unknown keys or an unknown status, which it would have to for rollback after Phase 4.
- [high] **The shim's behaviour when `ux_recast` is absent is undefined.** The `.agents/skills/` mirror is consumed by other agents' environments, and `requirements-ux-review.txt` may not be installed in all of them. Is an ImportError fail-closed with a message, or a silent fall back to legacy? Write that down and test it. The `UX_REVIEW_IMPL` setting also has to reach the MCP server child that `submit` starts. If two shells disagree on it, one session's state is driven by two implementations.
- [high] **The platform matrix is overstated.** Acceptance says 'both platforms', but S0.3 CI is `ubuntu-latest` on 3.11/3.13 only, and the Lugos CI is self-hosted Linux. The Windows result is therefore a manual run with no named recorder or artifact, and on 3.14.3, outside the CI range. The reuse map says 'Not tested: macOS', yet two of the four hosts are Macs. The Windows run needs a recorded artifact naming the Python version. macOS should be either covered or explicitly excluded.
- [high] **CRLF will break the hash checks.** S1.2's proof is '`rubric_sha256` of the relocated file equals the Lugos file's', and the mirror test is byte-identical. With git autocrlf on the Windows hosts, `rubric.md` and the shims can differ in bytes between hosts. That would change `rubric_sha256` inside packets and could break `test_distribution`. No `.gitattributes` step appears in either repo's plan.
- [medium] **The encoding fix changes stdout bytes.** S3.0 switches to `ensure_ascii=True`, so 'stdout JSON unchanged' only holds relative to the post-S3.0 baseline. Verify the 64 KiB evidence cap is not measured on re-serialized ASCII-escaped JSON: non-ASCII expands to `\uXXXX`, which could push previously valid evidence over the cap.

## Phase 5: what the reduced-viewport keyboard row fails to prove

- [critical] **A reduced viewport simulates the wrong mechanism.** iOS WebKit keeps the layout viewport when the keyboard opens and shrinks the visual viewport. Android Chrome's default since 108 also resizes only the visual viewport. Shrinking the Playwright viewport shrinks both together, so:
  - a repair using `dvh` or `100vh` passes the test but can fail on the phone;
  - a repair using `visualViewport` is never exercised;
  - fixed-position bars, scroll-into-view of the focused field, iOS auto-zoom on inputs under 16px, the accessory bar, safe-area insets and installed-PWA standalone mode are all outside what it can see.
  
  If the existing harness at 390x844 with `isMobile` runs on Chromium, it is not testing the user's WebKit engine at all (B-02 says iOS, model unrecorded). At minimum, add the WebKit project.
- [critical] **The real-device check is optional, has no target, and has no baseline.** Acceptance says a real-device observation is 'requested', not obtained, so Phase 5 can close without one. Only the after state is mentioned, so no keyboard improvement can be claimed. The plan also forbids the production host while the fixture runs on `--port 8879` locally, so the phone has no sanctioned page to open. The minimum observation, done before and after:
  - the user's phone, with model and OS version recorded, as the installed PWA (plus a Safari tab if cheap), loading a fixture reachable on the LAN;
  - focus the last field of the 8-question form, then the composer;
  - capture a screenshot or recording with the keyboard open showing the Send button and the active field;
  - note whether the page zooms on focus, and whether the layout recovers when the keyboard is dismissed.
- [high] **The five-screenshot cap conflicts with 'before and after evidence for every row'.** That is 8 rows x 2 viewports (S5.3), and S5.4 is 'one review pass with images' under 'at most five' screenshots and a 64 KiB evidence cap. The cap is per packet, so evidence includes 4096-character drafts and 1024-unit outputs. The plan doesn't say which five images the reviewer sees, or whether the three flows (S5.2) mean three runs against a `review_passes:1` budget. Rows the reviewer never saw were not reviewed.
- [high] **The comparison is graded by its author.** 'Taps and scroll count recorded' come from scripts written by the same agent that writes the repair. The before scripts and acceptance thresholds should be frozen and hashed before S5.5, then rerun unchanged afterwards. 'No duplicate send' should be checked against the fixture server's received-message count, not against the UI.
- [high] **The repair touches pages with no browser coverage.** Plan 1.2 says 'the approval page has no browser test' and 'the question page has a browser script with no pytest calling it'. S5.5 edits `approval_http.py` and `input_page.py`, and 'existing host-ops tests still pass' leaves those regressions invisible. Add coverage before the repair. Also, the browser suite runs only with `DIAS_MOBILE_BROWSER_TESTS=1`, so acceptance must require that flag explicitly.
- [medium] **Fixture-vs-production gaps aren't listed.** Not covered:
  - a real push notification tap opening the PWA (the 'deep link' row navigates by URL);
  - Cloudflare Access 401 and redirect behaviour;
  - the service worker serving a cached `app.js`, which would make before and after the same code. Record the build id in each proof, given the B-03 mismatch.
  - the 4096/4097 boundary, emoji and multibyte input;
  - enlarged text or 200% zoom (C-45);
  - the light-themed approval page under dark mode;
  - a screen reader actually announcing the `aria-live` region.
- [medium] **Approvals are dropped silently.** The 'Submission versus receipt versus resumption' row covers composer receipts only, and approvals end at 'Decision recorded.' (B-05). The row should state that the approval flow is excluded so the comparison doesn't imply it was covered.
- [medium] **Rejection doesn't stop cleanup.** Stage C removes legacy 'after the Dias pilot (Phase 5) has completed one cycle'. A user reject still completes a cycle, so legacy would be removed after a failed pilot. Gate S3.8 on an accepted Decision plus a passing rollback drill.

## Phase 6: is 'a second agent traces every value' a real test? As written, mostly theater.

- [high] **The tracer reads provenance the author wrote,** so it is circular, and its pass/fail sensitivity is unknown. Make most of it mechanical:
  - `css-literal` values re-read at the recorded file:line and revision;
  - `rendered` values re-measured with `measure.py` at the same revision, viewport, DPR and browser version, within a stated tolerance;
  - formulas recomputed.
  
  Keep the agent for the remainder, and test its sensitivity by seeding N mutated values or pointers that it must catch. It should be from a different model family and blind to the author's notes.
- [medium] **'Rendered' isn't precise enough.** Record CSS px vs device px, DPR, browser engine and version, and font availability; Windows and Linux font fallback changes heights. Without these, re-measurement on another host diverges and 'traceable' cannot be checked.
- [medium] **The validator is under-specified.** 'Unlabeled numeric value' needs a test corpus covering `0`, unitless line-height, hex colours, z-index, percentages and values inside SVG attributes. A sheet that is mostly `[TBD]` passes trivially, so report the `[TBD]` ratio. 'The product palette is untouched' should be shown as an empty host-ops diff for Phase 6.

## Phases 0, 1, 2, 4, 7 and 8

- [high] **Phase 1 tests plumbing, not review.** 'Repair (apply the known fix)' swaps in a predetermined `index.html`, so 'seven passing acceptance checks' would pass whatever the review found. Also:
  - S1.6's `sys.modules` assertion misses subprocess calls and file reads of `SKILL/` paths. Run it with no Lugos checkout on disk at all.
  - A 'clean venv with only `playwright`' also needs browser binaries (`playwright install`, which uses the network). That is an unstated precondition.
  - If `test_control.py` shells out to the script path, 'only the import line changed' cannot be true.
- [medium] **S1.3 validates against one historical packet** that has no `submit_*` fields (fact 3), so the schema is unproven for submit records. Add a live S3.5 packet to the corpus.
- [medium] **S2.2's 'two concurrent writers produce two intact lines' is a one-shot race.** Run many iterations on Windows and POSIX, with lines above 4 KiB. Windows append and lock semantics differ, and `os.replace` fails while a reader holds the file open. A lock left behind by a killed process (`.lock`, `dispatch.lock`) needs a recovery test.
- [medium] **The promotion rule is spoofable.** It depends on 'a second project', and project identity is undefined: a copy at a new path, or the fixture itself, could count. Test the 'explicit user instruction' bypass and confirm a refusal is logged.
- [high] **S4.2 can install software.** `npx impeccable detect` downloads the package when it is missing, which contradicts 'nothing is installed by ux-recast'. Use `--no-install` or a PATH check. Also test that exit code 2 means findings rather than failure (as the reuse map says) and that other codes mean error. Rendered rules need Chrome or Edge, so 'unavailable' must cover that case too.
- [medium] **The S4.3 five-finding cap has no ordering rule.** It doesn't say which five stay actionable (severity? input order?), so the test cannot be deterministic.
- [medium] **Image-policy regression isn't guarded.** Phase 5 depends on `assignment-policy.toml:171-174` in another repo. Add a preflight or contract test that an image packet is accepted, and define what happens when images are rejected: fail, or fall back to text-only and say so.
- [low] **S7.2 'plays' needs an operator.** Replace it with an `ffprobe` duration and frame count check, plus a non-zero ffmpeg exit failing the export.
- [medium] **S8.3 proves inclusion, not improvement.** It shows the lesson text appears in the next packet, not that it changes reviewer behaviour or outcomes. Without even a crude before/after check on the same input, the self-improvement claim (C-02) is unverified.

## Missing edge cases (cross-cutting)

- **Windows paths:**
  - MAX_PATH in deep worktrees;
  - session ids containing `:` or other characters invalid in `<session>-<run>` directory names;
  - the case-insensitive, drive-letter, junction and `..` forms of the 'inside the workspace' screenshot check;
  - backslash paths stored in packets and then read on a Mac.
- **Encoding:** `open()` without `encoding=` defaults to cp1252; the `--request -` stdin pipe.
- **Concurrency:** two sessions on one project; the same session from two processes; a claim race.
- **Stale packets:** prepared at revision A, recorded after the repair; a legacy packet consumed by the shim.
- **Evidence caps:** 65536 vs 65537 bytes (UTF-8 bytes or characters?); 5 vs 6 screenshots, duplicates, uppercase `.PNG`, a symlink escaping the workspace, and image byte size, for which no cap is stated.

## What I could not assess

- whether the tests import modules or shell out;
- what `coordination_trials.py` asserts;
- the exact 61-test inventory;
- the fixture's receipt-progression controls;
- which browser engine the host-ops harness uses;
- how Autowork rejects or times out a `submit`. <<tester/>>
