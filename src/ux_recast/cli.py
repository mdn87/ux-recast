"""``ux-recast`` command line.

Verbs mirror the Lugos scripts so a shim can forward argv unchanged:

    ux-recast control  --project P --session S <status|mode|checkpoint|phase|finish> ...
    ux-recast packet   --project P --session S --run R <prepare|claim|prompt|submit|record|consume> ...
    ux-recast review   --project P --session S --run R --evidence E.json [--mode review|walkthrough] [--config NAME=ID]
    ux-recast findings --project P --session S --run R --file findings.json
    ux-recast rubric   --version | --print <rubric.md|autowork-reviewer.md|walkthrough.md>
    ux-recast validate <task|state|packet|receipt|findings|comparison|documentation> FILE
    ux-recast document prepare --project P --request R.json [--measurement M.json]
    ux-recast document prompt  --project P --id ID
    ux-recast document render  --spec S.json --out S.html
    ux-recast document check   [--guide G.md] [--sheet S.html ...]
    ux-recast document record  --project P --id ID [--guide G.md] [--sheet S.json ...]
    ux-recast document measure --url U --parts P.json --property PART.PROP ... --revision REV [--viewport 390x844] [--dpr 3] [--engine chromium] [--ready SEL] --out M.json
    ux-recast document trace   --sheet S.html|S.json --repo R [--url U] [--parts P.json] [--ready SEL] [--explain E.json] [--sensitivity N]
    ux-recast lessons  new     --project P --title T --body-file F
    ux-recast lessons  support --project P --lesson ID --from Q --outcome OUTCOME_ID
    ux-recast lessons  promote --project P --lesson ID [--shared-dir D] [--user-instruction TEXT]
    ux-recast lessons  status  --project P --lesson ID --to STATUS [--reason R] [--superseded-by ID]

``document`` is the documentation request kind (D-07): style guides and component sheets,
prepared as a packet for a provider and validated before anything is written. It is separate
from review mode and never changes it.

``review`` prepares and claims a packet and writes a findings template; whoever
fills it is the reviewer. For a fresh-context evaluator, hand it exactly the
output of ``packet prompt`` and record its findings with ``findings``.
"""
import argparse
import json
from pathlib import Path
import sys


def _control(argv):
    from ux_recast.cycle import control
    sys.argv = ["control.py", *argv]
    return control.main()


def _packet(argv):
    from ux_recast.providers import lugos_autowork
    sys.argv = ["autowork_review.py", *argv]
    return lugos_autowork.main()


def _review(argv):
    from ux_recast.cycle.control import config_values
    from ux_recast.providers import local_agent
    p = argparse.ArgumentParser(prog="ux-recast review")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--session", required=True)
    p.add_argument("--run", required=True)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--config", action="append", default=None)
    p.add_argument("--mode", choices=["review", "walkthrough"], default="review",
                   help="review: bounded reviewer assignment; walkthrough: fresh-evaluator cognitive walkthrough")
    p.add_argument("--provider", choices=["local"], default="local",
                   help="who fulfils the packet; the Lugos Autowork lane is driven through 'packet submit' instead")
    a = p.parse_args(argv)
    config = config_values(a.config) if a.config is not None else None
    return _emit(lambda: local_agent.prepare(a.project, a.session, a.run, a.evidence, config=config, mode=a.mode))


def _findings(argv):
    from ux_recast.providers import local_agent
    p = argparse.ArgumentParser(prog="ux-recast findings")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--session", required=True)
    p.add_argument("--run", required=True)
    p.add_argument("--file", type=Path, required=True)
    a = p.parse_args(argv)
    return _emit(lambda: local_agent.record(a.project, a.session, a.run, a.file))


def _rubric(argv):
    from ux_recast import rubric
    p = argparse.ArgumentParser(prog="ux-recast rubric")
    p.add_argument("--version", action="store_true")
    p.add_argument("--print", choices=["rubric.md", "autowork-reviewer.md", "walkthrough.md"])
    a = p.parse_args(argv)
    if a.print:
        sys.stdout.write(rubric.read_text(a.print))
        return 0
    print(json.dumps({"rubric_version": rubric.version(), "VERSION": rubric.read_text("VERSION")}))
    return 0


