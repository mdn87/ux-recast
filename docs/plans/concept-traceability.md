# Concept traceability

Status: planning deliverable, prepared 2026-11-02. One row for every substantive proposal, constraint or open question in [the concept record](../CONCEPT.md), with its source section, who originated it, and its planned disposition. Phase numbers refer to [the initial implementation plan](initial-implementation-plan.md); slice ids refer to [the implementation slices](implementation-slices.md).

Origin vocabulary, as KICKOFF.md asks: **user decision** (a user instruction), **assistant proposal** (a suggestion from the originating conversation), **new finding** (something the 2026-11-02 inspection established), **open decision** (still unresolved).

Disposition vocabulary: **planned** (in a numbered phase), **deferred** (kept visible, no phase), **not applicable** (with the reason), **preserved as record** (history kept, no implementation meaning), **resolved** (an open question the plan answers, with the answer).

## Part I: conversation proposals

| Id | Source | Origin | Proposal or constraint | Disposition |
| --- | --- | --- | --- | --- |
| C-01 | Turn 1 | User decision | Improve the Dias mobile interface's user experience and make it look sharper. | Planned, Phase 5. The pilot's acceptance is the user's acceptance of a revised flow, not a reviewer score. |
| C-02 | Turn 2 | User decision | Prefer something open source that lets the system self-improve for similar work on other projects. | Planned, Phases 1, 2 and 8. The core is standalone and the learning loop is validated on a second project. |
| C-03 | Turn 3 | Assistant proposal | Impeccable as the main design-improvement capability, used to strengthen the optional Lugos `ux-review` workflow. | Planned, Phase 4 as an adapter. See the reuse map: not vendored, hook not installed. |
| C-04 | Turn 3 | Assistant proposal | Happy as the closest functional mobile reference to study. | Planned, Phase 5 as a documented reference. New finding: the Dias phone client is not Expo or React, so borrowing is pattern-level only. |
| C-05 | Turn 3 | Assistant proposal | UI UX Pro Max as a reference library when a specific gap appears. | Deferred, trigger recorded in the reuse map. |
| C-06 | Turn 3 | Assistant proposal | React Grab to let a person point at a Dias component and give source-linked feedback. | Not applicable to the pilot (new finding: no React tree in the phone client). Deferred for React projects. |
| C-07 | Turn 3 | Assistant proposal | Start with Impeccable and Happy; the other two when a gap is identified. | Planned, this ordering is kept. |
| C-08 | Turn 3 | Assistant proposal | Distinguish design quality (`critique`) from implementation quality (`audit`) and use both as inputs to the existing review system. | Planned, Phase 1 contracts carry a `kind` on findings; Phase 4 adapter maps both. |
| C-09 | Turn 3 | Assistant proposal | Capability mapping for Dias: `critique` (is the pending action immediately understandable), `adapt` (phone rework), `harden` (long content, missing states, errors, overflow), `polish` (typography and spacing after the flow works), `document` and `extract` (preserve accepted rules). | Planned, Phase 5 uses this as the pass order; Phase 2 and 6 use `document` and `extract` outputs. |
| C-10 | Turn 3 | Assistant proposal, with caveat | The Impeccable comparison gallery is the maintainer's showcase, not proof it improves Dias. | Preserved as record. The plan takes no evidence from the gallery. |
| C-11 | Turn 3 | Assistant proposal | Inspect Happy's session list hierarchy, pending-request framing, output presentation and return-to-session path first. | Planned, Phase 5 pre-pilot reading list. |
| C-12 | Turn 3 | Assistant proposal | Happy compatibility with Dias sessions and control paths would need examination before reuse. | Resolved by new finding: no code compatibility exists; patterns only. |
| C-13 | Turn 3 | Assistant proposal | The lasting improvement is retained evidence about which changes worked, built around the skill's output. | Planned, Phase 2 (records) and Phase 8 (validation). |
| C-14 | Turn 3 | Assistant proposal | Five-step loop: capture the starting point; focused critique; bounded revision; record the outcome; promote useful lessons. | Planned, Phase 1 contracts mirror the five steps; Phase 4 runs them. |
| C-15 | Turn 3 | Assistant proposal | Each finding identifies the affected element, the user difficulty and the evidence. | Planned, Phase 1 finding schema. New finding: the existing Lugos rubric already defines finding fields; the schema extends it rather than replacing it. |
| C-16 | Turn 3 | Assistant proposal | Impeccable's `PRODUCT.md`, `DESIGN.md` and saved critiques supply part of the persistence structure; ux-recast connects those to accepted changes and outcomes. | Planned, Phase 2. |
| C-17 | Turn 3 | Assistant proposal | Separate reusable interaction rules ("show the complete pending question before secondary session metadata") from project design decisions ("Dias uses red for needs-input status"). | Planned, Phase 2 two-tier record with an explicit promotion step. |
| C-18 | Turn 3 | Assistant proposal | Other projects (TableForge, the work portal) benefit without inheriting Dias's appearance. | Planned, Phase 8 second-project validation. |
| C-19 | Turn 3 | Assistant proposal | First Dias test spans three connected screens: Needs you; Request detail; Response status. | Planned, Phase 5. New finding: in the current client these are the `/sessions` card list, the `/input/<id>` or `/approve/<id>` page, and the receipt line on the card. |
| C-20 | Turn 3 | Assistant proposal | Compare old and revised on taps and scrolling required, completeness of the request, clarity of the action, and confidence the response reached the correct session. | Planned, Phase 5 acceptance measures. |
| C-21 | Turn 3 | Assistant proposal | Cover long questions, the phone keyboard, stale sessions and reconnects. | Planned, Phase 5 scenarios. New finding: keyboard handling is absent in the client, stale and reconnect handling exist and are testable through the fixture server. |
| C-22 | Turn 3 | Assistant proposal, caveat | The projects were verified by documentation and source, not run against Dias. A model awarding its own design a higher score is only a review signal. | Planned as a standing rule: Phase 1 records a reviewer score as a signal field, never as acceptance. |
| C-23 | Turn 4 | User decision | Spin up a new repository and extend the `ux-review` functionality into it. | Done 2026-11-02: `mdn87/ux-recast` exists with the seed. Extraction is Phases 1 to 4. |
| C-24 | Turn 5 | Assistant proposal | Name "Cruth"; alternatives Snas, Cuma; the Cruth name collision. | Preserved as record. Superseded by C-30. |
| C-25 | Turn 5 | Assistant proposal | Repository boundary: ux-recast owns design guidance, review rubrics, reference analysis, critique reports, refinement workflows and accepted lessons. | Planned, Phase 1 package boundary. |
| C-26 | Turn 5 | Assistant proposal | Lugos `ux-review` remains the entry point, calling the core through a small integration, keeping its enable/disable controls and review limits. | Planned, Phase 3. |
| C-27 | Turn 5 | Assistant proposal | Dias is the first validation project; Dias-specific interface requirements stay in Dias. | Planned, Phase 5. New finding: the phone client code lives in Lugos host-ops, so "stay in Dias" means Dias documentation and design context, with code changes landing in host-ops. |
| C-28 | Turn 5 | Assistant proposal | The core works without Lugos, for PADL, work projects or a standalone coding agent. | Planned, Phase 1 and the Phase 1 fixture (KICKOFF item 8). |
| C-29 | Turns 6 and 7 | User decision then assistant proposal | Brainstorm beyond Lugos naming; candidates Sightline, Caliper, Redline, Touchstone, Keen, Recast, Temper, Hone, Contour, Poise, Formative, Afterimage, Margin, Reframe, Second Look. | Preserved as record. |
| C-30 | Turn 8 | User decision | Working name `ux-recast`. | Done; repository and README carry it. |
| C-31 | Turn 8 | User decision | Add something that can optionally create a style guide like the supplied dimensional-drawing reference. | Planned, Phases 6 and 7. |
| C-32 | Turn 8 | User decision | Prepare a repo seed with the concept including all suggestions without reanalysis or summary, plus a kickoff prompt. | Done by the seed. This document and the plan are the separate files AGENTS.md requires. |
| C-33 | Turns 9 to 11 | User question, assistant finding | The drawing repository is a useful focused skill pack; borrow it for component sheets; the full style guide is our addition; two renderer defects; Chromium absent so no export verified. | Planned, Phase 6 (sheets) and Phase 7 (motion, gated). New finding 2026-11-02: both defects still present at `5c457437c8c8`. |

