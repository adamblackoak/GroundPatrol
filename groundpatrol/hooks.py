from __future__ import annotations

from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent
from strands.plugins import Plugin, hook


class PatrolAuditPlugin(Plugin):
    """Visible tool ledger for the governed decision path."""

    name = "groundpatrol-audit"

    @hook
    def before_tool(self, event: BeforeToolCallEvent) -> None:
        tool_use = event.tool_use
        print(
            "[groundpatrol] start tool=%s input=%s"
            % (tool_use["name"], tool_use.get("input", {}))
        )

    @hook
    def after_tool(self, event: AfterToolCallEvent) -> None:
        outcome = "error" if isinstance(event.result, Exception) else "ok"
        print(
            "[groundpatrol] end tool=%s outcome=%s duration=%s"
            % (event.tool_use["name"], outcome, event.duration)
        )
