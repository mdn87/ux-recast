"""S4.2: an image review is checked against the installed Autowork image policy before it is sent.

A review with screenshots always declares the image capability, the image
modality and the files together. Before ``submit`` sends one, it asks the
installed Autowork assignment policy whether that task class is granted image
input. A policy that would not grant it refuses the submit with a message:
nothing is sent, the claim is kept, and the request is never cut down to text.

The policy checks need the Autowork package and skip without it; the checks of
what happens when it is absent run everywhere.
"""
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

import pytest

from ux_recast.contracts import validate
from ux_recast.cycle.control import execute
from ux_recast.providers import lugos_autowork as packets

SESSION = "image-preflight-test"
SERVER = Path(__file__).parent / "lugos_compat" / "fixtures" / "mcp_fixture_server.py"
AUTOWORK_MODULES = ("autowork", "autowork.campaign", "autowork.campaign.assignment_policy",
                    "autowork.campaign.dispatcher")


def write_png(path):
    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff")) + chunk(b"IEND", b""))


@pytest.fixture
def image_run(tmp_path):
    """A claimed review whose evidence carries one screenshot: (root, run_id, packet, request)."""
    task = {"flow": "contact", "goal": "Send a request", "starting_conditions": "Signed out",
            "expected_outcome": "Request received without losing draft", "device_input": "Keyboard",
            "source": "Product requirement", "assumptions": [], "acceptance": ["Rejected email preserves draft"]}
    (tmp_path / "task.json").write_text(json.dumps(task), encoding="utf-8")
    write_png(tmp_path / "shot.png")
    (tmp_path / "observations.json").write_text(json.dumps(
        {"observations": [{"step": "Open the page", "visible_result": "The form renders"}],
         "screenshots": ["shot.png"]}), encoding="utf-8")
    execute(tmp_path, SESSION, ["mode", "once", "--scope", "contact"])
    run = execute(tmp_path, SESSION, ["checkpoint", "--id", "batch", "--stage", "plan",
                                      "--affected", "contact", "--task", str(tmp_path / "task.json")])
    packet = packets.prepare(tmp_path, SESSION, run["run_id"], "observations.json")
    request = packets.claim(tmp_path, SESSION, run["run_id"])
    return tmp_path, run["run_id"], packet, request


@pytest.fixture
def autowork():
    """The installed Autowork policy pieces, or a skip when the package is not installed."""
    pytest.importorskip("autowork")
    from types import SimpleNamespace
    from autowork.campaign import assignment_policy, dispatch_contract
    from autowork.campaign.dispatcher import CAMPAIGN_ROOT, DEFAULT_ASSIGNMENT_POLICY_PATH
    from autowork.campaign.model_catalog import load_model_catalog
    return SimpleNamespace(policy=assignment_policy, contract=dispatch_contract,
                           policy_path=DEFAULT_ASSIGNMENT_POLICY_PATH,
                           catalog=load_model_catalog(CAMPAIGN_ROOT / "model-catalog.toml"))


def without_image_opt_in(autowork, tmp_path):
    """A copy of the installed policy with its image opt-in table removed."""
    text = Path(autowork.policy_path).read_text(encoding="utf-8")
    changed, count = re.subn(r"\[image_input_opt_in\]\s*task_classes\s*=\s*\[[^\]]*\]\s*", "", text)
    assert count == 1, "the installed policy has no image_input_opt_in table to remove"
    path = tmp_path / "policy-without-image-opt-in.toml"
    path.write_text(changed, encoding="utf-8")
    return path


def autowork_grant(autowork, request, policy_path):
    """What Autowork's own compiler grants this request under the policy at ``policy_path``."""
    contract = autowork.contract
    dispatch_request = contract.DispatchRequest(
        version=2, correlation_id="ux-recast-image-preflight", caller="autowork", profile="spark-first",
        role=request["role"], workspace=request["workspace"], task=request["task"], write=False,
        allowed_paths=(), verification=(), timeout_seconds=request["timeout_seconds"],
        task_class_hint=request["task_class_hint"],
        required_capabilities=tuple(contract.Capability(name) for name in request["required_capabilities"]),
        input_modalities=tuple(request["input_modalities"]), visual_inputs=tuple(request["visual_inputs"]))
    policy = autowork.policy.load_assignment_policy(policy_path)
    grant = autowork.policy.compile_assignment_proposal(dispatch_request, autowork.catalog, policy).proposed_grant
    return {capability.value for capability in grant.granted}


def hide_autowork(monkeypatch):
    for name in AUTOWORK_MODULES:
        monkeypatch.setitem(sys.modules, name, None)


def stored_packet(root, run_id):
    return packets.load_packet(packets.folder_for(root, SESSION, run_id))


def sent(log):
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []


def submit(root, run_id, monkeypatch, **options):
    log = root / "fixture.log"
    monkeypatch.setenv("UX_FIXTURE_MODE", "ok")
    monkeypatch.setenv("UX_FIXTURE_LOG", str(log))
    return log, lambda: packets.submit(root, SESSION, run_id, root / "out" / "result.json",
                                       server_command=[sys.executable, str(SERVER)], **options)


