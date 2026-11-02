# Plan review roundtable, 2026-11-02

Times are UTC. Technique: three-amigos, driven by the Lugos roundtable CLI over the session document `lugos/.roundtable/sessions/ux-recast-plan-review-20261102.md`. Subject: the four planning documents under `docs/plans/` at commit `db78c53`, captured verbatim into the facilitator's framing. Lugos does not track that session file, so the three participant regions are copied verbatim into [plan-roundtable-2026-11-02-regions.md](plan-roundtable-2026-11-02-regions.md); this record holds the routes, the dispositions, and what changed.

## Participants and routes

| Participant | Role | Route | Outcome |
| --- | --- | --- | --- |
| facilitator | facilitator | the parent Claude session that wrote the plan set (a declared conflict of interest), committing through `roundtable.service.commit` | clarify at seq 1 (framing plus 77 KB captured plan); reconcile at seq 5 with the amended plan set as artifact |
| product | product | `agy:flash` through the Autowork packet adapter (pool `agy.gemini`, 97 percent weekly remaining) | moved at seq 2, 78 s, rc 0 |
| implementer | implementer | `agy:argon` through Autowork (pool `agy.argon`, 14 percent weekly remaining, state `low`) | moved at seq 4, 142 s, rc 0 |
| tester | tester | `agy:opus` through Autowork (pool `agy.claude_gpt`, 78 percent weekly remaining) | moved at seq 3, 133 s, rc 0 |

Mechanics: a scratchpad driver called `service.init_session` and `service.commit` for the facilitator because the clarify body exceeds the Windows command-line limit, then `runner.drive(..., retries=0, max_steps=1)` for one fan-out step. No dispatch failed, no move was recovered by hand, the session document was never hand-edited. Quota mode was `shadow`; no participant would have been blocked. The Agy participants received only the session document, so every finding rests on the captured plan text; each seat listed what it could not assess.

## Framing

The framing gave Matt's direction in his words, nine facts with their probes (the two inspections of 2026-11-02, the Lugos test results, the live-submit gap, the image-policy change, the Dias phone client's location and stack, the reference commits, the knowledge-base rights question), the AGENTS.md and KICKOFF.md constraints, and one assignment per seat: product on scope, acceptance observability and the Phase 5 versus Phase 6 order; implementer on the shim migration claim, the package boundary, the provider protocol, the rubric move and slice honesty; tester on how each phase is verified and what the proofs fail to cover.

## Dispositions

Severity is the participant's. "Accepted" means the plan set was changed; the column names where.

### Product (P)

| Id | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| P-1 | "Look sharper" dropped: S5.1, S5.5, S5.7 and Phase 6 acceptance protect the three inconsistent inline palettes instead of fixing them. | critical | Accepted. New 5b accepted design direction (D-16, B-12); visual criteria added to the Phase 5 table; Phase 6 "palette untouched" reworded as an empty host-ops code diff. |
| P-2 | Impeccable reduced to a linter (D-11, S4.2, S4.4), dropping its active design commands without the user's consent. | high | Accepted. D-11 amended: commands used by name where a project has the skill; `detect` is a pre-pass; install is the user's call (B-10). |
| P-3 | React Grab dropped with no substitute for pointing at an element. | high | Accepted. Tap-to-target evidence helper, S4.5; D-12 amended. |
| P-4 | Mandatory content-behavior section violates optionality. | medium | Narrowed. Concept C-45 requires it when a sheet uses slots; the plan now states it as that conditional rule. |
| P-5 | Phase 5 repairs before Phase 6 establishes a design standard. | high | Accepted in substance. The design direction step (5b) is inserted before repair rather than moving all of Phase 6 ahead of the pilot; full sheets still follow the pilot. |
| P-6 | 24 slices before the user sees a Dias improvement. | high | Accepted. Pre-pilot S5.0 on the existing skill right after Phase 0; first-batch recommendation rewritten. |
| P-7 | Phase 5 acceptance is mechanical, with no visual or readability criteria. | high | Accepted. Visual outcome row and contrast, type-scale and hierarchy criteria added. |
| P-8 | S6.6 "user accepts usefulness" is unobservable. | medium | Accepted. Replaced by a reproduction test: a developer rebuilds the card from the sheet and guide within tolerance. |
| P-9 | S8.3 proves string interpolation, not learning. | medium | Accepted. Before and after review of a frozen input must differ in the predicted direction. |
| P-10 | D-06 lands repairs in production host-ops without the user's decision. | critical | Accepted. D-06 reclassified as user decision B-09 with the plan's recommendation (a branch gated by the Decision). |
| P-11 | D-11 belonged to the user. | high | Accepted with P-2; B-10. |
| P-12 | D-08 defers motion without asking. | medium | Narrowed. Gate kept; the defect fix and a first export may run early if the user asks. |

