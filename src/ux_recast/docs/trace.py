"""Mechanical traceability check for a sheet, and the seeded mutations that prove it bites (S6.7; T-18).

``trace`` re-checks every value that can be checked without judgement:

- ``token``, ``css-literal`` and ``accepted`` values are re-read: the recorded file at the recorded
  revision (``git show``) must hold the literal, with this value in its ``{}`` slot, on the
  recorded line;
- ``rendered`` values are re-measured at the recorded engine, viewport and device pixel ratio and
  must land within the entry's tolerance; a re-measurement under different conditions is a delta,
  not a pass;
- formulas are recomputed.

What remains (``proposed`` values and anything ``[TBD]``) is listed as the remainder for a
reviewer from a different model family who has not seen the author's notes. A delta can be
explained by name with a reason; acceptance needs zero unexplained deltas.

``mutations`` seeds wrong values, lines and literals into a copy of the table; ``sensitivity``
runs the trace on each and reports which were caught. A trace that misses a seeded mutation is not
evidence of anything.
"""
import copy
import math
import random
import subprocess

from ux_recast.contracts import ContractError
from ux_recast.docs import variables

READ_SOURCES = {"token", "css-literal", "accepted"}


class SourceReader:
    """Reads ``file`` at ``revision`` from a git repository, with a cache."""

    def __init__(self, repo):
        self.repo, self.cache = repo, {}

    def line(self, revision, path, number):
        key = (revision, path)
        if key not in self.cache:
            done = subprocess.run(["git", "-C", str(self.repo), "show", f"{revision}:{path}"], capture_output=True)
            self.cache[key] = done.stdout.decode("utf-8").splitlines() if done.returncode == 0 else None
        lines = self.cache[key]
        if lines is None:
            return None
        return lines[number - 1] if 1 <= number <= len(lines) else None


def _delta(entry, kind, detail):
    return {"code": entry["code"], "name": entry["name"], "kind": kind, "detail": detail}


def trace(entries, *, reader, measurer=None, explanations=None):
    """Check ``entries``; ``measurer(rendered_entries) -> {code: (value, conditions)}`` re-measures."""
    explanations = explanations or {}
    variables.validate_table(entries)
    codes = {entry["code"]: entry for entry in entries}
    checked, deltas, remainder, unmeasured = [], [], [], []
    rendered = [e for e in entries if e["source"] == "rendered" and e["value"] != variables.TBD]
    measured = measurer(rendered) if (measurer and rendered) else {}
    for entry in entries:
        if entry["value"] == variables.TBD:
            remainder.append({"code": entry["code"], "reason": "unresolved; nothing to check"})
            continue
        if "formula" in entry:
            try:
                result = variables.evaluate(entry["formula"], codes)
            except ContractError as error:
                deltas.append(_delta(entry, "formula", str(error)))
            else:
                if not math.isclose(result, entry["value"], abs_tol=max(1e-6, entry.get("tolerance", 0) or 0)):
                    deltas.append(_delta(entry, "formula", f"{entry['formula']} = {variables.format_number(result)}, recorded {entry['value']}"))
        source = entry["source"]
        if source in READ_SOURCES:
            text = reader.line(entry["revision"], entry["file"], entry["line"])
            if text is None:
                deltas.append(_delta(entry, "source", f"{entry['file']}:{entry['line']} not readable at {entry['revision']}"))
            elif not variables.literal_holds(entry, text):
                deltas.append(_delta(entry, "source", f"{entry['file']}:{entry['line']} at {entry['revision'][:8]} does not hold "
                                                      f"{entry['literal']!r} with {variables.display(entry)}"))
            checked.append(entry["code"])
        elif source == "rendered":
            if entry["code"] not in measured:
                unmeasured.append(entry["code"])
                continue
            value, conditions = measured[entry["code"]]
            expected = (entry["engine"], entry["viewport"], entry["device_pixel_ratio"])
            observed = (conditions["engine"], conditions["viewport"], conditions["device_pixel_ratio"])
            if observed != expected:
                deltas.append(_delta(entry, "conditions", f"re-measured under {observed}, recorded under {expected}"))
            elif not isinstance(value, (int, float)) or abs(value - entry["value"]) > entry["tolerance"]:
                deltas.append(_delta(entry, "rendered", f"{entry['part']} {entry['property']} measured {value}, "
                                                        f"recorded {entry['value']} ±{entry['tolerance']}"))
            checked.append(entry["code"])
        else:
            remainder.append({"code": entry["code"], "reason": f"proposed: {entry['proposal']}"})
    for item in deltas:
        if item["code"] in explanations:
            item["explained"] = explanations[item["code"]]
    unexplained = [item for item in deltas if "explained" not in item]
    return {"checked": len(set(checked)), "deltas": deltas, "unexplained": len(unexplained), "remainder": remainder,
            "unmeasured": unmeasured, "passed": not unexplained and not unmeasured}


