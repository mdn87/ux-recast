"""D-21: walkthrough mode and the prompt hand-off on the packet provider.

A review-mode packet must stay byte-for-byte the Lugos legacy packet (D-15
parity, the differential baseline checks the rest); walkthrough mode swaps the
reviewer assignment, keeps the rubric, and records its mode and rubric version
in the outer packet only.
"""
import json

import pytest

from ux_recast import rubric
from ux_recast.contracts import validate
from ux_recast.cycle.control import execute
from ux_recast.providers import lugos_autowork as packets


@pytest.fixture
def opened(tmp_path):
    task = {"flow": "contact", "goal": "Send a request", "starting_conditions": "Signed out",
            "expected_outcome": "Request received without losing draft", "device_input": "Keyboard",
            "source": "Product requirement", "assumptions": [], "acceptance": ["Rejected email preserves draft"]}
    (tmp_path / "task.json").write_text(json.dumps(task), encoding="utf-8")
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps({"plan": "1. Open the form 2. Send", "observations": [], "screenshots": []}),
                        encoding="utf-8")
    execute(tmp_path, "session", ["mode", "once", "--scope", "contact"])
    run = execute(tmp_path, "session", ["checkpoint", "--id", "plan", "--stage", "plan",
                                        "--affected", "contact", "--task", str(tmp_path / "task.json")])
    return tmp_path, run["run_id"], evidence


def test_review_mode_packet_carries_no_new_fields(opened):
    root, run_id, evidence = opened
    packet = packets.prepare(root, "session", run_id, evidence)
    assert "review_mode" not in packet and "rubric_version" not in packet
    assert packet["request"]["task"].startswith("# Bounded UX reviewer assignment")


def test_walkthrough_mode_uses_the_fresh_evaluator_assignment(opened):
    root, run_id, evidence = opened
    with pytest.raises(ValueError, match="mode"):
        packets.prepare(root, "session", run_id, evidence, mode="scored")
    packet = packets.prepare(root, "session", run_id, evidence, mode="walkthrough")
    task = packet["request"]["task"]
    assert task.startswith("# Fresh-evaluator walkthrough assignment")
    assert "Bounded UX reviewer assignment" not in task
    assert "Recognition over recall" in task  # the rubric still travels
    assert packet["review_mode"] == "walkthrough"
    assert packet["rubric_version"] == rubric.version() == "1"
    assert packet["rubric_sha256"] == packets.digest(rubric.read_bytes("rubric.md"))
    assert set(packet["request"]) == {"action", "role", "workspace", "task", "task_class_hint",
                                      "required_capabilities", "input_modalities", "timeout_seconds"}
    validate("packet", packet)


def test_prompt_returns_the_claimed_task_exactly_and_only_after_claim(opened):
    root, run_id, evidence = opened
    packet = packets.prepare(root, "session", run_id, evidence, mode="walkthrough")
    with pytest.raises(ValueError, match="claim"):
        packets.prompt(root, "session", run_id)
    packets.claim(root, "session", run_id)
    handed = packets.prompt(root, "session", run_id)
    assert handed["task"] == packet["request"]["task"]
    assert handed["task_sha256"] == packet["task_sha256"]
    assert handed["visual_inputs"] == [] and handed["review_mode"] == "walkthrough"
    evidence.write_text(evidence.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        packets.prompt(root, "session", run_id)
    with pytest.raises(ValueError, match="Unknown controller run"):
        packets.prompt(root, "session", "0" * 12)
