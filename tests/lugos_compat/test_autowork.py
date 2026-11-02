"""Autowork payload and once-only dispatch contract, using real controller state."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

import ux_recast.providers.lugos_autowork as _packets
SCRIPTS = Path(_packets.__file__).parent
from ux_recast.cycle.control import execute


@pytest.fixture
def packet_module():
    spec = importlib.util.spec_from_file_location("ux_packet", SCRIPTS / "lugos_autowork.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_inputs(tmp_path):
    task = {"flow": "contact", "goal": "Send a request", "starting_conditions": "Signed out",
            "expected_outcome": "Request received without losing draft", "device_input": "Keyboard",
            "source": "Product requirement", "assumptions": [], "acceptance": ["Rejected email preserves draft"]}
    task_path = tmp_path / "task.json"
    task_path.write_text(json.dumps(task))
    evidence = tmp_path / "observations.json"
    evidence.write_text(json.dumps({"observations": [{"step": "Submit invalid email", "visible_result": "Name becomes empty"}],
                                    "screenshots": []}))
    return task_path, evidence


@pytest.fixture
def claimed(tmp_path):
    task_path, evidence = write_inputs(tmp_path)
    execute(tmp_path, "session", ["mode", "once", "--scope", "contact"])
    run = execute(tmp_path, "session", ["checkpoint", "--id", "batch", "--stage", "implementation",
                  "--affected", "contact", "--task", str(task_path)])
    return tmp_path, run["run_id"], evidence


@pytest.fixture
def bound(tmp_path):
    task_path, evidence = write_inputs(tmp_path)
    page = tmp_path / "page.html"
    page.write_text("A")
    execute(tmp_path, "session", ["mode", "session", "--scope", "contact"])
    run = execute(tmp_path, "session", ["checkpoint", "--id", "batch", "--stage", "implementation",
                  "--affected", "contact", "--task", str(task_path), "--input", "page.html",
                  "--origin", "checkpoint"])
    return tmp_path, run["run_id"], evidence, page


def deliver(packet_module, root, run_id, evidence):
    packet = packet_module.prepare(root, "session", run_id, evidence)
    packet_module.claim(root, "session", run_id)
    result = root / "result.json"
    result.write_text(json.dumps({"status": "completed", "run_id": "real-run", "answer": "Review finding",
                                  "task_sha256": packet["task_sha256"]}))
    return packet_module.record(root, "session", run_id, result)


def test_default_off_never_prepares_dispatch(packet_module, tmp_path):
    with pytest.raises(ValueError, match="off"):
        packet_module.prepare(tmp_path, "session", "no-run", tmp_path / "missing.json")


def test_payload_is_self_contained_and_read_only(packet_module, claimed):
    root, run_id, evidence = claimed
    packet = packet_module.prepare(root, "session", run_id, evidence)
    request = packet["request"]
    assert request["action"] == "delegate"
    assert request["role"] == "explorer"
    assert "allowed_paths" not in request and "verification" not in request
    assert "Send a request" in request["task"]
    assert "Name becomes empty" in request["task"]
    assert "Recognition over recall" in request["task"]
    assert request["required_capabilities"] == ["repository_read"]
    assert request["input_modalities"] == ["text"]
    assert packet["activation"]["mode"] == "once"
    assert packet["activation"]["scope"] == ["contact"]


def test_off_after_prepare_revokes_claim(packet_module, claimed):
    root, run_id, evidence = claimed
    packet_module.prepare(root, "session", run_id, evidence)
    execute(root, "session", ["mode", "off"])
    with pytest.raises(ValueError, match="off"):
        packet_module.claim(root, "session", run_id)


def test_claim_is_single_use_and_records_exact_request(packet_module, claimed):
    root, run_id, evidence = claimed
    packet = packet_module.prepare(root, "session", run_id, evidence)
    assert packet_module.claim(root, "session", run_id) == packet["request"]
    with pytest.raises(ValueError, match="already claimed"):
        packet_module.claim(root, "session", run_id)


def test_changed_evidence_cannot_be_dispatched(packet_module, claimed):
    root, run_id, evidence = claimed
    packet_module.prepare(root, "session", run_id, evidence)
    evidence.write_text('{"observations": [], "screenshots": []}')
    with pytest.raises(ValueError, match="changed"):
        packet_module.claim(root, "session", run_id)


def test_images_declare_capability_and_cannot_escape_workspace(packet_module, claimed, tmp_path):
    root, run_id, evidence = claimed
    image = root / "screen.png"
    # Real PNG fixture from the existing demonstration is unnecessary for payload construction.
    image.write_bytes(b"image fixture")
    evidence.write_text(json.dumps({"observations": ["Error state"], "screenshots": ["screen.png"]}))
    packet = packet_module.prepare(root, "session", run_id, evidence)
    assert packet["request"]["required_capabilities"] == ["repository_read", "image_input"]
    assert packet["request"]["input_modalities"] == ["text", "image"]
    assert packet["request"]["visual_inputs"] == [str(image.resolve())]
    evidence.write_text(json.dumps({"observations": [], "screenshots": ["../outside.png"]}))
    with pytest.raises((ValueError, FileNotFoundError)):
        packet_module.prepare(root, "session", run_id, evidence)


def test_result_retains_failure_without_granting_repair(packet_module, claimed):
    root, run_id, evidence = claimed
    packet_module.prepare(root, "session", run_id, evidence)
    packet_module.claim(root, "session", run_id)
    result = root / "result.json"
    result.write_text(json.dumps({"status": "failed_precondition", "run_id": "actual-run", "answer": ""}))
    receipt = packet_module.record(root, "session", run_id, result)
    assert receipt["accepted"] is False
    assert receipt["autowork_run_id"] == "actual-run"
    with pytest.raises(ValueError, match="already claimed"):
        packet_module.claim(root, "session", run_id)


@pytest.mark.parametrize("matching", [True, False])
def test_completed_delivery_must_match_original_task(packet_module, claimed, matching):
    root, run_id, evidence = claimed
    packet = packet_module.prepare(root, "session", run_id, evidence)
    packet_module.claim(root, "session", run_id)
    result = root / "result.json"
    result.write_text(json.dumps({"status": "completed", "run_id": "real-run", "answer": "Review finding",
                                 "task_sha256": packet["task_sha256"] if matching else "wrong-task"}))
    assert packet_module.record(root, "session", run_id, result)["accepted"] is matching


def test_changed_bound_input_is_rejected_at_claim(packet_module, bound):
    root, run_id, evidence, page = bound
    packet_module.prepare(root, "session", run_id, evidence)
    page.write_text("B")
    with pytest.raises(ValueError, match="changed"):
        packet_module.claim(root, "session", run_id)
    packet = json.loads((packet_module.folder_for(root, "session", run_id) / "packet.json").read_text())
    assert packet["dispatch_status"] == "prepared"


def test_changed_bound_input_leaves_old_findings_stale(packet_module, bound):
    root, run_id, evidence, page = bound
    assert deliver(packet_module, root, run_id, evidence)["accepted"] is True
    current = packet_module.consume(root, "session", run_id)
    assert (current["accepted"], current["applicable"], current["findings"]) == (True, True, "current")
    page.write_text("B")
    stale = packet_module.consume(root, "session", run_id)
    assert (stale["accepted"], stale["applicable"], stale["findings"]) == (True, False, "stale")
    assert stale["changed"] == ["page.html"]
    folder = packet_module.folder_for(root, "session", run_id)
    assert json.loads((folder / "autowork-result.json").read_text())["answer"] == "Review finding"
    receipt = json.loads((folder / "receipt.json").read_text())
    assert (receipt["accepted"], receipt["findings"]) == (True, "stale")
    page.write_text("A")
    assert packet_module.consume(root, "session", run_id)["applicable"] is False


def test_legacy_findings_reuse_packet_evidence_hashes(packet_module, claimed):
    root, run_id, evidence = claimed
    deliver(packet_module, root, run_id, evidence)
    assert packet_module.consume(root, "session", run_id)["applicable"] is True
    evidence.write_text('{"observations": ["changed"], "screenshots": []}')
    assert packet_module.consume(root, "session", run_id)["findings"] == "stale"


def test_consumption_requires_recorded_delivery(packet_module, bound):
    root, run_id, evidence, _ = bound
    packet_module.prepare(root, "session", run_id, evidence)
    packet_module.claim(root, "session", run_id)
    with pytest.raises(ValueError, match="recorded"):
        packet_module.consume(root, "session", run_id)


def test_absent_bound_source_becomes_stale_when_created(packet_module, tmp_path):
    task, evidence = write_inputs(tmp_path)
    execute(tmp_path, "session", ["mode", "session", "--scope", "contact"])
    run = execute(tmp_path, "session", ["checkpoint", "--id", "removed-page", "--stage", "implementation",
        "--affected", "contact", "--task", str(task), "--input", "removed.html", "--origin", "checkpoint"])
    assert run["manifest"]["inputs"] == {"removed.html": None}
    deliver(packet_module, tmp_path, run["run_id"], evidence)
    assert packet_module.consume(tmp_path, "session", run["run_id"])["applicable"]
    (tmp_path / "removed.html").write_text("restored")
    stale = packet_module.consume(tmp_path, "session", run["run_id"])
    assert not stale["applicable"]
    assert stale["changed"] == ["removed.html"]


def test_current_task_file_is_rechecked_at_claim_and_consumption(packet_module, bound):
    root, run_id, evidence, _ = bound
    packet_module.prepare(root, "session", run_id, evidence)
    task_path = root / "task.json"
    original = task_path.read_text()
    task = json.loads(original)
    task["acceptance"].append("New product requirement")
    task_path.write_text(json.dumps(task))
    with pytest.raises(ValueError, match="changed"):
        packet_module.claim(root, "session", run_id)
    task_path.write_text(original)
    deliver(packet_module, root, run_id, evidence)
    task_path.write_text(json.dumps(task))
    assert packet_module.consume(root, "session", run_id)["applicable"] is False


def test_current_configuration_is_required_at_claim_and_consumption(packet_module, tmp_path):
    task, evidence = write_inputs(tmp_path)
    (tmp_path / "page.html").write_text("A")
    execute(tmp_path, "session", ["mode", "session", "--scope", "contact"])
    run = execute(tmp_path, "session", ["checkpoint", "--id", "configured", "--stage", "implementation",
        "--affected", "contact", "--task", str(task), "--input", "page.html", "--origin", "checkpoint",
        "--config", "viewport=desktop"])
    run_id = run["run_id"]
    packet = packet_module.prepare(tmp_path, "session", run_id, evidence)
    with pytest.raises(ValueError, match="config"):
        packet_module.claim(tmp_path, "session", run_id)
    with pytest.raises(ValueError, match="changed"):
        packet_module.claim(tmp_path, "session", run_id, config={"viewport": "mobile"})
    packet_module.claim(tmp_path, "session", run_id, config={"viewport": "desktop"})
    result = tmp_path / "result.json"
    result.write_text(json.dumps({"status": "completed", "run_id": "real-run", "answer": "Review finding",
                                  "task_sha256": packet["task_sha256"]}))
    packet_module.record(tmp_path, "session", run_id, result)
    with pytest.raises(ValueError, match="config"):
        packet_module.consume(tmp_path, "session", run_id)
    assert packet_module.consume(tmp_path, "session", run_id, config={"viewport": "desktop"})["applicable"]
    assert not packet_module.consume(tmp_path, "session", run_id, config={"viewport": "mobile"})["applicable"]
