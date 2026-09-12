from __future__ import annotations

from dataclasses import dataclass

from .models import Decision


ALLOWED_NEXT_ACTIONS: dict[Decision, set[str]] = {
    Decision.APPROVE: {"execute", "human_review", "stop"},
    Decision.CONDITIONAL: {"human_review", "stop"},
    Decision.DEFER: {"refresh", "human_review", "stop"},
    Decision.DENY: {"human_review", "stop"},
}


@dataclass(frozen=True)
class EvaluationResult:
    verified: bool
    reason: str


def verify_output_contract(
    *,
    receipt_decision: str,
    claimed_decision: str,
    next_action: str,
) -> EvaluationResult:
    """Second-pass deterministic check over the agent's intended final decision."""
    try:
        actual = Decision(receipt_decision)
    except ValueError:
        return EvaluationResult(False, "invalid_receipt_decision")

    if claimed_decision != actual.value:
        return EvaluationResult(False, "claimed_decision_mismatch")

    normalized = next_action.strip().lower()
    if normalized not in ALLOWED_NEXT_ACTIONS[actual]:
        return EvaluationResult(False, "next_action_not_permitted_for_decision")

    return EvaluationResult(True, "decision_contract_verified")
