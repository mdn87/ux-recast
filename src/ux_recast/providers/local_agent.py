"""Local-agent provider: the agent running the cycle is the reviewer.

``prepare`` builds the same packet the Lugos Autowork provider builds (so the
reviewer sees the rubric, the task and the evidence in the same shape), claims
it, and writes ``findings.template.json`` next to it. The agent fills the
template, then ``record`` validates the findings and records them through the
ordinary packet lifecycle as a normalized result whose ``answer`` is the
findings JSON. No model provider and no network are involved.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from ux_recast.contracts import validate
from ux_recast.providers import lugos_autowork as packets

PROVIDER = "local-agent"


def prepare(project, session, run_id, evidence_path, *, config=None):
    packet = packets.prepare(project, session, run_id, evidence_path)
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
    packets.write_json(folder / "provider.json", {"provider": PROVIDER, "prepared_at": packets.now()})
    return {"packet": packet, "request_chars": len(request["task"]),
            "findings_template": str(folder / "findings.template.json")}


def record(project, session, run_id, findings_path):
    findings = json.loads(Path(findings_path).read_text(encoding="utf-8"))
    validate("findings", findings)
    folder = packets.folder_for(project, session, run_id)
    packet = packets.load_packet(folder)
    if findings["task_sha256"] != packet["task_sha256"]:
        raise ValueError("findings task_sha256 does not match the claimed packet")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    result = {"status": "completed", "run_id": f"local-{stamp}", "selected_route": PROVIDER,
              "model": findings.get("reviewer", "local agent"), "artifact_dir": str(folder),
              "changed_paths": [], "worktree": None,
              "answer": json.dumps(findings, ensure_ascii=False), "task_sha256": packet["task_sha256"]}
    result_path = folder / "local-result.json"
    packets.write_json(result_path, result)
    packets.write_json(folder / "findings.json", findings)
    receipt = packets.record(project, session, run_id, result_path)
    return {**receipt, "findings_count": len(findings["findings"])}
