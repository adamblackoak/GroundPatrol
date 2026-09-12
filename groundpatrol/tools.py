from __future__ import annotations

import json
from dataclasses import asdict

from strands import tool

from .gate import evaluate_action
from .models import ActionProposal
from .receipts import make_receipt, persist_receipt
from .scenarios import demo_snapshot


@tool
def get_patrol_snapshot(beach_id: str) -> str:
    """Return current evidence-backed operating state for a beach."""
    return json.dumps(asdict(demo_snapshot(beach_id)), indent=2)


@tool
def request_action_clearance(
    beach_id: str,
    action: str,
    rationale: str,
    autonomous: bool = False,
    target_mass_kg: float = 0.0,
) -> str:
    """Evaluate a proposed action at the deterministic GroundPatrol execution boundary.

    This tool is mandatory before claiming that any physical action may proceed.
    """
    snapshot = demo_snapshot(beach_id)
    proposal = ActionProposal(
        action=action,
        beach_id=beach_id,
        rationale=rationale,
        autonomous=autonomous,
        target_mass_kg=target_mass_kg,
    )
    result = evaluate_action(snapshot, proposal)
    receipt = make_receipt(snapshot, proposal, result)
    receipt_path = persist_receipt(receipt)
    return json.dumps(
        {
            "decision": result.decision.value,
            "reasons": result.reasons,
            "conditions": result.conditions,
            "receipt_id": receipt["receipt_sha256"],
            "receipt_path": receipt_path,
        },
        indent=2,
    )


@tool
def escalate_to_human(beach_id: str, reason: str) -> str:
    """Create a bounded human-review handoff instead of acting autonomously."""
    return json.dumps(
        {
            "status": "HUMAN_REVIEW_REQUIRED",
            "beach_id": beach_id,
            "reason": reason,
            "action_taken": "none",
        },
        indent=2,
    )
