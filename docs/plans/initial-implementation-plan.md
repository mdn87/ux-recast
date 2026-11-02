# Initial implementation plan

Status: planning deliverable, prepared 2026-11-02 from [the concept record](../CONCEPT.md), [KICKOFF.md](../../KICKOFF.md), and two read-only inspections run the same day (Lugos `ux-review`; the Dias phone client). Amended the same day after a three-amigos roundtable review (section 7 and [the evidence record](../evidence/plan-roundtable-2026-11-02.md)). Companion documents: [concept traceability](concept-traceability.md), [reuse and license map](reuse-and-license-map.md), [implementation slices](implementation-slices.md). This plan authorizes nothing; implementation starts on a separate explicit instruction (AGENTS.md).

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
- **Tests** on Windows, Python 3.14.3: `51 passed, 10 errors`; all ten errors are `test_submit.py` fixtures failing on `'charmap' codec can't encode` because `autowork_review.py:379` prints with `ensure_ascii=False` to a cp1252 stdout. With `PYTHONIOENCODING=utf-8` those ten pass. The seven-test demo passes with `DEMO_EVIDENCE_DIR` set. `scripts/lugos_catalog.py --check` exits 0. Whether the tests import the scripts as modules or shell out to them was not established. [run][new]
- **Rubric** (`SKILL/references/rubric.md`): twelve finding fields (id, category, task step, observed behavior, evidence, principle, likely consequence, severity, confidence with reason, proposed correction, verification, status and remaining uncertainty); categories observed failure, heuristic concern, unresolved question; severity Critical to Low; confidence high, medium, low as evidence quality; eight principles; no personas or SUS scores. [code]
- **Other callers**: `scripts/coordination_trials.py:78-140` imports both scripts as Python modules; `.github/workflows/coordination-evaluation.yml` triggers on the scripts path; `plugins/lugos-toolset/requirements-ux-review.txt` pins `mcp>=1.27,<2`; the MyDocs forwarder `MyDocs/.agents/skills/ux-review/scripts/control.py` imports the canonical script by relative path; rule files reference the skill by name. No Lugos MCP server code references ux-review; the only dispatch path runs outward from the skill. [code][new]
- **Existing mechanisms to reuse rather than reinvent** (KICKOFF, AGENTS.md): Autowork `campaign feedback` and `outcome` (`autowork/src/autowork/campaign/cli.py:1043-1119`), `DispatchFeedback` (`dispatch_contract.py:1931`), `dispatch_outcome.py` acceptance projection, `review_store.py` append-only JSONL, `campaign/atomic_io.py`, `attempt_ledger.py`, and `src/lugos_audit/` receipts with schemas under `config/cormac/audit-*.schema.json`. [code][new]

### 1.2 The Dias phone client

- The phone UI is **not in the Dias repository**. Dias (`MyDocs/dias`, worktree `MyDocs/dias-mobile`) is the Windows .NET producer that pushes session snapshots every 15 s (`dotnet/Dias.Host/RemoteSessions.cs:65-74`) and a React 19 desk display. The phone client is the Lugos host-ops service `lugos/lugos-node/services/lugos-host-ops/`, served at `/sessions` behind Cloudflare Access and installed as a PWA. [code][doc][new]
- **Stack**: server-rendered HTML from Python string templates (`lugos_host_ops/remote_sessions.py:275-395`), one vanilla JS file (`mobile_static/app.js`, 686 lines), a service worker. No framework, no build step, no design tokens. Three phone pages (`/sessions`, `/input/<id>`, `/approve/<id>`) carry separate inline style blocks with different palettes; the approval page is light-themed (`remote_sessions.py:368-379`, `input_page.py:156-166`, `approval_http.py:211-216`). [code][new]
- **State contract** is `data-*` attributes on cards (`data-session-state`, `data-receipt`, `data-message-status`, and others; `remote_sessions.py:335-341`). [code][new]
- **Receipts** for composer messages already distinguish `recorded`, `queued`, `received`, `resumed`, `finished`, `failed`, `rejected`, `outcome-unknown` (`operator_messages.py:12-16`) and surface as a "Receipt:" line with an `aria-live` status (`app.js:394,552-556`). Native questions carry `consumed` plus a separate `continuation` fact (`input_page.py:12-42`). Approvals end at "Decision recorded." with no resumption receipt (`approval_http.py:206-207`). [code][new]
- **Keyboard, safe area and visual viewport handling are absent**: no `visualViewport`, `interactive-widget`, `env(safe-area-inset-*)`, `dvh` or `enterkeyhint` in the phone pages or `app.js`. [new]
- **Stale and reconnect handling exist**: refresh failure shows "Last known", disables messaging, keeps drafts; a 401 keeps the draft; unsettled sends are never auto-resent and offer retry or edit; vanished sessions keep their card when a draft exists; a snapshot older than 60 s turns presence unconfirmed (`app.js:45-51,297-337,404-433,566-614`; `remote_sessions.py:229-235`). [code][new]
- **Fixture and tests**: `tests/mobile_browser_fixture.py --port 8879` serves controllable scenarios (`idle-current`, `ended`, `unconfirmed`, `missing`, `question`, `offline`, receipts) with no provider or push contact; opt-in Playwright phone checks at 390×844 run with `DIAS_MOBILE_BROWSER_TESTS=1` and write screenshots and `*-proof.json` (`README.md:531-538`). The browser engine the harness uses was not established. The question page has a browser script with no pytest calling it; the approval page has no browser test. [code][new]
- **Prior review evidence**: one plan-only `ux-review` checkpoint on 2026-10-28 (run `fb089312d601`, findings ux-F1 to ux-F5, no screenshots). Planned checkpoints 2 (real page on the virtual phone) and 3 (question flow end to end) have not run (`DIAS-MOBILE-NEEDS-YOU-INBOX.md:407-425,933-948`). [run][doc][new]
- **Caveats**: the `dias-mobile` worktree is a detached HEAD with uncommitted edits; local `app.js` says build `mobile-navigation-20261031-4` while docs say `20261031.5` is deployed (`app.js:6`, `MOBILE-SNAPSHOTS.md:5-6`). [new]

