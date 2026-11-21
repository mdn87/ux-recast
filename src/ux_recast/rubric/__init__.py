"""The shared review rubric and reviewer prompt.

Rubric 1 matched the Lugos copies through Phase 3 (D-15). Rubric 2 adds the
Impeccable vocabulary for bounded reviews. The D-21 walkthrough retains its
own assignment. ``VERSION`` records the sha256 of each packaged document.
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
