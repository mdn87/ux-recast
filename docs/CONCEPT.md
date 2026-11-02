# ux-recast: complete concept record

Working name: `ux-recast`  
Prepared: November 1, 2026, America/New_York  
Status: concept seed for a separate planning pass

## Preservation convention

Part I reproduces the substantive user requests and complete assistant proposals from the originating conversation in order. The earlier recommendations, caveats, alternatives, and naming discussion are retained without rewriting, reranking, or condensation. Chat citation widgets have been converted to ordinary source links so the record works outside ChatGPT. Wrapper headings identify the turns; intermediate tool plumbing is not part of this concept record.

The current working name is `ux-recast`. Earlier suggested names remain in the historical text. An assistant suggestion is not automatically a user-approved implementation commitment. The user's request to prepare this seed and add an optional style-guide capability appears at the end of Part I. Part II adds that new capability without changing the earlier proposals. The separate `KICKOFF.md` asks the next agent to build the implementation plan.

## Part I. Conversation proposals, preserved in full

### Turn 1. User: original goal

> i want to find something to use for inspiration on making the dias mobile interface a better user experience and look sharper

### Turn 2. User: reusable open-source direction

> perhaps something open source that we could use to self-improve the system for doing similar work on other projects

### Turn 3. Assistant: complete research recommendation

