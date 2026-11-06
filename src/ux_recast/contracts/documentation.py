"""The documentation request: which outputs to produce, on what basis, from which inputs (D-07, C-34 to C-39).

Three independent outputs: a style ``guide``, component ``sheets`` and a ``motion`` presentation.
A guide may come without sheets and a sheet without a guide. Motion animates a static sheet, so
it is refused unless this request also asks for sheets or names an existing one (C-47). The
``basis`` says whether the output documents the existing interface (``observed``), an accepted
redesign (``accepted``) or a proposal (``proposed``) (C-38). Inputs carry an authority: approved
guidance is authoritative and an inspirational ``reference`` never overrides it (C-39).
"""
import re

SCHEMA = "ux-recast/documentation-request@1"
BASES = {"observed", "accepted", "proposed"}
INPUT_ROLES = {"design", "source", "decision", "measurement", "fixture", "screenshot", "reference", "product"}
AUTHORITIES = {"approved", "observed", "reference"}
COMPONENT = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def _error(field, message):
    from ux_recast.contracts import ContractError
    return ContractError(field, message)


def validate_documentation(request, where="documentation"):
    from ux_recast.contracts import _require
    if not isinstance(request, dict):
        raise _error(where, "expected object")
    if _require(request, "schema", str, where) != SCHEMA:
        raise _error(f"{where}.schema", f"must be {SCHEMA}")
    if _require(request, "request_kind", str, where) != "documentation":
        raise _error(f"{where}.request_kind", "must be documentation; review mode is a separate request")
    for key in ("project", "subject"):
        if not _require(request, key, str, where).strip():
            raise _error(f"{where}.{key}", "empty")
    basis = _require(request, "basis", str, where)
    if basis not in BASES:
        raise _error(f"{where}.basis", f"{basis!r} not in {sorted(BASES)}")
    if basis != "observed" and not str(request.get("basis_reference", "")).strip():
        raise _error(f"{where}.basis_reference", f"a {basis} guide names the decision or proposal it rests on")
    outputs = _require(request, "outputs", dict, where)
    flags = {}
    for flag in ("guide", "sheets", "motion"):
        value = outputs.get(flag, False)
        if not isinstance(value, bool):
            raise _error(f"{where}.outputs.{flag}", "expected true or false")
        flags[flag] = value
    if not any(flags.values()):
        raise _error(f"{where}.outputs", "request at least one of guide, sheets or motion")
    components = request.get("components", [])
    if not isinstance(components, list) or not all(isinstance(c, str) and COMPONENT.match(c) for c in components):
        raise _error(f"{where}.components", "expected a list of lowercase hyphenated component names")
    if len(set(components)) != len(components):
        raise _error(f"{where}.components", "duplicate component")
    if flags["sheets"] and not components:
        raise _error(f"{where}.components", "sheets were requested; name at least one component")
    if not flags["sheets"] and components:
        raise _error(f"{where}.components", "components name sheets; set outputs.sheets or drop them")
    existing = request.get("existing_sheets", [])
    if not isinstance(existing, list) or not all(isinstance(p, str) and p.strip() for p in existing):
        raise _error(f"{where}.existing_sheets", "expected a list of paths")
    if flags["motion"] and not flags["sheets"] and not existing:
        raise _error(f"{where}.outputs.motion", "motion animates a static sheet; request sheets or name an existing one")
    inputs = _require(request, "inputs", list, where)
    if not inputs:
        raise _error(f"{where}.inputs", "name the inputs the output is drawn from")
    for index, item in enumerate(inputs):
        w = f"{where}.inputs[{index}]"
        if not isinstance(item, dict):
            raise _error(w, "expected object")
        if not _require(item, "path", str, w).strip():
            raise _error(f"{w}.path", "empty")
        role = _require(item, "role", str, w)
        if role not in INPUT_ROLES:
            raise _error(f"{w}.role", f"{role!r} not in {sorted(INPUT_ROLES)}")
        authority = item.get("authority", "reference" if role == "reference" else "approved")
        if authority not in AUTHORITIES:
            raise _error(f"{w}.authority", f"{authority!r} not in {sorted(AUTHORITIES)}")
        if role == "reference" and authority == "approved":
            raise _error(f"{w}.authority", "an inspirational reference is never approved guidance")
    if not _require(request, "out_dir", str, where).strip():
        raise _error(f"{where}.out_dir", "empty")
    return request
