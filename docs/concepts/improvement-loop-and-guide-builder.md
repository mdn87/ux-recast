ux-recast will offer two independent features that can share evidence and design guidance.

The **Improvement Loop** evaluates proposed changes to a product, workflow, or review method and retains lessons supported by observed results. The **Guide Builder** turns a specific demonstrated process into clear, illustrated instructions that another person can follow.

The two features serve different purposes. A user can improve a workflow without producing a guide, or document an existing workflow without changing it. When used together, they connect observed friction, tested improvements, and documentation of the resulting process.

This concept defines the intended experience, feature boundaries, outputs, and measures of success. Technical architecture, dependencies, repository structure, and implementation scheduling remain for a later plan.

# Feature boundaries

| Area | Improvement Loop | Guide Builder |
| - | - | - |
| User goal | Make a selected experience or method demonstrably better | Explain how to complete a specific process |
| Starting material | A goal, current behavior, feedback, and a proposed change | A demonstration, existing recording, or established procedure with supporting evidence |
| Main activity | Compare a candidate against a baseline and check for regressions | Organize observed actions into instructions and check completeness |
| Primary output | An evaluated change, a decision, and a retained lesson | An editable illustrated guide with a stated verification status |
| Success | Useful improvement with acceptable effort and preserved critical behavior | The intended reader can complete the process from the instructions |
| Relationship | May identify changes worth documenting | May reveal problems worth evaluating |

The existing UX-review capability supplies a natural starting point for the Improvement Loop. Tutorial creation becomes a separate Guide Builder capability. Optional style guides can inform both.

# Feature 1 Improvement Loop

## Purpose

Turn individual reviews and revisions into a repeatable way to improve experiences and learn which methods help. The loop should make it possible to explain what changed, why it was attempted, what happened, and whether the result deserves continued use.

Initial applications include interface clarity, task completion, mobile usability, error recovery, and the quality of the review process itself. Dias mobile is a useful first product context because it provides concrete tasks and observable outcomes.

## Two kinds of improvement

**Product improvement** changes the experience being reviewed. Examples include making an action easier to find, clarifying a delivery state, reducing unnecessary navigation, or improving layout and hierarchy.

**Method improvement** changes how ux-recast reviews or refines experiences. Examples include a better critique rubric, more useful reference selection, clearer verification instructions, or a less expensive review that finds the same important problems.

These require separate comparisons. A successful redesign establishes a result for that product. A reusable review method needs evidence from additional cases. During each comparison, the intended outcome and the basis for judging it stay stable so the result remains interpretable.

## Intended experience

1. **Choose the focus.** Identify a specific flow or review problem, the people affected, and what improvement would mean.

2. **Establish the baseline.** Capture the current behavior, relevant screenshots, known problems, and critical behavior that must continue working.

3. **Propose a bounded change.** Explain the problem, the proposed adjustment, its expected benefit, and possible tradeoffs.

4. **Evaluate the candidate.** Apply or demonstrate the change within the selected scope and compare it against the same criteria.

5. **Decide what to retain.** Accept it, revise it, keep it local to the project, reject it, or record that the evidence is insufficient.

6. **Retain the lesson.** Preserve the result and its context so later work can use it without repeating the investigation.

The default experience remains optional and bounded: a selected flow, up to five substantive findings, and one review, repair, and verification pass. Additional rounds are deliberate choices when an unresolved issue justifies them.

## Evidence and judgment

Functional outcomes and design judgment need different evidence. Actual interactions, state readback, and receipts can establish whether an operation worked. Before-and-after comparisons and user evaluation can establish whether the result is clearer, more attractive, or easier to understand.

A successful action performed through an internal application helper does not establish that the visible user journey works. Usability claims require the supported user interaction.

Findings should distinguish an observed failure, a concern based on a design principle, and an unresolved question. A higher score from the same model that proposed a change is supporting opinion; the outcome needs corroboration appropriate to the claim.

The loop should record effort as well as benefit. Additional review time, repeated retries, false findings, and user intervention can outweigh a small quality improvement. Keeping the baseline is a valid result.

## Retained knowledge

Each lesson should explain the original problem, relevant evidence, attempted change, observed result, tradeoffs, and conditions under which it may apply.

Lessons can remain:

- **Candidates:** plausible ideas awaiting a useful comparison.

- **Project guidance:** supported by the current project's needs and evidence.

- **Shared guidance:** supported across additional flows or projects.

- **Rejected or superseded ideas:** retained with the reason they failed or stopped applying.

