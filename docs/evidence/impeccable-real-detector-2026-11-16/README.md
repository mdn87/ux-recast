# Real Impeccable detector verification

On 2026-11-16, the existing ux-recast detector helper passed five checks against
Impeccable's actual Windows executable, through its actual npm batch launcher.
This closes the real-tool evidence gap in S4.3. It does not close S4.4, Phase 3,
or the B-10 decision about installing Impeccable agent skills in the Dias host
repository.

## Installation and provenance

The validation-only installation is under this repository's ignored
`.work/impeccable-validation`. It contains `impeccable@4.8.0` and
`@impeccable/cli-windows-x64@0.1.18`. No global package, agent skill, hook, or
runtime dependency was installed. Lifecycle scripts were disabled. The exact
npm distribution URLs and integrity values are in [package-lock.json](package-lock.json).

The [upstream package manifest at e89e3ada3e87](https://github.com/pbakaus/impeccable/blob/e89e3ada3e87/package.json)
confirms those versions. Both installed packages include the Apache-2.0 license.
The raw detector reports retained here contain upstream rule text; no upstream
implementation or skill source is copied into ux-recast.

The engine's SHA-256 is
`8f61e96b0c97001546a824d79b44f46b423b560f3eb1a0cc44a8695a1b395d9f`.
It matches the checksum manifest shipped with npm 4.8.0. The verification script
checks that before running the detector and sets `IMPECCABLE_BIN` to the installed
engine, preventing this run from needing the launcher's download fallback.

Environment: Windows 11, Python 3.14.3, Chromium 149.0.7827.55 from the existing
Playwright installation. [summary.json](summary.json) records executable and
fixture hashes. The original fixture files were not edited; their hashes were
checked again after all scans.

## Observed results

| Case | Real exit | Helper result | Evidence |
| --- | --- | --- | --- |
| Original contact-request HTML | 2 | One implementation heuristic | [Raw](static-before-raw.json), [mapped](static-before-helper.json) |
| Repaired contact-request HTML | 2 | The same implementation heuristic | [Raw](static-after-raw.json), [mapped](static-after-helper.json) |
| Minimal CSS with no detector hits | 0 | Clean, empty findings | [Raw](static-clean-raw.json), [mapped](static-clean-helper.json), [input](clean.css) |
| Nonexistent input file | 1 | Operational error raised | [Raw](missing-target-raw.json), [error](missing-target-helper.json) |
| Repaired page served locally at 390×844 | 2 | One implementation heuristic | [Raw](rendered-mobile-raw.json), [mapped](rendered-mobile-helper.json) |

The recipe invokes the upstream Node launcher directly to obtain reference
output, then invokes the helper through the real npm `.cmd` launcher. It compares
every field the helper currently promises to map, rule order, finding count,
status, arguments, version and exit code. The rendered URL contains `&`, exercising
the batch launcher's argument quoting with a real engine. The local HTTP server
is closed when the check finishes.

## What these results do and do not establish

- Static and rendered compatibility is observed for this Windows package pair.
  Linux and macOS real-detector compatibility remain unverified.
- All three fixture scans report `kicker-above-heading`. The unchanged result
  does not distinguish the defective task flow from its repair. These are
  heuristic inputs to review, not evidence that a user's task succeeds or fails.
- Rendered raw output includes `selector: div.eyebrow`; the current helper drops
  that field. This is a recorded limitation for S4.4 integration. The raw report
  preserves it here; the current S4.3 contract requires rule IDs, not selectors.
- The npm launcher can download a missing engine into its user cache. Thus
  finding a launcher on PATH alone does not guarantee an offline, complete
  installation. This run used the preinstalled, verified engine and a local
  tool-home directory. Before deployment, define how a complete installation is
  checked if the no-download guarantee must cover the upstream launcher too.
- The five real-tool cases do not cover advisory-only output or a missing
  browser. Those behaviors remain covered by the existing stand-in tests.
- This is direct helper verification. No review cycle invokes it yet, no
  model review ran, and no design judgment was accepted or applied.

## Reproduce

From the ux-recast root, install the optional validation tool explicitly:

```powershell
npm install --prefix .work/impeccable-validation --cache .work/npm-cache --ignore-scripts --no-audit --no-fund --save-exact impeccable@4.8.0
```

Then run [the verification recipe](../../../scripts/verify_impeccable.py), giving
an existing Chromium executable and a fresh output directory:

```powershell
python scripts/verify_impeccable.py --tool-root .work/impeccable-validation --browser C:/Users/Matt/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe --output .work/impeccable-real-run-new
```

The recipe installs nothing and requires all five checks to pass. Its output
directory retains raw stdout/stderr, mapped results, the clean input and hashes.
The checked-in JSON files are the captured run, with absolute paths and the
ephemeral local port retained as provenance.

## Repository verification

`python -m pytest tests -q -p no:cacheprovider` completed with exit 0: all
238 tests passed, with no skips reported. Both final board files also passed
Dias's exported `parseChipFile` and `parseProjectStatusFile` parsers; every
board string is shorter than 180 characters.
