---
name: improve-ux
description: Redesign, improve, review or critique the UX/UI of a project by organizing a task around the person's goal: brief, current and proposed flows, a complete visual design, a fresh-context cognitive walkthrough, verification and a before-and-after comparison, using ux-recast. Use when asked to improve the UX or UI of a project, redesign an interface, make a tool less awkward or more usable, review or critique a user interface, or suggest design improvements.
---

# Improve the UX/UI of a project

The job is product and interaction design on top of a working application: understand what it does, work out how a person should accomplish their task, and produce an interface that makes that path clear and looks intentionally designed. Finding defects and polishing is part of it, never the whole; an awkward organization that survives is a failed cycle. The tool is `ux-recast`; read its `docs/playbook-improve-ux.md` (commands and lessons) and the redesign section of `docs/REFERENCES.md` the first time you use this skill in a session. Templates: `templates/brief.md`, `templates/flows.md`, `templates/comparison.example.json`.

## Shape of the ask

| They said | Do |
| --- | --- |
| "improve", "redesign", "awkward", "make it usable" (default) | **Redesign**: stages 1 to 5 on one selected task |
| "what would you change", "review", "critique" | **Assess**: stages 1, 2 (current flow), 4 on the current interface |
| a named defect | **Fix**: one bounded cycle on the existing flow |

Unsure, ask in one line. Artifacts go in the project under `ux/<task>/`; controller state in `.ux-review/`.

## Stages

0. **Tooling.** `ux-recast rubric --version` (or `python -m ux_recast.cli rubric --version`); if missing, `pip install -e <ux-recast checkout>`. Read the project's `PRODUCT.md` and `DESIGN.md` if present. Install nothing without a go-ahead; no plugin, hook, MCP server or external design tool is needed.
1. **Brief.** From code, screens, docs and complaints: who does this and how often, what brings them, the result, what they already know, what the application can infer or remember, mandatory rules with sources, anti-goals, recovered capabilities. Derive the interface from the work, not from storage or processing. Mark `[assumed]`; ask only what would change the design. Write `task.json` with observable acceptance.
2. **Flows.** Current and proposed as step tables; a reason for every kept step; structural changes with reasons; alternatives compared where open; the expert path; states and recovery. Then a plan-stage checkpoint in walkthrough mode (`checkpoint --stage plan`, `review --mode walkthrough`, `packet prompt --out`): a **fresh subagent context** gets the hand-off text and images only, never code, brief or rationale; record its findings; revise the flow. Commit stages 1 and 2 and wait for a person to accept the direction. No cosmetic work before this exists.
3. **Visual design.** Build the proposed flow as a working revision or prototype with realistic content and states: primary action and reading order, grouping and density, navigation to content to actions, type, spacing, colour, components, empty/loading/error/complete, long content. Not accepted: old layout with a new palette; generic card dashboard. Stay inside `DESIGN.md` or seed one (`basis: proposed`).
4. **Evaluate.** Capture the real task at 375 px and the target width, every state, on the same synthetic seed as the before side. Run the functional verification and land its fixes, then take the implementation-stage checkpoint in walkthrough mode; fresh context again; record; `packet consume` must say `current`; address findings in the one repair batch (`phase repair`, re-checkpoint `--origin repair`, `phase verify`); rerun the verification. If a fix lands after the checkpoint, finish that run `remaining` and walk the repaired page in a new run. `finish --result verified|remaining`. The walkthrough is an automated inspection, not a user test; say so.
5. **Compare.** `comparison.json` validated with `ux-recast validate comparison`: same content and conditions, both flows, structural changes, improvements labelled `observed` or `judgement` with before and after evidence, findings disposition (ids prefixed by run: `plan F1`, `build-1 F1`), checks and failure paths, assumptions (including anything a stand-in could not produce), `decision: pending` for a person to set. Deliver brief, flows, the revision or prototype, before/after views, comparison, walkthrough findings.

## Rules

- The fresh evaluator never sees code, brief or rationale. If the building context fills the findings, name it in `reviewer` and treat the result as weaker.
- No finding without an observation; no `verified` without a rerun check; no score as evidence; fewer clicks is not the objective.
- Everything is a draft until a person reviews it; a redesign direction is implemented only after a person accepts it.
- Install nothing without a go-ahead.
