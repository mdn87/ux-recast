# Initial implementation plan

Status: planning deliverable, prepared 2026-11-02 from [the concept record](../CONCEPT.md), [KICKOFF.md](../../KICKOFF.md), and two read-only inspections run the same day (Lugos `ux-review`; the Dias phone client). Companion documents: [concept traceability](concept-traceability.md), [reuse and license map](reuse-and-license-map.md), [implementation slices](implementation-slices.md). This plan authorizes nothing; implementation starts on a separate explicit instruction (AGENTS.md).

Evidence tags: **[code]** observed in source, **[doc]** claimed in documentation, **[run]** verified by recorded run evidence, **[new]** established by the 2026-11-02 inspections. Paths under `lugos/` are relative to `C:\Users\Matt\Desktop\MyDocs\lugos`; the skill root `plugins/lugos-toolset/skills/ux-review/` is abbreviated `SKILL/`.

## 1. What exists today

### 1.1 The Lugos `ux-review` capability

- **Canonical location** `SKILL/`, discovered through `plugins/lugos-toolset/.claude-plugin/plugin.json` (`"skills": "./skills/"`). A byte-identical runtime mirror lives at `.agents/skills/ux-review/` without `tests/`. The mirror is maintained by hand in every commit, and enforced by `SKILL/tests/test_distribution.py:9-16` plus CI `.github/workflows/ux-review.yml` on a self-hosted Linux runner. [code][new]
- **Two scripts, standard library only.** `SKILL/scripts/control.py` (305 lines) owns mode, scope, checkpoints, phases and budget. `SKILL/scripts/autowork_review.py` (387 lines) owns packet preparation, single-use claim, submission to Autowork through the `lugos.models delegate` MCP tool, result recording, and staleness consumption. [code]
- **State and packets** live in the reviewed project: `PROJECT/.ux-review/<sha256(session)[:24]>.json` with a sibling `.lock` (`control.py:76-80`), and `PROJECT/.ux-review/packets/<session>-<run>/{packet.json,dispatch.lock,autowork-result.json,receipt.json}` (`autowork_review.py:55-59,141-146`). `.ux-review/` is gitignored in Lugos (`.gitignore:96`). [code]
- **Task contract** fields: `flow`, `goal`, `starting_conditions`, `expected_outcome`, `device_input`, `source`, `assumptions[]`, non-empty `acceptance[]`, flow in scope (`control.py:107-117`). [code]
- **Budget** `{review_passes:1, repair_batches:1, verification_passes:1, max_actionable_findings:5}` hard-coded at `control.py:174-175`. The controller enforces one repair and one verify transition (`control.py:263`); the five-finding cap is a prompt instruction only. [code][new]
- **Evidence limits**: 64 KiB JSON; keys `observations`, `screenshots`, `coverage`, `plan` only; at most five png/jpg/jpeg/webp screenshots inside the workspace (`autowork_review.py:62-66,104-116`). [code]
- **Reviewer request** is `{action:"delegate", role:"explorer", task_class_hint:"review", required_capabilities:["repository_read"], input_modalities:["text"], timeout_seconds:300}` plus `image_input`, the `image` modality and `visual_inputs` when screenshots exist (`autowork_review.py:128-135`). The task string embeds `references/autowork-reviewer.md`, the activation, the original task, the full rubric and the evidence labelled untrusted (`:119-127`). [code]
- **Image review** is now allowed for task class `review` by `autowork/campaign/assignment-policy.toml:171-174` (commit `b70bedc9`). The 2026-10-26 Dias recovery run completed with `image_input` and was recorded accepted and applicable. [code][run][new] `docs/ux-review.md:87-90`, which says the profile rejects `image_input`, is stale. [doc][new]
- **`submit` via MCP** (commit `310e0a28`, 2026-10-28) has never run live; all recorded runs predate it and were dispatched by the parent. It is covered by `tests/test_submit.py` against a fixture server. [code][run][new] `docs/ux-review.md:49` ("the helper never launches children") is contradicted by `autowork_review.py:1-7`. [doc][new]
- **Tests** on Windows, Python 3.14.3: `51 passed, 10 errors`; all ten errors are `test_submit.py` fixtures failing on `'charmap' codec can't encode` because `autowork_review.py:379` prints with `ensure_ascii=False` to a cp1252 stdout. With `PYTHONIOENCODING=utf-8` those ten pass. The seven-test demo passes with `DEMO_EVIDENCE_DIR` set. `scripts/lugos_catalog.py --check` exits 0. [run][new]
- **Rubric** (`SKILL/references/rubric.md`): twelve finding fields (id, category, task step, observed behavior, evidence, principle, likely consequence, severity, confidence with reason, proposed correction, verification, status and remaining uncertainty); categories observed failure, heuristic concern, unresolved question; severity Critical to Low; confidence high, medium, low as evidence quality; eight principles; no personas or SUS scores. [code]
- **Other callers**: `scripts/coordination_trials.py:78-140` imports both scripts; `.github/workflows/coordination-evaluation.yml` triggers on the scripts path; `plugins/lugos-toolset/requirements-ux-review.txt` pins `mcp>=1.27,<2`; rule files reference the skill by name. No Lugos MCP server code references ux-review; the only dispatch path runs outward from the skill. [code][new]
- **Existing mechanisms to reuse rather than reinvent** (KICKOFF, AGENTS.md): Autowork `campaign feedback` and `outcome` (`autowork/src/autowork/campaign/cli.py:1043-1119`), `DispatchFeedback` (`dispatch_contract.py:1931`), `dispatch_outcome.py` acceptance projection, `review_store.py` append-only JSONL, `campaign/atomic_io.py`, `attempt_ledger.py`, and `src/lugos_audit/` receipts with schemas under `config/cormac/audit-*.schema.json`. [code][new]