## 2. Target architecture

### 2.1 Boundary

ux-recast is a Python 3.11+ package, `ux_recast`, with a standard-library core and optional extras. It owns contracts, the rubric, records, the review cycle, the Lugos Autowork packet helper, the local-agent provider, evidence helpers, and the documentation outputs. Lugos `ux-review` remains the entry point; its two scripts become shims over the package that keep both the CLI and the Python module surface. Dias keeps its own design context; where the pilot's code changes land is a user decision (B-09).

```
ux_recast/
  contracts/     task, request, evidence, finding, revision, decision, outcome, lesson (dataclasses + JSON schema)
  rubric/        rubric.md, autowork-reviewer.md, VERSION (bytes frozen through the migration; see D-15)
  records/       project context (PRODUCT.md, DESIGN.md read as text, written only when absent), decisions.jsonl,
                 lessons (project tier, shared tier), evidence archive
  cycle/         review -> repair -> verify state machine, budget, checkpoint coalescing (ported from control.py)
  providers/     Provider protocol for review-packet fulfilment only: lugos_autowork (ported prepare/claim/submit/
                 record/consume), local_agent
  evidence/      capture manifest, screenshot limits, staleness, tap-to-target capture, optional Impeccable detect
                 pre-pass, optional Playwright measurement helper
  docs/          style guide, component sheets, variable tables, validators; documentation packet; motion (deferred)
  cli.py         ux-recast <command>, mirroring control.py and autowork_review.py verbs
fixtures/
  contact-request/   the existing seven-test demo, copied from SKILL/tests/demo with provenance
```

### 2.2 Contracts (KICKOFF item 2)

Every contract starts from what the Lugos scripts already write. The inner Autowork `delegate` request payload and the evidence allowed-keys check stay byte-identical through Phase 3; all new metadata lives in the outer `packet.json` envelope or in ux-recast's own records (roundtable finding I-4). Packet `schema_version` stays `1`.

| Contract | Starting point | Additions (outer envelope or ux-recast records only) |
| --- | --- | --- |
| Task | `control.py:107-117` fields | none; `flow` scoping unchanged |
| Review request | `autowork_review.py:128-135` request, packet `activation` | `request_kind: review | documentation`; `provider`; `rubric_version` in the outer packet |
| Evidence | `autowork_review.py:62-66,104-116` limits | a separate capture manifest file per packet (`revision`, `build_id`, `viewport`, `device_pixel_ratio`, `engine`, `state`, `theme`, `captured_at`); `screenshots` stays a list of paths; `observations[]` keep the demo's visible-text, input-value and focus shape |
| Finding | rubric fields (`rubric.md:30`) | `element` (selector, `data-*` reference, or tap coordinates mapped to a selector), `kind: design | implementation` (concept C-08), `score` as signal only, `status: actionable | deferred` |
| Revision | none today | `files[]`, `diff_ref`, `before_evidence`, `after_evidence`, bound to a run |
| Decision | none today | `accepted | rejected`, `rationale`, `by: user | parent | reviewer`, links to findings and revision |
| Outcome | receipt `meaning` (`autowork_review.py:304-310`) | `observed` measures from the acceptance list, `verified_by`, `remaining[]` |
| Lesson | none today | `tier: project | shared`, `supported_by[]` outcomes or decisions, `promoted_at`, `scope`, `project_identity` (git remote and root hash) |