Generalization should be deliberate. A mobile approval pattern may help other approval interfaces while being unsuitable for a different kind of product. Shared guidance must preserve those conditions and the project's visual identity.

The user retains control over what becomes accepted practice. Routine comparisons can proceed within the selected scope; changing the scope, success criteria, or permission boundaries is a separate decision.

## Outputs and success criteria

A completed comparison produces a concise result: the baseline, candidate, supporting evidence, remaining limitations, and adoption decision. It may also produce a project lesson or a candidate for broader reuse.

Success means that important problems are resolved, critical behavior remains intact, and later reviews become more useful or efficient. More findings, longer reports, more instructions, and more iterations are not success measures by themselves.

For method improvement, success must hold on cases that were not used to develop the method. Shared guidance should remain revisable as products, models, and user needs change.

## Example

A Dias mobile review finds that a response appears successful before delivery is confirmed. A proposed revision makes the intermediate state clearer.

The comparison checks whether users understand the state, whether the displayed result follows actual delivery evidence, and whether reconnecting preserves an accurate view. A successful result can become Dias guidance. Its broader lesson remains a candidate until tested in other relevant flows.

# Feature 2 Guide Builder

## Purpose

Create useful tutorials, standard operating procedures, onboarding guides, and reference checklists from real processes. The finished document should explain both what to do and how to recognize the expected result.

The reader determines the level of detail. A first-time user's tutorial may explain prerequisites and terminology, while an experienced user's checklist can be shorter. Both can be derived from the same observed process.

## Starting information

Each guide begins with a purpose, intended audience, starting condition, required access or role, necessary inputs, and a clear completion condition.

Capture can come from three sources:

- **A user demonstration.** The user performs the process while actions and screenshots are recorded. Optional narration explains decisions and exceptions.

- **An agent demonstration.** The agent performs an agreed process within an appropriate authorized environment and collects the evidence.

- **Existing material.** A screen recording, screenshots, or a written procedure supplies part of the process. Missing actions or outcomes remain visible gaps until resolved.

For work procedures, recording a user demonstration is a practical initial mode. It captures established practice and allows the person performing the task to explain business rules that are not visible on screen.

## Intended experience

1. **Define the guide.** Select the process, audience, starting point, and desired output.

2. **Capture the demonstration.** Record meaningful actions, relevant screen states, control names, and any explanation.

3. **Organize the procedure.** Group related actions, remove accidental detours, and preserve required order, prerequisites, and conditional branches.

4. **Prepare the illustrations.** Select real screenshots that show the control before an action or the result afterward. Crop and annotate them while retaining enough context to orient the reader.

5. **Write and format the guide.** Produce clear instructions, expected results, and conditional notes using the chosen presentation style.

6. **Check the instructions.** Compare them with the evidence and, where practical, have another reader or agent follow the guide from the stated starting condition.

7. **Retain an editable source.** Keep the steps and their illustrations available for correction, alternate formats, and later updates.

Removing a mistaken click is editorial cleanup. Changing an approval sequence, required field, or business rule is a process change. The Guide Builder preserves the established procedure and records proposed improvements separately.

## Guide contents

The typical output includes:

- A descriptive title and purpose.

- Intended audience, prerequisites, required access, and inputs.

- Numbered instructions with actual control labels.

- Screenshots with purposeful highlights or callouts.

- Expected results at meaningful checkpoints.

- Relevant exceptions, decision branches, and recovery guidance.

- A final completion check.

- The application or process version, date checked, and verification status.

A captured choice does not explain why it was correct. Narration, an established procedure, or clarification from the process owner supplies that meaning. Unseen steps and uncertain business rules should remain identified gaps.

Word is the preferred editable document output, with PDF for distribution and HTML for an internal portal. The underlying steps and illustrations remain reusable so the same process can support both a detailed tutorial and a compact checklist.

## Verification and freshness

The guide should communicate the strength of its verification:

- **Captured:** assembled from a recorded demonstration.

- **Checked against evidence:** instructions and illustrations have been reconciled with the recording.

- **Followed in a separate trial:** another reader or agent completed the process using the guide from the stated starting condition.

- **Needs review:** a change or reported problem may have made part of the guide inaccurate.

An agent following the instructions can reveal missing or ambiguous steps. Validation by a representative human reader is stronger evidence of clarity for that audience.

Processes with meaningful side effects should use demonstration records or an appropriate test environment for repeat checks. Documentation work should not repeat a real submission, approval, deletion, or message.

