# Plan: a redesign-first method

Status: adopted 2026-11-02 by [D-21](../decisions/0021-redesign-first-method-adopted.md). Lifted from the firm copy, bwa-ux-recast (`docs/plan-redesign-first.md`, its commits `74b8d39` and `e653fba`), and first proven end to end in `mdn87/email-automation` PR #35. The working version with commands is [the playbook](../playbook-improve-ux.md). This plan adds a method on top of [the initial implementation plan](initial-implementation-plan.md); it does not replace any phase.

## Why

The goal is an agent that does product and interaction design on top of a working application: understand what the software does, work out how a person should accomplish their task, and produce an interface that makes that path clear and looks intentionally designed.

The bounded cycle ux-recast ported from Lugos does something narrower. It verifies an implementation against a task contract: it captures evidence, records findings, bounds one repair and reruns the checks. That finds defects and polishes screens. It never requires a better workflow, so an awkward organization survives every cycle. Fixing a form that wipes its fields is useful; it leaves untouched the questions that matter more. Why does this form exist? Why is the person entering information the application already knows? Why are related decisions on three screens?

Three things the cycle already has are the right foundation and are kept:

1. **The task contract written before the code.** It states the person's goal and observable acceptance, apart from the implementation.
2. **The plan-stage checkpoint.** A proposed flow can be reviewed before anything is built. The method makes it mandatory.
3. **The read-only reviewer.** The reviewer prompt gives the reviewer evidence only, never source. That is the fresh evaluator the method needs. The local-agent provider undermines it when the same agent that built the thing fills in the findings, so the method requires a fresh context for that step.

## What the outside references contribute

Checked against the current playbooks on 2026-11-02; the revisions are in [the reference register](../REFERENCES.md#redesign-method-references). Every one is read as text and adapted in this project's own words with its source named; none is invoked as a command, plugin, hook or MCP server by the method.

| Reference | Contribution | Not imported |
| --- | --- | --- |
| Impeccable `shape` | The brief structure: job and audience; outcome and proof; the selected direction (structural and interaction thesis, sequence, focal moment); scope and anti-goals; states and realistic content ranges; interaction and layout intent, not CSS; the open decisions a builder must not invent. | Its interview cadence and its stop at a confirmed brief. The method asks only when an unresolved fact would materially change the design, labels assumptions otherwise, and continues. |
| Impeccable `distill` | Reorganizing a surface around its one primary goal: consolidate, disclose progressively, remove what does not earn its place, and document what was removed and why. | Its "ask if unclear from the codebase" interruption. |
| Impeccable `critique` | Cognitive load, the heuristics and persona testing, as background for the evaluator. | Its mandatory detector run, 0 to 40 health score and closing question. A score is a signal, never the evidence (D-09). |
| UI UX Pro Max | Its UX guidelines on forms, feedback, progressive disclosure, navigation and predictable back behaviour, and the pre-delivery checklist. | Its design-system generator as a substitute for the brief. |
| Task analysis and cognitive walkthrough (Nielsen Norman Group) | The two inspection methods the stages are built on. | Nothing; these are references. |

Where a project already has the Impeccable skill installed, D-11 still applies: its agent commands may be used by name. The method itself needs none of them.

## The method

Five stages for one selected task. Artifacts live in the project under review, under `ux/<task>/`, beside the `.ux-review/` state the controller keeps.

1. **Recover the work and the constraints.** From the implementation, the current screens, process documentation and known complaints, write `brief.md` (`templates/brief.md`): who does the task and how often, what brings them, the result they need, what they already know, what the application can infer, remember or calculate, the mandatory rules with their sources, and the anti-goals. Derive the organization of the interface from the person's work: a database entity does not earn a navigation item, a backend operation does not earn a button, an existing screen boundary does not have to survive. Write the task contract `task.json`.
2. **Current flow and proposed flow.** `flows.md` (`templates/flows.md`): both flows as step tables, a reason for every kept step, structural changes with reasons, alternatives where the structure is open, the expert path, states and recovery. A fresh evaluator walks the proposed flow at a plan-stage checkpoint before anything is built. No cosmetic work is accepted before this exists.
3. **The complete visual design.** A working revision or an interactive prototype with realistic content and the states that matter. Two results do not pass: the old layout under a new palette, and a generic dashboard of cards. Where the project has an accepted `DESIGN.md` (D-16), stay inside it; otherwise seed one marked `basis: proposed`.
4. **Evaluate without giving the evaluator the answer.** The built result is captured through the real task and walked by a fresh evaluator at an implementation-stage checkpoint; one repair batch; then the implementer's functional verification, including failure and recovery paths. The walkthrough is an inspection by a model, not a test with people.
5. **The comparison record.** Before and after under the same content and conditions: the two flows, the structural changes with reasons, each improvement with its evidence labelled `observed` or `judgement`, what became of every finding, the verification, the assumptions, and a decision a person sets. No score; fewer clicks is not the objective.

**Acceptance criterion.** Starting from the working application, produce a revised experience that organizes the selected task around the person's goal, improves its visual hierarchy and presentation, and demonstrates the resulting flow with realistic content and relevant states.

## Tool changes (implemented with D-21)

1. `rubric/walkthrough.md`, a second reviewer assignment (goal, starting knowledge and the visible interface only; four questions per step; no inference from code), selected with `review --mode walkthrough` or `packet prepare --mode walkthrough`. Additive: the frozen `rubric.md` and `autowork-reviewer.md` are untouched and `rubric_version` stays 1 until Phase 4 (D-15). A walkthrough packet records `review_mode` and `rubric_version` in the outer packet; a review-mode packet is unchanged, so legacy parity holds.
2. `packet prompt [--out]` prints the claimed packet's exact task text so a fresh agent context can be given that and nothing else; its findings are recorded with the existing `findings` verb. No MCP registration, no hook.
3. The `comparison` contract and `schemas/comparison.schema.json` (`ux-recast/comparison@1`), with `templates/comparison.example.json`. Slice S2.6's comparison record (kinds, effort, the six decision values) extends this record rather than adding a second one.
4. Templates for the brief and the flows; the playbook; the `skills/improve-ux` skill.

## Open

- Whether the plan-stage walkthrough should be able to run through the Lugos Autowork lane as well as a fresh local subagent. The packet is the same either way; only who fills the findings differs.
- Whether any deterministic auditor (Impeccable `detect`, axe-core, Lighthouse) joins stage 4 by default. Phase 4's `impeccable_detect` pre-pass (S4.3) is where that would land.