### 1.2 The Dias phone client

- The phone UI is **not in the Dias repository**. Dias (`MyDocs/dias`, worktree `MyDocs/dias-mobile`) is the Windows .NET producer that pushes session snapshots every 15 s (`dotnet/Dias.Host/RemoteSessions.cs:65-74`) and a React 19 desk display. The phone client is the Lugos host-ops service `lugos/lugos-node/services/lugos-host-ops/`, served at `/sessions` behind Cloudflare Access and installed as a PWA. [code][doc][new]
- **Stack**: server-rendered HTML from Python string templates (`lugos_host_ops/remote_sessions.py:275-395`), one vanilla JS file (`mobile_static/app.js`, 686 lines), a service worker. No framework, no build step, no design tokens. Three phone pages (`/sessions`, `/input/<id>`, `/approve/<id>`) carry separate inline style blocks with different palettes; the approval page is light-themed (`remote_sessions.py:368-379`, `input_page.py:156-166`, `approval_http.py:211-216`). [code][new]
- **State contract** is `data-*` attributes on cards (`data-session-state`, `data-receipt`, `data-message-status`, and others; `remote_sessions.py:335-341`). [code][new]
- **Receipts** for composer messages already distinguish `recorded`, `queued`, `received`, `resumed`, `finished`, `failed`, `rejected`, `outcome-unknown` (`operator_messages.py:12-16`) and surface as a "Receipt:" line with an `aria-live` status (`app.js:394,552-556`). Native questions carry `consumed` plus a separate `continuation` fact (`input_page.py:12-42`). Approvals end at "Decision recorded." with no resumption receipt (`approval_http.py:206-207`). [code][new]
- **Keyboard, safe area and visual viewport handling are absent**: no `visualViewport`, `interactive-widget`, `env(safe-area-inset-*)`, `dvh` or `enterkeyhint` in the phone pages or `app.js`. [new]
- **Stale and reconnect handling exist**: refresh failure shows "Last known", disables messaging, keeps drafts; a 401 keeps the draft; unsettled sends are never auto-resent and offer retry or edit; vanished sessions keep their card when a draft exists; a snapshot older than 60 s turns presence unconfirmed (`app.js:45-51,297-337,404-433,566-614`; `remote_sessions.py:229-235`). [code][new]
- **Fixture and tests**: `tests/mobile_browser_fixture.py --port 8879` serves controllable scenarios (`idle-current`, `ended`, `unconfirmed`, `missing`, `question`, `offline`, receipts) with no provider or push contact; opt-in Playwright phone checks at 390×844 run with `DIAS_MOBILE_BROWSER_TESTS=1` and write screenshots and `*-proof.json` (`README.md:531-538`). The question page has a browser script with no pytest calling it; the approval page has no browser test. [code][new]
- **Prior review evidence**: one plan-only `ux-review` checkpoint on 2026-10-28 (run `fb089312d601`, findings ux-F1 to ux-F5, no screenshots). Planned checkpoints 2 (real page on the virtual phone) and 3 (question flow end to end) have not run (`DIAS-MOBILE-NEEDS-YOU-INBOX.md:407-425,933-948`). [run][doc][new]
- **Caveats**: the `dias-mobile` worktree is a detached HEAD with uncommitted edits; local `app.js` says build `mobile-navigation-20261031-4` while docs say `20261031.5` is deployed (`app.js:6`, `MOBILE-SNAPSHOTS.md:5-6`). [new]

