# Lugos ux-review corpus, 2026-10-24

Recorded artifacts from the two live Autowork submits the Lugos `ux-review` skill made on 2026-10-24 against the contact-request fixture (`docs/evidence/ux-review-autowork/` in Lugos): the controller state file, the plan-stage and implementation-stage packets, and their receipts. They are the shapes the ux-recast contracts must accept (plan slice S1.4) and the baseline for the Phase 3 differential harness.

Sanitized before commit: the local worktree path became `/workspace`, the Autowork run directory became `/autowork-runs`, and any other home-directory path became `/home/user`. Because the embedded `request.task` text carried those paths, the recorded `task_sha256` values no longer equal the sha256 of the sanitized text. The contracts check hash shape and packet-receipt agreement, not recomputation. Do not recompute them against these files.
