from __future__ import annotations

import json

from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent
from strands.plugins import Plugin, hook


class PatrolAuditPlugin(Plugin):
    """Visible tool ledger for the governed decision path."""

    name = "groundpatrol-audit"

    def __init__(self) -> None:
        self.receipt_ids: list[str] = []
        self.work_orders: list[dict] = []

    @staticmethod
    def _documents(value) -> list[dict]:
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except (ValueError, TypeError):
                return []
            return [parsed] if isinstance(parsed, dict) else []
        if not isinstance(value, dict):
            return []
        docs = []
        for item in value.get("content", []):
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                docs.extend(PatrolAuditPlugin._documents(item["text"]))
        if "receipt_id" in value or "work_order_id" in value:
            docs.append(value)
        return docs

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
        if outcome == "ok":
            name = event.tool_use.get("name", "")
            for record in self._documents(event.result):
                if name == "request_action_clearance":
                    receipt_id = record.get("receipt_id")
                    if isinstance(receipt_id, str) and receipt_id not in self.receipt_ids:
                        self.receipt_ids.append(receipt_id)
                elif name == "dispatch_collection_work_order":
                    if record.get("status") == "QUEUED_FOR_COLLECTION" and isinstance(record.get("work_order_id"), str):
                        self.work_orders.append(record)
        print(
            "[groundpatrol] end tool=%s outcome=%s duration=%s"
            % (event.tool_use["name"], outcome, event.duration)
        )
