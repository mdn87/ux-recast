# Agent instructions for ux-recast

## Initial task

This repository starts as a concept seed. Follow `KICKOFF.md` to produce the initial implementation plan. The initial handoff is a planning task. A later explicit user instruction may authorize implementation.

## Preserve the source record

- Read all of `docs/CONCEPT.md` before forming the plan.
- Preserve its historical conversation text. The user explicitly requested all suggestions without reanalysis or summary. Do not replace that text with a shorter specification, remove alternatives, or silently reinterpret a proposal as a settled decision.
- Put the implementation plan and new evidence in separate files. Record changes of direction explicitly, with the relevant concept section and reason.
- The chosen working name is `ux-recast`. Other names appear only because the naming discussion is preserved.
- A user instruction takes precedence over an assistant suggestion. Earlier tool recommendations are candidates to evaluate in the implementation plan, not already-installed dependencies.

## Existing work and scope

- Inspect the actual current Lugos `ux-review` implementation and its callers before planning an extraction or replacement. Paths cited in the concept or kickoff are discovery leads until confirmed in the checkout.
- Preserve the optional review controls and bounded review behavior already established in Lugos.
- Plan a standalone core with a narrow Lugos integration. Dias is the first validation project; its product-specific details belong in Dias.
- Preserve the roles assigned to Impeccable, Happy, UI UX Pro Max, and React Grab, including the qualifications in the concept. New source findings may change the plan, but must not rewrite the historical record.
- Include the optional style-guide and component-specification capability. Generation of guides, dimensional sheets, and animated presentations must be separately selectable.

## Evidence and design decisions

- Distinguish observed implementation, measured rendered behavior, proposed designs, estimates, and unknowns.
- Do not invent measurements or imply a schematic is an exact implementation specification. Missing values remain explicitly unresolved.
- Preserve accepted and rejected changes, their reasoning, and the associated before/after evidence when available.
- Keep project-specific visual decisions separate from reusable UX lessons.
- Treat model critique and self-scoring as review signals. Plan verification of actual user tasks and observable behavior.
- Record the source and license when proposing copied or adapted third-party material. Do not silently install an entire overlapping toolset.

## Deliverable discipline

- Keep the complete concept in `docs/CONCEPT.md`.
- Write the initial plan separately, with a traceability map covering every substantive proposal and the new documentation capability.
- Mark unverified assumptions and concrete access blockers. Continue all planning that is possible with available evidence.
- Avoid creating extra orchestration, memory, or review services before checking what the existing system already provides.
