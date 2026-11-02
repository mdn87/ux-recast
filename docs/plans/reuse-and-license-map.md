# Reuse and license map

Status: planning deliverable, prepared 2026-11-02. Maps existing Lugos functionality and the external references in [the reference register](../REFERENCES.md) to a proposed reuse disposition, the evidence behind it, attribution duty, and the revision the plan assumes. Dispositions use the vocabulary KICKOFF.md asks for: **external tool**, **adapter**, **narrow adaptation** (a copied or adapted component or rubric), **documented reference**, or **deferred**. Phase numbers refer to [the initial implementation plan](initial-implementation-plan.md).

Revisions below were read from the GitHub API on 2026-11-02 (default-branch head commit, SPDX license id, latest release tag where one exists). They are the revisions inspected for this plan, not a claim about what will be current at implementation time. Pin again at implementation.

## External references

| Reference | Revision inspected | License | Disposition | Phase |
| --- | --- | --- | --- | --- |
| Impeccable | `e89e3ada3e87` on `main`, release `cli-v4.8.0`, npm `impeccable@4.8.0` | Apache-2.0 | **External tool where installed + documented reference.** Where a project already has the Impeccable skill, the review and repair passes invoke `critique`, `adapt`, `harden`, `polish`, `document` and `extract` by name; `detect --json` is an evidence pre-pass when the binary is on PATH. Its `PRODUCT.md` and `DESIGN.md` are read as text. ux-recast never vendors the skill, never installs through `npx`, and never installs the design hook (amended after the roundtable, P-2 and T-25). | 2 (context records), 4 (evidence pre-pass, command passes) |
| Happy | `1a1bd4346c31` on `main`, release `cli-1.2.5` | MIT | **Documented reference.** Pattern source for the Dias pilot: session list hierarchy, pending-request framing, output on a phone, return to a session. No code copied in the initial phases. | 5 (Dias pilot) |
| UI UX Pro Max | `3a13158ff1f3` on `main`, release `v2.15.0` | MIT | **Deferred.** Candidate searchable guidance library and per-project design-system persistence. Overlaps Impeccable `DESIGN.md` and the ux-recast style guide. Revisit only when a concrete guidance gap is recorded in a review. | Deferred |
| React Grab | `ea4bbec9e80f` on `main`, release `@react-grab/cli@0.2.0`, last push 2026-08-22 | MIT | **Not applicable to the pilot, deferred otherwise.** It needs a React tree. The Dias phone client is server-rendered HTML with one vanilla JS file (see Dias inspection, below). Remains a candidate for React projects once a feedback-capture flow exists. | Deferred |
| Dimensional Drawing | `5c457437c8c8` on `main`, no releases | MIT | **Narrow adaptation (static sheets) + deferred (motion).** Adopt the sheet format and measurement checklist from `skills/dimensional-drawing/SKILL.md` as the component-specification output. Treat the motion renderer as a separately optional output gated on a verified export. | 6 (sheets), 7 (motion) |

### Impeccable

Observed at `e89e3ada3e87`:

- Top-level `skill/` holds the agent-facing skill. `cli/bin/cli.js` is the `impeccable` binary. `plugin/` and `.claude-plugin/` package it for Claude Code. Twenty-four commands grouped as Review (`critique`, `audit`), Finish (`polish`, `harden`, `clarify`, `adapt`, `optimize`, `onboard`), Plan and set up (`shape`, `init`, `document`, `extract`) and others (README lines 52 to 60).
- Persistence: `PRODUCT.md` (written by `init`), `DESIGN.md` (written by `document`), and `.impeccable/` with shared artifacts `config.json`, `live/config.json`, `design.json`, `surfaces/*.md`, `critique/*.md` (README lines 164 to 190). The README publishes an ignore block for the ephemeral remainder.
- Detector: `npx impeccable detect <dir|url> --json` gives machine-readable findings with exit code 2 on findings (README lines 79 to 88). Rendered-page rules need a URL and an installed Chrome or Edge.
- Install modes: `npx impeccable install` (per tool, project or global, offers a design hook), Claude Code marketplace plugin, or `npx impeccable link --source=vendor/impeccable` from a git submodule (README lines 92 to 123). Linking installs skills without hooks.

Plan consequences:

