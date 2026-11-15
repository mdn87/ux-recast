"""S4.3: ``impeccable detect --json`` as an evidence pre-pass.

The tool is used only when it is already on PATH. These tests put a stand-in
``impeccable`` there that replays what the real one prints: a JSON list of rule
hits on stdout, exit 2 for findings, 0 for none, 1 when a target could not be
scanned. That shape and those exit codes were read from Impeccable at
``e89e3ada3e87`` (``cli-v4.8.0``): ``crates/detect/src/cli.rs`` and the
``tests/oracle/golden/detect-fixture-json-*`` outputs. The real tool was not run.
"""
import json
import os
import stat
import sys
import textwrap

import pytest

from ux_recast.evidence import impeccable_detect

STAND_IN = textwrap.dedent('''\
    import json, os, sys
    with open(os.environ["STAND_IN_LOG"], "a", encoding="utf-8") as log:
        log.write(json.dumps([os.environ["STAND_IN_NAME"], *sys.argv[1:]]) + "\\n")
    if sys.argv[1:2] == ["--version"]:
        print(os.environ.get("STAND_IN_VERSION", "4.8.0"))
        raise SystemExit(int(os.environ.get("STAND_IN_VERSION_EXIT", "0")))
    sys.stdout.buffer.write(os.environ.get("STAND_IN_STDOUT", "").encode("utf-8"))
    sys.stderr.buffer.write(os.environ.get("STAND_IN_STDERR", "").encode("utf-8"))
    raise SystemExit(int(os.environ.get("STAND_IN_EXIT", "0")))
''')

# Two primary hits and one advisory note, in the field layout the tool prints.
HITS = [
    {"antipattern": "dark-glow", "name": "Glowing shadow accents",
     "description": "A coloured glow where a neutral elevation shadow would do — use lighting with a purpose.",
     "severity": "warning", "category": "slop", "file": "site/index.html", "line": 0,
     "snippet": "Zero-offset box-shadow glow (#3b82f6)"},
    {"antipattern": "tiny-text", "name": "Undersized interface text",
     "description": "Interface text below a readable size.",
     "severity": "warning", "category": "quality", "file": "site/index.html", "line": 41,
     "snippet": "font-size: 9px"},
    {"antipattern": "em-dash-overuse", "name": "Em dash overuse",
     "description": "Many em dashes in running text.",
     "severity": "advisory", "category": "slop", "file": "site/index.html", "line": 12,
     "snippet": "4 em dashes in one paragraph", "advisory": True},
]
NO_BROWSER = ("Error: No Chrome, Chromium, Edge, or Brave installation found for URL scanning. Install Google "
              "Chrome, or point IMPECCABLE_BROWSER at a Chromium-based browser executable.\n")


def put_on_path(directory, name):
    """A stand-in command ``name`` in ``directory``: a batch file on Windows, a shell script elsewhere."""
    script = directory / "stand_in.py"
    script.write_text(STAND_IN, encoding="utf-8")
    if os.name == "nt":
        (directory / f"{name}.cmd").write_text(
            f'@set "STAND_IN_NAME={name}"\r\n@"{sys.executable}" "{script}" %*\r\n', encoding="utf-8")
    else:
        launcher = directory / name
        launcher.write_text(f'#!/bin/sh\nSTAND_IN_NAME={name} exec "{sys.executable}" "{script}" "$@"\n',
                            encoding="utf-8")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)


@pytest.fixture
def path_dir(tmp_path, monkeypatch):
    """An empty directory that is the whole of PATH, and the log the stand-ins write their calls to."""
    directory = tmp_path / "bin"
    directory.mkdir()
    monkeypatch.setenv("PATH", str(directory))
    monkeypatch.setenv("STAND_IN_LOG", str(tmp_path / "calls.log"))
    return directory


@pytest.fixture
def tool(path_dir, monkeypatch):
    """``impeccable`` on PATH; ``tool(stdout, exit, stderr)`` sets what its next scan prints and returns."""
    put_on_path(path_dir, "impeccable")

    def answer(stdout="[]\n", exit_code=0, stderr=""):
        monkeypatch.setenv("STAND_IN_STDOUT", stdout if isinstance(stdout, str) else json.dumps(stdout) + "\n")
        monkeypatch.setenv("STAND_IN_EXIT", str(exit_code))
        monkeypatch.setenv("STAND_IN_STDERR", stderr)
    return answer


def calls(tmp_path):
    log = tmp_path / "calls.log"
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []


def test_without_the_binary_the_pre_pass_is_unavailable_and_nothing_is_run(path_dir, tmp_path):
    put_on_path(path_dir, "npx")
    outcome = impeccable_detect.detect("site/index.html")
    assert outcome["schema"] == "ux-recast/impeccable-detect@1"
    assert outcome["status"] == "unavailable"
    assert "not on PATH" in outcome["reason"]
    assert outcome["findings"] == []
    assert "provenance" not in outcome
    assert calls(tmp_path) == [], "npx is never used to fetch the tool"


