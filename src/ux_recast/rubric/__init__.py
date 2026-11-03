"""The shared review rubric and reviewer prompt.

The bytes of ``rubric.md`` and ``autowork-reviewer.md`` are frozen to the Lugos
copies through the migration (plan decision D-15); ``tests/test_rubric_bytes.py``
enforces it. ``walkthrough.md`` is the fresh-evaluator alternative to the
reviewer assignment (a cognitive walkthrough of a proposed flow or a built
interface from the person's goal and the visible evidence only); it is a
ux-recast addition outside the freeze (D-21). ``VERSION`` records the rubric
version, its source revision and the sha256 of each file.
"""
from importlib import resources

__all__ = ["read_text", "read_bytes", "version"]


def read_bytes(name: str) -> bytes:
    return resources.files(__name__).joinpath(name).read_bytes()


def read_text(name: str) -> str:
    return read_bytes(name).decode("utf-8")


def version() -> str:
    for line in read_text("VERSION").splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "rubric_version":
            return value.strip()
    raise ValueError("VERSION has no rubric_version line")