- The concept's capability mapping (`critique`, `adapt`, `harden`, `polish`, `document` and `extract`) is preserved as the vocabulary of the review adapter. ux-recast does not reimplement those commands.
- ux-recast reads Impeccable's record files as text where a project already has them and writes starter templates only when absent. The plan does not create a second authority for product context or the visual system (concept Part II section 6).
- The design hook is not installed by ux-recast, and `detect` is never run through `npx` auto-install. AGENTS.md forbids silently installing an overlapping toolset, and Lugos `ux-review` already defaults off. Installing the skill in a project (for the pilot, the host-ops repository) is the user's decision, B-10.
- `detect` is an evidence pre-pass, not a review provider: it does not consume a packet or rubric, so modelling it as one would be a false abstraction (roundtable I-7).
- Pin to `cli-v4.8.0` or later at implementation. Record the installed version in the review packet so a critique's rubric version is traceable.
- Attribution: Apache-2.0 requires the license and any NOTICE to travel with redistributed material. Copying a rubric fragment into ux-recast triggers that duty; calling the CLI does not.

### Happy

Observed at `1a1bd4346c31`: `packages/happy-app` is an Expo application (`app.config.js`, `eas.json`, `metro.config.js`, `nativewind-env.d.ts`, `sources/`, `src-tauri/`) with its own `LICENSE` and `TERMS.md`. The concept's four inspection targets (session list hierarchy, pending requests, output presentation, returning to a session) remain the inspection scope.

Plan consequences: documented reference only. If a later phase copies a component, record the file, commit and MIT notice in this map. Because the Dias phone client is not React Native or Expo, any borrowing is of interaction patterns, not code.

### UI UX Pro Max

Observed at `3a13158ff1f3`: a Claude Code plugin (`.claude-plugin/`, `skill.json`) with `src/`, `stack/`, `projects/`, `gallery/`, `cli/` and localized READMEs. Deferred because its project design-system persistence overlaps Impeccable `DESIGN.md` and the ux-recast style guide, and the concept introduced it as useful "when we identify a specific gap" (Part I, Turn 3).

### React Grab

Observed at `ea4bbec9e80f`: packages `react-grab`, `grab`, `cli`, `playwright-coverage`. Last push 2026-08-22. Not applicable to the Dias pilot for the reason in the table.

### Dimensional Drawing

Observed at `5c457437c8c8` on 2026-11-02. The three files inspected for [the seed assessment](../references/dimensional-drawing-assessment.md) are unchanged: content-blob SHAs `53ac26f4…`, `fe7f7f20…` and `508be6fa…` match the assessment exactly. Both renderer findings in that assessment still hold at this commit:

- `adapters/headless/render.mjs` line 93 awaits ffmpeg's `close` event without reading the exit code, then closes the browser.
- `mkdirSync(dirname(OUT), { recursive: true })` appears only in the still-image branch (line 69). The video branch has no equivalent.

Plan consequences:

- Static component sheets adopt the documented format (self-contained HTML with SVG, variable table, notes, title block, detail views, `[TBD]` for unknowns) and the SKILL.md measurement checklist. This is a narrow adaptation: ux-recast carries its own sheet template derived from that format, with the MIT notice and the pinned commit recorded in the template header.
- The motion renderer is not adopted until a real export on an environment with Chromium has been performed and the two defects above are fixed locally or upstream. Until then motion is deferred and the static sheet is the deliverable.
- No releases exist upstream, so pin by commit.

## Existing Lugos functionality

Inspected 2026-11-02, read-only. Paths are relative to `C:\Users\Matt\Desktop\MyDocs\lugos`; `SKILL/` abbreviates `plugins/lugos-toolset/skills/ux-review/`. Lugos is the user's own code, so the question here is placement, not license.

