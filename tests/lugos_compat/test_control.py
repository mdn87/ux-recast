"""Public mode/checkpoint contract. No browser or model calls required."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import ux_recast.cycle.control as _control
SCRIPT = Path(_control.__file__)


class ControlTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("ux_control", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = self.root / "task.json"
        self.task.write_text(json.dumps({
            "flow": "signup", "goal": "Create an account",
            "starting_conditions": "Signed out", "expected_outcome": "Account exists",
            "device_input": "Desktop keyboard", "assumptions": [],
            "acceptance": ["Invalid input preserves valid entries"],
            "source": "Product requirement provided before implementation",
        }))
        self.page = self.root / "page.html"
        self.page.write_text("A")

    def call(self, *args, session="session-a"):
        return self.module.execute(self.root, session, list(args))

    def command(self, *args):
        return [sys.executable, str(SCRIPT), "--project", str(self.root), "--session", "session-a", *args]

    def cli(self, *args):
        # A separate process per call: only the persisted state survives.
        done = subprocess.run(self.command(*args), capture_output=True, text=True, check=True)
        return json.loads(done.stdout)

    def snapshot_args(self, name, origin="checkpoint", *extra):
        return ["checkpoint", "--id", name, "--stage", "implementation", "--affected", "signup",
                "--task", str(self.task), "--input", "page.html", "--origin", origin, *extra]

    def snapshot(self, name, origin="checkpoint", *extra):
        return self.call(*self.snapshot_args(name, origin, *extra))

    def close(self, run):
        self.call("phase", run["run_id"], "verify")
        self.call("finish", run["run_id"], "--result", "verified")

    def enable(self, mode="session"):
        return self.call("mode", mode, "--scope", "signup", "--shared", "form-field=signup")

    def checkpoint(self, name="batch-1", affected="signup"):
        return self.call("checkpoint", "--id", name, "--stage", "implementation",
                         "--affected", affected, "--task", str(self.task))

    def test_default_off_creates_no_review(self):
        self.assertEqual(self.call("status")["mode"], "off")
        self.assertFalse(self.checkpoint()["invoke"])

    def test_once_is_consumed_only_by_matching_flow(self):
        self.enable("once")
        self.assertFalse(self.checkpoint(affected="unrelated")["invoke"])
        run = self.checkpoint()
        self.assertTrue(run["invoke"])
        self.assertEqual(run["mode"], "once")
        self.assertFalse(self.checkpoint("batch-2")["invoke"])
        self.assertTrue(self.call("phase", run["run_id"], "repair")["allowed"])
        self.assertTrue(self.call("phase", run["run_id"], "verify")["allowed"])
        self.call("finish", run["run_id"], "--result", "verified")
        self.assertEqual(self.call("status")["mode"], "off")

    def test_session_is_isolated_and_checkpoint_is_idempotent(self):
        self.enable()
        self.assertTrue(self.checkpoint()["invoke"])
        self.assertFalse(self.checkpoint()["invoke"])
        self.assertEqual(self.call("status", session="another-session")["mode"], "off")

    def test_off_revokes_existing_run_and_preserves_history(self):
        self.enable()
        run = self.checkpoint()
        self.call("mode", "off")
        self.assertFalse(self.call("phase", run["run_id"], "repair")["allowed"])
        self.assertFalse(self.checkpoint("later")["invoke"])
        self.assertEqual(len(self.call("status")["runs"]), 1)

    def test_shared_component_maps_to_affected_flow(self):
        self.enable()
        self.assertTrue(self.checkpoint(affected="form-field")["invoke"])

    def test_original_contract_is_snapshotted_and_cycle_is_bounded(self):
        self.enable()
        run = self.checkpoint()
        self.task.write_text('{"flow": "signup", "goal": "changed"}')
        self.assertEqual(run["task"]["goal"], "Create an account")
        self.assertTrue(self.call("phase", run["run_id"], "repair")["allowed"])
        self.assertFalse(self.call("phase", run["run_id"], "repair")["allowed"])
        self.assertTrue(self.call("phase", run["run_id"], "verify")["allowed"])
        self.assertFalse(self.call("phase", run["run_id"], "repair")["allowed"])
        self.call("finish", run["run_id"], "--result", "remaining")
        self.assertFalse(self.checkpoint()["invoke"])

    def test_missing_outcome_fails_before_creating_run(self):
        self.enable()
        self.task.write_text('{"flow": "signup", "goal": "Click button"}')
        with self.assertRaises(ValueError):
            self.checkpoint()
        self.assertEqual(self.call("status")["runs"], [])

    def test_verified_requires_verification_and_task_must_match_scope(self):
        self.enable()
        run = self.checkpoint()
        with self.assertRaises(ValueError):
            self.call("finish", run["run_id"], "--result", "verified")
        self.call("finish", run["run_id"], "--result", "remaining")
        task = json.loads(self.task.read_text())
        task["flow"] = "unrelated"
        self.task.write_text(json.dumps(task))
        with self.assertRaises(ValueError):
            self.checkpoint("batch-2")

    def test_unknown_mode_fails_closed(self):
        self.enable()
        path = next((self.root / ".ux-review").glob("*.json"))
        state = json.loads(path.read_text())
        state["mode"] = "always"
        path.write_text(json.dumps(state))
        with self.assertRaises(ValueError):
            self.checkpoint()

    def test_plan_and_implementation_are_distinct_checkpoints(self):
        self.enable()
        plan = self.call("checkpoint", "--id", "batch-1", "--stage", "plan",
                         "--affected", "signup", "--task", str(self.task))
        self.call("phase", plan["run_id"], "verify")
        self.call("finish", plan["run_id"], "--result", "verified")
        self.assertTrue(self.checkpoint()["invoke"])

    def test_verification_without_repair_is_allowed(self):
        self.enable()
        run = self.checkpoint()
        self.assertTrue(self.call("phase", run["run_id"], "verify")["allowed"])
        self.assertFalse(self.call("phase", run["run_id"], "verify")["allowed"])
        self.call("finish", run["run_id"], "--result", "verified")
        self.assertTrue(self.checkpoint("batch-2")["invoke"])

    def test_legacy_checkpoint_keeps_stable_id_contract_without_manifest(self):
        self.enable()
        run = self.checkpoint()
        self.assertNotIn("manifest", run)
        self.close(run)
        self.page.write_text("B")
        self.assertFalse(self.checkpoint()["invoke"])
        self.assertTrue(self.checkpoint("batch-renamed")["invoke"])

    def test_five_event_snapshot_sequence_requests_two_reviews(self):
        self.enable()
        invoked = []
        for name, content, origin in [("batch-a", "A", "checkpoint"), ("batch-a", "A", "checkpoint"),
                                      ("batch-b", "A", "checkpoint"), ("review-output", "A", "reviewer-output"),
                                      ("batch-a", "B", "checkpoint")]:
            self.page.write_text(content)
            result = self.snapshot(name, origin)
            if result["invoke"]:
                self.close(result)
            invoked.append(result["invoke"])
        self.assertEqual(invoked, [True, False, False, False, True])
        manifests = [r["manifest"] for r in self.call("status")["runs"]]
        self.assertEqual([m["inputs"]["page.html"] for m in manifests],
                         [self.module.hashlib.sha256(c).hexdigest() for c in (b"A", b"B")])
        self.assertEqual({(m["flow"], m["stage"]) for m in manifests}, {("signup", "implementation")})

    def test_same_snapshot_coalesces_after_process_restart(self):
        self.cli("mode", "session", "--scope", "signup")
        first = self.cli(*self.snapshot_args("batch-a"))
        self.assertTrue(first["invoke"])
        self.cli("phase", first["run_id"], "verify")
        self.cli("finish", first["run_id"], "--result", "verified")
        renamed = self.cli(*self.snapshot_args("renamed-after-restart"))
        self.assertFalse(renamed["invoke"])
        self.assertIn("snapshot previously verified", renamed["reason"])

    def test_concurrent_repeated_triggers_create_one_cycle(self):
        self.enable()
        for round_number in range(2):
            processes = [subprocess.Popen(self.command(*self.snapshot_args("label-%d" % n)),
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                         for n in range(6)]
            results = []
            for process in processes:
                output, error = process.communicate(timeout=30)
                self.assertEqual(process.returncode, 0, error or output)
                result = json.loads(output)
                self.assertNotIn("error", result)
                results.append(result)
            self.assertEqual(sum(r["invoke"] for r in results), 1 if round_number == 0 else 0)
            for result in results:
                if not result["invoke"]:
                    self.assertIn("active bounded cycle" if round_number == 0 else "snapshot previously verified",
                                  result["reason"])
            if round_number == 0:
                self.close(next(r for r in results if r["invoke"]))
        self.assertEqual(len(self.call("status")["runs"]), 1)

    def test_changed_manifest_waits_for_cycle_and_includes_configuration(self):
        self.enable()
        run = self.snapshot("batch-a", "checkpoint", "--config", "viewport=desktop")
        self.page.write_text("B")
        self.assertIn("active", self.snapshot("batch-b")["reason"])
        self.close(run)
        self.page.write_text("A")
        self.assertFalse(self.snapshot("batch-c", "checkpoint", "--config", "viewport=desktop")["invoke"])
        self.assertTrue(self.snapshot("batch-c", "checkpoint", "--config", "viewport=mobile")["invoke"])

    def test_changed_task_contract_is_a_changed_manifest(self):
        self.enable()
        self.close(self.snapshot("batch-a"))
        task = json.loads(self.task.read_text())
        task["acceptance"].append("Errors are announced")
        self.task.write_text(json.dumps(task))
        self.assertTrue(self.snapshot("batch-a")["invoke"])

    def test_only_completed_checkpoints_request_review(self):
        self.enable()
        self.assertFalse(self.snapshot("edit", "event")["invoke"])
        self.assertFalse(self.snapshot("repair-outside-cycle", "repair")["invoke"])
        self.assertTrue(self.snapshot("batch-a")["invoke"])

    def test_repair_origin_keeps_cycle_budget_and_does_not_retrigger(self):
        self.enable()
        run = self.snapshot("batch-a")
        self.assertTrue(self.call("phase", run["run_id"], "repair")["allowed"])
        self.page.write_text("A repaired")
        self.assertFalse(self.snapshot("repair-1", "repair")["invoke"])
        status = self.call("status")
        self.assertEqual(len(status["runs"]), 1)
        self.assertEqual(status["runs"][0]["budget"], run["budget"])
        self.assertEqual(status["runs"][0]["phase"], "repair")
        self.assertFalse(self.call("phase", run["run_id"], "repair")["allowed"])
        self.assertTrue(self.call("phase", run["run_id"], "verify")["allowed"])
        self.call("finish", run["run_id"], "--result", "verified")
        self.assertFalse(self.snapshot("after-repair")["invoke"])
        self.page.write_text("C")
        self.assertTrue(self.snapshot("later-batch")["invoke"])

    def test_snapshot_once_and_off_keep_cycle_rules(self):
        self.enable("once")
        run = self.snapshot("batch-a")
        self.assertEqual(run["mode"], "once")
        self.close(run)
        self.page.write_text("B")
        self.assertEqual(self.snapshot("batch-b")["reason"], "off")
        self.enable()
        active = self.snapshot("batch-b")
        self.call("mode", "off")
        self.assertFalse(self.call("phase", active["run_id"], "repair")["allowed"])
        self.assertEqual(self.snapshot("batch-c")["reason"], "off")
        self.enable()
        cancelled = self.snapshot("batch-c")
        self.assertFalse(cancelled["invoke"])
        self.assertIn("cancelled", cancelled["reason"])
        self.assertIn(active["run_id"], cancelled["reason"])
        self.page.write_text("C")
        self.assertTrue(self.snapshot("batch-c")["invoke"])

    def test_repair_requires_claimed_phase_and_original_task_and_stage(self):
        self.enable()
        run = self.snapshot("batch-a")
        self.page.write_text("B")
        self.snapshot("unclaimed-repair", "repair")
        self.assertEqual(self.call("status")["runs"][0]["repair_manifests"], [])
        self.page.write_text("A")
        self.call("phase", run["run_id"], "repair")
        task = json.loads(self.task.read_text())
        task["acceptance"].append("A different requirement")
        self.task.write_text(json.dumps(task))
        with self.assertRaises(ValueError, msg="Repair cannot change the task contract"):
            self.snapshot("different-task", "repair")
        self.assertEqual(self.call("status")["runs"][0]["repair_manifests"], [])
        task["acceptance"].pop()
        self.task.write_text(json.dumps(task))
        with self.assertRaises(ValueError, msg="Repair cannot change the stage"):
            self.call(*self.snapshot_args("wrong-stage", "repair"), "--stage", "plan")
        task["acceptance"].append("A different requirement")
        self.task.write_text(json.dumps(task))
        self.call("finish", run["run_id"], "--result", "remaining")
        self.assertTrue(self.snapshot("new-requirement")["invoke"])

    def test_repair_phase_records_final_inputs_without_an_extra_event(self):
        self.enable()
        run = self.snapshot("batch-a")
        self.call("phase", run["run_id"], "repair")
        self.page.write_text("repaired")
        self.call("phase", run["run_id"], "verify")
        self.call("finish", run["run_id"], "--result", "verified")
        self.assertFalse(self.snapshot("renamed-after-repair")["invoke"])

    def test_snapshot_inputs_must_be_explicit_contained_project_files(self):
        self.enable()
        with self.assertRaises(ValueError):
            self.call("checkpoint", "--id", "x", "--stage", "implementation", "--affected", "signup",
                      "--task", str(self.task), "--input", "page.html")
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        stray = Path(outside.name) / "stray.html"
        stray.write_text("A")
        review = self.root / ".ux-review" / "result.json"
        review.write_text("{}")
        for path in (stray, review):
            with self.assertRaises(ValueError):
                self.call("checkpoint", "--id", "x", "--stage", "implementation", "--affected", "signup",
                          "--task", str(self.task), "--input", str(path), "--origin", "checkpoint")
        self.assertEqual(self.call("status")["runs"], [])

    def test_relative_task_is_read_from_project_outside_working_directory(self):
        self.enable()
        args = self.snapshot_args("relative-task")
        args[args.index("--task") + 1] = "task.json"
        result = self.cli(*args)
        self.assertTrue(result["invoke"])
        self.assertEqual(result["manifest"]["task_path"], "task.json")
        self.assertEqual(result["task"], json.loads(self.task.read_text()))

    def test_snapshot_repair_rejects_changed_source_task_and_configuration(self):
        self.enable()
        run = self.snapshot("configured", "checkpoint", "--config", "viewport=desktop")
        args = ["phase", run["run_id"], "repair", "--config", "viewport=desktop"]
        self.page.write_text("B")
        with self.assertRaisesRegex(ValueError, "changed"):
            self.call(*args)
        self.page.write_text("A")
        original = self.task.read_text()
        self.task.write_text(original.replace("Create an account", "New task"))
        with self.assertRaisesRegex(ValueError, "changed"):
            self.call(*args)
        self.task.write_text(original)
        with self.assertRaisesRegex(ValueError, "config"):
            self.call("phase", run["run_id"], "repair")
        with self.assertRaisesRegex(ValueError, "changed"):
            self.call(*args[:-1], "viewport=mobile")
        self.assertEqual(self.call("status")["runs"][0]["phase"], "review")
        self.assertTrue(self.call(*args)["allowed"])

    def test_repair_seals_expanded_and_deleted_inputs(self):
        self.enable()
        run = self.snapshot("batch-a")
        self.call("phase", run["run_id"], "repair")
        extra = self.root / "new.html"
        extra.write_text("first repair")
        self.snapshot("expanded", "repair", "--input", "page.html", "new.html")
        extra.write_text("final repair")
        self.page.unlink()
        self.call("phase", run["run_id"], "verify")
        self.call("finish", run["run_id"], "--result", "verified")
        self.assertFalse(self.snapshot("expanded-final", "checkpoint", "--input", "page.html", "new.html")["invoke"])
        self.page.write_text("restored")
        self.assertTrue(self.snapshot("later", "checkpoint", "--input", "page.html", "new.html")["invoke"])


if __name__ == "__main__":
    unittest.main()
