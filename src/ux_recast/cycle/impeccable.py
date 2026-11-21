"""Route Impeccable's agent commands within the existing review and repair passes."""
import hashlib
import re


# Project skill locations from Impeccable's provider registry. Codex and Replit share .agents.
PROVIDERS = (".agents", ".codex", ".claude", ".cursor", ".gemini", ".github", ".grok", ".devin", ".dsh",
             ".agent", ".hermes", ".kiro", ".opencode", ".pi", ".omp", ".qoder", ".trae",
             ".trae-cn", ".rovodev", ".vibe", ".veto")
CODEX_PROVIDERS = {".agents", ".codex"}


def installation(project, *, sources=None):
    """Identify the project's installed review commands and optionally bind the review reference."""
    selected = None
    selected_codex = None
    for provider in PROVIDERS:
        codex = provider in CODEX_PROVIDERS
        if selected_codex == codex:
            continue
        manifest = project / provider / "skills" / "impeccable" / "SKILL.md"
        try:
            content = manifest.read_bytes()
        except (FileNotFoundError, NotADirectoryError, IsADirectoryError, PermissionError):
            continue
        header = content[:8192].decode("utf-8-sig", errors="replace").replace("\r\n", "\n").split("---", 2)
        if len(header) != 3 or header[0].strip() or not re.search(r"(?m)^name: *['\"]?impeccable['\"]? *$", header[1]):
            continue
        references = manifest.parent / "reference"
        if not all((references / f"{name}.md").is_file() for name in ("critique", "adapt", "harden", "polish")):
            continue
        if sources is not None:
            critique = references / "critique.md"
            sources[str(manifest)] = hashlib.sha256(content).hexdigest()
            sources[str(critique)] = hashlib.sha256(critique.read_bytes()).hexdigest()
        version = re.search(r"(?m)^ *version: *['\"]?([0-9][\w.+-]*)['\"]? *$", header[1])
        skill = {"mode": "skill", "path": manifest.relative_to(project).as_posix(),
                 "version": version.group(1) if version else None}
        if selected:
            return {**selected, "alternative": skill}
        selected = skill
        selected_codex = codex
    return selected or {"mode": "guidance"}


def command(skill, name):
    # Codex builds in the upstream universal bundle use the native skill mention.
    prefix = "$" if skill["path"].split("/", 1)[0] in CODEX_PROVIDERS else "/"
    return f"{prefix}impeccable {name}"


def review_instruction(skill):
    if skill["mode"] == "guidance":
        return "Use the four review lenses above on the supplied evidence."
    choices = [skill, skill["alternative"]] if "alternative" in skill else [skill]
    invocation = " or ".join(f"{command(item, 'critique')} ({item['path']})" for item in choices)
    return (f"Invoke {invocation} in the reviewing agent. "
            "Use its critique reference on the supplied task and evidence in this one read-only review. "
            "Skip setup, repository inspection, reports on disk and additional agents. "
            "If your harness cannot use the skill within those limits, use the four lenses above "
            "and report that you used built-in guidance.")


def repair_pass(project, stage):
    skill = installation(project)
    if skill["mode"] != "skill":
        return None
    target = "the proposed plan" if stage == "plan" else "the reviewed interface"
    names = ("adapt", "harden", "polish")
    passes = {**skill, "commands": [command(skill, name) for name in names],
              "instruction": f"In this single parent-owned repair batch, use the syntax for your agent. "
                             f"Invoke each applicable command once on {target} for accepted, current findings. "
                             "Skip unrelated changes and setup. Verify the original task once after the batch."}
    if "alternative" in skill:
        passes["alternative_commands"] = [command(skill["alternative"], name) for name in names]
    return passes
