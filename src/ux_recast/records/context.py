"""Project design context: ``PRODUCT.md`` and ``DESIGN.md`` at the project root.

Both files belong to the project (and to Impeccable, where it is installed), so
ux-recast reads them as text and never rewrites them: no parsing, no Markdown
round-trip, line endings kept as stored. A starter template is written only when
the file is absent, through ``O_CREAT | O_EXCL``, so an existing file is never
touched and two writers racing to create one produce exactly one file.
"""
from importlib import resources
import os
from pathlib import Path

NAMES = ("PRODUCT.md", "DESIGN.md")


def _check(name):
    if name not in NAMES:
        raise ValueError(f"context record must be one of {', '.join(NAMES)}: {name}")


def read(root, name):
    """Return the record's text exactly as stored, or None when it does not exist."""
    _check(name)
    try:
        with open(Path(root) / name, encoding="utf-8", newline="") as handle:
            return handle.read()
    except FileNotFoundError:
        return None


def starter(name):
    """Return the packaged starter template for ``name``."""
    _check(name)
    return resources.files(__package__).joinpath("templates", name).read_bytes()


def create(root, name):
    """Write the starter template if the record is absent. Return True only when this call created it."""
    data = starter(name)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(Path(root) / name, flags, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
    return True


def ensure(root):
    """Create whichever starters are missing; map each name to whether this call created it."""
    return {name: create(root, name) for name in NAMES}