### 2.3 Separation of project context from shared guidance (KICKOFF item 3)

- Project tier: `PRODUCT.md`, `DESIGN.md` (Impeccable-compatible, read as text, written only when absent), `.ux-recast/decisions.jsonl`, `.ux-recast/lessons/project/*.md`, `.ux-recast/evidence/<run>/` (archived copies of accepted packet evidence, since `.ux-review/` is gitignored), and generated guides and sheets, all committed in the target repository.
- Shared tier: the rubric and `lessons/shared/*.md` inside ux-recast. Promotion from project to shared requires a lesson with at least one `supported_by` outcome or user decision from a second project identity, or an explicit user instruction; refusals are logged. A reviewer's own score never qualifies (concept C-22, C-53).
- Precedence: approved project guidance over any reference; shared rubric over reviewer preference; a documentation output records its `basis` as `observed`, `accepted` or `proposed` (concept C-38).

### 2.4 Optional controls and bounded cycles (KICKOFF item 4)

The `cycle` module is a port of `control.py` with the same state file, schema, budget and transitions, so the existing controller tests run unchanged against it. Cycle state lives in `.ux-review/` for every project, Lugos or standalone (D-03). Two gaps become enforced after the migration: the five-finding cap is applied when recording a result (findings ranked by severity then input order; overflow kept as `deferred`), and a run records how many review dispatches it consumed. Lugos mode semantics (`off`, `once`, `session`, scope, shared-component mapping, per-session state) are untouched. Documentation outputs are a separate `request_kind`, invoked directly and never gated on review mode (concept C-35).

## 3. Phases

Dependencies run top to bottom unless stated. Each phase lists acceptance criteria that an agent can observe. Slices with sizes are in [implementation slices](implementation-slices.md). The roundtable's main ordering changes: the Windows test fix and a baseline live submit come first; the Autowork packet helper is ported in Phase 1, not Phase 4; a pre-pilot Dias checkpoint on the existing skill runs early so the user sees Dias value before the extraction completes; and an accepted design direction precedes any Dias repair.

### Phase 0: Foundations and the Lugos baseline

Outcome: a buildable, testable, licensed package skeleton, and a green, recorded Lugos baseline to migrate from.

- License done (D-01, Apache-2.0). `pyproject.toml` for `ux_recast`, Python 3.11+, no runtime dependencies; extras `playwright`, `mcp`; package data declared and loaded through `importlib.resources`.
- CI on GitHub-hosted `ubuntu-latest` (public repository, no billing). Windows runs are manual but recorded with Python version and artifact; macOS is excluded from the initial phases unless the user wants it covered (B-11).
- `.gitattributes` already forces LF for `.md`, `.json`, `.yaml` in ux-recast; confirm the Lugos skill files carry the same, since `rubric_sha256` and the mirror test are byte-level (roundtable T-8).
- In Lugos: fix `autowork_review.py:379` (`ensure_ascii=True`, matching `autowork_adapter.py:254-257`), produce the test inventory by test id, and run one baseline live `submit` on the legacy code, text-only and then with an image, so later shim results have something to be compared against (roundtable T-4).

Acceptance: `python -m pytest` passes in CI; `pip install .` from a built wheel in a clean virtual environment imports `ux_recast.rubric` and `ux_recast.contracts` data files; the Lugos suite passes on Windows with no encoding override, recorded with Python version; two legacy live-submit receipts with `accepted: true`.

### Phase 1: Standalone core, both scripts ported, and the independence fixture (KICKOFF items 1, 2, 8)

Outcome: contracts, rubric, cycle and the Autowork packet helper exist in ux-recast, and a review runs end to end with no Lugos, Autowork or Dias present.

- Port `control.py` into `cycle/` and `autowork_review.py` into `providers/lugos_autowork` behind the same CLI verbs and the same module-level names. Copy `SKILL/tests/test_control.py`, `test_autowork.py` and `test_submit.py` (with its fixture server) and make them pass against `ux-recast` with only import lines changed. If a test shells out to a script path, say so and adapt the harness, not the claim.
- Move `rubric.md` and `autowork-reviewer.md` into `rubric/` with their bytes unchanged; version them; add a cross-package test that the Lugos copies match the packaged bytes (D-15).
- Define contracts as dataclasses with JSON schema export; validate the 2026-10-24 `packet.json`, state file and receipt and the Phase 0 live-submit packets against them.
- `providers/local_agent`: writes the reviewer packet to disk and reads a findings file back, so a standalone coding agent can be the reviewer.
- A differential harness: a frozen corpus of argv and stdin cases (valid, malformed contract, out-of-scope flow, double claim, stale consume, over-cap result) run against fresh project copies, diffing stdout bytes, exit code and the resulting `.ux-review/` tree between two implementations (roundtable T-1). Used in Phase 3.
- Copy the contact-request demo (`SKILL/tests/demo/`, locally authored, seven Playwright tests) into `fixtures/contact-request/` with its report as provenance. Run one full cycle through `local_agent` where the repair is written from the recorded findings, not swapped in from the corrected file; the corrected file is the oracle the result is compared against (roundtable T-21).

