# Playbook: improve the UX/UI of a project

What an agent does when someone says "improve the UX/UI of this project", "redesign this", "this tool is awkward" or "review this interface". The method and its reasons are in [plans/redesign-first.md](plans/redesign-first.md) (decision D-21); this is the working version with the commands. The [`skills/improve-ux`](../skills/improve-ux/SKILL.md) skill packages it.

The job is product and interaction design on top of a working application: understand what the software does, work out how a person should accomplish their task, and produce an interface that makes that path clear and looks intentionally designed. Finding defects and polishing screens is part of the work, never the whole of it. An awkward organization that survives a cycle is a failed cycle.

Everything produced is advisory and a draft until a person has reviewed it. Say so in every deliverable.

## Shapes of the ask

| Ask | Stages | Output |
| --- | --- | --- |
| **Redesign** (default): "improve", "redesign", "make this usable", "this is awkward" | 1 to 5 on one selected task | Brief, flows, a working revision or prototype, walkthrough and verification, comparison record |
| **Assess**: "what would you change", "review this" | 1, 2 (current flow only), 4 on the current interface | Brief, the current flow with its problems, walkthrough findings ranked |
| **Fix**: "fix the error handling on X", a named defect | a bounded cycle on the existing flow | Findings, one repair, before and after evidence |

Unsure, ask in one line; otherwise Redesign. Everything below runs in the project under review; artifacts go under `ux/<task>/`, controller state under `.ux-review/`.

## 0. Tooling

```bash
ux-recast rubric --version
```

If that fails, install the package from a ux-recast checkout into the environment you run it from (`python -m pip install -e <ux-recast checkout>`); `python -m ux_recast.cli` works where the console script is not on PATH. Read the project's `PRODUCT.md` and `DESIGN.md` if present as the design context; do not modify them unless the redesign is accepted. Install nothing on the project or the machine without a person's go-ahead; the method needs no plugin, hook, MCP server or external design tool.

## 1. Recover the work and the constraints

Read the implementation, the current screens, process documentation and known complaints. Write `ux/<task>/brief.md` from `templates/brief.md`: who does this and how often, what brings them, the result they need, what they already know, what the application can infer, remember or calculate, the mandatory rules with their sources, the anti-goals, and the capabilities recovered from the code.

Derive the organization of the interface from the person's work, not from storage or processing. Mark assumptions `[assumed]`. Ask only when an unresolved fact would substantially change the design.

Write the task contract, `ux/<task>/task.json` (`ux-recast validate task`): the flow id, the goal in the person's words, starting conditions, expected outcome, device and input, source, assumptions, observable acceptance statements. It is the yardstick for everything that follows.

## 2. Current flow and proposed flow

Write `ux/<task>/flows.md` from `templates/flows.md`: the current flow as steps, with what the person must know or enter and where that comes from; the proposed flow with the structural changes and the reason for every kept step; alternatives compared briefly where the structure is open; the expert path; states and recovery. No cosmetic work is accepted before this exists.

Have a fresh evaluator walk the proposed flow before building. Put the proposed steps into `ux/<task>/evidence-plan.json` as `plan` (with current screenshots as `screenshots` if useful) and run a plan-stage checkpoint:

```bash
ux-recast control --project . --session <s> mode session --scope <task>
ux-recast control --project . --session <s> checkpoint --id <task>-plan --stage plan --affected <task> --task ux/<task>/task.json --input ux/<task>/flows.md --origin checkpoint
ux-recast review  --project . --session <s> --run <run> --evidence ux/<task>/evidence-plan.json --mode walkthrough
ux-recast packet  --project . --session <s> --run <run> prompt --out ux/<task>/handoff-plan.txt
```

Give a **fresh agent context** (a subagent started fresh, not a fork of this conversation) exactly the contents of the hand-off file and the listed visual inputs, nothing else: no code, no brief, no rationale. It fills the findings template; record them:

```bash
ux-recast findings --project . --session <s> --run <run> --file ux/<task>/findings-plan.json
ux-recast control  --project . --session <s> finish <run> --result remaining --report ux/<task>/flows.md
```

Revise the proposed flow for what the walkthrough found. Then stop for a person's acceptance of the direction before building (D-16 where the project has a design standard).

## 3. The complete visual design

Build the proposed flow as a working revision, or as an interactive prototype when the application cannot yet carry it, with realistic content and the states that matter. Work through the primary action and reading order; information grouping and useful density; how navigation, content and actions relate; typography, spacing, colour and component consistency; empty, loading, error and completion states; long content and realistic data volumes.

