"""S4.1: a run records how many review dispatches it consumed, on the packet's outer envelope.

The Autowork lane counts when ``submit`` has actually sent the request: a
delivered result, a rejected result and an unknown outcome each consumed the
run's one dispatch; a submit refused or failed before anything was sent
consumed none. The local lane is covered in ``test_local_agent``.
"""
import sys

import pytest

pytest.importorskip("mcp")

from tests.lugos_compat.test_submit import claimed, helper, invocations, packet_of, submit  # noqa: E402,F401


def test_a_delivered_submit_counts_one_dispatch(claimed):
    root, run_id, _, request, _ = claimed
    assert "review_dispatches" not in packet_of(root, run_id)
    code, output, _ = submit(root, run_id)
    assert code == 0, output
    packet = packet_of(root, run_id)
    assert packet["review_dispatches"] == 1
    assert packet["request"] == request, "the count lives on the outer envelope, never in the request"
    code, receipt = helper(root, run_id, "record", "--result", str(root / "out" / "result.json"))
    assert code == 0 and receipt["accepted"] is True
    assert packet_of(root, run_id)["review_dispatches"] == 1


def test_a_rejected_result_still_consumed_the_dispatch(claimed):
    root, run_id, _, _, _ = claimed
    code, output, _ = submit(root, run_id, mode="empty_answer")
    assert code == 2 and "not eligible" in output["error"]
    assert packet_of(root, run_id)["review_dispatches"] == 1
    code, output, log = submit(root, run_id, mode="empty_answer")
    assert code == 2 and "already submitted" in output["error"]
    assert packet_of(root, run_id)["review_dispatches"] == 1
    assert len(invocations(log)) == 1


def test_an_unknown_outcome_still_consumed_the_dispatch(claimed):
    root, run_id, _, _, _ = claimed
    code, output, _ = submit(root, run_id, mode="hang", timeout_seconds=2)
    assert code == 2 and "outcome unknown" in output["error"]
    assert packet_of(root, run_id)["review_dispatches"] == 1


def test_a_submit_refused_before_sending_consumes_nothing(claimed):
    root, run_id, _, _, evidence = claimed
    evidence.write_text(evidence.read_text(encoding="utf-8") + " ", encoding="utf-8")
    code, output, log = submit(root, run_id)
    assert code == 2 and "Evidence changed" in output["error"]
    assert invocations(log) == []
    assert "review_dispatches" not in packet_of(root, run_id)


def test_a_server_that_never_starts_consumes_nothing(claimed):
    root, run_id, _, _, _ = claimed
    missing = root / "no-such-server.py"
    code, output = helper(root, run_id, "submit", "--result", str(root / "out" / "result.json"),
                          "--server-command", sys.executable, "--server-arg", str(missing),
                          "--timeout-seconds", "5")
    assert code == 2 and "Nothing was dispatched" in output["error"], output
    packet = packet_of(root, run_id)
    assert packet["dispatch_status"] == "claimed"
    assert "review_dispatches" not in packet