## Part II: optional style guides and component specifications

| Id | Source | Origin | Proposal or constraint | Disposition |
| --- | --- | --- | --- | --- |
| C-34 | II.1 | Concept requirement | Three separately selectable outputs: project style guide; component specifications; animated specification presentation. A guide may include sheets; a sheet may be requested alone; animation is separately optional. | Planned, Phase 6 request contract carries three independent flags; Phase 7 implements the third. |
| C-35 | II.1 | Concept requirement | These choices stay independent of the Lugos review switch and of the product's own animation behavior. | Planned, Phase 3 keeps the Lugos controls unchanged; Phase 6 is invoked directly, not through review mode. |
| C-36 | II.2 | Concept requirement | Guide content list: audience and principles; color and status semantics; typography; spacing and layout; component anatomy; interaction states including stale and disconnected; input and feedback conventions including submitted versus completed; accessibility; motion rules where accepted; examples, counterexamples, open questions, reasons. | Planned, Phase 6 guide template with every section optional. |
| C-37 | II.2 | Concept requirement | The product determines which sections apply. Dias status meanings do not become defaults. | Planned, Phase 6 template has no default palette or status vocabulary. |
| C-38 | II.3 | Concept requirement | A guide states whether it documents the existing interface, describes an accepted redesign, or proposes a direction. | Planned, Phase 6 `basis` field: `observed`, `accepted`, `proposed`. |
| C-39 | II.3 | Concept requirement | Inputs may include documentation, source, tokens, stories or fixtures, rendered pages, accepted examples, screenshots and recorded decisions. Approved guidance is authoritative; an inspirational reference does not overwrite it. | Planned, Phase 6 input manifest; Phase 2 precedence rule. |
| C-40 | II.3 | Concept requirement | Every meaningful value retains its origin: source or token, rendered measurement, accepted decision, explicit proposal, or unresolved. Record component, state, viewport, theme and source revision. | Planned, Phase 6 provenance record per value. |
| C-41 | II.3 | Concept requirement | Unknown measurements stay unresolved; estimates are labeled; exact-looking drawings must not imply unsupported precision; CSS units and screenshot pixels are distinguished. | Planned, Phase 6 validation rejects a sheet with an unlabeled numeric value. |
| C-42 | II.4 | Concept requirement | Sheets follow the reference's documented format: self-contained HTML with SVG, variable tables, notes, title block, detail views, monochrome, neutral labels, structural slots, `[TBD]`. | Planned, Phase 6 template (narrow adaptation, see reuse map). |
| C-43 | II.4 | Concept requirement | Useful views: overall arrangement, spacing chains, control and hit-area relationships, nested radii, border and elevation relationships, layer stack, placement in the surrounding interface. | Planned, Phase 6 view catalog; each sheet picks a subset. |
| C-44 | II.4 | Concept requirement | Stable variable names connect drawings to tokens; formulas for derived values; explicit units, inputs, state and viewport; missing or conflicting tokens surface as open issues. | Planned, Phase 6 variable table schema and validator. New finding: Dias has no tokens, so the first Dias sheet will carry literal values with `source: rendered` or `source: css-literal` provenance. |
| C-45 | II.4 | Concept requirement | Slots keep sheets useful as content changes, but the guide still captures wrapping, long requests, overflow, translated or enlarged text. A placeholder never justifies truncating the real request. | Planned, Phase 6 guide section "content behavior" is mandatory when a sheet uses slots. |
| C-46 | II.4 | Concept requirement | Monochrome belongs to the technical documentation and must not force the product into monochrome. | Planned, Phase 6 template note; Phase 5 keeps the product palette. |
| C-47 | II.5 | Concept requirement | Motion presentation is a documentation presentation, distinct from product interaction animation. Offered only after a static sheet exists; same geometry and variables; static artifact remains. | Planned, Phase 7, gated on Phase 6 output. |
| C-48 | II.5 | Concept requirement | The rendering path is verified on a supported environment before unattended use. | Planned, Phase 7 entry criterion: one real export with Chromium, defects fixed. |
| C-49 | II.6 | Concept requirement | Human-readable guide and machine-readable data where useful; planner picks formats per target repository; candidates include Markdown, HTML guide, SVG or HTML sheets, semantic token files, print or video exports. | Resolved in the plan: Markdown guide plus JSON design data in Phase 6; HTML sheets per the reference format; print and video deferred to Phase 7. |
| C-50 | II.6 | Concept requirement | Connect outputs to existing design context; preserve the roles of product context, visual-system documentation and accepted decisions; avoid competing authorities for a token or rule. | Planned, Phase 2 precedence and Phase 6 writes to the same records. |
| C-51 | II.6 | Concept requirement | Updates make changed decisions and measurements reviewable; preserve earlier accepted versions or rely on repository history; identifiers map back to components and evidence. | Planned, Phase 6 output is committed in the target repository; sheet ids are stable per component. |
| C-52 | II.7 | Concept requirement | A guide is an output of an accepted refinement and an input to the next review. Keep accepted and rejected changes with rationale and before/after evidence. | Planned, Phase 2 record links guide revisions to review outcomes. |
| C-53 | II.7 | Concept requirement | Do not update the shared rubric because a model prefers its own output; use the Part I evidence and acceptance approach. | Planned, Phase 2 promotion requires an observed outcome or user acceptance, recorded on the lesson. |