def test_exit_2_is_findings_that_carry_rule_ids_and_kind_implementation(tool, tmp_path):
    tool(HITS, exit_code=2)
    outcome = impeccable_detect.detect("site/index.html")
    assert (outcome["status"], outcome["target"]) == ("findings", "site/index.html")
    assert [finding["rule_id"] for finding in outcome["findings"]] == ["dark-glow", "tiny-text", "em-dash-overuse"]
    for finding in outcome["findings"]:
        assert finding["kind"] == "implementation"
        assert finding["category"] == "heuristic concern"
    first = outcome["findings"][0]
    assert first == {"rule_id": "dark-glow", "kind": "implementation", "category": "heuristic concern",
                     "rule_name": "Glowing shadow accents", "description": HITS[0]["description"],
                     "observed": "Zero-offset box-shadow glow (#3b82f6)", "file": "site/index.html", "line": 0,
                     "tool_severity": "warning", "tool_category": "slop", "advisory": False}
    assert [finding["advisory"] for finding in outcome["findings"]] == [False, False, True]


def test_the_record_says_which_tool_and_version_produced_it(tool, tmp_path):
    tool(HITS, exit_code=2)
    provenance = impeccable_detect.detect("site/index.html")["provenance"]
    assert provenance["tool"] == "impeccable"
    assert provenance["version"] == "4.8.0"
    assert provenance["arguments"] == ["detect", "--json", "site/index.html"]
    assert provenance["exit_code"] == 2
    assert provenance["ran_at"].endswith("Z")
    assert calls(tmp_path) == [["impeccable", "--version"], ["impeccable", "detect", "--json", "site/index.html"]]


def test_a_version_the_tool_will_not_give_is_recorded_as_unknown(tool, monkeypatch):
    tool(HITS, exit_code=2)
    monkeypatch.setenv("STAND_IN_VERSION_EXIT", "1")
    outcome = impeccable_detect.detect("site/index.html")
    assert outcome["status"] == "findings"
    assert outcome["provenance"]["version"] is None


def test_exit_0_is_clean(tool):
    tool("[]\n", exit_code=0)
    outcome = impeccable_detect.detect("site/")
    assert (outcome["status"], outcome["findings"]) == ("clean", [])
    assert outcome["provenance"]["exit_code"] == 0


def test_exit_0_with_only_advisory_notes_is_clean_and_lists_them(tool):
    tool(HITS[2:], exit_code=0)
    outcome = impeccable_detect.detect("site/")
    assert outcome["status"] == "clean"
    assert [(finding["rule_id"], finding["advisory"]) for finding in outcome["findings"]] == [("em-dash-overuse", True)]


@pytest.mark.parametrize("exit_code", [1, 3])
def test_any_other_exit_is_an_error_that_carries_the_tools_message(tool, exit_code):
    tool("", exit_code=exit_code, stderr="Error: --viewport requires a WxH value, e.g. --viewport 390x844\n")
    with pytest.raises(impeccable_detect.DetectError, match=f"exited {exit_code}") as caught:
        impeccable_detect.detect("site/")
    assert "--viewport requires a WxH value" in str(caught.value)


def test_a_url_scan_without_a_browser_is_unavailable(tool):
    tool("", exit_code=1, stderr=NO_BROWSER)
    outcome = impeccable_detect.detect("http://localhost:8000/")
    assert outcome["status"] == "unavailable"
    assert "No Chrome, Chromium, Edge, or Brave installation found" in outcome["reason"]
    assert outcome["findings"] == []
    assert outcome["provenance"]["exit_code"] == 1


def test_a_launcher_without_its_engine_is_unavailable(tool):
    tool("", exit_code=127, stderr="impeccable: no binary for windows-x64.\n")
    outcome = impeccable_detect.detect("site/")
    assert outcome["status"] == "unavailable"
    assert "no binary" in outcome["reason"]


@pytest.mark.parametrize("stdout", ["scanned 3 files\n", '{"antipattern": "dark-glow"}\n', '[{"name": "no rule id"}]\n'])
def test_output_that_is_not_a_list_of_rule_hits_is_an_error(tool, stdout):
    tool(stdout, exit_code=2)
    with pytest.raises(impeccable_detect.DetectError, match="rule hits"):
        impeccable_detect.detect("site/")


def test_a_viewport_is_passed_to_the_tool(tool, tmp_path):
    tool("[]\n")
    outcome = impeccable_detect.detect("http://localhost:8000/", viewport="390x844")
    arguments = ["detect", "--json", "--viewport", "390x844", "http://localhost:8000/"]
    assert outcome["provenance"]["arguments"] == arguments
    assert calls(tmp_path)[-1] == ["impeccable", *arguments]


def test_a_url_with_shell_characters_reaches_the_tool_whole(tool, tmp_path):
    # On Windows the launcher is a batch file, and cmd.exe would act on & | < > ^ unless they are quoted.
    target = "http://localhost:8000/page?a=1&b=2|c<d>e^f"
    tool("[]\n")
    assert impeccable_detect.detect(target)["status"] == "clean"
    assert calls(tmp_path)[-1] == ["impeccable", "detect", "--json", target]


@pytest.mark.skipif(os.name != "nt", reason="only a Windows batch launcher re-reads its arguments")
@pytest.mark.parametrize("target", ['http://localhost/?q="x"', "http://localhost/?q=1\n2"])
def test_a_target_a_batch_launcher_cannot_carry_is_refused(tool, tmp_path, target):
    tool("[]\n")
    with pytest.raises(ValueError, match="batch launcher"):
        impeccable_detect.detect(target)
    assert calls(tmp_path) == []
