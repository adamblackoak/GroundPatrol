from __future__ import annotations

from strands.hooks import BeforeToolCallEvent
from strands.plugins import Plugin, hook


class PatrolAuditPlugin(Plugin):
    """Small hook layer: visible tool ledger without making the model authoritative."""

    name = "groundpatrol-audit"

    @hook
    def before_tool(self, event: BeforeToolCallEvent) -> None:
        tool_use = event.tool_use
        print(
            "[groundpatrol] tool=%s input=%s"
            % (tool_use["name"], tool_use.get("input", {}))
        )