## Part II section 8: open planning questions

| Id | Question | Disposition |
| --- | --- | --- |
| Q-01 | How do the existing `ux-review` request and result contracts expose optional documentation outputs? | Resolved in Phase 3 and 6: documentation outputs are a separate request kind to the core, not a field on the review packet. The Lugos skill gains one additional invocation for it; review mode is untouched. Depends on the Lugos inspection for exact packet fields. |
| Q-02 | Which guide and token formats fit the current projects and which belong in the initial phase? | Resolved: Markdown guide and JSON design data first; HTML sheets per the reference format; no CSS token emission until a project has tokens to emit (Dias does not). |
| Q-03 | How are source inspection and rendered evidence captured, correlated and kept current? | Planned, Phase 1 evidence contract (capture manifest with revision, viewport, state, theme) and Phase 6 staleness check against the recorded revision. |
| Q-04 | Is the drawing reference invoked as a tool, adapted narrowly, or used as a presentation reference? | Resolved: adapted narrowly for static sheets; motion renderer deferred until verified. |
| Q-05 | How are source-specific notices and attribution preserved for copied material? | Resolved: the reuse map is the register; copied templates carry a header with license, upstream path and pinned commit. |
| Q-06 | How are guide changes, acceptance and unresolved values represented through existing project conventions? | Planned, Phase 2 and 6: committed files in the target repository; unresolved values are `[TBD]` entries listed in an "open values" section of the guide. |
| Q-07 | What validation proves a useful static guide before adding animation? | Resolved: Phase 7 entry requires one Dias component sheet whose values a second agent can trace to evidence without the author, plus a user acceptance of the sheet's usefulness. |

