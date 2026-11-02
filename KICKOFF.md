# ux-recast: planning kickoff

You are starting work in the new `ux-recast` repository. Your assignment is to build an implementation plan from the complete concept and the existing code. The user selected this working name and asked for a repository seed containing every suggestion from the originating conversation, without reanalysis or summary, plus this separate planning prompt.

Read `AGENTS.md`, then read **all of `docs/CONCEPT.md`**, `docs/REFERENCES.md`, and `docs/references/dimensional-drawing-assessment.md`. View `docs/references/dimensional-drawing-reference.png`. Do not substitute the README or this prompt for the complete concept.

## What to accomplish

Prepare an actionable, evidence-backed plan for extending the existing Lugos `ux-review` functionality into a standalone reusable project. The scope includes the design critique, refinement, feedback, and retained design knowledge described in the concept, plus optional project style guides, component dimensional specifications, and separately optional animated presentations of those specifications.

The initial assignment ends with the planning deliverables. Do not begin the production implementation merely because the concept describes possible features. Do the useful inspection and planning work autonomously, and ask only about a decision that genuinely blocks the plan and cannot be resolved from the provided context or existing authorization.

## Preserve the complete concept

The historical source record in `docs/CONCEPT.md` is intentional. Do not rewrite it into a summary, prune alternatives, replace it with the plan, or re-run the earlier recommendation exercise. Preserve the original suggestions, qualifications, and naming history. Treat the final working name as `ux-recast`.

The plan may resolve implementation choices based on the actual current code. Record any changed direction separately and explain what evidence caused it. Distinguish user decisions, assistant proposals, new source findings, and open implementation decisions. Do not silently promote all proposals into mandatory first-release requirements.

## Inspect the existing implementation

Locate the actual current Lugos checkout and read its applicable instructions. The previously identified discovery leads are:

- `plugins/lugos-toolset/skills/ux-review/`
- `.agents/skills/ux-review/`
- `autowork_review.py`
- The Lugos MCP dispatch path and associated review packets, snapshot/evidence handling, tests, configuration, and result delivery.

Confirm these paths and relationships rather than assuming they are still current. Determine which location is canonical and how any mirror is maintained. Inspect the call sites, interfaces, lifecycle, enable/disable behavior, bounded review/repair behavior, and delivery of screenshot evidence. Identify what is implemented, what has only been proposed, and what has been verified in a real run.

Map the existing contracts that a standalone extraction must preserve. Locate the existing project mechanisms for outcomes, acceptance feedback, durable records, and orchestration before proposing new ones. Keep actual source citations or file paths with each important architectural conclusion.

Locate the current Dias mobile implementation as the first integration and validation target. Confirm its framework, component conventions, existing design tokens, pending-request presentation, input paths, and delivery/resumption receipts. Do not make production changes during this planning pass.

If a required checkout is unavailable, list the exact unavailable evidence and continue with a clearly provisional interface plan. Do not fabricate an inspection or claim a migration is safe without seeing its consumers.

## Evaluate reuse against the concept

Use the reference register to inspect only the details needed for the plan. Preserve the roles already proposed:

- Impeccable: design critique, targeted refinement, implementation audit, and persistent product/design context.
- Happy: mobile-session interaction and implementation reference for Dias.
- UI UX Pro Max: optional searchable design guidance and project design-system persistence.
- React Grab: optional source-aware visual feedback for compatible interfaces.
- Dimensional Drawing: optional component anatomy/specification sheets and separate motion presentation.

For each proposed reuse, decide whether the plan calls for an external tool, an adapter, a narrowly adapted component or rubric, a documented reference, or a deferred option. Identify the relevant version or commit, license, integration assumptions, and overlap with existing functionality. Keep credits and notices for copied or adapted material. Do not automatically import every candidate or install global hooks.

The new drawing repository has been inspected as a focused skill/template reference. Read its assessment for the exact verification performed and outstanding execution limits. Its drawing output is one part of the broader optional style-guide feature. Its motion feature animates a specification sheet; it does not establish the product's interaction motion behavior.

## Build the plan

Derive the implementation sequence from the concept and current code. Address:

1. The standalone core, narrow provider/project adapters, and the Lugos `ux-review` entry point.
2. Contracts for review requests, rendered evidence, findings, revisions, acceptance/rejection, and observed outcomes.
3. Separation of project-specific design context from shared review guidance and reusable lessons.
4. Optional controls, bounded review/repair/verify cycles, and integration with existing orchestration.
5. The style-guide and component-specification capability, including its input evidence, generated formats, unresolved values, provenance, state/viewport coverage, and separate motion option.
6. A staged migration that preserves existing callers and permits recovery if the extraction introduces a regression.
7. A first Dias mobile validation scenario that covers the complete interaction, not only the appearance of a screenshot.
8. A second, small project or fixture that can demonstrate the core does not require Lugos or Dias-specific infrastructure.

Use the concept's complete proposals and caveats to decide the phase boundaries. Keep optional and deferred ideas visible. Prefer existing conventions and the smallest coherent implementation that can prove the end-to-end behavior. Make the proposed work concrete enough for another agent to implement without rediscovering the architecture.

## Planning deliverables

Create these as separate documents, adjusting the directory convention only if this repository already establishes a better one:

- `docs/plans/initial-implementation-plan.md`: ordered phases, dependencies, acceptance criteria, likely files/modules, migration and recovery approach, and unresolved decisions.
- `docs/plans/concept-traceability.md`: a row for every substantive concept proposal or constraint, with its source section and planned disposition. Use implemented/proposed/deferred/not-applicable distinctions accurately; do not silently drop suggestions.
- `docs/plans/reuse-and-license-map.md`: existing Lugos functionality and external references mapped to the proposed reuse, evidence, attribution, and version assumptions.

Use a concise decision log within the plan for choices that materially affect architecture, scope, or later reversibility. Do not create a second planning system just to hold this initial work.

## Verification expectations for the plan

Make the acceptance criteria observable. For the Dias pilot, retain the concept's complete request and response flow: find the blocked session, understand the full request, respond to the correct session, distinguish submission from receipt and resumption, and exercise long content, keyboard obstruction, stale state, and reconnects.

For style-guide output, account for provenance, complete token references, consistent units, variable/formula validity, legibility, state and viewport differences, and explicit unknowns. Verify any claim of exact measurement against source or rendered evidence. Keep the project's actual visual design distinct from the monochrome presentation of its dimensional sheets.

For the learning capability, plan how accepted and rejected changes, before/after evidence, and observed outcomes inform subsequent work. A model raising its own score does not by itself demonstrate a better user experience. Preserve project identity while allowing supported cross-project lessons to accumulate.

Finish by linking the planning documents and reporting the substantive decisions and remaining blockers. Do not report production code, a GitHub repository, or an integration as completed unless you actually created and verified it under the user's authorization.