Two results do not pass: the old layout under a new palette, and a generic dashboard of cards. Where the project has `DESIGN.md`, stay inside it; where it has none, write the reusable decisions that emerge as a `DESIGN.md` seed marked `basis: proposed`.

Reference material for this stage, read as text and adapted: Impeccable's `distill` and UI UX Pro Max's UX guidelines on forms, feedback, navigation and disclosure (see [the reference register](REFERENCES.md#redesign-method-references)).

## 4. Evaluate without giving the evaluator the answer

Capture the built result through the real task with realistic content: screenshots and per-step observations at 375 px and the target desktop width, every state that matters (`fixtures/contact-request/test_flow.py` is the Playwright pattern). Run the functional verification first (see the lessons below), then bundle `ux/<task>/evidence-after.json` and take an implementation-stage checkpoint in walkthrough mode:

```bash
ux-recast control --project . --session <s> checkpoint --id <task>-build --stage implementation --affected <task> --task ux/<task>/task.json --input <changed files...> --origin checkpoint
ux-recast review  --project . --session <s> --run <run> --evidence ux/<task>/evidence-after.json --mode walkthrough
ux-recast packet  --project . --session <s> --run <run> prompt --out ux/<task>/handoff-after.txt
```

Same rule: a fresh context gets the hand-off text and the screenshots only. Record its findings with `findings`, confirm `packet consume` says `current`, then address what it found within the cycle's one repair batch (`control phase <run> repair`, re-checkpoint the repaired files with `--origin repair`, `control phase <run> verify`). Rerun the functional verification: the project's checks, the task's acceptance statements, and the failure and recovery paths (missing data, service unavailable, cancel mid-way, stale state). Finish the run:

```bash
ux-recast control --project . --session <s> finish <run> --result verified|remaining --report ux/<task>/comparison.json
```

The walkthrough is an inspection by an automated evaluator, not a test with people; say so.

## 5. The comparison record

Write `ux/<task>/comparison.json` (`templates/comparison.example.json`; `ux-recast validate comparison`): the same content and conditions on both sides, references to the two flows, the structural changes with reasons, each improvement with its before and after evidence labelled `observed` or `judgement`, what became of every walkthrough finding, the checks and failure paths run, the assumptions that remain, and `decision: pending`. A person sets the decision, with `decided_by` and `decided_at`. No score; fewer clicks is not the objective.

Deliver: the brief, the flows, the working revision or prototype, comparable before and after views, the comparison record, and the walkthrough findings. State what was observed and what is design judgement.

## Lessons from the first run

From the request-to-letter redesign of the email-automation intake companion (`mdn87/email-automation` PR #35: stages 1 and 2 in `64a198e`, stages 3 to 5 in `8654dd3`, artifacts under `ux/request-to-letter/`), run with the firm copy's equivalent commands (bwa-ux-recast):

- **Verify before the build-stage checkpoint.** The first build walkthrough's findings went stale because two verification fixes landed after its checkpoint bound the files. The run was finished `remaining` and a second checkpoint taken on the repaired page; that one took its single repair batch and finished `verified`. Land the functional verification's fixes first, then checkpoint. If a fix lands afterwards, do not repair on stale findings: finish the run `remaining` and walk the repaired page in a new run.
- **Prefix finding ids by run in the comparison.** Every run numbers its findings from F1, so `findings_disposition` ids name the run: `plan F1`, `build-1 F1`, `build-2 F1`.
- **Say when the evidence comes from a stand-in.** Both sides were captured against the test suite's stand-in for the letter generator. The evaluator raised findings about the stand-in's fixed answers; those were dispositioned `rejected` with that reason. Paths the stand-in cannot produce went under `assumptions` as not observed, never under `improvements`.
- **Keep the capture and verification scripts with the artifacts.** `ux/<task>/tools/` held the before capture, the after capture and a 24-check verification of the acceptance statements and failure paths. The after side reused the before side's synthetic seed, so the conditions matched by construction; the before README named the seed and that no real data was read.
- **Commit stages 1 and 2 on their own and wait.** The brief, flows and plan walkthrough landed before any page change; the five plan findings revised the proposed flow, and every one was addressed in the build. The owner's answers to the open questions were recorded with their date and cited as the reason for the structural changes they settled.

## Rules

- A better workflow is the requirement. Cosmetic work before `flows.md` exists is out of order.
- The fresh evaluator never sees code, brief or rationale; it gets the hand-off text and the images. If the same context that built the thing fills the findings, say so in `reviewer`, and treat the result as weaker.
- No finding without an observation; no `verified` without a rerun check; no score as evidence (D-09).
- Everything is a draft until a person reviews it. A redesign direction is implemented only after a person accepts it.
- Install nothing on the project or the machine without a go-ahead.
