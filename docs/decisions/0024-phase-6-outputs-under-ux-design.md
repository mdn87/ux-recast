# D-24: Phase 6 Dias outputs live under `lugos-host-ops/ux/design/`

- Status: accepted (implementation decision 2026-11-06, within the operator's instruction to finish Phase 6)
- Source: `docs/plans/implementation-slices.md` S6.8; `docs/plans/initial-implementation-plan.md` Phase 6

## Decision

The first Dias guide and sheet are written to `lugos-node/services/lugos-host-ops/ux/design/`
(`guide.md`, `sheets/sessions-card.html`, `sheets/sessions-card.json`) instead of the planned
`lugos-host-ops/docs/design/`.

## What it was decided on

- The host-ops release builder (`deploy/build-lugos-host-ops-release.py`) skips only `DESIGN.md`,
  `PRODUCT.md` and `ux/` as documentation and rejects any other unknown top-level root; its test
  `test_builder_skips_service_documentation_and_still_rejects_unknown_roots` asserts that. A new
  `docs/` root would have made the next phone release fail to build.
- Widening the builder would put a host-ops code change into Phase 6, whose acceptance asks for an
  empty host-ops code diff. `ux/` is already the never-deployed home of the redesign records.

## Also decided while building the sheet

- The sheet is a JSON spec rendered to HTML; the spec is embedded in the page and the page must
  match its own re-rendering, so table, drawing and data cannot drift apart (C-49).
- Literals carry a `{}` slot for the value (`padding:{} 12px`), so a check pins one value and not a
  neighbour on the same line.
- The plan's "waiting" state is the D-22 `needs-you` state (the Question row); the D-18 word
  "waiting" survives only as a CSS class name.

## Cost to reverse

Low: move the three files and add `docs` to the builder's documentation-only roots with a test.
