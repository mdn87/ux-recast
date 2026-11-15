"""Budget limits a cycle enforces on record (plan Phase 4, slice S4.1).

``cycle.control`` already holds a run to one review pass, one repair batch and
one verification pass. Two limits were only a prompt instruction or left
implicit, and are enforced and recorded here:

- the cap on actionable findings (``max_actionable_findings`` in the run's
  budget), applied when structured findings are recorded;
- how many review dispatches the run consumed, kept on the packet's outer
  envelope as ``review_dispatches``. The inner request is never touched.
"""
SEVERITY_ORDER = ("Critical", "High", "Medium", "Low")
ACTIONABLE = "actionable"
DEFERRED = "deferred"
DISPATCH_KEY = "review_dispatches"


def apply_finding_cap(findings, cap):
    """Rank findings by severity, then input order; the first ``cap`` are actionable, the rest deferred.

    Returns new finding objects in rank order, each carrying a ``status``. A
    finding the reviewer already marked ``deferred`` stays deferred and takes no
    actionable slot; no other reviewer-supplied status is trusted. The input is
    left unmodified, and the same input always gives the same output.
    """
    rank = {severity: position for position, severity in enumerate(SEVERITY_ORDER)}
    ordered = sorted(enumerate(findings), key=lambda pair: (rank[pair[1]["severity"]], pair[0]))
    recorded, slots = [], cap
    for _, item in ordered:
        if item.get("status") != DEFERRED and slots > 0:
            slots -= 1
            recorded.append({**item, "status": ACTIONABLE})
        else:
            recorded.append({**item, "status": DEFERRED})
    return recorded


def finding_counts(recorded):
    actionable = sum(1 for item in recorded if item["status"] == ACTIONABLE)
    return {"findings_count": len(recorded), "actionable_count": actionable,
            "deferred_count": len(recorded) - actionable}


def count_review_dispatch(packet):
    """Note on the packet that its review request reached a reviewer once more; returns the new count."""
    packet[DISPATCH_KEY] = packet.get(DISPATCH_KEY, 0) + 1
    return packet[DISPATCH_KEY]
