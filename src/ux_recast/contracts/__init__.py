"""Contracts: the shapes ux-recast reads and writes.

The JSON Schema documents under ``ux_recast.schemas`` are the published form.
This module is a small standard-library validator that enforces the parts of
those schemas the code relies on (required keys, types, enumerations) and names
the offending field. The Lugos artifacts (``.ux-review`` state, ``packet.json``,
``receipt.json``) keep ``schema_version: 1`` exactly as the Lugos scripts write
them; nothing here changes the inner Autowork request. A walkthrough-mode
packet adds ``review_mode`` and ``rubric_version`` to the outer packet only.
``comparison`` is the before-and-after record that closes a redesign (D-21);
version 2 adds the Improvement Loop fields (kind, baseline and candidate, frozen
criteria, cited evidence, limitations, effort, and the six-value decision).
``lesson`` is the front matter of a project or shared lesson. ``documentation`` is the request
for a style guide, component sheets or a motion presentation (``contracts.documentation``).
"""
from importlib import resources
import json

KINDS = ("task", "state", "packet", "receipt", "findings", "comparison", "lesson", "documentation")

TASK_STRINGS = ("flow", "goal", "starting_conditions", "expected_outcome", "device_input", "source")
STATE_MODES = {"off", "once", "session"}
RUN_STATUSES = {"active", "cancelled", "verified", "remaining", "unavailable"}
RUN_PHASES = {"review", "repair", "verify"}
DISPATCH_STATUSES = {"prepared", "claimed", "submitted", "recorded"}
SUBMIT_OUTCOMES = {"delivered", "rejected", "unknown"}
FINDING_CATEGORIES = {"observed failure", "heuristic concern", "unresolved question"}
SEVERITIES = {"Critical", "High", "Medium", "Low"}
CONFIDENCES = {"high", "medium", "low"}
FINDING_KINDS = {"design", "implementation"}
REVIEW_MODES = {"review", "walkthrough"}
COMPARISON_SCHEMA = "ux-recast/comparison@1"
IMPROVEMENT_KINDS = {"observed", "judgement"}
DISPOSITIONS = {"addressed", "deferred", "rejected"}
COMPARISON_DECISIONS = {"pending", "accepted", "revise", "rejected"}
COMPARISON_SCHEMA_V2 = "ux-recast/comparison@2"
COMPARISON_KINDS = {"product", "method"}
COMPARISON_DECISIONS_V2 = {"accept", "revise", "keep_local", "reject", "insufficient_evidence", "keep_baseline"}
EFFORT_FIELDS = ("review_passes", "retries", "false_findings", "user_interventions", "wall_time_seconds")
LESSON_STATUSES = ("candidate", "project", "shared", "rejected", "superseded")


class ContractError(ValueError):
    def __init__(self, field, message):
        super().__init__(f"{field}: {message}")
        self.field = field


def schema(kind):
    """The JSON Schema document for ``kind``, as shipped in the package."""
    if kind not in KINDS:
        raise ContractError("kind", f"unknown contract {kind!r}")
    return json.loads(resources.files("ux_recast.schemas").joinpath(f"{kind}.schema.json").read_text("utf-8"))


def _require(obj, field, types, where):
    if field not in obj:
        raise ContractError(f"{where}.{field}", "missing")
    if not isinstance(obj[field], types):
        raise ContractError(f"{where}.{field}", f"expected {types}")
    return obj[field]


def _enum(value, allowed, where):
    if value not in allowed:
        raise ContractError(where, f"{value!r} not in {sorted(allowed)}")


def validate_task(task, where="task"):
    if not isinstance(task, dict):
        raise ContractError(where, "expected object")
    for field in TASK_STRINGS:
        if not _require(task, field, str, where).strip():
            raise ContractError(f"{where}.{field}", "empty")
    _require(task, "assumptions", list, where)
    acceptance = _require(task, "acceptance", list, where)
    if not acceptance or not all(isinstance(a, str) and a.strip() for a in acceptance):
        raise ContractError(f"{where}.acceptance", "must be a non-empty list of non-empty strings")
    return task