## 2. Target architecture

### 2.1 Boundary

ux-recast is a Python 3.11+ package, `ux_recast`, with a standard-library core and optional extras. It owns contracts, the rubric, records, the review cycle, provider adapters, and the documentation outputs. Lugos `ux-review` remains the entry point, its two scripts becoming thin shims over the package. Dias keeps its own design context; the pilot's code changes land in Lugos host-ops.

```
ux_recast/
  contracts/     task, request, evidence, finding, revision, decision, outcome, lesson (dataclasses + JSON schema)
  rubric/        rubric.md (single source), principles, severity anchors, reviewer prompt
  records/       project context (PRODUCT.md, DESIGN.md compatibility), decisions.jsonl, lessons (project tier, shared tier)
  cycle/         review -> repair -> verify state machine, budget, checkpoint coalescing (ported from control.py)
  providers/     Provider protocol; lugos_autowork (ported prepare/claim/submit/record/consume); local_agent; impeccable_detect
  evidence/      capture manifest, screenshot limits, staleness; optional Playwright helper
  docs/          style guide, component sheets, variable tables, validators; motion (deferred)
  cli.py         ux-recast <command>, mirroring control.py and autowork_review.py verbs
fixtures/
  contact-request/   the existing seven-test demo, copied from SKILL/tests/demo with provenance
```

### 2.2 Contracts (KICKOFF item 2)

Every contract starts from what the Lugos scripts already write, so packet `schema_version` stays `1` through the migration. New fields are additive and optional.

| Contract | Starting point | Additions |
| --- | --- | --- |
| Task | `control.py:107-117` fields | none; `flow` scoping unchanged |
| Review request | `autowork_review.py:128-135` request, packet `activation` | `request_kind: review | documentation`; `provider`; `rubric_version` |
| Evidence | `autowork_review.py:62-66,104-116` limits | capture manifest per screenshot: `revision`, `viewport`, `state`, `theme`, `captured_at`; `observations[]` keep the demo's visible-text, input-value and focus shape |
| Finding | rubric fields (`rubric.md:30`) | `element` (selector or `data-*` reference), `kind: design | implementation` (concept C-08), `score` as signal only |
| Revision | none today | `files[]`, `diff_ref`, `before_evidence`, `after_evidence`, bound to a run |
| Decision | none today | `accepted | rejected`, `rationale`, `by: user | parent | reviewer`, links to findings and revision |
| Outcome | receipt `meaning` (`autowork_review.py:304-310`) | `observed` measures from the acceptance list, `verified_by`, `remaining[]` |
| Lesson | none today | `tier: project | shared`, `supported_by[]` outcomes or decisions, `promoted_at`, `scope` |

### 2.3 Separation of project context from shared guidance (KICKOFF item 3)