## Constraints from AGENTS.md and KICKOFF.md carried into the plan

| Id | Source | Constraint | Where honored |
| --- | --- | --- | --- |
| K-01 | AGENTS.md | Preserve `docs/CONCEPT.md` verbatim; plan in separate files. | This document set. |
| K-02 | AGENTS.md | Inspect the actual Lugos implementation and callers before planning extraction. | Lugos and Dias inspections, 2026-11-02; findings in the plan with citations. |
| K-03 | AGENTS.md | Preserve optional controls and bounded behavior. | Phase 3. |
| K-04 | AGENTS.md | Generation of guides, sheets and animations separately selectable. | C-34. |
| K-05 | AGENTS.md | Do not invent measurements. | C-41. |
| K-06 | AGENTS.md | Record source and license for copied material; do not install an overlapping toolset. | Reuse map; Impeccable hook not installed. |
| K-07 | AGENTS.md | Avoid extra orchestration, memory or review services before checking what exists. | Phase 1 reuses Lugos audit receipts and Autowork dispatch; no new service. |
| K-08 | KICKOFF item 6 | Staged migration preserving callers with recovery. | Phase 3. |
| K-09 | KICKOFF item 7 | Dias pilot covers the complete interaction, not a screenshot. | Phase 5 scenarios. |
| K-10 | KICKOFF item 8 | A second small project proving independence from Lugos and Dias. | Phase 1 fixture; Phase 8. |
| K-11 | KICKOFF | License selection belongs in the plan. | Decision log D-01 in the plan. |
