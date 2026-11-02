"""Contracts: the shapes ux-recast reads and writes.

The JSON Schema documents under ``ux_recast.schemas`` are the published form.
This module is a small standard-library validator that enforces the parts of
those schemas the code relies on (required keys, types, enumerations) and names
the offending field. The Lugos artifacts (``.ux-review`` state, ``packet.json``,
``receipt.json``) keep ``schema_version: 1`` exactly as the Lugos scripts write
them; nothing here changes the inner Autowork request.
"""
from importlib import resources
import json

KINDS = ("task", "state", "packet", "receipt", "findings")

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


_VALIDATORS = {"task": validate_task, "state": validate_state, "packet": validate_packet,
               "receipt": validate_receipt, "findings": validate_findings}


def validate(kind, data):
    """Validate ``data`` as contract ``kind``; raises ContractError naming the field."""
    if kind not in _VALIDATORS:
        raise ContractError("kind", f"unknown contract {kind!r}")
    return _VALIDATORS[kind](data)