def mutations(entries, count, *, seed=0):
    """Up to ``count`` copies of ``entries``, each with one seeded error a mechanical trace must catch."""
    rng = random.Random(seed)
    candidates = []
    for index, entry in enumerate(entries):
        if entry["value"] == variables.TBD:
            continue
        if entry["source"] in READ_SOURCES:
            candidates += [(index, "value"), (index, "line"), (index, "literal")]
        if entry["source"] == "rendered":
            candidates.append((index, "value"))
        if "formula" in entry:
            candidates.append((index, "formula"))
    rng.shuffle(candidates)
    seeded = []
    for index, kind in candidates[:count]:
        mutated = copy.deepcopy(entries)
        entry = mutated[index]
        if kind == "value":
            entry["value"] = _shifted(entry, rng)
            entry.pop("formula", None)
        elif kind == "line":
            entry["line"] += rng.choice((-1, 1)) if entry["line"] > 1 else 1
        elif kind == "literal":
            entry["literal"] = entry["literal"].replace("{}", "{} ", 1) if not entry["literal"].endswith("{}") else "x" + entry["literal"]
        elif kind == "formula":
            # The formula stays; its recorded result is wrong.
            entry["value"] = _shifted(entry, rng)
        seeded.append({"code": entry["code"], "kind": kind, "entries": mutated})
    return seeded


def _shifted(entry, rng):
    value, unit = entry["value"], entry["unit"]
    if unit == "color":
        digits = "0123456789abcdef"
        text = value.lower()
        position = rng.randrange(1, len(text))
        return text[:position] + digits[(digits.index(text[position]) + 7) % 16] + text[position + 1:]
    if unit == "keyword":
        return value + "-x"
    step = max(2, (entry.get("tolerance") or 0) * 4 + 1)
    shifted = value + step if rng.random() < 0.5 or value - step < 0 else value - step
    return int(shifted) if isinstance(value, int) else round(shifted, 3)


def sensitivity(entries, count, *, reader, measurer=None, seed=0):
    """Run the trace on ``count`` seeded mutations; every one must be caught."""
    results = []
    for mutation in mutations(entries, count, seed=seed):
        try:
            report = trace(mutation["entries"], reader=reader, measurer=measurer)
            caught = any(d["code"] == mutation["code"] for d in report["deltas"])
        except ContractError as error:
            # The table validator refusing the mutated table also counts: the error cannot be published.
            caught, report = True, {"refused": str(error)}
        results.append({"code": mutation["code"], "kind": mutation["kind"], "caught": caught})
    return {"seeded": len(results), "caught": sum(r["caught"] for r in results),
            "missed": [r for r in results if not r["caught"]], "results": results}


def page_measurer(url, parts, *, ready=None, revision="unrecorded"):
    """A measurer that re-measures rendered entries on ``url`` under each entry's recorded conditions."""
    from ux_recast.evidence import measure

    def run(entries):
        groups = {}
        for entry in entries:
            width, height = (int(n) for n in entry["viewport"].split("x"))
            key = (entry["engine"].split()[0], (width, height), entry["device_pixel_ratio"])
            groups.setdefault(key, []).append(entry)
        results = {}
        for (engine, viewport, ratio), group in groups.items():
            missing = sorted({e["part"] for e in group} - set(parts))
            if missing:
                raise ContractError("measurement.parts", f"no selector for parts {missing}")
            properties = [(e["part"], e["property"]) for e in group]
            done = measure.measure(url, parts, properties, revision=revision, viewport=viewport,
                                   device_pixel_ratio=ratio, engine=engine, ready=ready)
            for e in group:
                results[e["code"]] = (done["values"].get(f'{e["part"]}.{e["property"]}'), done["conditions"])
        return results
    return run
