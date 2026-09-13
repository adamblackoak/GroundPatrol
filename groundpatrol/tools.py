from __future__ import annotations

import json
from dataclasses import asdict
from typing import Literal

from strands import tool

from .evaluator import verify_output_contract
from .execution import DispatchRejected, dispatch_collection_work_order as dispatch_work_order
from .feeds import get_feed
from .gate import evaluate_action
from .models import ActionProposal, Decision
from .receipts import load_receipt, make_receipt, persist_receipt, verify_receipt
from .state import SNAPSHOTS


AllowedAction = Literal["collect_debris", "inspect", "map", "request_human_review"]
AllowedDecision = Literal["APPROVE", "CONDITIONAL", "DEFER", "DENY"]
AllowedNextAction = Literal["execute", "refresh", "human_review", "stop"]


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
    action: AllowedAction,
    rationale: str,
    autonomous: bool = False,
    target_mass_kg: float = 0.0,
) -> str:
    """Evaluate a proposed action against the exact previously observed snapshot.

    This tool is mandatory before claiming that any physical action may proceed.
    Use action='collect_debris' for both manual and autonomous debris collection;
    the execution mode is expressed separately with the autonomous boolean.
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
    claimed_decision: AllowedDecision,
    next_action: AllowedNextAction,
) -> str:
    """Verify receipt integrity and final decision/next-action consistency.

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
def dispatch_collection_work_order(receipt_id: str) -> str:
    """Create an idempotent field collection work order from an APPROVE receipt only.

    The side-effect boundary independently re-verifies the receipt and gate decision.
    In the hackathon demo the adapter writes to a local queue; production deployments
    would replace that adapter with the target work-management or robotics API.
    """
    try:
        result = dispatch_work_order(receipt_id)
    except DispatchRejected as exc:
        return json.dumps(
            {
                "status": "DISPATCH_REJECTED",
                "reason": str(exc),
                "receipt_id": receipt_id,
            },
            indent=2,
        )
    return json.dumps(result, indent=2)


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
