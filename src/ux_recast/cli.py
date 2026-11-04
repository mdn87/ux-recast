"""``ux-recast`` command line.

Verbs mirror the Lugos scripts so a shim can forward argv unchanged:

    ux-recast control  --project P --session S <status|mode|checkpoint|phase|finish> ...
    ux-recast packet   --project P --session S --run R <prepare|claim|prompt|submit|record|consume> ...
    ux-recast review   --project P --session S --run R --evidence E.json [--mode review|walkthrough] [--config NAME=ID]
    ux-recast findings --project P --session S --run R --file findings.json
    ux-recast rubric   --version | --print <rubric.md|autowork-reviewer.md|walkthrough.md>
    ux-recast validate <task|state|packet|receipt|findings|comparison> FILE
    ux-recast lessons  new     --project P --title T --body-file F
    ux-recast lessons  support --project P --lesson ID --from Q --outcome OUTCOME_ID
    ux-recast lessons  promote --project P --lesson ID [--shared-dir D] [--user-instruction TEXT]

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
    p.add_argument("kind", choices=["task", "state", "packet", "receipt", "findings", "comparison"])
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
    a = p.parse_args(argv)
    if a.verb == "new":
        return _emit(lambda: {"lesson": lessons.create(a.project, a.title, a.body_file.read_text(encoding="utf-8"))})
    if a.verb == "support":
        return _emit(lambda: {"supported_by": lessons.add_support(a.project, a.lesson, a.supporter, a.outcome)})
    return _emit(lambda: lessons.promote(a.project, a.lesson, a.shared_dir, instruction=a.user_instruction))


def _emit(call):
    try:
        print(json.dumps(call(), indent=2, ensure_ascii=True))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({"invoke": False, "error": str(error)}))
        return 2


COMMANDS = {"control": _control, "packet": _packet, "review": _review, "findings": _findings,
            "rubric": _rubric, "validate": _validate, "lessons": _lessons}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"} or argv[0] not in COMMANDS:
        sys.stderr.write(__doc__)
        return 0 if argv and argv[0] in {"-h", "--help"} else 2
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main())