- Project tier: `PRODUCT.md`, `DESIGN.md` (Impeccable-compatible, written only when absent), `.ux-recast/decisions.jsonl`, `.ux-recast/lessons/project/*.md`, generated guides and sheets committed in the target repository.
- Shared tier: the rubric and `lessons/shared/*.md` inside ux-recast. Promotion from project to shared requires a lesson with at least one `supported_by` outcome or user decision from a second project, or an explicit user instruction. A reviewer's own score never qualifies (concept C-22, C-53).
- Precedence: approved project guidance over any reference; shared rubric over reviewer preference; a documentation output records its `basis` as `observed`, `accepted` or `proposed` (concept C-38).

### 2.4 Optional controls and bounded cycles (KICKOFF item 4)

The `cycle` module is a port of `control.py` with the same state file, schema, budget and transitions, so the existing 27 controller tests run unchanged against it. Two gaps become enforced: the five-finding cap is applied when recording a result (overflow findings are kept but marked `deferred`), and a run records how many review dispatches it consumed. Lugos mode semantics (`off`, `once`, `session`, scope, shared-component mapping, per-session state) are untouched. Documentation outputs are a separate `request_kind`, invoked directly and never gated on review mode (concept C-35).

## 3. Phases

Dependencies run top to bottom unless stated. Each phase lists acceptance criteria that an agent can observe. Slices with sizes are in [implementation slices](implementation-slices.md).

### Phase 0: Repository foundations

Outcome: a buildable, testable, licensed package skeleton.

- License chosen (decision D-01, Apache-2.0); `LICENSE` and `NOTICE` are committed.
- `pyproject.toml` for `ux_recast`, Python 3.11+, no runtime dependencies; extras `playwright`, `mcp`.
- CI on GitHub-hosted `ubuntu-latest` (public repository, no billing; the private-repository self-hosted rule does not apply), running pytest and a docs link check.
- `docs/decisions/` for the decision log; this plan's log seeds it.

Acceptance: `python -m pytest` passes an empty suite in CI; `pip install -e .` works on Windows and Linux.

### Phase 1: Standalone core and the independence fixture (KICKOFF items 1, 2, 8)

Outcome: contracts, rubric and cycle exist in ux-recast and a review runs end to end with no Lugos, Autowork or Dias present.

- Port `control.py` into `cycle/` behind the same CLI verbs; copy `SKILL/tests/test_control.py` and make it pass against `ux-recast` unchanged except the import.
- Move `rubric.md` and `autowork-reviewer.md` into `rubric/` as the single source; version them.
- Define contracts as dataclasses with JSON schema export; validate the existing `packet.json` and state files from `.lugos-audit/ux-review-promotion-20261024/` against them.
- `providers/local_agent`: writes the reviewer packet to disk and reads a findings file back, so a standalone coding agent can be the reviewer.
- Copy the contact-request demo (`SKILL/tests/demo/`, locally authored, seven Playwright tests) into `fixtures/contact-request/` with its report as provenance. Run one full cycle on it through `local_agent`: checkpoint, review, repair (apply the known fix), verify.

Acceptance: `ux-recast checkpoint ... && ux-recast review ... && ux-recast verify ...` completes on the fixture in a clean virtual environment with only `playwright` installed; the recorded outcome lists seven passing acceptance checks; the controller tests pass.

### Phase 2: Project design context and retained knowledge (KICKOFF item 3)

Outcome: decisions, outcomes and lessons are durable and tiered.

- `records/`: `PRODUCT.md` and `DESIGN.md` readers and writers compatible with Impeccable's files; `decisions.jsonl` append-only (same discipline as Lugos `review_store.py`); lessons in two tiers with the promotion rule.
- Link every Decision to findings and a Revision; every Outcome to a run and its before/after evidence.
- A `ux-recast lessons promote` command that refuses without `supported_by` evidence and prints why.

Acceptance: the Phase 1 fixture run yields one project-tier lesson ("preserve entered values on validation failure") whose record links the finding, the diff, the before and after screenshots and the passing test; promotion to shared is refused until a second project's outcome exists.

### Phase 3: Lugos entry point and staged migration (KICKOFF items 1, 6)

Outcome: Lugos `ux-review` runs on ux-recast with callers, tests and packet formats unchanged, and can fall back.

