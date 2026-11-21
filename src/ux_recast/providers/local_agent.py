"""Local-agent provider: the agent running the cycle is the reviewer.

``prepare`` builds the same packet the Lugos Autowork provider builds (so the
reviewer sees the rubric, the task and the evidence in the same shape), claims
it, and writes ``findings.template.json`` next to it. The agent fills the
template, then ``record`` validates the findings and records them through the
ordinary packet lifecycle as a normalized result whose ``answer`` is the
findings JSON. No model provider and no network are involved.

``record`` also applies the run's finding cap (``cycle.budget``): the recorded
``findings.json`` is in severity-then-input order with each finding marked
``actionable`` or ``deferred``, while ``local-result.json`` keeps the findings
exactly as the reviewer delivered them. A recorded local review counts as the
run's one review dispatch. Local records take turns on ``findings.lock``, and a
repeat record is refused before it writes anything, so both files always belong
to the one record the packet accepted.

Who fills the template is the caller's choice. For a fresh evaluation (the
``walkthrough`` mode especially) hand a separate agent context exactly the text
``lugos_autowork.prompt`` returns plus the listed visual inputs, nothing else,
and record what it returns. The ``reviewer`` field of the findings names it.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from ux_recast.contracts import validate
from ux_recast.cycle import budget
from ux_recast.providers import lugos_autowork as packets

PROVIDER = "local-agent"


def prepare(project, session, run_id, evidence_path, *, config=None, mode="review", detect_target=None):
    packet = packets.prepare(project, session, run_id, evidence_path, mode=mode, detect_target=detect_target)
    request = packets.claim(project, session, run_id, config=config)
    folder = packets.folder_for(project, session, run_id)
    template = {
        "schema": "ux-recast/findings@1",
        "provider": PROVIDER,
        "task_sha256": packet["task_sha256"],
        "reviewer": "<who reviewed: agent name and model>",
        "findings": [{
            "id": "F1",
            "category": "observed failure | heuristic concern | unresolved question",
            "task_step": "<which step of the task>",
            "observed": "<what the evidence shows>",
            "evidence": "<observation step or screenshot filename>",
            "principle": "<named principle from the rubric>",
            "likely_consequence": "<inference, labelled as such>",
            "severity": "Critical | High | Medium | Low",
            "confidence": "high | medium | low",
            "confidence_reason": "<why>",
            "proposed_correction": "<concrete change>",
            "verification": "<how to check it against the original outcome>",
            "element": "<selector or data-* reference, optional>",
            "kind": "design | implementation",
        }],
        "remaining_uncertainty": "<what the reviewer could not assess>",
    }
    packets.write_json(folder / "findings.template.json", template)
    packets.write_json(folder / "provider.json", {"provider": PROVIDER, "mode": mode, "prepared_at": packets.now()})
    return {"packet": packet, "request_chars": len(request["task"]), "review_mode": mode,
            "findings_template": str(folder / "findings.template.json"),
            "hand_off": "For a fresh-context evaluator: give it only the output of 'packet prompt' "
                        "and the visual_inputs files, then record its findings with 'findings'."}


def record(project, session, run_id, findings_path):
    findings = json.loads(Path(findings_path).read_text(encoding="utf-8"))
    validate("findings", findings)
    folder = packets.folder_for(project, session, run_id)
    # Local records take turns, and a repeat is refused before it writes anything, so the
    # files below always belong to the one record the packet accepted.
    with packets.locked(folder / "findings.lock"):
        packet = packets.load_packet(folder)
        packets.require_unrecorded(packet)
        if findings["task_sha256"] != packet["task_sha256"]:
            raise ValueError("findings task_sha256 does not match the claimed packet")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        result = {"status": "completed", "run_id": f"local-{stamp}", "selected_route": PROVIDER,
                  "model": findings.get("reviewer", "local agent"), "artifact_dir": str(folder),
                  "changed_paths": [], "worktree": None,
                  "answer": json.dumps(findings, ensure_ascii=False), "task_sha256": packet["task_sha256"]}
        result_path = folder / "local-result.json"
        packets.write_json(result_path, result)
        capped = budget.apply_finding_cap(findings["findings"],
                                          packet["activation"]["budget"]["max_actionable_findings"])
        packets.write_json(folder / "findings.json", {**findings, "findings": capped})
        receipt = packets.record(project, session, run_id, result_path)
        # The hand-off to a local reviewer is not observable; its recorded result is.
        with packets.locked(folder / "dispatch.lock"):
            packet = packets.load_packet(folder)
            dispatches = budget.count_review_dispatch(packet)
            packets.write_json(folder / "packet.json", packet)
    return {**receipt, **budget.finding_counts(capped), "review_dispatches": dispatches}
