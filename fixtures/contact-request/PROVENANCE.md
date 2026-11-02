# Provenance: contact-request fixture

Copied on 2026-11-02 from the Lugos repository, `plugins/lugos-toolset/skills/ux-review/tests/demo/`, as it stood at the Lugos commit recorded below. The files are the local staged demonstration written for the Lugos `ux-review` capability on 2026-10-24: an intentionally defective contact form (`index.before.html`), the corrected form (`index.html`), the independent task contract (`task.json`), the reviewed plan (`plan.txt`), and seven Playwright regression tests (`test_flow.py`). They are locally authored and carry no third-party provenance.

| File | SHA-256 at copy |
| --- | --- |
| `index.before.html` | `a21bc7401f384d1749049e4591079017275bf1a7c1fdc2ca102f3a4cc8742a45` |
| `index.html` | `c04cfbe2a4c9c70165ec06f5ce738a736d0a2774d4e3df4aa9716ed5d027a3a6` |
| `plan.txt` | `a181b555dc208d20d8c64e9f248295d41619cabb7b68d0cc6e01ed4c3ac5dfd4` |
| `task.json` | `4ec6c90eb49fb8a530cde4ee15995b749127be7df288e6fbade806f8238203b1` |
| `test_flow.py` | `5b4ba5f9a598ed2a48f399bfff78b8f072ab2c2fb523751b39b3d7d571e378e2` |

Source commit: Lugos `cfe7b333a4841e458c20957bc92fd6cea2926a1e` (checkout HEAD at copy); the demo directory last changed in `1a7b41485b04b943c26bbeb556afecdb20eb8196`.

Role in ux-recast: the independence fixture (KICKOFF item 8; plan Phase 1). A cycle on it must run with no Lugos checkout present. `index.html` is the oracle a findings-driven repair is compared against; it is not swapped in as the repair.

Run the regression suite: `python fixtures/contact-request/test_flow.py -v`. Set `DEMO_PAGE=index.before.html` to replay the defective baseline and `DEMO_EVIDENCE_DIR` to keep screenshots, observation JSON and traces. Requires `playwright` and `python -m playwright install chromium`.
