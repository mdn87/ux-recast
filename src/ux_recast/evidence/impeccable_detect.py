"""Impeccable detect as an evidence pre-pass (S4.3; roundtable I-7, T-25).

``detect`` runs ``impeccable detect --json`` on a file, a directory or a URL and returns the rule
hits as evidence for a review. It is a pre-pass and not a provider. A hit names a rule and where it
fired, and carries ``kind: implementation`` and ``category: heuristic concern``. It has no task
step, consequence or correction, so the reviewer who relies on one writes the finding and supplies
those.

The tool is used only when ``impeccable`` is already on PATH. Nothing is installed and ``npx`` is
never called. The record's ``status`` is one of:

``findings``     the scan completed with primary findings (exit 2)
``clean``        the scan completed with none (exit 0); advisory notes may still be listed
``unavailable``  no ``impeccable`` on PATH, a launcher without its engine (exit 127), or no browser
                 for a URL scan. The ``reason`` says which, and the caller carries on without it.

Any other exit, and output that is not a JSON list of rule hits, raises ``DetectError``.

The output layout, the exit codes and the missing-browser messages were read from Impeccable at
``e89e3ada3e87`` (``cli-v4.8.0``): ``crates/detect/src/cli.rs``, ``crates/browser/src/discovery.rs``
and the ``tests/oracle/golden/detect-fixture-json-*`` outputs.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess

SCHEMA = "ux-recast/impeccable-detect@1"

# What the tool prints when a URL scan has no browser to drive.
NO_BROWSER = ("No Chrome, Chromium, Edge, or Brave installation found",
              "Browser was not found at the configured executablePath",
              "puppeteer is required for URL scanning")


class DetectError(RuntimeError):
    """``impeccable detect`` failed in a way that is neither findings nor a missing tool or browser."""


def detect(target, *, viewport=None, timeout_seconds=120):
    """Rule hits for ``target`` (a file, a directory or a URL) as an evidence record; see the module text."""
    target = str(target)
    binary = shutil.which("impeccable")
    if binary is None:
        return {"schema": SCHEMA, "status": "unavailable", "target": target, "findings": [],
                "reason": "impeccable is not on PATH; nothing was installed or run"}
    arguments = ["detect", "--json", *(["--viewport", viewport] if viewport else []), target]
    launcher = _launcher(binary)
    if _batch(launcher[0]) and any(character in argument for argument in arguments for character in '"\r\n%!'):
        raise ValueError("This argument cannot be passed literally through the impeccable batch launcher")
    version = _run(launcher, ["--version"], timeout_seconds)
    ran = _run(launcher, arguments, timeout_seconds)
    record = {"schema": SCHEMA, "target": target, "findings": [], "provenance": {
        "tool": "impeccable", "version": version.stdout.strip() or None if version.returncode == 0 else None,
        "arguments": arguments, "exit_code": ran.returncode,
        "ran_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}}
    message = ran.stderr.strip()
    if ran.returncode == 127 or (ran.returncode == 1 and any(phrase in message for phrase in NO_BROWSER)):
        return {**record, "status": "unavailable", "reason": message or "the impeccable launcher found no engine"}
    if ran.returncode not in (0, 2):
        raise DetectError(f"impeccable detect exited {ran.returncode}: {message[-500:] or 'no message'}")
    try:
        hits = json.loads(ran.stdout)
    except ValueError:
        hits = None
    if not isinstance(hits, list) or not all(isinstance(hit, dict) and isinstance(hit.get("antipattern"), str)
                                             for hit in hits):
        raise DetectError("impeccable detect did not print a JSON list of rule hits, each with its rule id")
    return {**record, "status": "findings" if ran.returncode == 2 else "clean",
            "findings": [_finding(hit) for hit in hits]}


def _finding(hit):
    return {"rule_id": hit["antipattern"], "kind": "implementation", "category": "heuristic concern",
            "rule_name": hit.get("name"), "description": hit.get("description"), "observed": hit.get("snippet"),
            "file": hit.get("file"), "line": hit.get("line"), "tool_severity": hit.get("severity"),
            **({"selector": hit["selector"]} if hit.get("selector") else {}),
            "tool_category": hit.get("category"), "advisory": hit.get("advisory") is True}


def _batch(binary):
    """Whether the launcher is a Windows batch file, such as the shim npm installs."""
    return os.name == "nt" and binary.lower().endswith((".cmd", ".bat"))


def _launcher(binary):
    """Prefer npm's installed JS entry point on Windows so URLs travel as literal arguments."""
    if _batch(binary):
        folder = Path(binary).parent
        node = shutil.which("node")
        roots = [folder / "node_modules"]
        if folder.name == ".bin":
            roots.append(folder.parent)
        for root in roots:
            cli = root / "impeccable" / "cli" / "bin" / "cli.js"
            if node and cli.is_file():
                return [node, str(cli)]
    return [binary]


def _run(launcher, arguments, timeout_seconds):
    command = [*launcher, *arguments]
    if _batch(launcher[0]):
        # A batch launcher hands its arguments to cmd.exe, which would act on the & | < > ^ in a
        # URL. Quoting every argument keeps them literal; detect refuses what quoting cannot carry.
        command = " ".join(f'"{part}"' for part in command)
    try:
        # The 4.8 npm and skill launchers honor this release base. An unsupported transport
        # makes a missing engine unavailable before a downloader can contact a release host.
        env = {**os.environ, "IMPECCABLE_DOWNLOAD_BASE": "disabled://offline"}
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout_seconds, env=env)
    except subprocess.TimeoutExpired:
        raise DetectError(f"impeccable {arguments[0]} did not finish within {timeout_seconds} seconds") from None
