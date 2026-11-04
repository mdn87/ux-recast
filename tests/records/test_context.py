"""S2.1: PRODUCT.md and DESIGN.md are read as text and written only when absent."""
import os
from pathlib import Path
import tempfile
import threading
import unittest

from ux_recast.records import context


class ContextRecords(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_read_returns_text_as_stored_or_none(self):
        self.assertIsNone(context.read(self.root, "PRODUCT.md"))
        raw = "# Product\r\n\r\nAudience: équipe on phones\r\n<!-- kept -->\n"
        (self.root / "PRODUCT.md").write_bytes(raw.encode("utf-8"))
        self.assertEqual(context.read(self.root, "PRODUCT.md"), raw)

    def test_existing_records_are_never_modified(self):
        stored = {"PRODUCT.md": b"# Ours\r\nno template here\r\n", "DESIGN.md": b"---\nbasis: accepted\n---\n"}
        for name, data in stored.items():
            path = self.root / name
            path.write_bytes(data)
            os.utime(path, (1_000_000_000, 1_000_000_000))
        self.assertEqual(context.ensure(self.root), {"PRODUCT.md": False, "DESIGN.md": False})
        for name, data in stored.items():
            path = self.root / name
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(path.stat().st_mtime, 1_000_000_000)

    def test_missing_records_get_the_packaged_starter(self):
        (self.root / "DESIGN.md").write_bytes(b"mine\n")
        self.assertEqual(context.ensure(self.root), {"PRODUCT.md": True, "DESIGN.md": False})
        self.assertEqual((self.root / "PRODUCT.md").read_bytes(), context.starter("PRODUCT.md"))
        self.assertEqual((self.root / "DESIGN.md").read_bytes(), b"mine\n")
        self.assertNotIn(b"\r\n", context.starter("PRODUCT.md"))
        self.assertTrue(context.starter("DESIGN.md").startswith(b"---\nbasis: proposed\n---\n"))

    def test_only_the_two_context_records_are_accepted(self):
        for name in ("README.md", "../PRODUCT.md", "product.md"):
            with self.assertRaises(ValueError):
                context.create(self.root, name)
            with self.assertRaises(ValueError):
                context.read(self.root, name)

    def test_a_race_to_create_yields_exactly_one_file(self):
        for round_ in range(50):
            root = self.root / str(round_)
            root.mkdir()
            barrier = threading.Barrier(8)
            results = []

            def worker():
                barrier.wait()
                results.append(context.create(root, "DESIGN.md"))

            threads = [threading.Thread(target=worker) for _ in range(8)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(results.count(True), 1, f"round {round_}: {results}")
            self.assertEqual([p.name for p in root.iterdir()], ["DESIGN.md"])
            self.assertEqual((root / "DESIGN.md").read_bytes(), context.starter("DESIGN.md"))


if __name__ == "__main__":
    unittest.main()