### Implementer (I)

| Id | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| I-1 | Phase 3 shims `autowork_review.py` before its helper is ported in Phase 4. | critical | Accepted. Both scripts ported in Phase 1 (S1.2); D-13. |
| I-2 | CLI-only shims break importing callers and tests. | high | Accepted. Shims re-export the module surface and delegate at function level; D-14. |
| I-3 | `_legacy/` subdirectory breaks `__file__`-relative lookups and doubles the mirror. | high | Accepted. Legacy kept as sibling files in `scripts/`; import guard before `ux_recast`. |
| I-4 | Additive contract fields can break the inner delegate payload and `task_sha256`. | high | Accepted. Section 2.2 now restricts additions to the outer envelope and a separate capture manifest; inner payload byte-identical. |
| I-5 | Non-editable install omits package data. | medium | Accepted. S0.2 wheel verification; D-02 names `importlib.resources`. |
| I-6 | Rubric move creates a three-way sync trap and drifts `rubric_sha256` between legacy and shim. | medium | Accepted. Bytes frozen through Phase 3 (D-15); cross-package byte test (S1.3); vocabulary change moved to S4.4. |
| I-7 | `impeccable_detect` is not a provider. | high | Accepted. Moved to `evidence/`; D-05 narrowed to packet fulfilment. |
| I-8 | Durable `.ux-recast/` records link into gitignored `.ux-review/`. | high | Accepted. Evidence archive S2.3; D-03 states cycle state location for all projects. |
| I-9 | No execution model for `request_kind: documentation`, no Lugos entry point. | medium | Accepted. Documentation packet (S6.1, D-07) and skill entry point (S6.2). |
| I-10 | Slice sizes: S2.1 and S2.2 understated or mis-scoped; S5.5 bundles three pages and net-new keyboard work; S6.5 and S6.6 are the hardest greenfield work. | n/a | Accepted. S2.1 reduced to text read plus create-if-absent; S2.2 reuses the cycle lock and is M; S5.5 split into S5.8 to S5.10; S6.6 to S6.8 resized. |
| I-11 | Reorder: S3.0 first; port the packet helper before tagging. | n/a | Accepted. S0.4 and S1.2. |
| I-12 | Merge S0.1 to S0.4; merge S1.2 with S4.4 or defer the prompt change; drop Markdown round-trip; move `impeccable_detect` out of providers. | n/a | Accepted, except that the prompt change is deferred to S4.4 rather than merged, per I-6. |
| I-13 | Missing slices: wheel verification, evidence archival, documentation dispatch and Lugos entry point. | n/a | Accepted. S0.2, S2.3, S6.1, S6.2. |

### Tester (T)