def validate_state(state, where="state"):
    if not isinstance(state, dict):
        raise ContractError(where, "expected object")
    if _require(state, "version", int, where) != 1:
        raise ContractError(f"{where}.version", "must be 1")
    _enum(_require(state, "mode", str, where), STATE_MODES, f"{where}.mode")
    _require(state, "scope", list, where)
    _require(state, "shared", dict, where)
    for index, run in enumerate(_require(state, "runs", list, where)):
        w = f"{where}.runs[{index}]"
        if not isinstance(run, dict):
            raise ContractError(w, "expected object")
        _require(run, "run_id", str, w)
        checkpoint = _require(run, "checkpoint", list, w)
        if not checkpoint or not all(isinstance(part, str) for part in checkpoint):
            raise ContractError(f"{w}.checkpoint", "expected a non-empty list of strings")
        validate_task(run.get("task"), f"{w}.task")
        _enum(_require(run, "status", str, w), RUN_STATUSES, f"{w}.status")
        _enum(_require(run, "phase", str, w), RUN_PHASES, f"{w}.phase")
        budget = _require(run, "budget", dict, w)
        for key in ("review_passes", "repair_batches", "verification_passes", "max_actionable_findings"):
            _require(budget, key, int, f"{w}.budget")
        if "manifest" in run:
            manifest = _require(run, "manifest", dict, w)
            for key in ("flow", "stage", "task_sha256", "task_path"):
                _require(manifest, key, str, f"{w}.manifest")
            _require(manifest, "inputs", dict, f"{w}.manifest")
            _require(manifest, "config", dict, f"{w}.manifest")
    return state


def validate_packet(packet, where="packet"):
    if not isinstance(packet, dict):
        raise ContractError(where, "expected object")
    if _require(packet, "schema_version", int, where) != 1:
        raise ContractError(f"{where}.schema_version", "must be 1")
    activation = _require(packet, "activation", dict, where)
    _enum(_require(activation, "mode", str, f"{where}.activation"), STATE_MODES, f"{where}.activation.mode")
    _require(activation, "scope", list, f"{where}.activation")
    _require(activation, "checkpoint", list, f"{where}.activation")
    _require(activation, "controller_run_id", str, f"{where}.activation")
    _require(activation, "budget", dict, f"{where}.activation")
    request = _require(packet, "request", dict, where)
    w = f"{where}.request"
    if _require(request, "action", str, w) != "delegate":
        raise ContractError(f"{w}.action", "must be delegate")
    if _require(request, "role", str, w) != "explorer":
        raise ContractError(f"{w}.role", "must be explorer")
    _require(request, "workspace", str, w)
    _require(request, "task", str, w)
    caps = _require(request, "required_capabilities", list, w)
    modalities = _require(request, "input_modalities", list, w)
    _require(request, "timeout_seconds", int, w)
    has_images = "visual_inputs" in request
    if has_images != ("image_input" in caps) or has_images != ("image" in modalities):
        raise ContractError(w, "visual_inputs, image_input and the image modality must appear together")
    for key in ("allowed_paths", "verification"):
        if key in request:
            raise ContractError(f"{w}.{key}", "forbidden in a read-only review request")
    digest = _require(packet, "task_sha256", str, where)
    if len(digest) != 64:
        raise ContractError(f"{where}.task_sha256", "expected sha256 hex")
    _require(packet, "sources", dict, where)
    _require(packet, "rubric_sha256", str, where)
    _enum(_require(packet, "dispatch_status", str, where), DISPATCH_STATUSES, f"{where}.dispatch_status")
    if "submit_outcome" in packet:
        _enum(packet["submit_outcome"], SUBMIT_OUTCOMES, f"{where}.submit_outcome")
    if "review_mode" in packet:
        _enum(packet["review_mode"], REVIEW_MODES, f"{where}.review_mode")
        _require(packet, "rubric_version", str, where)
    return packet


def validate_receipt(receipt, where="receipt"):
    if not isinstance(receipt, dict):
        raise ContractError(where, "expected object")
    _require(receipt, "accepted", bool, where)
    _require(receipt, "status", str, where)
    _require(receipt, "task_sha256", str, where)
    _require(receipt, "meaning", str, where)
    if receipt["accepted"] and receipt["status"] != "completed":
        raise ContractError(f"{where}.accepted", "accepted requires status completed")
    if "findings" in receipt and receipt["findings"] != "stale":
        raise ContractError(f"{where}.findings", "only 'stale' is recorded on a receipt")
    return receipt