| Component | Evidence | Disposition | Phase |
| --- | --- | --- | --- |
| Controller: modes, scope, shared-component mapping, checkpoints, phases, budget, per-session state | `SKILL/scripts/control.py` (305 lines, stdlib only); state at `PROJECT/.ux-review/<sha256(session)[:24]>.json` (`:76-83`); budget `:174-175`; transitions `:262-283` | **Extract into `ux_recast.cycle`** as a port, then **wrap** the Lugos script as a shim with the same argv, stdout JSON, exit codes and file paths. State schema `version: 1` unchanged. | 1 (port), 3 (shim) |
| Packet helper: `prepare`, `claim`, `submit`, `record`, `consume` | `SKILL/scripts/autowork_review.py` (387 lines); packet schema `:137-139,161,243,253-257,274-281`; receipt schema `:304-310,335`; evidence limits `:62-66,104-116` | **Extract into `ux_recast.providers.lugos_autowork`** behind a Provider protocol; **wrap** the script as a shim. `schema_version: 1` preserved so recorded packets stay readable. | 3 (shim), 4 (provider) |
| Windows output defect | `autowork_review.py:379` prints `ensure_ascii=False` to a cp1252 stdout; 10 `test_submit.py` errors on Windows, 0 with `PYTHONIOENCODING=utf-8` | **Fix upstream first** (plan B-07, slice S3.0), matching `lugos-mcp/src/lugos_mcp/adapters/autowork_adapter.py:254-257` which uses `ensure_ascii=True`. | 3 |
| Rubric and reviewer prompt | `SKILL/references/rubric.md` (fields `:30`, categories `:32-34`, severity `:36-41`, confidence `:43`, principles `:15-24`); `references/autowork-reviewer.md` embedded by `prepare` (`autowork_review.py:119-127`) | **Move the source into `ux_recast.rubric`**; the Lugos copies become distributed artifacts covered by `test_distribution.py`. Version the rubric and record `rubric_sha256` per packet (already in the packet schema). | 1 |
| Mirror discipline | `.agents/skills/ux-review/` byte-identical to `SKILL/` minus `tests/`; enforced by `SKILL/tests/test_distribution.py:9-16` and `.github/workflows/ux-review.yml` | **Keep.** Extend the distribution test to cover the shims. No sync script exists; the plan does not add one. | 3 |
| MyDocs forwarder | `MyDocs/.agents/skills/ux-review/` (12-line `SKILL.md`, 15-line `control.py` importing the canonical one by relative path, 3-line reference stubs, older `tests/test_control.py`) | **Keep as is.** It resolves to whatever the canonical script is, so the shim covers it. Its stale local test is out of scope. | n/a |
| Autowork dispatch route | `lugos.models delegate` alias (`lugos-mcp/tests/test_command_catalog.py:113-124`) to `autowork_adapter.py:516-545`, which runs `python -m autowork.main campaign dispatch --request -` and validates `task_sha256` (`:615-636`) | **Reuse unchanged.** ux-recast never talks to Autowork except through this tool. | 4 |
| Image review policy | `autowork/campaign/assignment-policy.toml:171-174` opts task class `review` into `image_input` (commit `b70bedc9`); `dispatch_contract.py:1076-1084` requires `visual_inputs`, `image_input` and the `image` modality together; 2026-10-26 run accepted with images | **Reuse unchanged.** The provider declares all three together or none. `docs/ux-review.md:87-90` is stale and is corrected in Phase 3. | 4, 5 |
| Snapshot checkpoints and staleness | `control.py:181-216` manifests and coalescing; `autowork_review.py:318-342` `consume` | **Extract with the controller.** Behavior preserved; the 27 controller tests and 15 Autowork tests are the regression contract. | 1, 4 |
| Demo fixture | `SKILL/tests/demo/` (`test_flow.py`, seven Playwright scenarios, baseline and corrected form, `task.json`), locally authored for the 2026-10-24 demonstration | **Copy into `fixtures/contact-request/`** with a `PROVENANCE.md` naming the Lugos commit and path. This is the KICKOFF item 8 independence fixture. | 1 |
| Outcomes and acceptance feedback | `autowork/src/autowork/campaign/cli.py:1043-1119` (`feedback`, `outcome`), `dispatch_contract.py:1931` (`DispatchFeedback`), `dispatch_outcome.py:414-442,517-518` | **Reuse for Lugos-dispatched runs**; the ux-recast Outcome record links to the Autowork outcome rather than duplicating it. Standalone runs carry their own Outcome. | 2, 4 |
| Durable records | `campaign/dispatch_store.py`, `campaign/atomic_io.py`, `attempt_ledger.py`, `review_store.py` (append-only JSONL) | **Pattern reuse, not import.** `.ux-recast/decisions.jsonl` follows the append-only, no-clobber discipline; ux-recast stays free of an Autowork dependency. | 2 |
| Audit receipts | `src/lugos_audit/` (`models.py`, `engine.py`, `cli.py`, `checks/`), schemas `config/cormac/audit-*.schema.json` | **Reuse unchanged** for closing receipts on ux-recast and Lugos work; no new receipt format. | all |
| Other callers | `scripts/coordination_trials.py:78-140` imports both scripts; `.github/workflows/coordination-evaluation.yml:37,74`; `requirements-ux-review.txt` pins `mcp>=1.27,<2`; rule files name the skill | **Preserve by keeping argv and paths.** Replay `coordination_trials.py` in Phase 3 Stage B. | 3 |

Verified in a real run versus only implemented: modes, scope and budget state transitions; `prepare`, `claim`, `record`; image review (accepted 2026-10-26); snapshot coalescing and `consume` staleness. Implemented but never run live: `submit` through MCP (commit `310e0a28`). Not exercised on a live product: repair to verify. Not tested: macOS.

## Dias (first validation target)

