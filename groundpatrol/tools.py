from __future__ import annotations

import json
from dataclasses import asdict

from strands import tool

from .evaluator import verify_output_contract
from .feeds import get_feed
from .gate import evaluate_action
from .models import ActionProposal, Decision
from .receipts import load_receipt, make_receipt, persist_receipt, verify_receipt
from .state import SNAPSHOTS


@tool
def get_patrol_snapshot(beach_id: str) -> str:
    """Observe and freeze the current evidence-backed operating state for a beach.

    Returns a snapshot_id that MUST be supplied to request_action_clearance.
    """
    snapshot = get_feed().snapshot(beach_id)
    snapshot_id = SNAPSHOTS.put(snapshot)
    return json.dumps(
        {
            "snapshot_id": snapshot_id,
            "snapshot": asdict(snapshot),
        },
        indent=2,
    )


@tool
def request_action_clearance(
    snapshot_id: str,
    action: str,
    rationale: str,
    autonomous: bool = False,
    target_mass_kg: float = 0.0,
) -> str:
    """Evaluate a proposed action against the exact previously observed snapshot.

    This tool is mandatory before claiming that any physical action may proceed.
    """
    snapshot = SNAPSHOTS.get(snapshot_id)
    if snapshot is None:
        return json.dumps(
            {
                "decision": Decision.DEFER.value,
                "reasons": ["snapshot_not_found"],
                "conditions": ["observe_again"],
                "receipt_id": None,
            },
            indent=2,
        )

    proposal = ActionProposal(
        action=action,
        beach_id=snapshot.beach_id,
        rationale=rationale,
        autonomous=autonomous,
        target_mass_kg=target_mass_kg,
    )
    result = evaluate_action(snapshot, proposal)
    receipt = make_receipt(
        snapshot,
        proposal,
        result,
        snapshot_id=snapshot_id,
    )
    receipt_path = persist_receipt(receipt)
    return json.dumps(
        {
            "decision": result.decision.value,
            "reasons": result.reasons,
            "conditions": result.conditions,
            "evidence_used": result.evidence_used,
            "receipt_id": receipt["receipt_sha256"],
            "receipt_path": receipt_path,
        },
        indent=2,
    )


@tool
def finalize_patrol_decision(
    receipt_id: str,
    claimed_decision: str,
    next_action: str,
) -> str:
    """Verify receipt integrity and final decision/next-action consistency.

    next_action must be one of: execute, refresh, human_review, stop.
    GroundPatrol should call this after clearance and before its final answer.
    """
    receipt = load_receipt(receipt_id)
    if receipt is None:
        return json.dumps(
            {"status": "REJECTED", "reason": "receipt_not_found"}, indent=2
        )
    if not verify_receipt(receipt):
        return json.dumps(
            {"status": "REJECTED", "reason": "receipt_integrity_failure"}, indent=2
        )

    result = verify_output_contract(
        receipt_decision=receipt["gate_result"]["decision"],
        claimed_decision=claimed_decision,
        next_action=next_action,
    )
    return json.dumps(
        {
            "status": "VERIFIED" if result.verified else "REJECTED",
            "reason": result.reason,
            "receipt_id": receipt_id,
            "decision": receipt["gate_result"]["decision"],
            "next_action": next_action,
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
