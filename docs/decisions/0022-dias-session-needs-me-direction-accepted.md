# D-22: Dias phone client redesign direction accepted (session-needs-me)

- Status: accepted (user decision 2026-11-03)
- Source: the redesign-first method (D-21) run on the Dias phone client; artifacts in Lugos `lugos-node/services/lugos-host-ops/ux/session-needs-me/` on branch `ux/dias-phone-redesign` (stages 1 and 2 at `474e2705`, plan walkthrough run `4f966d359f28` and revised flow at `35548428`/`f6d6ebff`, mockup at `c398b9d2`)

## Decision

The operator accepted the proposed `session-needs-me` direction and answered its open questions:

1. The session report carries the working folder name, so every session is named agent · host · folder ("Claude on 4070pc · ux-recast"); a short id appears only on a name collision.
2. A permission notification opens the permission request itself.
3. Drafts are not kept after the app closes; no message text is stored on the phone, and the screen says so.
4. The direction is accepted together with the Mimo look shown in the mockup: the Dias display's palette (cyan accent on a near-black grid ground, thin outlined cards, pill status chips), a 14 px base and visually smaller buttons with hit areas of at least 44 px. This revises the phone client's `DESIGN.md` (supersedes the type-scale and button-size rules accepted in D-18; the status vocabulary and wording rules stand).

## Why

The 5c repair (D-20) made each page pass its thresholds; what remained was the joins between three pages organized by system entity. The plan walkthrough's five findings were all addressed in the revised flow before this decision. The mockup let the operator judge the look and the flow before anything was built.

## Cost to reverse

Low until the build lands: a flows.md and DESIGN.md edit. After the build, reversing means reverting the Lugos change and re-running the frozen pilot scripts, whose 17 px and 48 px thresholds belong to the D-18 standard.