def _validate(argv):
    from ux_recast.contracts import ContractError, validate
    p = argparse.ArgumentParser(prog="ux-recast validate")
    p.add_argument("kind", choices=["task", "state", "packet", "receipt", "findings", "comparison", "documentation"])
    p.add_argument("file", type=Path)
    a = p.parse_args(argv)
    try:
        validate(a.kind, json.loads(a.file.read_text(encoding="utf-8")))
    except ContractError as error:
        print(json.dumps({"valid": False, "field": error.field, "error": str(error)}))
        return 2
    print(json.dumps({"valid": True, "kind": a.kind, "file": str(a.file)}))
    return 0


def _lessons(argv):
    from ux_recast.records import lessons
    p = argparse.ArgumentParser(prog="ux-recast lessons")
    verbs = p.add_subparsers(dest="verb", required=True)
    new = verbs.add_parser("new")
    new.add_argument("--project", type=Path, required=True)
    new.add_argument("--title", required=True)
    new.add_argument("--body-file", type=Path, required=True)
    support = verbs.add_parser("support")
    support.add_argument("--project", type=Path, required=True)
    support.add_argument("--lesson", required=True)
    support.add_argument("--from", dest="supporter", type=Path, required=True)
    support.add_argument("--outcome", required=True)
    promote = verbs.add_parser("promote")
    promote.add_argument("--project", type=Path, required=True)
    promote.add_argument("--lesson", required=True)
    promote.add_argument("--shared-dir", type=Path, default=lessons.SHARED_DIR)
    promote.add_argument("--user-instruction", help="the user's explicit instruction to promote without a second project")
    status = verbs.add_parser("status")
    status.add_argument("--project", type=Path, required=True)
    status.add_argument("--lesson", required=True)
    status.add_argument("--to", required=True, choices=lessons.STATUSES)
    status.add_argument("--reason")
    status.add_argument("--superseded-by")
    a = p.parse_args(argv)
    if a.verb == "status":
        return _emit(lambda: lessons.set_status(a.project, a.lesson, a.to, reason=a.reason, superseded_by=a.superseded_by))
    if a.verb == "new":
        return _emit(lambda: {"lesson": lessons.create(a.project, a.title, a.body_file.read_text(encoding="utf-8"))})
    if a.verb == "support":
        return _emit(lambda: {"supported_by": lessons.add_support(a.project, a.lesson, a.supporter, a.outcome)})
    return _emit(lambda: lessons.promote(a.project, a.lesson, a.shared_dir, instruction=a.user_instruction))