Stage A, dependency and shim:

- Add `ux-recast` pinned by tag to `plugins/lugos-toolset/requirements-ux-review.txt`.
- Replace the bodies of `control.py` and `autowork_review.py` with shims that call `ux_recast.cli`, keeping argv, stdout JSON, exit codes, file paths and `schema_version: 1`. A `UX_REVIEW_IMPL=legacy` environment variable selects the retained legacy modules for one release.
- Fix the Windows encoding defect in the shim's output path by matching the MCP adapter (`ensure_ascii=True`, `autowork_adapter.py:254-257`).
- Keep the `.agents/skills/ux-review/` mirror; extend `test_distribution.py` to assert the mirrored shims match.

Stage B, verification:

- Run the full `SKILL/tests` suite on Windows and on the Linux CI runner with both `UX_REVIEW_IMPL` values; all 61 tests pass under both (today 51 pass and 10 error on Windows).
- Replay `scripts/coordination_trials.py` against the shim.
- One live `submit` through the real `lugos.models delegate` tool on a text-only packet, recorded as run evidence, since no live submit exists today.

Stage C, cleanup: remove the legacy modules only after the Dias pilot (Phase 5) has completed one cycle on the shim.

Recovery: at any stage, set `UX_REVIEW_IMPL=legacy` or pin the previous `lugos-toolset` commit; no state or packet format changed, so recorded runs remain readable either way.

Also in this phase: correct `docs/ux-review.md:49` and `:87-90`.

Acceptance: the 61 Lugos tests pass on both implementations on both platforms; one live submit receipt with `accepted: true`; `lugos_catalog.py --check` exits 0; a recorded rollback drill.

### Phase 4: Review, repair and verify cycle with provider adapters (KICKOFF item 4)

Outcome: the same cycle runs through Autowork from Lugos and through a local agent elsewhere, with Impeccable as an optional audit source.

- `providers/lugos_autowork`: the ported `prepare`, `claim`, `submit`, `record`, `consume` behind the Provider protocol, including the `image_input` declaration rules (`dispatch_contract.py:1076-1084`).
- `providers/impeccable_detect`: runs `npx impeccable detect --json` on a directory or URL when the tool is installed and maps rule hits to `kind: implementation` findings with `confidence: high` and the rule id as evidence. Absent tool, the provider reports `unavailable`; nothing is installed by ux-recast.
- The reviewer prompt gains the concept's capability vocabulary (`critique`, `adapt`, `harden`, `polish`) as pass names, not as new commands.
- Enforce the five-finding cap on record.

Acceptance: the fixture cycle passes through `local_agent`; a Lugos checkpoint on the fixture passes through `lugos_autowork` with a recorded receipt; with Impeccable installed, `detect` findings appear with provenance; without it, the run records `impeccable: unavailable` and still completes.

### Phase 5: Dias mobile pilot (KICKOFF item 7)

Outcome: the unrun Dias checkpoints 2 and 3 complete on ux-recast, with a before/after the user accepts or rejects.

Setup:

- Pin a committed `lugos-host-ops` revision; record it in the task. Resolve the `dias-mobile` worktree state first (blocker B-03).
- Serve `tests/mobile_browser_fixture.py --port 8879`. Never the production host.
- Reuse the existing Playwright harness (390×844, `isMobile`, `hasTouch`) and add 375×812.
- Write `PRODUCT.md` and `DESIGN.md` for the phone client with `basis: observed`, recording the three inline palettes as literals with provenance.

Task contract (concept C-19 to C-21), one flow per checkpoint:

