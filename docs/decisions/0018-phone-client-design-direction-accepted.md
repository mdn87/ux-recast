# D-18: Phone client design direction accepted (B-12)

- Status: accepted (user decision 2026-11-02)
- Source: `docs/plans/initial-implementation-plan.md`, decision log row D-18 and user decision B-12; the direction itself is `lugos/lugos-node/services/lugos-host-ops/DESIGN.md` (`basis: accepted`, Lugos master)

## Decision

The proposed direction in the Dias phone client's `DESIGN.md` is accepted as written, no section reworked: one palette (the sessions page's tokens extended to the question and approval pages, with WCAG contrast figures), one type scale on a 17 px base, one status vocabulary (needs-approval, needs-your-answer, working, idle, last-known; receipt and refusal wording; words kept out of visible text) and one layout rhythm (page and card order, touch sizes, a fold rule the frozen scripts check). It is the standard the Phase 5c repairs are measured against. Dias meanings stay in Dias documentation; nothing enters the shared rubric.

## Inputs

The pre-pilot evidence in `lugos/docs/evidence/dias-pre-pilot/`: accepted review runs `0e9a46b057ac` (needs-you) and `7481242fed57` (response-status), and the held, unaccepted review `e1dcd0fe8f3a` (request-detail, lost to Autowork's completion checker, reviewer text retained). Observed palettes at Lugos `f722cccc`, app.js build `mobile-navigation-20261031-6`.

## Why

D-16 requires an accepted standard before any visual repair. The direction keeps what already passes on the sessions page and changes only what a finding or a contrast figure requires, so each rule traces to a review finding and the repair diff stays bounded.

## Cost to reverse

Low until 5c lands: a `DESIGN.md` edit and a new decision. After 5c, reversing a rule means re-running the frozen before-and-after scripts for the affected flow.