def _document(argv):
    from ux_recast.contracts import ContractError
    from ux_recast.docs import guide, packet, sheet, trace
    p = argparse.ArgumentParser(prog="ux-recast document")
    verbs = p.add_subparsers(dest="verb", required=True)
    prep = verbs.add_parser("prepare")
    prep.add_argument("--project", type=Path, required=True)
    prep.add_argument("--request", type=Path, required=True)
    prep.add_argument("--measurement", type=Path)
    show = verbs.add_parser("prompt")
    show.add_argument("--project", type=Path, required=True)
    show.add_argument("--id", required=True)
    render = verbs.add_parser("render")
    render.add_argument("--spec", type=Path, required=True)
    render.add_argument("--out", type=Path, required=True)
    check = verbs.add_parser("check")
    check.add_argument("--guide", type=Path)
    check.add_argument("--sheet", type=Path, action="append", default=[])
    rec = verbs.add_parser("record")
    rec.add_argument("--project", type=Path, required=True)
    rec.add_argument("--id", required=True)
    rec.add_argument("--guide", type=Path)
    rec.add_argument("--sheet", type=Path, action="append", default=[])
    meas = verbs.add_parser("measure")
    meas.add_argument("--url", required=True)
    meas.add_argument("--parts", type=Path, required=True, help="JSON {part: selector}")
    meas.add_argument("--property", action="append", required=True, help="PART.PROPERTY, e.g. row.height")
    meas.add_argument("--revision", required=True)
    meas.add_argument("--viewport", default="390x844")
    meas.add_argument("--dpr", type=float, default=3)
    meas.add_argument("--engine", choices=["chromium", "webkit", "firefox"], default="chromium")
    meas.add_argument("--ready")
    meas.add_argument("--out", type=Path, required=True)
    tr = verbs.add_parser("trace")
    tr.add_argument("--sheet", type=Path, required=True, help="a rendered sheet (.html) or its spec (.json)")
    tr.add_argument("--repo", type=Path, required=True, help="git repository the source files are read from")
    tr.add_argument("--url", help="page to re-measure rendered values on")
    tr.add_argument("--parts", type=Path, help="JSON {part: selector}; defaults to the sheet's measurement parts")
    tr.add_argument("--ready")
    tr.add_argument("--explain", type=Path, help="JSON {code: reason} for deltas that are explained")
    tr.add_argument("--sensitivity", type=int, default=0, help="also seed N mutations and require every one caught")
    tr.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)

    def load_spec(path):
        text = path.read_text(encoding="utf-8")
        return sheet.spec_of(text) if path.suffix.lower() in {".html", ".htm"} else json.loads(text)

    def run():
        if a.verb == "prepare":
            return packet.prepare(a.project, a.request, measurement_path=a.measurement)
        if a.verb == "prompt":
            sys.stdout.write((packet.folder_for(a.project, a.id) / "prompt.md").read_text(encoding="utf-8"))
            return None
        if a.verb == "render":
            html = sheet.render(json.loads(a.spec.read_text(encoding="utf-8")))
            a.out.parent.mkdir(parents=True, exist_ok=True)
            a.out.write_text(html, encoding="utf-8", newline="\n")
            return {"written": str(a.out), **sheet.validate(html)}
        if a.verb == "check":
            sheets = {str(path): sheet.validate(path.read_text(encoding="utf-8")) for path in a.sheet}
            result = {"sheets": sheets}
            if a.guide:
                slots = any(s["uses_slots"] for s in sheets.values())
                result["guide"] = guide.validate(a.guide.read_text(encoding="utf-8"), sheet_uses_slots=slots)
            return result
        if a.verb == "record":
            return packet.record(a.project, a.id, guide_path=a.guide, sheet_paths=a.sheet)
        if a.verb == "measure":
            from ux_recast.evidence import measure
            parts = json.loads(a.parts.read_text(encoding="utf-8"))
            props = [tuple(item.split(".", 1)) for item in a.property]
            width, height = (int(n) for n in a.viewport.split("x"))
            result = measure.measure(a.url, parts, props, revision=a.revision, viewport=(width, height),
                                     device_pixel_ratio=a.dpr, engine=a.engine, ready=a.ready)
            a.out.parent.mkdir(parents=True, exist_ok=True)
            a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
            return result
        spec = load_spec(a.sheet)
        setup = spec.get("measurement", {})
        parts = json.loads(a.parts.read_text(encoding="utf-8")) if a.parts else setup.get("parts", {})
        url = a.url or setup.get("url")
        measurer = trace.page_measurer(url, parts, ready=a.ready or setup.get("ready")) if url else None
        reader = trace.SourceReader(a.repo)
        explanations = json.loads(a.explain.read_text(encoding="utf-8")) if a.explain else None
        report = trace.trace(spec["variables"], reader=reader, measurer=measurer, explanations=explanations)
        if a.sensitivity:
            report["sensitivity"] = trace.sensitivity(spec["variables"], a.sensitivity, reader=reader,
                                                      measurer=measurer, seed=a.seed)
            report["passed"] = report["passed"] and not report["sensitivity"]["missed"]
        return report

    try:
        result = run()
    except ContractError as error:
        print(json.dumps({"valid": False, "field": error.field, "error": str(error)}))
        return 2
    except (ValueError, OSError) as error:
        print(json.dumps({"invoke": False, "error": str(error)}))
        return 2
    if result is None:
        return 0
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result.get("passed", True) else 1


def _emit(call):
    try:
        print(json.dumps(call(), indent=2, ensure_ascii=True))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({"invoke": False, "error": str(error)}))
        return 2


COMMANDS = {"control": _control, "packet": _packet, "review": _review, "findings": _findings,
            "rubric": _rubric, "validate": _validate, "lessons": _lessons, "document": _document}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"} or argv[0] not in COMMANDS:
        sys.stderr.write(__doc__)
        return 0 if argv and argv[0] in {"-h", "--help"} else 2
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main())
