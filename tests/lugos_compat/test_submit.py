"""submit carries the claimed request to the Lugos MCP server byte for byte, once."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("mcp")

HERE = Path(__file__).resolve().parent
import ux_recast.providers.lugos_autowork as _packets  # noqa: E402
SCRIPTS = Path(_packets.__file__).parent
FIXTURE = HERE / "fixtures" / "mcp_fixture_server.py"
from ux_recast.cycle.control import execute  # noqa: E402

SPECIAL = "café — ‘curly’ \"straight\" back\\slash tab\t crlf\r\n lf\n cr\r 日本語 🙂 "


def write_inputs(root):
    task = {"flow": "contact", "goal": "Send a request", "starting_conditions": "Signed out",
            "expected_outcome": "Request received without losing draft", "device_input": "Keyboard",
            "source": "Product requirement", "assumptions": [], "acceptance": ["Rejected email preserves draft"]}
    task_path = root / "task.json"
    task_path.write_text(json.dumps(task), encoding="utf-8")
    evidence = root / "observations.json"
    evidence.write_text(json.dumps({"observations": [{"step": "Open the page", "visible_result": "The form renders"}],
                                    "screenshots": [], "plan": (SPECIAL * 400)[:20000]}, ensure_ascii=False),
                        encoding="utf-8")
    return task_path, evidence


def helper(root, run_id, *args, env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    proc = subprocess.run([sys.executable, str(SCRIPTS / "lugos_autowork.py"), "--project", str(root),
                           "--session", "session", "--run", run_id, *args],
                          capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)
    return proc.returncode, json.loads(proc.stdout) if proc.stdout.strip() else {"stderr": proc.stderr}


@pytest.fixture
def claimed(tmp_path):
    task_path, evidence = write_inputs(tmp_path)
    execute(tmp_path, "session", ["mode", "once", "--scope", "contact"])
    run = execute(tmp_path, "session", ["checkpoint", "--id", "batch", "--stage", "plan",
                  "--affected", "contact", "--task", str(task_path)])
    code, packet = helper(tmp_path, run["run_id"], "prepare", "--evidence", "observations.json")
    assert code == 0, packet
    code, request = helper(tmp_path, run["run_id"], "claim")
    assert code == 0, request
    return tmp_path, run["run_id"], packet, request, evidence


def submit(root, run_id, mode="ok", timeout_seconds=None, extra=()):
    log = root / "fixture.log"
    args = ["submit", "--result", str(root / "out" / "result.json"),
            "--server-command", sys.executable, "--server-arg", str(FIXTURE), *extra]
    if timeout_seconds:
        args += ["--timeout-seconds", str(timeout_seconds)]
    code, output = helper(root, run_id, *args, env_extra={"UX_FIXTURE_MODE": mode, "UX_FIXTURE_LOG": str(log)})
    return code, output, log


def invocations(log):
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []


def packet_of(root, run_id):
    folder = next((root / ".ux-review" / "packets").glob(f"*-{run_id}"))
    return json.loads((folder / "packet.json").read_text(encoding="utf-8"))


def test_submit_carries_the_claimed_request_unchanged_and_record_accepts(claimed):
    root, run_id, packet, request, _ = claimed
    assert len(request["task"]) >= 20000
    code, output, log = submit(root, run_id)
    assert code == 0, output
    received = invocations(log)
    assert len(received) == 1
    assert received[0]["name"] == "lugos.models"
    assert received[0]["arguments"] == request == packet["request"]
    assert hashlib.sha256(received[0]["arguments"]["task"].encode()).hexdigest() == packet["task_sha256"]
    result = json.loads((root / "out" / "result.json").read_text(encoding="utf-8"))
    assert result["task_sha256"] == packet["task_sha256"] == output["task_sha256"]
    assert output["selected_route"] == "fixture:route"
    state = packet_of(root, run_id)
    assert (state["dispatch_status"], state["submit_outcome"]) == ("submitted", "delivered")
    code, consumed = helper(root, run_id, "consume")
    assert code == 2 and "recorded" in consumed["error"]  # submit alone consumes nothing
    code, receipt = helper(root, run_id, "record", "--result", str(root / "out" / "result.json"))
    assert code == 0 and receipt["accepted"] is True and receipt["autowork_run_id"] == "fixture-run"
    code, consumed = helper(root, run_id, "consume")
    assert code == 0 and consumed["applicable"] is True


def test_tampered_evidence_is_refused_before_anything_is_sent(claimed):
    root, run_id, _, _, evidence = claimed
    evidence.write_text(evidence.read_text(encoding="utf-8") + " ", encoding="utf-8")
    code, output, log = submit(root, run_id)
    assert code == 2 and "Evidence changed" in output["error"]
    assert invocations(log) == []
    assert packet_of(root, run_id)["dispatch_status"] == "claimed"


def test_request_file_that_differs_is_refused(claimed):
    root, run_id, _, request, _ = claimed
    altered = root / "altered.json"
    altered.write_text(json.dumps({**request, "task": request["task"] + "x"}), encoding="utf-8")
    code, output, log = submit(root, run_id, extra=("--request-file", str(altered)))
    assert code == 2 and "differs" in output["error"]
    assert invocations(log) == []


def test_mode_off_after_claim_blocks_submit(claimed):
    root, run_id, _, _, _ = claimed
    execute(root, "session", ["mode", "off"])
    code, output, log = submit(root, run_id)
    assert code == 2 and "off" in output["error"]
    assert invocations(log) == []


@pytest.mark.parametrize("mode", ["wrong_digest", "missing_digest", "empty_answer", "changed_paths", "error"])
def test_a_result_record_would_refuse_is_never_published(claimed, mode):
    root, run_id, _, _, _ = claimed
    code, output, log = submit(root, run_id, mode=mode)
    assert code == 2 and "not eligible" in output["error"]
    assert not (root / "out" / "result.json").exists()
    rejected = json.loads((root / "out" / "result.rejected.json").read_text(encoding="utf-8"))
    assert rejected["problems"]
    state = packet_of(root, run_id)
    assert (state["dispatch_status"], state["submit_outcome"]) == ("submitted", "rejected")
    code, output, log = submit(root, run_id, mode=mode)
    assert code == 2 and "already submitted" in output["error"]
    assert len(invocations(log)) == 1


def test_timeout_leaves_the_outcome_unknown_and_never_redispatches(claimed):
    root, run_id, _, _, _ = claimed
    code, output, log = submit(root, run_id, mode="hang", timeout_seconds=2)
    assert code == 2 and "outcome unknown" in output["error"]
    assert len(invocations(log)) == 1
    state = packet_of(root, run_id)
    assert (state["dispatch_status"], state["submit_outcome"]) == ("submitted", "unknown")
    code, output, log = submit(root, run_id, mode="hang", timeout_seconds=2)
    assert code == 2 and "already submitted" in output["error"]
    assert len(invocations(log)) == 1