**[Impeccable](https://github.com/pbakaus/impeccable) is the strongest fit I found for that.** It is an open-source toolkit for improving a coding agent’s design work, with commands for critique, mobile adaptation, visual refinement, and documenting a project’s design system. It uses Apache 2.0 and supports Claude Code, Codex, Gemini CLI, and other agents. [Source](https://github.com/pbakaus/impeccable)

I’d use it to strengthen the **optional `ux-review` workflow we’ve been developing in Lugos**, with Dias mobile as the first practical test. For an actual interface to study alongside it, **Happy is a particularly close open-source reference**.

#### The useful shortlist

| Project | What it contributes | How I would use it |
|---|---|---|
| **[Impeccable](https://github.com/pbakaus/impeccable)** | Design critique, implementation audits, targeted refinement, persistent product and design context. **Apache 2.0.** | The main design improvement capability for our agents. [Source](https://github.com/pbakaus/impeccable) |
| **[Happy](https://github.com/slopus/happy)** | A working mobile and web interface for coding sessions, messages, and permission requests. **MIT.** | Study its phone workflows and source for Dias-specific ideas. [Repository](https://github.com/slopus/happy) · [Mobile documentation](https://happy.engineering/mobile-app/) |
| **[UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** | Searchable design guidance and a persistent project design system with page-specific overrides. **MIT.** | A reference library for typography, color, interaction patterns, and implementation guidance. [Source](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| **[React Grab](https://github.com/aidenybai/react-grab)** | Connects an element selected in the browser to its source context. Exposes primitives for building your own selection interface. **MIT.** | Let you point at a Dias component and give feedback the agent can connect to the right code. [Source](https://github.com/aidenybai/react-grab) |

**I would start with Impeccable and Happy.** The other two become useful when we identify a specific gap.

#### Why Impeccable is more relevant than another component library

Its useful distinction is between **design quality** and **implementation quality**.

Its `critique` command reviews hierarchy, clarity, usability, and character. It can inspect the rendered page when browser tools are available, and saves reviews so later refinement can use the findings. Its `audit` command separately examines accessibility, performance, theming, responsive behavior, and implementation problems. Those are useful inputs to the review system you already have. [Critique](https://impeccable.style/docs/critique/) · [Audit](https://impeccable.style/docs/audit/)

For Dias, I would map its capabilities to concrete work:

| Capability | Dias application |
|---|---|
| **`critique`** | Determine whether the question or pending action is immediately understandable, and whether session metadata is competing with it. |
| **`adapt`** | Rework the interaction for phone use, including the available space, controls, and task. |
| **`harden`** | Address long content, missing states, errors, and overflow. |
| **`polish`** | Refine typography, spacing, alignment, and visual consistency after the flow works. |
| **`document` / `extract`** | Preserve the accepted design rules and consolidate patterns we actually reuse. |

Those are documented capabilities; the Dias applications above are my proposed use of them. [Repository](https://github.com/pbakaus/impeccable) · [Adapt](https://impeccable.style/docs/adapt/) · [Document](https://impeccable.style/docs/document/) · [Extract](https://impeccable.style/docs/extract/)

For a quick visual assessment, its **[comparison gallery](https://impeccable.style/gallery/)** includes dashboard-oriented examples under **Observability** and **Infrastructure**. Treat those as the maintainer’s showcase, not independent proof that it will improve Dias. [Source](https://impeccable.style/gallery/)

#### Happy gives us something concrete to borrow from

Happy’s mobile documentation covers reading sessions and changes, sending messages, answering permission requests, and stopping a turn. Its repository contains the iOS, Android, and web client in `packages/happy-app`, built with Expo. That makes it a much closer functional reference than a generic dashboard template. [Mobile documentation](https://happy.engineering/mobile-app/) · [Repository](https://github.com/slopus/happy)

The parts I would inspect first are:

- **Session list hierarchy:** what remains visible before opening a session.
- **Pending requests:** how the requested decision relates to the surrounding conversation.
- **Output presentation:** how tool activity and long responses remain readable on a phone.
- **Returning to a session:** how notification entry and retained access affect the interaction.

This is a source to investigate for patterns and selectively reusable code. Compatibility with Dias’ existing sessions and control paths would still need examination.

#### How this could improve the system across projects

**The lasting improvement comes from retaining evidence about which changes worked.** Installing a design skill gives agents better instructions; we would build the learning process around its output.

I would extend the existing review workflow like this:

1. **Capture the starting point.** Save the relevant screens, task, viewport, and current problems. For Dias: find the blocked session, understand its request, respond, and verify that it resumed.

2. **Run a focused critique.** Give the reviewer both the rendered interface and the task. Each finding should identify the affected element, the user difficulty, and the evidence.

3. **Make a bounded revision.** Change one flow or a small related group of components, then inspect the same scenarios again.

4. **Record the outcome.** Keep the before and after, your accepted or rejected decisions, the reasoning, and any observed improvement or regression.

5. **Promote useful lessons.** Put project-specific choices into that project’s design guidance. Add broadly applicable lessons to the shared review rubric only when the evidence supports them.

Impeccable already provides part of the persistence structure: `PRODUCT.md` records the audience, tasks, and constraints; `DESIGN.md` records the visual system; saved critiques preserve review history. Our contribution would be connecting those records to accepted changes and actual outcomes. [Init](https://impeccable.style/docs/init/) · [Document](https://impeccable.style/docs/document/) · [Critique](https://impeccable.style/docs/critique/)

For example, **“show the complete pending question before secondary session metadata”** could become a reusable interaction rule. **“Dias uses red for needs-input status”** should remain a Dias design decision. Keeping that distinction would let TableForge, the work portal, and other projects benefit without inheriting the same appearance.

##### The first Dias test I would choose

Use three connected screens:

- **Needs you:** pending approvals, questions, planning choices, and manual actions.
- **Request detail:** complete context and choices, with a clear way to respond.
- **Response status:** distinguish submission, receipt by the session, and resumed work.

Then compare the old and revised versions on **taps and scrolling required, completeness of the request, clarity of the action, and confidence that the response reached the correct session**. Have the review also cover long questions, the phone keyboard, stale sessions, and reconnects.

I have verified these projects’ documentation and relevant source, but haven’t run them against Dias. The critical test is whether the revised interface makes those tasks easier and earns your acceptance. An agent awarding its own design a higher score is only a review signal.

### Turn 4. User: new repository and naming

> lets spin up a new repo and extend the ux-review functionality into it.. what should i call it

### Turn 5. Assistant: complete first naming and repository-boundary proposal

I’d call it **Cruth**. Irish *cruth* means **shape or appearance**, which fits a system that evaluates interfaces, improves their design, and retains what worked. [Source](https://www.teanglann.ie/en/fgb/cruth)

It fits alongside **Lugos, Dias, Torc, and Bran**, and leaves room for more than reviewing an existing screen.

| Name | Meaning | Fit |
|---|---|---|
| **Cruth** | Shape, appearance. | **My pick.** Broad enough for design exploration, critique, refinement, and reusable design knowledge. |
| **Snas** | Finish, polish, good appearance; also elegance of style. | Catchier and shorter, but suggests visual finishing more than deeper interaction design. [Source](https://www.teanglann.ie/en/fgb/snas) |
| **Cuma** | Shape, form, appearance, look. | Compact and appropriate, though less distinctive to my ear. [Source](https://www.teanglann.ie/en/fgb/cuma) |

One naming wrinkle: **Cruth is already used by an unrelated iPad sculpting project**, so it isn’t a globally unique software name. [Source](https://www.fiavaion.com/)

#### Proposed repo

**`mdn87/cruth`**

**Description:**  
Design review, refinement, and reusable design knowledge for coding agents.

I’d give the split a clear boundary:

- **Cruth owns** the design guidance, review rubrics, reference analysis, critique reports, refinement workflows, and accepted design lessons.
- **Lugos’ `ux-review` remains the entry point**, calling Cruth through a small integration while keeping its existing enable/disable controls and review limits.
- **Dias is the first project used to validate it**, with its specific interface requirements kept in Dias.

The core should work without Lugos so you can also use it with PADL, work projects, or a standalone coding agent.

### Turn 6. User: expand naming beyond the Lugos convention

> hmm maybe another brainstorm and we dont have to stay inside lugos naming conventions

### Turn 7. Assistant: complete broader naming brainstorm

**Sightline, Recast, and Formative** are stronger candidates once we drop the Celtic constraint. They suggest a broader capability for developing design judgment and improving work over time.

#### Design judgment and critique

| Name | What it suggests |
|---|---|
| **Sightline** | Seeing what matters, directing attention, and understanding the interface from the user’s perspective. |
| **Caliper** | Precision, proportion, and checking whether a design fits its purpose. Has a useful workshop feel. |
| **Redline** | Concrete, actionable critique. Strong if annotated reviews remain central. |
| **Touchstone** | A dependable standard against which work is evaluated. Fits reusable examples and accumulated knowledge. |
| **Keen** | Perceptive, discerning, sharp. Short and flexible, although fairly abstract. |

#### Craft and refinement

| Name | What it suggests |
|---|---|
| **Recast** | Reshaping existing work into something better. Fits both interface changes and improving the process itself. |
| **Temper** | Developing stronger work through controlled refinement. Substantial without sounding corporate. |
| **Hone** | Continual improvement through small, deliberate changes. Probably the most direct name. |
| **Contour** | Form, structure, and visual relationships. Strong design identity. |
| **Poise** | Balance, restraint, and confident composition. More expressive and less technical. |

#### Learning and visual memory

| Name | What it suggests |
|---|---|
| **Formative** | Evaluation that helps shape the next result. Closest to the full review, improve, learn cycle. |
| **Afterimage** | Retaining something from what was seen before. A more distinctive identity for visual memory and learned preferences. |
| **Margin** | Observations and feedback alongside the work. Quiet, approachable, and suited to a tool that assists other agents. |
| **Reframe** | Revisiting assumptions and finding a better way to present or solve something. |
| **Second Look** | A deliberate review with fresh eyes. Immediately understandable; repo slug would be `secondlook`. |

#### My picks for this project

**Sightline** is my favorite overall. It has a clear connection to visual judgment, but also fits attention, usability, and understanding a workflow. It sounds natural in use: “Run a Sightline review on the mobile flow.”

**Recast** is the strongest if the system will actively redesign and implement improvements. “Give this screen a Recast pass” works well.

**Formative** best expresses the longer-term ambition: each review contributes to better work on the next project. It has the strongest conceptual fit, though it feels more academic.

**Afterimage** is the most interesting creative choice. I’d favor it if you want the project to have a more distinctive visual identity and make retained design knowledge a central feature.

### Turn 8. User: selected working name, optional guide, and seed deliverables

> i'll just do something like ux-recast ... can we add in something that can optionally create a style guide kinda like this thing ... then we want to prepare a repo seed with the concept document including all suggestions from this chat without reanalysis or summary then also a kickoff prompt for the agent to start building a plan from the concept

Attached reference: [dimensional-drawing-reference.png](references/dimensional-drawing-reference.png).

The screenshot identifies `enesozturk/dimensional-drawing`: <https://github.com/enesozturk/dimensional-drawing>.

### Turn 9. User: verify the new reference

> did you check out the repo from the screenshot or is it junk?

### Turn 10. Assistant: source-review response during preparation

Yes. I’ve checked the repo, and the source review found a useful, focused skill pack: it has card and dialog examples, instructions for deriving measurements from source and rendered CSS, and an optional Playwright/ffmpeg video renderer. Unknown dimensions must stay marked `[TBD]`.

I’d borrow it for component specification sheets. A full style guide would be our addition, covering color, typography, states, accessibility, and usage rules. I haven’t run the renderer, so I’m treating its execution claims as unverified while I finish the seed package.

### Turn 11. Assistant: new-reference execution limitation

The renderer has two concrete rough edges: it ignores ffmpeg’s exit code and doesn’t create the output folder for video exports. It’s worth borrowing, with those fixes before unattended use. I couldn’t run an export here because Chromium is missing.

The seed structure and kickoff prompt are written. I’m preserving the earlier proposals in full, including the alternatives and naming history, and adding the style-guide feature separately.

## Part II. Additive concept: optional style guides and component specifications

This section adds the newly requested capability. It does not revise or replace Part I and does not establish an implementation sequence. The invocation syntax, implementation stack, module layout, and phase boundaries remain for the planning agent.

### 1. Optional capability and selectable outputs

ux-recast should be able to create or update a project's style guide when requested. The capability should use the accepted project direction, existing interface evidence, and retained design decisions. Ordinary review and refinement should remain usable without generating a guide.

The requested output should be selectable at three levels:

- **Project style guide:** a readable account of the visual and interaction system, with examples and reusable rules.
- **Component specifications:** measured or explicitly schematic anatomy sheets for selected components, suitable for implementation and review.
- **Animated specification presentation:** an optional presentation of a completed component sheet, useful for explaining its layers and relationships.

A guide may include component sheets, and a component sheet may be requested on its own. Animation is separately optional. These choices should remain independent of the optional Lugos review switch and of the project's actual animation behavior.

### 2. Project style-guide content

The guide can cover the following where supported by the project and requested scope:

- Product audience, primary tasks, tone, and design principles already accepted for that project.
- Color palette, semantic colors, status meanings, theme variants, and contrast expectations.
- Typography, hierarchy, text roles, density, line height, and content behavior.
- Spacing, sizing, grids, alignment, borders, radii, elevation, and responsive rules.
- Component anatomy, variants, usage guidance, and relationships to shared components.
- Interaction states, including loading, empty, selected, focused, disabled, error, stale, and disconnected states where relevant.
- Input and navigation conventions, feedback, confirmation, recovery, and the distinction between an action being submitted and actually completed.
- Accessibility expectations, keyboard and touch behavior, focus visibility, readable scaling, and motion preferences.
- Product motion rules and timing where the product has an accepted motion system.
- Examples of accepted use, counterexamples, unresolved design questions, and the reasons behind significant decisions.

The actual product determines which sections apply. Dias-specific status meanings or interface constraints should not silently become defaults for every project.

### 3. Evidence, observed design, and proposed design

Guide generation may document the existing interface, describe an accepted redesign, or propose a direction for review. The output must say which of those it represents.

Inputs may include existing project documentation, source components, design tokens, component stories or fixtures, rendered pages, accepted design examples, screenshots, and recorded review decisions. Approved project guidance remains authoritative. An inspirational reference should not silently overwrite that guidance.

For meaningful values and claims, retain their origin: source or token, rendered measurement, accepted decision, explicit proposal, or unresolved value. Record the relevant component, state, viewport, theme, and source revision when available. A screenshot can support a visual observation without proving the underlying CSS value or the behavior at another viewport.

Unknown measurements must remain unresolved. Estimates should be identified as estimates, and exact-looking drawings should not be used to imply precision that the input cannot support. Distinguish CSS units from screenshot pixels where that distinction affects a measurement.

### 4. Dimensional component sheets

The supplied reference is a focused implementation and presentation source for this output. Its documented drawing format is self-contained HTML with SVG, variable tables, notes, a title block, and detail views. It favors one legible sheet, monochrome drawing conventions, neutral labels, structural content slots, and explicit `[TBD]` values for unknown dimensions. The source inspection is recorded separately in [the assessment](references/dimensional-drawing-assessment.md). [Drawing skill](https://github.com/enesozturk/dimensional-drawing/blob/main/skills/dimensional-drawing/SKILL.md)

For ux-recast, component specifications should make it possible to inspect the component's structure and trace important dimensions back to their evidence. Depending on the component, useful views include its overall arrangement, spacing chains, control and hit-area relationships, nested radii, border and elevation relationships, layer stack, and placement within the surrounding interface.

Use stable variable names or codes that connect the drawing to the project's tokens or documented values. Record relationships as formulas where a value is genuinely derived. Keep units, formula inputs, state, and viewport assumptions explicit. Missing tokens or conflicting values should be visible as open issues.

A drawing may use structural slots to stay useful as content changes. The accompanying guide must still capture content constraints and behavior, including wrapping, long requests, overflow, and translated or enlarged text where relevant. A placeholder on a technical sheet does not justify truncating the user's actual task or request in the application.

The monochrome presentation belongs to the technical documentation. It must not force the product itself into a monochrome design. Preserve the project's actual color, typography, semantic status system, and approved personality in the broader style guide.

### 5. Optional animated presentations

The reference has a separate motion skill and a headless renderer. Its presentation reveals the drawing and separates its layers. That is a documentation presentation, distinct from the application's own interaction animation. [Motion skill](https://github.com/enesozturk/dimensional-drawing/blob/main/skills/dimensional-drawing-motion/SKILL.md)

ux-recast may offer this as an additional output after a static specification has been established. The animation should use the same geometry and variables as the static sheet, preserve the explanatory meaning, and remain unnecessary for reading or using the guide. A static artifact must remain available.

The rendering path should be verified on a supported environment before unattended use. The new-reference assessment records the actual checks performed during this seed preparation and the remaining renderer issues; it is not a claim that a video export has passed.

### 6. Readable and reusable deliverables

The capability should account for a human-readable guide and machine-readable design data when that data is useful to the project. The planning agent should choose formats and integration conventions based on the target repository. Candidate deliverables include Markdown design guidance, an HTML guide, SVG or HTML component sheets, semantic token files, and optional print or video exports.

Connect these outputs to the project's existing design context. Preserve the previously discussed roles of product context, visual-system documentation, and accepted review decisions. Avoid establishing multiple competing authorities for the same token or rule.

An update should make its changed decisions and measurements reviewable. Preserve earlier accepted versions or normal repository history so future agents can understand why a rule changed. Generated examples and sheet identifiers should map back to the relevant components and evidence.

### 7. Relationship to the retained learning loop

The guide can be an output of an accepted refinement and an input to the next review. Preserve accepted and rejected changes, their rationale, and supporting before/after evidence. Keep reusable interaction lessons separate from project-specific visual choices.

Do not update the shared design rubric solely because a model prefers its own latest output. Use the same evidence and acceptance approach described in Part I. A guide should help later agents maintain the accepted system and make deliberate improvements without repeatedly rediscovering or overwriting its identity.

### 8. Planning questions left open

The next agent should resolve these from the concept and inspected code rather than treating this seed as a preselected architecture:

- How the existing `ux-review` request and result contracts expose optional documentation outputs.
- Which guide and token formats fit the current projects and which outputs belong in the initial phase.
- How source inspection and rendered evidence are captured, correlated, and kept current.
- Whether the drawing reference is invoked as a tool, adapted narrowly, or used as a presentation reference.
- How the source-specific notices and attribution are preserved for any copied material.
- How guide changes, acceptance, and unresolved values are represented through existing project conventions.
- What validation is necessary to prove a useful static guide before adding optional animation.

The implementation plan must be a separate document. The complete proposals above remain the concept record.
