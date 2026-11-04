"""Comparison records: ``.ux-recast/comparisons.jsonl``, append-only beside the decisions.

A comparison (``ux-recast/comparison@2``) weighs a candidate against a baseline,
either two versions of an interface (``product``) or two ways of working on a
held-out case (``method``), against criteria frozen before it started. It cites
its evidence, states its limitations, records the effort it cost and ends in one
of six decisions; keeping the baseline is a valid result (C-55, C-58, C-60). A
Decision or Outcome may cite a comparison by id; the comparison never replaces
them. Appends share the decision log's lock-and-recover writer.
"""
from ux_recast.contracts import COMPARISON_SCHEMA_V2, ContractError, validate
from ux_recast.records import decisions

LOG = "comparisons"


def append(project, comparison):
    """Validate a v2 comparison and append it; return it with its assigned ``id`` and ``recorded_at``."""
    if not isinstance(comparison, dict) or comparison.get("schema") != COMPARISON_SCHEMA_V2:
        raise ValueError(f"schema: the comparison log takes {COMPARISON_SCHEMA_V2} records")
    for key in ("id", "recorded_at"):
        if key in comparison:
            raise ValueError(f"{key}: assigned by ux-recast")
    try:
        validate("comparison", comparison)
    except ContractError as error:
        raise ValueError(str(error)) from error
    return decisions._append(project, LOG, comparison)


def read(project):
    return decisions.read(project, LOG)


def effort_from_cycle(cycle_log, findings_disposition=()):
    """Fill the effort fields from a fixture-cycle log, and say what the log cannot show."""
    phases = cycle_log.get("phases", [])
    wall = sum(cycle_log.get(side, {}).get("seconds", 0) for side in ("before", "after", "oracle"))
    return {
        "review_passes": phases.count("record"),
        "retries": sum(max(0, phases.count(phase) - 1) for phase in set(phases)),
        "false_findings": sum(1 for item in findings_disposition if item.get("disposition") == "rejected"),
        "user_interventions": 0,
        "wall_time_seconds": round(wall, 1),
        "basis": ("From the cycle log: review passes are recorded findings sets, retries are repeated phases, "
                  "false findings are findings this comparison marks rejected, and wall time is the measured "
                  "before, after and oracle test runs only. The log records no user step, so interventions are 0; "
                  "reviewing, authoring and reruns outside the logged run are not counted."),
    }
