# Reference register

This register supplies ordinary URLs for the references already discussed in the concept. It does not rerank them or select new dependencies. License labels below are the labels observed during the conversation; inspect the selected revision before copying or adapting source.

## Design and review references

### Impeccable

Role preserved from the concept: design critique, refinement, implementation audits, and persistent product/design context. Observed license: Apache 2.0.

- Repository: <https://github.com/pbakaus/impeccable>
- License: <https://github.com/pbakaus/impeccable/blob/main/LICENSE>
- Documentation: <https://impeccable.style/docs/>
- Critique: <https://impeccable.style/docs/critique/>
- Audit: <https://impeccable.style/docs/audit/>
- Adapt: <https://impeccable.style/docs/adapt/>
- Init / product context: <https://impeccable.style/docs/init/>
- Document / design context: <https://impeccable.style/docs/document/>
- Extract: <https://impeccable.style/docs/extract/>
- Comparison gallery: <https://impeccable.style/gallery/>

### Happy

Role preserved from the concept: a mobile-session interaction and implementation reference for Dias. Observed license: MIT.

- Repository: <https://github.com/slopus/happy>
- Mobile documentation: <https://happy.engineering/mobile-app/>
- Mobile and web source: <https://github.com/slopus/happy/tree/main/packages/happy-app>
- License: <https://github.com/slopus/happy/blob/main/LICENSE>

### UI UX Pro Max

Role preserved from the concept: optional searchable design guidance and project design-system persistence. Observed license: MIT.

- Repository: <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>
- License: <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/LICENSE>

### React Grab

Role preserved from the concept: optional visual selection linked to source context. Observed license: MIT.

- Repository: <https://github.com/aidenybai/react-grab>
- Demo: <https://www.react-grab.com/>
- License: <https://github.com/aidenybai/react-grab/blob/main/LICENSE>

## Redesign method references

Added 2026-11-02 with the redesign-first method ([plan](plans/redesign-first.md), decision D-21), carried over from the firm copy's resource register. Each is read as text and adapted in this project's own words with the source named; nothing is vendored or invoked as a command, plugin, hook or MCP server by the method. The revisions are those the firm copy checked on 2026-11-02 with the GitHub API, not rechecked here; inspect the revision you use before adapting anything, and keep its notice if you do.

| Reference | Licence, revision | Contribution | Not imported |
| --- | --- | --- | --- |
| Task analysis (Nielsen Norman Group, <https://www.nngroup.com/articles/task-analysis/>) | article | The sequence, complexity and decisions involved in accomplishing a goal; the basis for changing the interaction rather than the surface. Stages 1 and 2. | |
| Cognitive walkthrough (Nielsen Norman Group, <https://www.nngroup.com/articles/cognitive-walkthroughs/>) | article | Step by step: is the next action recognizable, is its meaning clear, does the result communicate progress. `rubric/walkthrough.md` is this method written for a fresh-context agent. Stage 4. | |
| Impeccable `shape` (`skill/reference/shape.md`) | Apache-2.0; `c3c94b960276`, release `cli-v4.8.0` | The brief structure `templates/brief.md` adapts. | Its interview cadence and its stop at a confirmed brief. |
| Impeccable `distill` (`skill/reference/distill.md`) | same | Reorganize a surface around its one primary goal; document what was removed and why. Stage 3. | Its "ask if unclear from the codebase" interruption. |
| Impeccable `critique` reference material (`skill/reference/critique.md`: cognitive load, heuristics, persona testing) | same | Background reading for the evaluator. | Its mandatory detector run, 0 to 40 health score and closing question (D-09). |
| UI UX Pro Max | MIT; `713eef51b04e`, release `v2.15.0` | UX guidelines on forms, feedback, progressive disclosure, navigation and back behaviour in stage 3; its pre-delivery checklist (contrast 4.5:1, visible focus, reduced motion, reflow at 375/768/1024/1440) in stage 4. | Its design-system generator as a substitute for the brief. |

The roles above for Impeccable (including D-11's agent commands), UI UX Pro Max and React Grab stand. Happy keeps its Dias role and contributes nothing to the redesign method.

## Newly supplied component-documentation reference

### Dimensional Drawing

Role added at the user's request: component anatomy and dimensional sheets within an optional style-guide capability, with separately optional animated sheet presentations. Observed license: MIT.

- Repository: <https://github.com/enesozturk/dimensional-drawing>
- License: <https://github.com/enesozturk/dimensional-drawing/blob/main/LICENSE>
- Drawing skill: <https://github.com/enesozturk/dimensional-drawing/blob/main/skills/dimensional-drawing/SKILL.md>
- Motion skill: <https://github.com/enesozturk/dimensional-drawing/blob/main/skills/dimensional-drawing-motion/SKILL.md>
- Example directory: <https://github.com/enesozturk/dimensional-drawing/tree/main/skills/dimensional-drawing/examples>
- Card example: <https://github.com/enesozturk/dimensional-drawing/blob/main/skills/dimensional-drawing/examples/card-sheet.html>
- Dialog example: <https://github.com/enesozturk/dimensional-drawing/blob/main/skills/dimensional-drawing/examples/dialog-sheet.html>
- Headless renderer: <https://github.com/enesozturk/dimensional-drawing/blob/main/skills/dimensional-drawing-motion/adapters/headless/render.mjs>
- Motion example: <https://github.com/enesozturk/dimensional-drawing/blob/main/assets/dialog-motion.mp4>
- User-supplied visual reference: [dimensional-drawing-reference.png](references/dimensional-drawing-reference.png)
- Inspection and execution limits: [dimensional-drawing-assessment.md](references/dimensional-drawing-assessment.md)

## Local knowledge base

### UX Practices Knowledge Base

Role: a secondary, local-only source of reusable UX method pages (about 100 pages across research, ideation, UI foundations, interaction systems, projects, and front-end basics) and the existing opt-in agent UX review write-up. It is not vendored into this repository and is not a dependency of the plan; the planning agent may cite it as evidence when a method page is relevant. Not yet a git repository and has no remote. Source: distilled from UX/UI bootcamp course materials, so confirm distribution rights before publishing it or copying pages into this repository.

- Local path (sibling of this repository in MyDocs): `../ux-knowledge-base/`
- Start page: `../ux-knowledge-base/README.md`
- Process map: `../ux-knowledge-base/process-map.md`
- Opt-in agent UX review section: `../ux-knowledge-base/07-agent-review/index.md`
- Caveat: that section links into `lugos/` and `.agents/` by relative path, so its links resolve only inside the MyDocs workspace.

## Historical naming sources

These remain solely to preserve the earlier naming discussion. The working name is `ux-recast`.

- Cruth: <https://www.teanglann.ie/en/fgb/cruth>
- Snas: <https://www.teanglann.ie/en/fgb/snas>
- Cuma: <https://www.teanglann.ie/en/fgb/cuma>
- Previously noted Cruth sculpting project: <https://www.fiavaion.com/>

The additional English naming candidates were a creative brainstorm, not an availability or trademark search.
