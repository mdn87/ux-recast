"""Pin the Phase 4 rubric and reviewer bytes and the original D-21 walkthrough assignment."""
import hashlib
import unittest

from ux_recast import rubric

PINNED = {
    "rubric.md": "151a63d36374bdcba28cf07590ef1027f9f168dcd7c427680b997547db90dbb4",
    "autowork-reviewer.md": "a6ba939e3737f3c75c5369b5ce6345533b1cd7bbd514b4a55b689afddf8d339d",
    "walkthrough.md": "939abcc15e9128e984c81f30236c88e66e1361a771165b74e03be2ae811b97a6",
}


class RubricBytes(unittest.TestCase):
    def test_pinned_digests(self):
        for name, digest in PINNED.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256(rubric.read_bytes(name)).hexdigest(), digest)

    def test_version_file_agrees_with_pins(self):
        text = rubric.read_text("VERSION")
        self.assertEqual(rubric.version(), "2")
        for name, digest in PINNED.items():
            self.assertIn(f"{name}_sha256: {digest}", text)

    def test_walkthrough_asks_the_four_questions_and_forbids_inference(self):
        text = rubric.read_text("walkthrough.md")
        for needle in ("know what to try next", "notice", "recognise", "understand what happened",
                       "must not fill a gap", "No aggregate score"):
            self.assertIn(needle, text)

if __name__ == "__main__":
    unittest.main()