def validate_findings(findings, where="findings"):
    if not isinstance(findings, dict):
        raise ContractError(where, "expected object")
    if _require(findings, "schema", str, where) != "ux-recast/findings@1":
        raise ContractError(f"{where}.schema", "must be ux-recast/findings@1")
    _require(findings, "provider", str, where)
    _require(findings, "task_sha256", str, where)
    _require(findings, "reviewer", str, where)
    items = _require(findings, "findings", list, where)
    seen = set()
    for index, item in enumerate(items):
        w = f"{where}.findings[{index}]"
        if not isinstance(item, dict):
            raise ContractError(w, "expected object")
        fid = _require(item, "id", str, w)
        if fid in seen:
            raise ContractError(f"{w}.id", "duplicate")
        seen.add(fid)
        for field in ("task_step", "observed", "evidence", "principle", "likely_consequence",
                      "confidence_reason", "proposed_correction", "verification"):
            if not _require(item, field, str, w).strip():
                raise ContractError(f"{w}.{field}", "empty")
        _enum(_require(item, "category", str, w), FINDING_CATEGORIES, f"{w}.category")
        _enum(_require(item, "severity", str, w), SEVERITIES, f"{w}.severity")
        _enum(_require(item, "confidence", str, w), CONFIDENCES, f"{w}.confidence")
        if "kind" in item:
            _enum(item["kind"], FINDING_KINDS, f"{w}.kind")
        if "score" in item and not isinstance(item["score"], (int, float)):
            raise ContractError(f"{w}.score", "a score is a numeric signal, never acceptance")
    return findings


def _list_of_objects(obj, field, required, where, *, allow_empty=True):
    items = _require(obj, field, list, where)
    if not items and not allow_empty:
        raise ContractError(f"{where}.{field}", "must not be empty")
    for index, item in enumerate(items):
        w = f"{where}.{field}[{index}]"
        if not isinstance(item, dict):
            raise ContractError(w, "expected object")
        for key in required:
            if not _require(item, key, str, w).strip():
                raise ContractError(f"{w}.{key}", "empty")
    return items


def validate_comparison(comparison, where="comparison"):
    """The before-and-after record that closes a redesign: same content, same conditions, claims separated by kind."""
    if not isinstance(comparison, dict):
        raise ContractError(where, "expected object")
    version = _require(comparison, "schema", str, where)
    if version not in (COMPARISON_SCHEMA, COMPARISON_SCHEMA_V2):
        raise ContractError(f"{where}.schema", f"must be {COMPARISON_SCHEMA} or {COMPARISON_SCHEMA_V2}")
    v2 = version == COMPARISON_SCHEMA_V2
    if not _require(comparison, "task", str, where).strip():
        raise ContractError(f"{where}.task", "empty")
    conditions = _require(comparison, "conditions", dict, where)
    for key in ("content", "viewports", "revision_before", "revision_after"):
        if key not in conditions:
            raise ContractError(f"{where}.conditions.{key}", "missing")
    if not isinstance(conditions["viewports"], list) or not conditions["viewports"]:
        raise ContractError(f"{where}.conditions.viewports", "expected a non-empty list")
    for side in ("before", "after"):
        view = _require(comparison, side, dict, where)
        if not _require(view, "flow", str, f"{where}.{side}").strip():
            raise ContractError(f"{where}.{side}.flow", "empty")
        _require(view, "evidence", list, f"{where}.{side}")
    _list_of_objects(comparison, "structural_changes", ("change", "reason"), where)
    # Keeping the baseline is a valid result (C-58), so a v2 record that does not adopt the candidate may claim nothing.
    claims_optional = v2 and comparison.get("decision") in {"pending", "keep_baseline", "reject", "insufficient_evidence"}
    for index, item in enumerate(_list_of_objects(comparison, "improvements",
                                                  ("claim", "evidence_before", "evidence_after"), where,
                                                  allow_empty=claims_optional)):
        _enum(_require(item, "kind", str, f"{where}.improvements[{index}]"), IMPROVEMENT_KINDS,
              f"{where}.improvements[{index}].kind")
    for index, item in enumerate(_list_of_objects(comparison, "findings_disposition", ("id",), where)):
        _enum(_require(item, "disposition", str, f"{where}.findings_disposition[{index}]"), DISPOSITIONS,
              f"{where}.findings_disposition[{index}].disposition")
    verification = _require(comparison, "verification", dict, where)
    _require(verification, "checks", list, f"{where}.verification")
    _require(verification, "failure_paths", list, f"{where}.verification")
    _require(comparison, "assumptions", list, where)
    if "score" in comparison:
        raise ContractError(f"{where}.score", "a comparison records evidence and a decision, never a score")
    if v2:
        _validate_comparison_v2(comparison, where)
    _enum(_require(comparison, "decision", str, where),
          (COMPARISON_DECISIONS_V2 | {"pending"}) if v2 else COMPARISON_DECISIONS, f"{where}.decision")
    if comparison["decision"] != "pending":
        for key in ("decided_by", "decided_at"):
            if not _require(comparison, key, str, where).strip():
                raise ContractError(f"{where}.{key}", "a decision names who made it and when")
    return comparison