| Step | Scenario on the fixture | Observable acceptance |
| --- | --- | --- |
| Find the blocked session | notification deep link `/sessions?host=&run=`; list sorted approvals first | target card opened and scrolled into view once; gone-target message shown when `missing` |
| Understand the full request | `question` scenario with an 8-question, long-legend form; an approval with long pretty-printed JSON | no horizontal overflow at 375 px; full legend readable without truncation; taps and scroll count recorded |
| Respond to the correct session | composer send with stale `expectedGeneration` | 409 "binding generation changed" surfaced, draft kept |
| Submission versus receipt versus resumption | receipt scenarios `recorded` through `resumed` | "Receipt:" line and `aria-live` text change per state; `finished` reached |
| Long content | 4096-character draft; 1024-unit output | wrap, no clipping, Send reachable |
| Keyboard obstruction | reduced-height viewport approximating an open keyboard | Send button and the active field remain reachable; measured, since the client has no viewport handling today |
| Stale state | `unconfirmed` and `ended` scenarios | "Last known" shown, messaging disabled, draft kept |
| Reconnect | `offline` then online | refresh on `online` event, no duplicate send, unsettled send offered for retry |

Cycle: one review pass with screenshots through `lugos_autowork` (image review is now permitted), one repair batch in host-ops limited to the affected pages, one verification pass against the same contract. Dias-specific decisions go to `dias-mobile/docs` and the phone client's `DESIGN.md`; reusable lessons stay project-tier until Phase 8.

Acceptance: before and after evidence for every row; the comparison on taps and scrolling, request completeness, action clarity and receipt confidence; the user's accept or reject recorded as a Decision; existing host-ops tests still pass; a real-device keyboard observation requested from the user as the one check automation cannot make (blocker B-02).

### Phase 6: Style guide and component specification sheets (KICKOFF item 5)

Outcome: a Dias phone-client style guide and at least one component sheet with traceable values.

- `docs/` request contract with three independent flags `guide`, `sheets`, `motion` and a `basis` field.
- Guide template: the concept's section list (C-36), every section optional, no default palette.
- Sheet template adapted from Dimensional Drawing's format with license header and pinned commit; variable table schema `{name, value | [TBD], unit, source: token | css-literal | rendered | accepted | proposed, state, viewport, formula?}`; validator rejects an unlabeled numeric value.
- Inputs: source files, rendered measurements from Playwright on the fixture, `DESIGN.md`, decisions. Staleness check against the recorded revision.
- First outputs: the sessions card at `needs-approval` and `waiting` states at 390 px; the guide's "content behavior" section mandatory because the card uses slots.

Acceptance: a second agent traces every non-`[TBD]` value on the card sheet to source or a rendered measurement without the author's help; the guide states `basis: observed`; the product palette is untouched; the user accepts the sheet as useful (entry criterion for Phase 7).

### Phase 7: Animated specification presentation (deferred until gated)

Entry criteria: Phase 6 acceptance; one real export with Chromium on a supported environment; the two renderer defects fixed locally or upstream (`render.mjs:93` exit code, video-branch `mkdirSync`). Output uses the sheet's geometry and variables; the static sheet remains the deliverable.

### Phase 8: Second-project validation of the learning loop

Outcome: proof that the core and the lessons transfer without Lugos or Dias.

- Run the full cycle on a second small project (candidate: a PADL screen or a work-portal form, chosen by the user) through `local_agent`.
- Promote one lesson from project tier to shared tier with two supporting outcomes; show it changes the reviewer prompt on the next run.

Acceptance: the second project's run records a Decision and an Outcome; the promoted lesson appears in the next review packet's rubric section with its `supported_by` links.

## 4. Decision log

