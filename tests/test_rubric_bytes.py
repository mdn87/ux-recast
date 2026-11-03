"""S1.3 / decision D-15: the packaged rubric bytes are frozen to the Lugos copies through the migration.

``walkthrough.md`` (D-21) is a ux-recast addition, not a Lugos copy: its digest
is recorded in ``VERSION`` so a change to it is deliberate, and adding it leaves
the frozen files and the rubric version untouched.

The pinned digests are the sha256 of the Lugos files at copy time. When a Lugos
checkout is present next to this repository (../lugos) the test also compares
against it byte for byte; otherwise that half is skipped and the pins stand.
"""
import hashlib
import os
from pathlib import Path
import unittest

from ux_recast import rubric

PINNED = {
    "rubric.md": "caeb6d842db6baf74f84f82d189ba5942064d591201399904af7610e231dfecf",
    "autowork-reviewer.md": "31329ddaab5f28d79d178278c7eaeaf59a4c07f9706887f4a4b423afc6c4e6f5",
}
LUGOS = Path(os.environ.get("UX_RECAST_LUGOS_CHECKOUT", Path(__file__).parents[2] / "lugos"))
LUGOS_REFERENCES = LUGOS / "plugins" / "lugos-toolset" / "skills" / "ux-review" / "references"


class RubricBytes(unittest.TestCase):
    def test_pinned_digests(self):
        for name, digest in PINNED.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256(rubric.read_bytes(name)).hexdigest(), digest)

    def test_version_file_agrees_with_pins(self):
        text = rubric.read_text("VERSION")
        self.assertEqual(rubric.version(), "1")
        for name, digest in PINNED.items():
            self.assertIn(f"{name}_sha256: {digest}", text)

    def test_walkthrough_digest_is_recorded(self):
        digest = hashlib.sha256(rubric.read_bytes("walkthrough.md")).hexdigest()
        self.assertIn(f"walkthrough.md_sha256: {digest}", rubric.read_text("VERSION"))
        self.assertNotIn(b"\r", rubric.read_bytes("walkthrough.md"))

    def test_walkthrough_asks_the_four_questions_and_forbids_inference(self):
        text = rubric.read_text("walkthrough.md")
        for needle in ("know what to try next", "notice", "recognise", "understand what happened",
                       "must not fill a gap", "No aggregate score"):
            self.assertIn(needle, text)

    @unittest.skipUnless(LUGOS_REFERENCES.is_dir(), "no Lugos checkout beside this repository")
    def test_matches_lugos_checkout(self):
        for name in PINNED:
            with self.subTest(name=name):
                self.assertEqual(rubric.read_bytes(name), (LUGOS_REFERENCES / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