def test_an_image_review_declares_the_capability_the_modality_and_the_files(image_run):
    root, _, packet, request = image_run
    assert request == packet["request"]
    assert request["required_capabilities"] == ["repository_read", "image_input"]
    assert request["input_modalities"] == ["text", "image"]
    assert request["visual_inputs"] == [str((root / "shot.png").resolve())]
    validate("packet", packet)


def test_a_text_only_request_needs_no_preflight():
    assert packets.image_preflight({"task": "Review the plan.", "input_modalities": ["text"]}) is None


def test_without_autowork_the_preflight_says_it_could_not_check(image_run, monkeypatch):
    hide_autowork(monkeypatch)
    outcome = packets.image_preflight(image_run[3])
    assert outcome["status"] == "unavailable"
    assert "Autowork" in outcome["reason"]


def test_the_installed_policy_accepts_an_image_review(image_run, autowork):
    request = image_run[3]
    outcome = packets.image_preflight(request)
    assert outcome == {"status": "accepted", "task_class": "review",
                       "policy_sha256": hashlib.sha256(Path(autowork.policy_path).read_bytes()).hexdigest()}
    # The preflight reads the policy; Autowork's own compiler agrees about the grant.
    assert "image_input" in autowork_grant(autowork, request, autowork.policy_path)


def test_a_policy_without_the_opt_in_refuses_with_a_message(image_run, autowork, tmp_path):
    request = image_run[3]
    refusing = without_image_opt_in(autowork, tmp_path)
    with pytest.raises(ValueError, match="grants no image input to a 'review' task") as caught:
        packets.image_preflight(request, policy_path=refusing)
    assert "never reduced to text" in str(caught.value)
    # Autowork's own compiler refuses the same request under the same policy.
    with pytest.raises(ValueError, match="authority expansion: image_input"):
        autowork_grant(autowork, request, refusing)


def test_submit_refuses_an_image_review_the_policy_would_not_grant(image_run, autowork, tmp_path, monkeypatch):
    pytest.importorskip("mcp")
    root, run_id, _, request = image_run
    log, send = submit(root, run_id, monkeypatch, image_policy=without_image_opt_in(autowork, tmp_path))
    with pytest.raises(ValueError, match="grants no image input"):
        send()
    assert sent(log) == [], "a refused preflight must send nothing"
    packet = stored_packet(root, run_id)
    assert packet["dispatch_status"] == "claimed"
    assert packet["request"] == request, "the request keeps its images; it is never cut down to text"
    for key in ("review_dispatches", "submitted_at", "image_preflight"):
        assert key not in packet


def test_submit_sends_an_accepted_image_review_with_its_images(image_run, autowork, monkeypatch):
    pytest.importorskip("mcp")
    root, run_id, _, request = image_run
    log, send = submit(root, run_id, monkeypatch)
    send()
    assert [call["arguments"] for call in sent(log)] == [request]
    packet = stored_packet(root, run_id)
    assert packet["image_preflight"]["status"] == "accepted"
    assert packet["image_preflight"]["task_class"] == "review"
    assert packet["review_dispatches"] == 1
    assert packet["request"] == request
    validate("packet", packet)


def test_submit_proceeds_and_says_so_when_the_policy_cannot_be_checked(image_run, monkeypatch):
    pytest.importorskip("mcp")
    root, run_id, _, request = image_run
    hide_autowork(monkeypatch)
    log, send = submit(root, run_id, monkeypatch)
    send()
    assert [call["arguments"] for call in sent(log)] == [request], "the images go with the request or nothing goes"
    packet = stored_packet(root, run_id)
    assert packet["image_preflight"]["status"] == "unavailable"
    validate("packet", packet)


def test_a_text_only_submit_records_no_preflight(tmp_path, monkeypatch):
    pytest.importorskip("mcp")
    (tmp_path / "task.json").write_text(json.dumps(
        {"flow": "contact", "goal": "Send a request", "starting_conditions": "Signed out",
         "expected_outcome": "Request received", "device_input": "Keyboard", "source": "Product requirement",
         "assumptions": [], "acceptance": ["Rejected email preserves draft"]}), encoding="utf-8")
    (tmp_path / "observations.json").write_text(json.dumps(
        {"observations": [{"step": "Open the page", "visible_result": "The form renders"}]}), encoding="utf-8")
    execute(tmp_path, SESSION, ["mode", "once", "--scope", "contact"])
    run = execute(tmp_path, SESSION, ["checkpoint", "--id", "batch", "--stage", "plan",
                                      "--affected", "contact", "--task", str(tmp_path / "task.json")])
    packets.prepare(tmp_path, SESSION, run["run_id"], "observations.json")
    packets.claim(tmp_path, SESSION, run["run_id"])
    log, send = submit(tmp_path, run["run_id"], monkeypatch)
    send()
    assert len(sent(log)) == 1
    assert "image_preflight" not in stored_packet(tmp_path, run["run_id"])
