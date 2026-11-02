# Contextual rubric and evidence

This rubric is self-contained for remote workers. It distills the established interaction principles already used by the local UX knowledge base and the operator's development-review requirements. Original course materials are not bundled. Optional background in `ux-knowledge-base`, when available:

- `02-ideation-prototyping-testing/user-flow-analysis.md`: task steps and opportunities.
- `02-ideation-prototyping-testing/usability-test-plan-and-script.md`: outcome-led tasks.
- `02-ideation-prototyping-testing/usability-test-analysis-and-reporting.md`: observation versus inference, before/after evidence.
- `03-ui-foundations/heuristic-evaluation.md`: Nielsen heuristics and contextual review.
- `03-ui-foundations/accessibility-checks.md`: accessible interaction.
- `04-interaction-systems-responsive/web-form-design.md`: input and recovery.
- `04-interaction-systems-responsive/ui-components-and-interaction-states.md`: state coverage.

## Questions that change implementation decisions

| Principle | Review question | Possible choice, subject to context |
|---|---|---|
| Discoverability and signifiers | Can users find the next action and anticipate its result? | Verb-and-object action labels; visible primary action |
| Hierarchy and grouping | Does order, proximity and readable content explain what belongs together? | Group dependent inputs and put instructions before the decision |
| Consistency and mental models | Does the flow match product conventions and user terminology? | Reuse established navigation and domain labels |
| Recognition over recall | Must users remember hidden information or re-enter known values? | Keep relevant context visible and preserve valid entries |
| Visibility of system status | Can users distinguish waiting, saving, completion and failure? | Explicit progress and completion feedback; avoid duplicate submissions |
| Error prevention and recovery | Are mistakes preventable, discoverable and recoverable? | Field-specific errors, draft retention, retry from the failed step |
| User control and freedom | Can users back out or cancel safely? | Clear cancellation outcome and preserved unfinished work |
| Accessibility and input parity | Can the intended keyboard/touch/pointer user complete the task? | Labels, focus visibility/order, announced status, usable targets and reflow |

Fewer clicks, controls, words or screens are not inherently better. Consider error cost, comprehension, decision load and reversibility. A deliberate confirmation may protect an expensive action. A short label may be ambiguous. Automated accessibility checks supplement, not replace, keyboard and rendered-state checks.

## Finding record

Record: ID; category; task/step; observed behavior; evidence path or reproducible steps; named principle; likely user consequence (inference); severity; confidence with supporting reason; proposed correction; verification against original outcome; status and remaining uncertainty.

- **Observed failure**: reproduced breakage, information loss, inaccessible interaction, or failed intended outcome. Describe actual browser/app behavior, not just a suspicious code path.
- **Heuristic concern**: plausible friction predicted by a named principle. Do not label a guess about comprehension an observed user failure.
- **Unresolved question**: requires user research, preference or domain knowledge. Record the decision needed and why it matters.

Severity anchors (introduced by this capability, not claimed as part of the original course):

- **Critical**: irreversible loss or a central task impossible with no workable recovery.
- **High**: main task blocked for a relevant group or substantial work lost; workaround is burdensome.
- **Medium**: recoverable errors, repeated effort or an important ambiguity with a feasible workaround.
- **Low**: localized friction or presentation issue with small task impact.

Confidence: **high** for repeatable direct evidence; **medium** for a clear principle/context match with incomplete behavioral evidence; **low** for an uncertain prediction. These are evidence descriptions, not probabilities. A severe hypothetical consequence is still a low-confidence concern until supported.

Agent execution time is not human time-on-task. Agent-generated feelings, personas or SUS answers are not participant evidence. Screenshots show visible states, not proof that humans comprehend them. Keep these limits explicit where they affect a conclusion.