Acceptance: the copied Lugos tests pass against ux-recast by test id; the fixture cycle completes in a clean virtual environment with `playwright` and its browser binaries installed and no Lugos checkout on disk; the recorded outcome lists seven passing acceptance checks and the findings that drove the repair; the differential harness runs the corpus against ux-recast and records the baseline.

### Phase 2: Project design context and retained knowledge (KICKOFF item 3)

Outcome: decisions, outcomes and lessons are durable, tiered, and keep their evidence.

- `records/context.py`: read `PRODUCT.md` and `DESIGN.md` as text; write starter templates only when absent with `O_CREAT | O_EXCL`. No Markdown round-tripping.
- `records/decisions.py`: `decisions.jsonl` append-only, reusing the `cycle/` lock; tested with many iterations on Windows and POSIX, lines above 4 KiB, and a stale-lock recovery case.
- Evidence archive: when a Decision or Lesson is recorded, copy the packet, receipt and before/after screenshots it cites from `.ux-review/packets/` into `.ux-recast/evidence/<run>/` so links survive a clean checkout (roundtable I-8).
- Lessons in two tiers; project identity is the git remote plus root hash; promotion refuses without a second identity's `supported_by` and logs the refusal; the explicit-user-instruction bypass is tested.

Acceptance: the Phase 1 fixture run yields one project-tier lesson whose record links the finding, the diff, the archived before and after screenshots and the passing test; promotion to shared is refused and logged until a second project identity's outcome exists.

### Phase 3: Lugos entry point and staged migration (KICKOFF items 1, 6)

Outcome: Lugos `ux-review` runs on ux-recast with callers, tests and packet formats unchanged, and can fall back in either direction.

Stage A, dependency and shim:

- Pin `ux-recast` by tag in `plugins/lugos-toolset/requirements-ux-review.txt`.
- Keep the legacy scripts as sibling files in the same directory (`control_legacy.py`, `autowork_review_legacy.py`) so `__file__`-relative reference lookups keep working and the existing mirror test covers them without a new directory (roundtable I-3).
- `control.py` and `autowork_review.py` become shims that check `UX_REVIEW_IMPL` before importing `ux_recast`, re-export the legacy module surface (functions, constants) by delegating at function level, and fail closed with a clear message when `ux_recast` is not importable and legacy was not selected (roundtable I-2, T-6). The setting is passed explicitly to the MCP server child that `submit` starts.
- Extend `test_distribution.py` to cover the shims and the legacy siblings.

Stage B, verification:

- Run the Lugos suite on Windows and on the Linux CI runner with both `UX_REVIEW_IMPL` values; pass by test id against the Phase 0 inventory.
- Run the Phase 1 differential corpus under `legacy` and under the shim; stdout bytes, exit codes and `.ux-review/` trees match except where Phase 0's encoding fix is the documented cause.
- Replay `scripts/coordination_trials.py` and the MyDocs forwarder with a stated expected output.
- Repeat the Phase 0 live submits (text and image) on the shim; compare receipts to the legacy baseline. Exercise one rejection or timeout path.
- Rollback drills in both directions, including a crossover while `dispatch.lock` is held, and a test that the legacy code tolerates the post-migration `deferred` status and unknown outer-envelope keys.

Stage C, cleanup: remove the legacy siblings only after the Dias pilot's Decision is `accepted` and the rollback drills have passed (roundtable T-17).

Also in this phase: correct `docs/ux-review.md:49` and `:87-90`.

Acceptance: test-id parity on both implementations on both platforms, recorded; differential corpus parity; live-submit receipts on the shim with `accepted: true` for text and image; `lugos_catalog.py --check` exits 0; recorded rollback drills in both directions.

### Phase 4: Cycle hardening and evidence helpers (KICKOFF item 4)

Outcome: the cycle enforces its own limits and has the optional helpers the pilot needs, with Impeccable used where a project has it and never installed by ux-recast.

