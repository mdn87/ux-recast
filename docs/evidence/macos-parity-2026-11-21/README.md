# ux-recast and Lugos parity on macOS

On 2026-11-21 UTC, `applemac` ran the package and both Lugos implementations on macOS 27.2 (26B123), arm64, with CPython 3.11.15. The run used the inventoried Tailscale SSH route with strict host-key checking and the existing interpreter at `/opt/homebrew/bin/python3.11`. This completes the macOS check required by [D-23](../../decisions/0023-macos-covered-in-phase-3.md).

| Check | Passed | Skipped | Elapsed |
| --- | ---: | ---: | ---: |
| Package installed from `v0.1.0.dev3` | 236 | 2 | 49.86 s |
| Package wheel built from `main` at `69e9e60` | 238 | 2 | 40.18 s |
| Lugos shim, including 46 catalog tests | 115 | 0 | 23.75 s |
| Lugos legacy implementation | 69 | 0 | 20.78 s |

All four suites exited 0. The two package skips in each run exercise Windows batch-launcher argument handling. The browser and Autowork policy tests ran on the Mac. Each package run also reported 80 passing subtests. The separate Lugos catalog consistency check exited 0.

The shim and legacy JUnit reports contained exactly the same 69 passing review test IDs, including all 54 contract IDs in the original Lugos inventory. The two Lugos totals match the earlier Windows and Linux results. [Shared passing test IDs](lugos-shared-test-ids.txt) · [Windows and Linux evidence](../lugos-dev3-adoption-2026-11-16.md)

## Reproducing the checks

The checkouts were siblings in a temporary directory. Lugos was detached at its dev3 adoption commit, `ba6ff9f0f641e99a29c5f8a407293b5e2fec4590`. The release and Lugos environments both installed `plugins/lugos-toolset/requirements-ux-review.txt`. In both, pip recorded tag `v0.1.0.dev3` and commit `646e8728786232c3abae95b053f326b025c0cde1` for ux-recast. A third environment installed the wheel built from `69e9e604cde141802369c2c89731bf16558ebb43` to exercise the package tests added after the release.

For each package run, the environment included pytest 9.2.0, MCP 1.30.0, build 1.6.1, Playwright 1.65.2 and the editable `autowork` package from the Lugos checkout. Playwright installed its Chromium headless shell (159.0.8154.6) under the temporary directory. From each matching package checkout, with its environment active and `PLAYWRIGHT_BROWSERS_PATH` set to that browser directory, run

```sh
UX_RECAST_BROWSER_TESTS=1 python -m pytest tests -ra --junitxml=package.xml
```

For Lugos, activate a fresh Python 3.11.15 environment and run these commands from the adoption checkout. The review suite uses its fixture MCP server. The demo directory is excluded from the Windows, Linux and Mac contract runs.

```sh
python -m pip install pytest -r plugins/lugos-toolset/requirements-ux-review.txt
suite=plugins/lugos-toolset/skills/ux-review/tests
UX_REVIEW_IMPL=ux_recast python -m pytest "$suite" --ignore="$suite/demo" scripts/test_lugos_catalog.py -q -ra --junitxml=shim.xml
UX_REVIEW_IMPL=ux_recast python scripts/lugos_catalog.py --check
UX_REVIEW_IMPL=legacy python -m pytest "$suite" --ignore="$suite/demo" -q -ra --junitxml=legacy.xml
```