| Id | Decision | Reason | Reversibility |
| --- | --- | --- | --- |
| D-01 | **License: Apache-2.0.** Confirmed by the user 2026-11-02; `LICENSE` and `NOTICE` committed. | Rubric fragments may be adapted from Impeccable (Apache-2.0); same-license redistribution is simplest; the explicit patent grant; MIT references compose freely. | Easy before first external contribution. |
| D-02 | Python 3.11+, standard-library core, optional extras. | Matches `control.py` and `autowork_review.py` (stdlib only, 3.11+ in `docs/ux-review.md`), so the port is a move, not a rewrite. | Moderate. |
| D-03 | Lugos controller state stays in `.ux-review/` with `schema_version: 1`; ux-recast records go to `PRODUCT.md`, `DESIGN.md` and `.ux-recast/`. | Preserves callers and recorded runs; avoids a second authority for product and design context (concept C-50). | Easy until Phase 3 Stage C. |
| D-04 | The rubric moves into ux-recast; the Lugos copy becomes a distributed artifact checked by `test_distribution.py`. | One source of truth; the mirror discipline already exists. | Easy. |
| D-05 | Review dispatch is provider-pluggable; the Lugos Autowork provider is a port, byte-compatible on packets. | Standalone use (concept C-28) without breaking Lugos. | Moderate. |
| D-06 | The Dias pilot runs on `mobile_browser_fixture.py`, and repairs land in Lugos host-ops. | The phone client lives there; production sits behind Cloudflare Access on a live host. | n/a |
| D-07 | Documentation outputs are a separate `request_kind`, not a review-packet field. | Keeps review mode semantics untouched (concept C-35). | Easy. |
| D-08 | Motion deferred behind a verified export. | Both renderer defects still present at `5c457437c8c8`; no export has run anywhere. | n/a |
| D-09 | A reviewer score is a signal field; acceptance is a user Decision or an observed Outcome. | Concept C-22, C-53. | n/a |
| D-10 | ux-recast CI on GitHub-hosted Linux. | Public repository, free; the self-hosted rule covers private repositories. | Easy. |
| D-11 | Impeccable consumed as `detect --json` and record-file compatibility only; no hook, no vendoring. | AGENTS.md overlap rule; Lugos review already defaults off. | Easy. |
| D-12 | React Grab not applicable to the pilot. | No React tree in the phone client. | Revisit per project. |

## 5. Unresolved decisions and blockers

| Id | Item | Owner | Effect |
| --- | --- | --- | --- |
| B-01 | License choice (D-01). | User | Resolved 2026-11-02: Apache-2.0. |
| B-02 | Real-device keyboard behavior on the user's phone; model and iOS version are unrecorded (`DIAS-MOBILE-NEEDS-YOU-INBOX.md:910-911`). | User observation | Phase 5 keyboard row is approximated by viewport height until observed. |
| B-03 | `dias-mobile` worktree is a detached HEAD with uncommitted edits, and local `app.js` build id differs from the documented deployed build. | User or a Dias session | Must be committed or discarded before any host-ops change lands. Not touched by this plan. |
| B-04 | `submit` through the real `lugos.models` tool has never run live. | Phase 3 Stage B | First live submit is a planned acceptance step, not an assumption. |
| B-05 | Approvals have no resumption receipt (`approval_http.py:206-207`). | Dias and host-ops product decision | A likely pilot finding; closing it is host-ops work outside ux-recast. |
| B-06 | Knowledge-base distribution rights. | User | Blocks copying method pages; the fixture is sourced from `SKILL/tests/demo` instead, which removes the question for Phase 1. |
| B-07 | Whether to fix the `autowork_review.py:379` encoding defect upstream before the shim lands. | Lugos maintainer | Small; proposed as the first slice of Phase 3 so the test baseline is green on Windows. |
| B-08 | Second project for Phase 8. | User | Blocks Phase 8 scheduling only. |

## 6. Reading list before implementation

- Lugos: `SKILL/SKILL.md`, `references/workflow.md`, `references/rubric.md`, `references/autowork-reviewer.md`, `scripts/control.py`, `scripts/autowork_review.py`, `tests/`, `docs/ux-review.md`, `.github/workflows/ux-review.yml`, `autowork/campaign/assignment-policy.toml:171-174`, `lugos-mcp/src/lugos_mcp/adapters/autowork_adapter.py:516-636`.
- Dias phone client: `lugos/lugos-node/services/lugos-host-ops/lugos_host_ops/{remote_sessions.py,input_page.py,approval_http.py,operator_messages.py,attention_server.py}`, `mobile_static/app.js`, `tests/mobile_browser_fixture.py`, `tests/test_mobile_current_ui.py`, `dias-mobile/docs/{MOBILE-SNAPSHOTS.md,DIAS-MOBILE-NEEDS-YOU-INBOX.md}`, `dias-mobile/docs/evidence/ux-review-needs-you-item-2026-10-28/`.
- References at the pinned revisions in the reuse map.