- Enforce the five-finding cap on record with severity-then-input ordering; record dispatch counts.
- Image-policy preflight: a contract test that an image packet is accepted by the installed Autowork policy, and a defined behavior when it is not (fail with a message; no silent text-only fallback) (roundtable T-27).
- `evidence/impeccable_detect`: a pre-pass, not a provider. Runs `impeccable detect --json` only when the binary is already on PATH (no `npx` auto-install), maps rule hits to `kind: implementation` findings, treats exit code 2 as findings and other non-zero codes as errors, and reports `unavailable` when the binary or a browser is missing (roundtable I-7, T-25).
- Impeccable's agent commands (`critique`, `adapt`, `harden`, `polish`, `document`, `extract`): where a project has the Impeccable skill installed, the reviewer and repair passes invoke them by name; where it does not, the reviewer prompt carries the pass vocabulary. ux-recast installs nothing (D-11 amended; roundtable P-2). Whether the Dias phone client's repository gets Impeccable installed is the user's call (B-10).
- `evidence/tap_to_target`: a Playwright helper that maps a tap coordinate to the deepest element's selector and `data-*` state so a person can point at a thing on the fixture page and the finding carries that reference (the product need behind React Grab; roundtable P-3).
- Reviewer prompt pass names and the rubric version bump happen here, after Phase 3 parity, in one change (roundtable I-6).

Acceptance: a seven-finding result records five actionable and two deferred in a deterministic order; the image preflight passes against the installed policy; with Impeccable on PATH, detect findings carry rule ids and provenance; without it, the run records `unavailable` and completes; a tap on the fixture yields a selector that the finding schema accepts.

### Phase 5: Dias mobile pilot (KICKOFF item 7)

Outcome: the unrun Dias checkpoints 2 and 3 complete, the phone client gets an accepted design direction and a repair the user accepts or rejects, and the pilot's visual outcome is measured, not only its plumbing.

Pre-pilot (can start right after Phase 0): run Dias checkpoint 2 on the existing Lugos skill against `mobile_browser_fixture.py` with screenshots, so the user gets review findings on the real page before the extraction lands (roundtable P-6). Its findings feed 5b.

Setup:

- Pin a committed `lugos-host-ops` revision and record it and the `app.js` build id in every proof. Resolve the `dias-mobile` worktree state first (B-03). Decide where repairs land (B-09).
- Serve `tests/mobile_browser_fixture.py --port 8879`, reachable on the LAN for the device check. Never the production host.
- Reuse the existing Playwright harness (390×844, `isMobile`, `hasTouch`) and add 375×812 and a WebKit project; record the engine in the proof (roundtable T-10).
- Add browser coverage for the question page and the approval page before any repair touches them (roundtable T-14).
- Freeze and hash the before scripts and the acceptance thresholds before the repair; rerun them unchanged after (roundtable T-13).

5a, observe and critique: write `PRODUCT.md` and `DESIGN.md` for the phone client with `basis: observed`, recording the three inline palettes as literals with provenance. Run one review pass per flow (three flows, three packets, each within the five-screenshot and 64 KiB caps, with the rows each packet covers stated) through `lugos_autowork` with images.

5b, accepted design direction: from the critique and the concept's "look sharper" goal, propose one palette, one type scale, one status-colour vocabulary and one layout rhythm for the three phone pages, written to `DESIGN.md` with `basis: proposed`, and put to the user. On acceptance it becomes `basis: accepted` and is the standard 5c repairs against (roundtable P-1, P-5). Dias-specific meanings stay in Dias documentation; nothing enters the shared rubric.

5c, repair: one bounded repair batch split into three slices (sessions page and `app.js`; question page; approval page), each limited to its flow, each landing where B-09 decided. Keyboard and viewport handling is in scope only for what the device check in 5d can confirm.

5d, verify and decide: the frozen scripts rerun; the comparison table; the device observation; the user's accept or reject recorded as a Decision.

Task contract rows (concept C-19 to C-21), one flow per packet:

| Step | Scenario on the fixture | Observable acceptance |
| --- | --- | --- |
| Find the blocked session | notification deep link `/sessions?host=&run=`; list sorted approvals first | target card opened and scrolled into view once; gone-target message shown when `missing`; taps and scroll count from the frozen script |
| Understand the full request | `question` scenario with an 8-question, long-legend form; an approval with long pretty-printed JSON | no horizontal overflow at 375 px; full legend readable without truncation; text contrast meets WCAG AA; one type scale across the three pages |
| Respond to the correct session | composer send with stale `expectedGeneration` | 409 "binding generation changed" surfaced, draft kept |
| Submission versus receipt versus resumption (composer only; approvals have no resumption receipt and are excluded, B-05) | receipt scenarios `recorded` through `resumed` | "Receipt:" line and `aria-live` text change per state; `finished` reached |
| Long content | 4096- and 4097-character drafts, multibyte and emoji input; 1024-unit output | wrap, no clipping, Send reachable; the fixture server's received count shows one message |
| Keyboard | WebKit project with a reduced visual viewport as a smoke check only; the real check is the device observation | before and after on the user's phone as the installed PWA: model and OS recorded; focus the last field of the 8-question form and the composer; screenshot with the keyboard open showing Send and the active field; note auto-zoom on focus and recovery on dismiss (roundtable T-11) |
| Stale state | `unconfirmed` and `ended` scenarios | "Last known" shown, messaging disabled, draft kept |
| Reconnect | `offline` then online | refresh on `online` event; the fixture server's received count shows no duplicate; unsettled send offered for retry |
| Visual outcome | the three pages at 390 and 375 | one palette and one type scale across the three pages per the accepted `DESIGN.md`; hierarchy of request over metadata on the card; the user's accept or reject |

