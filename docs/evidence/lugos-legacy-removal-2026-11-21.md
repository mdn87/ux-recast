# Lugos legacy removal

Lugos removed `control_legacy.py` and `autowork_review_legacy.py` from both skill copies and retired `UX_REVIEW_IMPL`. The existing controller and packet entry points now import the pinned ux-recast v0.1.0.dev3 package directly. The change landed on `master` at `4219f207f9b4209d577b7f20c2ed7995d7330d8e`, completing S3.9 and Phase 3. [Lugos PR #750](https://github.com/mdn87/lugos/pull/750)

## Verification

| Platform | Python | Review tests | Catalog tests | Catalog consistency |
| --- | --- | ---: | ---: | --- |
| Windows (4070pc) | 3.14.3 | 64 passed | 46 passed | Passed |
| macOS 27.2 arm64 (applemac) | 3.11.15 | 64 passed | 46 passed | Passed |
| Linux (lugos-host) | 3.11.16 | 64 passed | 46 passed | Passed |

All three runs used release commit `646e8728786232c3abae95b053f326b025c0cde1` and completed without skips. Windows and macOS ran Lugos revision `21587b55` and reported identical test IDs, including all 54 original review contracts. Linux ran the same suite in PR CI. The landed revision contains the tested entry points, tests, dependency pin and workflow. [Linux contract run](https://github.com/mdn87/lugos/actions/runs/44870224391) · [Pre-removal parity evidence](macos-parity-2026-11-21/README.md)

- **Open review at upgrade.** On Windows, the old scripts created and claimed a review. With the old environment setting still present, the new entry points recorded its result, consumed current findings, advanced it through repair and verification, and finished the same run.
- **Caller compatibility.** All eight frozen scenarios matched the saved exit codes, normalized output and review files. The MyDocs forwarder passed its 11 tests against the new controller. The coordination replay matched both archived reports after removing the source revision.
- **Package requirement.** Before removal, the new regression checks failed because the controller could still run without the package and both copies still shipped the legacy scripts. After removal, both entry points report the required install when the package is unavailable.
