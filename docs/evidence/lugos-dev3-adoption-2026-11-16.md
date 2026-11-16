# Lugos adoption of ux-recast v0.1.0.dev3

The released package is pinned by Lugos commit `ba6ff9f0f641e99a29c5f8a407293b5e2fec4590`, landed on `master` on 2026-11-16 UTC. The requirements file is now included in both existing ux-review CI path filters, so a dependency-only change triggers the contract checks. The workflow retains its self-hosted Linux runner.

## Windows evidence

A new virtual environment on 4070pc, Python 3.14.3, installed `pytest` and Lugos's updated `plugins/lugos-toolset/requirements-ux-review.txt`. Installed package metadata reports `0.1.0.dev3`, requested tag `v0.1.0.dev3`, and source commit `646e8728786232c3abae95b053f326b025c0cde1`.

Commands ran from an isolated Lugos checkout based on `b5a1a6816022fb2aba9aec33a0a4697f3c36b007`:

- With `UX_REVIEW_IMPL=ux_recast`: `python -m pytest plugins/lugos-toolset/skills/ux-review/tests --ignore=plugins/lugos-toolset/skills/ux-review/tests/demo scripts/test_lugos_catalog.py -q` — 115 passed in 58.25 seconds, exit 0.
- With `UX_REVIEW_IMPL=legacy`: the same test command without `scripts/test_lugos_catalog.py` — 69 passed in 37.44 seconds, exit 0.
- `python scripts/lugos_catalog.py --check` — exit 0.

These include the existing rollback crossover, distribution, module surface, packet and fixture MCP submission checks. They do not constitute a new live Autowork submission or real Impeccable run.

## Remaining Phase 3 gates

This release adoption does not close Phase 3. D-23 still requires macOS parity; the recorded applemac SSH failure needs resolution before that check. S3.9 legacy removal remains separate and requires its existing approval. The frozen reviewer rubric remains unchanged. S4.4 and the Impeccable installation decision remain open.

## Linux evidence

[UX review contracts run 43800074518](https://github.com/mdn87/lugos/actions/runs/43800074518) passed on the landed commit, using the existing self-hosted lugos-host runner and Python 3.11 workflow. The install resolved the same release commit. The shim/catalog suite passed 115 tests in 25.11 seconds and the legacy suite passed 69 in 24.50 seconds. The catalog consistency command also passed. Neither suite reported skips.

Lugos Audit quick receipt `receipt-0e2af8f71e06` is valid for `ba6ff9f0f6`. This is hygiene evidence, separate from the test results above.