Not covered by the fixture and stated as such: a real push-notification tap opening the PWA, Cloudflare Access 401 and redirect behavior, the service worker serving a cached `app.js` (mitigated by recording the build id), 200 percent text zoom, the approval page under dark mode, and screen-reader announcement of the `aria-live` region.

Acceptance: before and after evidence for every row with the frozen scripts; the device observation before and after; the comparison on taps and scrolling, request completeness, action clarity, receipt confidence, and the visual criteria; the user's Decision recorded; existing host-ops tests and the opt-in browser suite (with `DIAS_MOBILE_BROWSER_TESTS=1`) pass.

### Phase 6: Style guide and component specification sheets (KICKOFF item 5)

Outcome: a Dias phone-client style guide and at least one component sheet with values a machine can re-check.

- `docs/` request contract with three independent flags `guide`, `sheets`, `motion` and a `basis` field; `motion` without an existing sheet is refused.
- Execution model: `ux-recast document` prepares a documentation packet (inputs manifest, measurements, `DESIGN.md`, decisions) for a provider to fill, then validates the returned guide and sheet with the variable-table validator before writing them (roundtable I-9). The Lugos skill gains one invocation for it (concept Q-01).
- Guide template: the concept's section list (C-36), every section optional, no default palette. When a sheet uses structural slots, the guide's content-behavior section is required by concept C-45; that is a conditional rule, not a global mandate.
- Sheet template adapted from Dimensional Drawing's format with license header and pinned commit; variable table schema `{name, value | [TBD], unit, source: token | css-literal | rendered | accepted | proposed, state, viewport, device_pixel_ratio, engine, formula?}`; validator corpus covers `0`, unitless line-height, hex colours, z-index, percentages and SVG attribute values; the sheet reports its `[TBD]` ratio.
- Traceability check is mechanical where it can be: `css-literal` values re-read at the recorded file, line and revision; `rendered` values re-measured at the same revision, viewport, device pixel ratio, engine and version within a stated tolerance; formulas recomputed. A second agent from a different model family, blind to the author's notes, checks the remainder, and its sensitivity is tested by seeding mutated values it must catch (roundtable T-18).
- First outputs: the sessions card at `needs-approval` and `waiting` states at 390 px, against the accepted `DESIGN.md` from 5b.

Acceptance: the mechanical trace passes with zero unexplained deltas and the seeded mutations are all caught; the guide states its `basis`; the Phase 6 host-ops diff is empty (documentation only); a developer who has only the sheet and the guide reproduces the card within the stated tolerance (this replaces "the user finds it useful"; roundtable P-8).

### Phase 7: Animated specification presentation (deferred until gated)

Entry criteria: Phase 6 acceptance; one real export with Chromium on a supported environment; the two renderer defects fixed locally or upstream (`render.mjs:93` exit code, video-branch `mkdirSync`). The defect fix and a first export may be done early in parallel if the user wants motion sooner (roundtable P-12). Output uses the sheet's geometry and variables; verification is `ffprobe` duration and frame count plus a failing exit on ffmpeg error, not "it plays".

### Phase 8: Second-project validation of the learning loop

Outcome: proof that the core and the lessons transfer without Lugos or Dias, and that a promoted lesson changes a result.

