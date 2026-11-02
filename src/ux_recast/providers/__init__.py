"""Review-packet providers.

A provider fulfils one claimed review packet: ``lugos_autowork`` sends it to
Autowork through the ``lugos.models`` MCP tool; ``local_agent`` hands it to
the agent running the cycle and takes a findings file back. Linters and
measurement helpers are not providers; they live in ``ux_recast.evidence``.
"""
