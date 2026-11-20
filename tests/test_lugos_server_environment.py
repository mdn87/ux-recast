"""A saved MCP entry must not become a static credential store for UX dispatch."""

import json
from pathlib import Path

import pytest

from ux_recast.providers.lugos_autowork import server_parameters


def test_saved_mcp_credentials_are_rejected_before_server_launch(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    (tmp_path / ".claude.json").write_text(json.dumps({
        "mcpServers": {"lugos": {
            "command": "lugos-mcp",
            "env": {"LUGOS_AUTOWORK_REQUEST_PROFILE": "review", "OPENAI_API_KEY": "old-key"},
        }}
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="launch through GLAS"):
        server_parameters(None)


def test_saved_nonsecret_settings_preserve_injected_process_credentials(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("LUGOS_OPERATOR_API_TOKEN", "synthetic-glas-token")
    (tmp_path / ".claude.json").write_text(json.dumps({
        "mcpServers": {"lugos": {
            "command": "lugos-mcp",
            "args": ["serve"],
            "env": {"LUGOS_AUTOWORK_REQUEST_PROFILE": "review"},
        }}
    }), encoding="utf-8")
    command, args, env = server_parameters(None)
    assert (command, args) == ("lugos-mcp", ["serve"])
    assert env["LUGOS_AUTOWORK_REQUEST_PROFILE"] == "review"
    assert env["LUGOS_OPERATOR_API_TOKEN"] == "synthetic-glas-token"