- Run the full cycle on a second small project (user's choice, B-08) through `local_agent`, with its own project identity.
- Promote one lesson from project tier to shared tier with two supporting outcomes from two identities.
- Rerun the review on a frozen input before and after promotion; the finding set must differ in the direction the lesson predicts (roundtable P-9, T-29).

Acceptance: the second project's run records a Decision and an Outcome; the promoted lesson appears in the next packet with its `supported_by` links; the before/after rerun shows the predicted difference.

## 4. Decision log

| Id | Decision | Reason | Reversibility |
| --- | --- | --- | --- |
| D-01 | **License: Apache-2.0.** Confirmed by the user 2026-11-02; `LICENSE` and `NOTICE` committed. | Rubric fragments may be adapted from Impeccable (Apache-2.0); same-license redistribution is simplest; the explicit patent grant; MIT references compose freely. | Easy before first external contribution. |
| D-02 | Python 3.11+, standard-library core, optional extras, package data via `importlib.resources`. | Matches `control.py` and `autowork_review.py` (stdlib only, 3.11+), so the port is a move, not a rewrite. | Moderate. |
| D-03 | Cycle state and packets stay in `.ux-review/` with `schema_version: 1` for every project; ux-recast durable records go to `PRODUCT.md`, `DESIGN.md` and `.ux-recast/`, with cited evidence archived under `.ux-recast/evidence/`. | Preserves callers and recorded runs; one location for state; durable records must not link into a gitignored folder (roundtable I-8). | Easy until Phase 3 Stage C. |
| D-04 | The rubric moves into ux-recast; the Lugos copies become distributed artifacts checked by `test_distribution.py` and a cross-package byte test. | One source of truth; the mirror discipline already exists. | Easy. |
| D-05 | Review dispatch is provider-pluggable for packet fulfilment only (`lugos_autowork`, `local_agent`); the Lugos provider is a port, byte-compatible on the inner request. | Standalone use (concept C-28) without breaking Lugos; linters are not providers (roundtable I-7). | Moderate. |
| D-06 | Reclassified as user decision B-09. The plan's recommendation: pilot runs on `mobile_browser_fixture.py`; repairs land on a host-ops branch gated by the Decision, not directly on the deployed service. | The phone client lives in host-ops and production sits behind Cloudflare Access, but committing an experimental toolset's repairs to a live operator service is the user's call (roundtable P-10). | n/a |
| D-07 | Documentation outputs are a separate `request_kind`, prepared as a documentation packet and validated on return. | Keeps review mode semantics untouched (concept C-35); gives Phase 6 an execution model (roundtable I-9). | Easy. |
| D-08 | Motion deferred behind a verified export, with the defect fix allowed early in parallel if the user asks. | Both renderer defects still present at `5c457437c8c8`; no export has run anywhere. | n/a |
| D-09 | A reviewer score is a signal field; acceptance is a user Decision or an observed Outcome. | Concept C-22, C-53. | n/a |
| D-10 | ux-recast CI on GitHub-hosted Linux; Windows manual and recorded; macOS excluded pending B-11. | Public repository, free; the self-hosted rule covers private repositories. | Easy. |
| D-11 | Impeccable is used through its agent commands where a project already has it installed, and through `detect` as an evidence pre-pass when the binary is on PATH. ux-recast installs nothing and never auto-installs through `npx`. | Preserves the concept's active design role (roundtable P-2) without violating the AGENTS.md overlap rule; installation per project is a user decision (B-10). | Easy. |
| D-12 | React Grab not applicable to the pilot; the product need is met by a tap-to-target evidence helper on the fixture page. | No React tree in the phone client; the need to point at an element survives (roundtable P-3). | Revisit per project. |
| D-13 | Both Lugos scripts are ported in Phase 1; Phase 3 shims depend on both. | The original Phase 3 shimmed `autowork_review.py` before its helper existed in ux-recast (roundtable I-1). | n/a |
| D-14 | Shims keep the Python module surface, check `UX_REVIEW_IMPL` before importing `ux_recast`, and fail closed with a message when `ux_recast` is absent and legacy was not selected. | Importing callers exist (`coordination_trials.py`, the MyDocs forwarder); a silent fallback would hide a broken install (roundtable I-2, T-6). | Easy. |
| D-15 | Rubric and reviewer-prompt bytes are frozen through Phase 3; vocabulary changes and the version bump land in Phase 4 after parity. | `rubric_sha256` and `task_sha256` must match between legacy and shim for the rollback drill to mean anything (roundtable I-6). | Easy. |
| D-16 | An accepted design direction (`DESIGN.md`, `basis: accepted`, approved by the user) precedes any Dias visual repair. | "Look sharper" was the founding goal and a repair needs a standard to repair against (roundtable P-1, P-5). | n/a |

## 5. Unresolved decisions and blockers

| Id | Item | Owner | Effect |
| --- | --- | --- | --- |
| B-01 | License choice (D-01). | User | Resolved 2026-11-02: Apache-2.0. |
| B-02 | Real-device keyboard behavior on the user's phone, before and after the repair, as the installed PWA, with model and OS recorded; the fixture must be reachable from the phone on the LAN. | User observation | Required for Phase 5 acceptance, no longer optional (roundtable T-11). |
| B-03 | `dias-mobile` worktree is a detached HEAD with uncommitted edits, and local `app.js` build id differs from the documented deployed build. | User or a Dias session | Must be committed or discarded before any host-ops change lands. Not touched by this plan. |
| B-04 | `submit` through the real `lugos.models` tool has never run live. | Phase 0 | Baseline live submits on legacy are now a Phase 0 step. |
| B-05 | Approvals have no resumption receipt (`approval_http.py:206-207`). | Dias and host-ops product decision | Excluded from the receipt row; a likely pilot finding; closing it is host-ops work outside ux-recast. |
| B-06 | Knowledge-base distribution rights. | User | Blocks copying method pages; the fixture is sourced from `SKILL/tests/demo` instead. |
| B-07 | Fix the `autowork_review.py:379` encoding defect upstream. | Lugos maintainer | Now the first Phase 0 step in Lugos. |
| B-08 | Second project for Phase 8. | User | Blocks Phase 8 scheduling only. |
| B-09 | Where Dias pilot repairs land: a host-ops branch gated by the pilot Decision (recommended), directly on the deployed service, or a fork of the phone pages. | User | Blocks Phase 5c. |
| B-10 | Whether to install the Impeccable skill in the host-ops repository for the pilot, so `critique`, `adapt`, `harden` and `polish` run as commands rather than as prompt vocabulary. | User | Changes how 5a and 5c are executed, not whether. |
| B-11 | macOS coverage for the Lugos shim and the ux-recast package: cover in Phase 3, or exclude explicitly. Two of the four hosts are Macs. | User | Blocks the platform claim in Phase 3 acceptance. |
| B-12 | Approval of the accepted design direction for the phone client (5b). | User | Blocks Phase 5c. |

## 6. Reading list before implementation

- Lugos: `SKILL/SKILL.md`, `references/workflow.md`, `references/rubric.md`, `references/autowork-reviewer.md`, `scripts/control.py`, `scripts/autowork_review.py`, `tests/`, `docs/ux-review.md`, `.github/workflows/ux-review.yml`, `autowork/campaign/assignment-policy.toml:171-174`, `lugos-mcp/src/lugos_mcp/adapters/autowork_adapter.py:516-636`, `autowork/src/autowork/campaign/dispatch_contract.py` (whether `DispatchRequest` forbids extra fields).
- Dias phone client: `lugos/lugos-node/services/lugos-host-ops/lugos_host_ops/{remote_sessions.py,input_page.py,approval_http.py,operator_messages.py,attention_server.py}`, `mobile_static/app.js`, `tests/mobile_browser_fixture.py`, `tests/test_mobile_current_ui.py` and its Playwright config (to learn the engine), `dias-mobile/docs/{MOBILE-SNAPSHOTS.md,DIAS-MOBILE-NEEDS-YOU-INBOX.md}`, `dias-mobile/docs/evidence/ux-review-needs-you-item-2026-10-28/`.
- References at the pinned revisions in the reuse map.

## 7. Roundtable review, 2026-11-02

A three-amigos roundtable reviewed the plan set at `db78c53` the day it was written. Participants and routes, the findings in full, and every disposition are in [the evidence record](../evidence/plan-roundtable-2026-11-02.md). The changes folded in above:

- Phase 1 ports both Lugos scripts, not one, so the Phase 3 shims have something to call (I-1, D-13). The Windows encoding fix and baseline live submits move to Phase 0 (T-4, B-07).
- Shims keep the Python API, keep legacy as sibling files, fail closed without `ux_recast`, and are proven by a differential corpus in both directions, not only by the existing unit tests (I-2, I-3, T-1, T-5, T-6, D-14).
- New contract metadata stays out of the inner Autowork payload (I-4). Rubric bytes are frozen through the migration (I-6, D-15).
- `impeccable_detect` is an evidence pre-pass, not a provider, and never auto-installs; Impeccable's agent commands are used where a project has them (I-7, T-25, P-2, D-11).
- Durable records archive their evidence out of the gitignored `.ux-review/` (I-8, D-03). The documentation output has an execution model and a Lugos entry point (I-9, D-07).
- The Dias pilot gains a pre-pilot checkpoint on the existing skill, an accepted design direction before any repair, visual acceptance criteria, a WebKit project, required before-and-after device observation, frozen comparison scripts, coverage for the two untested pages, per-flow packets within the evidence caps, an explicit list of what the fixture cannot prove, and a tap-to-target helper in place of React Grab (P-1, P-3, P-5, P-6, P-7, T-10 to T-16, D-12, D-16).
- Where repairs land is the user's decision, not the planner's (P-10, B-09). Impeccable installation and macOS coverage are likewise the user's (B-10, B-11).
- Phase 6 tracing is mechanical with seeded mutations; "useful" is replaced by a reproduction test (P-8, T-18 to T-20). Phase 8 proves a promoted lesson changes a result on a frozen input (P-9, T-29).
- Legacy cleanup is gated on an accepted Decision, not on a cycle completing (T-17).

Rejected or narrowed: the content-behavior section is required by concept C-45 when slots are used, so it stays as a conditional rule (P-4); motion stays gated but may be worked early (P-12); the plan does not reorder Phase 6 wholesale ahead of Phase 5 but inserts the design-direction step the product seat was asking for (P-5).