Changes should be traceable to the affected steps. A renamed control may require a local correction; a changed approval flow may require broader review. Freshness checks and regenerated sections can be added later as optional capabilities.

## Outputs and success criteria

The main output is an editable illustrated guide with clear scope and verification status. Supporting outputs include identified gaps, process questions, and optional UX findings.

Success means the intended audience can complete the procedure, instructions and screenshots agree, and the guide requires less manual authoring and maintenance than the current approach. A polished document still needs complete and correct instructions.

## Example

A user demonstrates how to locate and review a draft invoice, narrating any relevant conditions. The Guide Builder organizes the observed process, selects screenshots, and produces an illustrated document.

Any confusing navigation or unnecessary repetition can become a separate UX finding. The guide can still describe the existing process accurately while that issue remains unresolved.

# Shared foundation

## Process goals and evidence

Both features use a clear description of the task, its audience, starting state, requirements, and expected outcome. They can reuse the same screenshots, action history, feedback, and verification results.

Evidence must remain connected to the claim it supports. Screenshots show an interface state. Actual interactions show that a user path can be performed. Receipts or state readback help confirm results and persistence.

## Optional style guidance

An optional style guide can inform visual consistency, preferred terminology, tone, and presentation.

Application design guidance concerns the product's interface. Document presentation guidance concerns headings, typography, captions, page structure, and screenshot treatment. Either may draw from the same brand, while preserving the needs of its medium.

Users should be able to supply existing guidance, generate a proposed guide, or work without one. A generated guide becomes authoritative through the user's decision to adopt it.

## History and user control

Preserve the relationship between the observed process, proposed changes, adopted decisions, and resulting guides. A later revision should not erase the context needed to understand an earlier result.

Both features respect the selected scope and existing permissions. Capturing or documenting a process does not grant authority to change the application, redefine business rules, or publish the output.

Work examples should use appropriate sample data or sanitized evidence. Screenshots, typed text, page content, and links all need consideration before a capture is shared or sent to an external writing service.

## Independence and portability

The capabilities belong conceptually in ux-recast and should remain useful independently of Lugos. Existing execution and measurement systems can supply context, run permitted actions, and consume results without becoming mandatory for basic use.

This plan assigns responsibilities by purpose. The choice of tools, runtime, integration boundaries, and storage belongs to implementation planning.

# Using the features together

A user may begin with either feature.

Starting with the Guide Builder, a demonstration produces a usable guide and may reveal friction. Selected findings can enter the Improvement Loop. If a change is adopted and the revised process is verified, the affected instructions can be updated from new evidence.

Starting with the Improvement Loop, a reviewed flow may produce a tested improvement and a retained lesson. The user can then choose to document the resulting process with the Guide Builder.

These handoffs are optional. An awkward workflow can still be documented. A product improvement can be completed without creating training material.

When the loop improves the Guide Builder's own writing or screenshot-selection method, that remains a method experiment. A nicer-looking document becomes evidence of a useful improvement only when the chosen criteria, reader results, and authoring effort support that conclusion.

# First useful outcomes

The first useful outcome for the **Improvement Loop** is a bounded comparison on one Dias mobile flow: a recorded baseline, a proposed revision, evidence of the result, and a clear adoption decision. The resulting lesson is then considered on a separate relevant flow before being promoted as reusable guidance.

The first useful outcome for the **Guide Builder** is one real process converted into an editable illustrated document, checked against its source evidence and followed independently where practical.

The combined outcome is a traceable connection between a known problem, an accepted improvement, and accurate instructions for the resulting experience.

Later possibilities include comparisons among several candidate methods, broader transfer of lessons, selective guide refreshes, different reader versions, and interactive or narrated walkthroughs. Each should address a demonstrated need after the core outcomes are useful.

# Design references

These references inform the concepts. Selecting or adopting a dependency remains a later decision.

- [DarwinX and Beagle](https://github.com/SalesforceAIResearch/Beagle): evaluated harness changes, preserved baselines, and recorded lineage.

- [MetaHarness Darwin](https://github.com/ruvnet/metaharness/tree/main/packages/darwin-mode): separate candidate development and confirmation.

- [aSPARK](https://github.com/a-lottes/aSPARK): continuity between acceptance criteria, review, and browser verification.

- [Mimik](https://github.com/westpoint-io/mimik): browser demonstrations converted into illustrated, editable guides.

- [OpenSteps](https://github.com/ebanez8/openstep): capture and editing of Windows desktop procedures.

- [Playwright](https://playwright.dev/docs/codegen): recorded browser interactions that can support repeatable demonstrations and checks.