Inspected 2026-11-02, read-only. Full detail is folded into the plan's Phase 5. The facts that change reuse decisions:

| Fact | Evidence | Consequence |
| --- | --- | --- |
| The phone client is not in the Dias repo. It is the Lugos host-ops service at `lugos/lugos-node/services/lugos-host-ops/`, served at `/sessions` behind Cloudflare Access. | `dias-mobile/docs/MOBILE-SNAPSHOTS.md:205-207`; `lugos_host_ops/remote_sessions.py:275-395` | Pilot changes are Lugos host-ops changes with their own deploy controller. Dias-specific design decisions still belong with Dias documentation, as the concept requires. |
| Server-rendered HTML from Python string templates plus one vanilla JS file (`mobile_static/app.js`, 686 lines) and a service worker. No framework, no build step. | `remote_sessions.py:275-395`; `app.js:1` | React Grab is not applicable. Source-aware feedback for this client would need a different mechanism (the `data-*` state attributes are the only structural hook). |
| No design tokens. Three phone pages carry separate inline `<style>` blocks with hard-coded hex values and inconsistent palettes; the approval page is light-themed while the others are dark. | `remote_sessions.py:368-379`; `input_page.py:156-166`; `approval_http.py:211-216` | The style-guide capability's first Dias output documents an observed system that does not yet exist as tokens. Any "token compliance" check is against duplicated literals. |
| Message receipts already distinguish `recorded`, `queued`, `received`, `resumed`, `finished`, `failed`, `rejected`, `outcome-unknown`, surfaced as a "Receipt:" line plus an `aria-live` status. | `operator_messages.py:12-16`; `app.js:75-77, 394, 552-556` | The concept's "submission versus receipt versus resumption" distinction already has a backend contract for messages. Approvals do not: the approval page only says "Decision recorded." (`approval_http.py:206-207`). |
| No keyboard, safe-area or visual-viewport handling anywhere in the phone pages. | grep across `remote_sessions.py`, `input_page.py`, `app.js` for `visualViewport`, `interactive-widget`, `env(safe-area-inset`, `dvh`, `enterkeyhint`: no matches | The concept's keyboard-obstruction scenario is unhandled and untested, so it is a real pilot target rather than a regression check. |
| A disposable fixture server exists with controllable scenarios (`idle-current`, `ended`, `unconfirmed`, `missing`, `question`, `offline`, receipts). Playwright phone checks at 390×844 are opt-in via `DIAS_MOBILE_BROWSER_TESTS=1`. | `tests/mobile_browser_fixture.py:23-48, 186-193`; `README.md:531-538` | The pilot runs against the fixture, never the production host, and reuses the existing Playwright harness for before/after evidence. |
| One prior `ux-review` checkpoint ran against Dias (plan-only, 2026-10-28, five findings ux-F1 to ux-F5, no screenshots). Checkpoints 2 and 3 (real page on the virtual phone; question flow end to end) have not run. | `dias/.ux-review/packets/fa6a443dc4582e80214edcc2-fb089312d601/`; `DIAS-MOBILE-NEEDS-YOU-INBOX.md:407-425, 933-948` | The pilot's first checkpoint is the unrun checkpoint 2, so it extends existing evidence rather than starting over. |
| The `dias-mobile` worktree is a detached HEAD with uncommitted local edits. Local `app.js` says build `mobile-navigation-20261031-4` while docs say `20261031.5` is deployed. | `app.js:6`; `MOBILE-SNAPSHOTS.md:5-6` | Pin the pilot to a committed revision of host-ops and record it in the review packet. Treat the worktree state as a blocker to resolve before production changes, not during planning. |

## Knowledge base

| Source | Location | License and provenance | Disposition |
| --- | --- | --- | --- |
| UX Practices Knowledge Base | `../ux-knowledge-base/` (sibling folder, not a git repository) | Distilled from bootcamp course materials; distribution rights unconfirmed | **Documented reference.** Method pages may be cited in findings. Nothing copied into ux-recast until rights are confirmed. |
| Contact-request demo fixture (knowledge-base copy) | `../ux-knowledge-base/07-agent-review/demo/` (`task.json`, `index.before.html`, `index.html`, `test_flow.py`, `REPORT.md`, evidence) | A copy of the demonstration written for Lugos ux-review on 2026-10-24 | **Not the source.** The canonical copy is `lugos/plugins/lugos-toolset/skills/ux-review/tests/demo/` (see the Lugos table above), which is locally authored and carries no bootcamp provenance. Phase 1 copies from Lugos, so the knowledge-base rights question does not touch the fixture. `REPORT.md` here remains useful reading for the expected cycle shape. |