| Id | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| T-1 | Unit tests only assert what they already assert; a differential corpus is needed. | critical | Accepted. S1.6 harness; S3.4 parity. |
| T-2 | Shim must keep the Python API; S3.4 "runs clean" has no pass criterion. | high | Accepted with I-2; S3.5 names expected outputs for both importing callers. |
| T-3 | Test counts (27, 25, 15, 61) do not reconcile. | high | Accepted. S0.5 inventory by id; acceptance by id everywhere. |
| T-4 | Live submit is n=1, after the shim, text-only. | high | Accepted. Baseline on legacy in Phase 0 (S0.6, text and image, one failure path); repeated on the shim (S3.6). |
| T-5 | Rollback drill is one-directional and new keys will reach legacy. | high | Accepted. S3.7 both directions, lock crossover, unknown-key tolerance. |
| T-6 | Shim behavior without `ux_recast` undefined; env var must reach the MCP child. | high | Accepted. Fail closed with message (D-14); setting passed to the child explicitly. |
| T-7 | Platform matrix overstated; Windows unrecorded; macOS absent. | high | Accepted. Windows runs recorded with Python version; macOS is B-11. |
| T-8 | CRLF will break byte hashes. | high | Accepted. S0.3; ux-recast `.gitattributes` already pins LF for md, json, yaml. |
| T-9 | The encoding fix changes stdout bytes; the 64 KiB cap may be measured on escaped JSON. | medium | Accepted. S3.4 names the fix as the one documented delta; cap unit added to the Phase 1 corpus. |
| T-10 | Reduced viewport simulates the wrong keyboard mechanism; the harness may not even be WebKit. | critical | Accepted. WebKit project (S5.2); viewport trick demoted to a smoke check. |
| T-11 | Real-device check optional, no target, no baseline, no sanctioned page. | critical | Accepted. B-02 made required before and after, with the procedure in the Phase 5 table and the fixture reachable on the LAN. |
| T-12 | Five-screenshot and 64 KiB caps conflict with evidence for every row. | high | Accepted. Three per-flow packets with their rows stated (S5.4). |
| T-13 | Comparison graded by its author; duplicate send checked in the UI. | high | Accepted. Scripts frozen and hashed before repair; fixture server counts used. |
| T-14 | Repair touches pages with no browser coverage. | high | Accepted. S5.1 before any repair; the opt-in flag named in acceptance. |
| T-15 | Fixture-versus-production gaps unlisted. | medium | Accepted. Non-coverage list added to Phase 5; build id recorded. |
| T-16 | Approvals silently dropped from the receipt row. | medium | Accepted. Exclusion stated in the row. |
| T-17 | A rejected pilot still triggers legacy cleanup. | medium | Accepted. S3.9 gated on an accepted Decision. |
| T-18 | Phase 6 tracing is circular. | high | Accepted. Mechanical trace plus seeded mutations and a blind, different-family checker (S6.7). |
| T-19 | "Rendered" lacks DPR, engine, fonts. | medium | Accepted. Variable schema and S6.6 provenance extended. |
| T-20 | Validator under-specified; `[TBD]` ratio; empty host-ops diff. | medium | Accepted. S6.5 corpus; ratio reported; Phase 6 acceptance. |
| T-21 | Phase 1 cycle swaps in the known fix, so it tests plumbing; `sys.modules` misses subprocesses; browser binaries unstated. | high | Accepted. S1.8 findings-driven repair with the fixed file as oracle, no Lugos checkout on disk, access logged; `playwright install` named. |
| T-22 | S1.3 validates one historical packet without `submit_*` fields. | medium | Accepted. Live-submit packets added to the corpus (S1.4). |
| T-23 | S2.2 race is one-shot; stale locks unhandled. | medium | Accepted. 200 iterations, large lines, stale-lock recovery. |
| T-24 | Promotion rule spoofable; project identity undefined. | medium | Accepted. Identity is git remote plus root hash; refusals logged; bypass tested (S2.4). |
| T-25 | `npx impeccable detect` installs software. | high | Accepted. PATH check only; exit-code semantics tested (S4.3). |
| T-26 | Five-finding cap has no ordering rule. | medium | Accepted. Severity then input order (S4.1). |
| T-27 | Image-policy regression unguarded. | medium | Accepted. Preflight contract test with defined failure (S4.2). |
| T-28 | S7.2 "plays" needs an operator. | low | Accepted. `ffprobe` check (S7.3). |
| T-29 | S8.3 proves inclusion, not improvement. | medium | Accepted with P-9. |
| T-30 | Cross-cutting edge cases: Windows paths, encodings, concurrency, stale packets, evidence caps. | n/a | Accepted as test-corpus content for S1.6 and S2.2; not all are slices of their own. |

## What was not changed

- The eight-phase shape and the standalone-core boundary. No seat argued against them.
- Phase 6 stays after Phase 5; only the design-direction step moved ahead of repair.
- No concept proposal was dropped; the traceability rows C-01, C-03, C-06 and Q-01 were amended.

## Limits of this review

- The three reviewing seats could not read the Lugos or Dias repositories; they reasoned from the captured plan text and said so. Their factual premises are the plan's own facts, which came from the two Explore inspections and were not independently re-probed.
- The facilitator who reconciled is the plan's author.
- One round only. The reconcile is the three-amigos technique's terminal move, so the seats did not see or rebut the dispositions. A second session on the amended set would be the way to check them.
- Nothing here is a review of code; none exists.
