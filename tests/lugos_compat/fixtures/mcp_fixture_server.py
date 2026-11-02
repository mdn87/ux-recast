"""Stdio MCP server standing in for lugos.models in the submit tests.

It hashes the task it receives on its own, appends every invocation to
UX_FIXTURE_LOG, and shapes the result by UX_FIXTURE_MODE: ok (default),
wrong_digest, missing_digest, error, empty_answer, changed_paths, hang.
"""
import asyncio
import hashlib
import json
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

server = Server("ux-review-fixture")


@server.list_tools()
async def list_tools():
    return [types.Tool(name="lugos.models", description="fixture stand-in", inputSchema={"type": "object"})]


@server.call_tool()
async def call_tool(name, arguments):
    mode = os.environ.get("UX_FIXTURE_MODE", "ok")
    log = os.environ.get("UX_FIXTURE_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"name": name, "arguments": arguments}, ensure_ascii=False) + "\n")
    if mode == "hang":
        await asyncio.sleep(60)
    if mode == "error":
        raise RuntimeError("fixture failure")
    task = (arguments or {}).get("task", "")
    result = {"status": "completed", "run_id": "fixture-run", "selected_route": "fixture:route",
              "model": "fixture", "artifact_dir": "fixture-artifacts", "changed_paths": [], "worktree": None,
              "warnings": [], "answer": "Finding: the fixture reviewed the task",
              "task_sha256": hashlib.sha256(task.encode()).hexdigest()}
    if mode == "wrong_digest":
        result["task_sha256"] = "0" * 64
    elif mode == "missing_digest":
        del result["task_sha256"]
    elif mode == "empty_answer":
        result["answer"] = "   "
    elif mode == "changed_paths":
        result["changed_paths"] = ["src/app.py"]
    return [types.TextContent(type="text", text=json.dumps(result))]


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
