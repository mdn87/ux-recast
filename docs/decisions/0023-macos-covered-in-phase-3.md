# D-23: macOS is covered in Phase 3 (B-11)

- Status: accepted (user decision 2026-11-04)
- Source: `docs/plans/initial-implementation-plan.md`, blocker B-11 and decision D-10

## Decision

Phase 3 covers macOS for both the Lugos `ux-review` shim and the ux-recast package; macOS is not excluded. The implementing host is `applemac`, which the operator made available for this work.

## What it was decided on

- Two of the four hosts are Macs, so a platform claim without macOS would leave half of them unverified.
- `applemac` was probed on 2026-11-04 over its inventoried SSH alias: macOS 27.2 on arm64, system `python3` 3.9.6, no Homebrew and no `uv`, and Syncthing copies of `lugos` and `ux-recast` under `~/MyDocs`. ux-recast requires Python 3.11 or later, so macOS coverage needs a supported Python on that host first. Installing one is a host-level install and is asked for separately.

## Consequences

- Phase 3 acceptance names macOS beside Windows and Linux for the shim and the package tests.
- D-10 stands for CI: hosted macOS runners stay off push and pull-request triggers. macOS evidence comes from `applemac` runs recorded with the Python version, as Windows runs already are.

## Cost to reverse

Low: excluding macOS later means dropping it from the Phase 3 acceptance text and recording why.