def _validate_comparison_v2(comparison, where):
    _enum(_require(comparison, "kind", str, where), COMPARISON_KINDS, f"{where}.kind")
    for key in ("baseline", "candidate"):
        if not _require(comparison, key, str, where).strip():
            raise ContractError(f"{where}.{key}", "empty")
    criteria = _require(comparison, "criteria", dict, where)
    if not _require(criteria, "frozen_at", str, f"{where}.criteria").strip():
        raise ContractError(f"{where}.criteria.frozen_at", "criteria are frozen before the comparison starts; say when")
    items = _require(criteria, "items", list, f"{where}.criteria")
    if not items or not all(isinstance(i, str) and i.strip() for i in items):
        raise ContractError(f"{where}.criteria.items", "expected a non-empty list of criteria")
    evidence = _require(comparison, "evidence", list, where)
    if not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
        raise ContractError(f"{where}.evidence", "cite at least one piece of evidence")
    limitations = _require(comparison, "limitations", list, where)
    if not all(isinstance(item, str) and item.strip() for item in limitations):
        raise ContractError(f"{where}.limitations", "expected a list of statements")
    effort = _require(comparison, "effort", dict, where)
    for key in EFFORT_FIELDS:
        value = _require(effort, key, (int, float), f"{where}.effort")
        if isinstance(value, bool) or value < 0 or (key != "wall_time_seconds" and not isinstance(value, int)):
            raise ContractError(f"{where}.effort.{key}", "expected a non-negative count" if key != "wall_time_seconds"
                                else "expected non-negative seconds")


def validate_lesson(lesson, where="lesson"):
    """A lesson's front matter: its tier status, identity, links and support; rejected and superseded need a reason."""
    if not isinstance(lesson, dict):
        raise ContractError(where, "expected object")
    for key in ("id", "title", "identity", "created_at"):
        _require(lesson, key, str, where)
    status = _require(lesson, "status", str, where)
    _enum(status, set(LESSON_STATUSES), f"{where}.status")
    if status in {"rejected", "superseded"} and not str(lesson.get("reason", "")).strip():
        raise ContractError(f"{where}.reason", f"a {status} lesson records why")
    links = lesson.get("links", {})
    if not isinstance(links, dict) or not all(isinstance(v, list) and all(isinstance(s, str) for s in v) for v in links.values()):
        raise ContractError(f"{where}.links", "expected {name: [path, ...]}")
    _list_of_objects(lesson, "supported_by", ("identity", "outcome"), where)
    return lesson


from ux_recast.contracts.documentation import validate_documentation  # noqa: E402

_VALIDATORS = {"task": validate_task, "state": validate_state, "packet": validate_packet,
               "receipt": validate_receipt, "findings": validate_findings, "comparison": validate_comparison,
               "lesson": validate_lesson, "documentation": validate_documentation}


def validate(kind, data):
    """Validate ``data`` as contract ``kind``; raises ContractError naming the field."""
    if kind not in _VALIDATORS:
        raise ContractError("kind", f"unknown contract {kind!r}")
    return _VALIDATORS[kind](data)
