# ux-recast

Design review, refinement, and reusable design knowledge for coding agents.

This is the repository seed for the concept-to-plan handoff. The working name selected in the conversation is `ux-recast`.

## Start here

1. Read [AGENTS.md](AGENTS.md).
2. Read [the complete concept record](docs/CONCEPT.md), including the optional style-guide and component-specification addition.
3. Give the planning agent [KICKOFF.md](KICKOFF.md).
4. Use the [reference register](docs/REFERENCES.md) to locate the projects discussed in the concept.
5. The planning pass of 2026-11-02 produced [the initial implementation plan](docs/plans/initial-implementation-plan.md), [concept traceability](docs/plans/concept-traceability.md), [the reuse and license map](docs/plans/reuse-and-license-map.md), and [implementation slices](docs/plans/implementation-slices.md). Implementation is not yet authorized.
6. To improve or redesign a project's UX with the package, follow [the improve-UX playbook](docs/playbook-improve-ux.md) (the redesign-first method, [D-21](docs/decisions/0021-redesign-first-method-adopted.md)); [`skills/improve-ux`](skills/improve-ux/SKILL.md) packages it as an agent skill and `templates/` holds the brief, flows and comparison templates.

The concept preserves the earlier recommendations and naming discussions in full. Earlier proposed names remain in that historical record; `ux-recast` is the current working name. The concept is not an implementation plan.

## Seed contents

| File | Purpose |
| --- | --- |
| `AGENTS.md` | Instructions for preserving the concept and conducting the initial planning work. |
| `docs/CONCEPT.md` | Unabridged user requests and substantive assistant proposals from the conversation, followed by the new optional documentation capability. |
| `KICKOFF.md` | Complete prompt for the agent that will inspect the existing functionality and build a plan. |
| `docs/REFERENCES.md` | Source links and their roles as already discussed. |
| `docs/playbook-improve-ux.md`, `docs/plans/redesign-first.md` | The redesign-first method and its working commands (D-21). |
| `skills/improve-ux/SKILL.md`, `templates/` | The method as an agent skill; brief, flows and comparison templates. |
| `docs/references/dimensional-drawing-assessment.md` | Inspection evidence for the newly supplied drawing repository. |
| `docs/references/dimensional-drawing-reference.png` | The user's visual reference supplied with the style-guide request. |

## Repository initialization

Extract this directory as the new repository root. The planning agent should use the current name and existing GitHub authorization when creating or connecting a remote. The conversation previously proposed the personal `mdn87` account; no remote URL is asserted by this seed.

ux-recast is licensed under [Apache-2.0](LICENSE); see [NOTICE](NOTICE). The references retain their own licenses. This seed does not vendor their source code or install their skills.
