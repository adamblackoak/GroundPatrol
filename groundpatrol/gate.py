from __future__ import annotations

from datetime import datetime, timezone

from .models import ActionProposal, Decision, GateResult, PatrolSnapshot


MAX_EVIDENCE_AGE_MIN = 45.0
MAX_AUTONOMOUS_MASS_KG = 20.0
MAX_AUTONOMOUS_WIND_KPH = 35.0
MIN_VISIBILITY_M = 150


def evaluate_action(
    snapshot: PatrolSnapshot,
    proposal: ActionProposal,
    *,
    now: datetime | None = None,
) -> GateResult:
    """Deterministic runtime action-clearance boundary.

    The model may propose. This function decides whether action is permitted.
    """
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    conditions: list[str] = []

    if proposal.beach_id != snapshot.beach_id:
        return GateResult(
            decision=Decision.DENY,
            reasons=("proposal_scope_mismatch",),
        )

    if not snapshot.evidence:
        return GateResult(
            decision=Decision.DEFER,
            reasons=("no_evidence",),
        )

    stale = [
        e.source for e in snapshot.evidence
        if e.age_minutes(now) > MAX_EVIDENCE_AGE_MIN
    ]
    if stale:
        return GateResult(
            decision=Decision.DEFER,
            reasons=("stale_evidence",),
            conditions=("refresh_runtime_observations",),
            evidence_used=tuple(e.source for e in snapshot.evidence),
        )

    if not snapshot.access_open:
        return GateResult(
            decision=Decision.DENY,
            reasons=("site_access_closed",),
            evidence_used=tuple(e.source for e in snapshot.evidence),
        )

    if snapshot.protected_habitat:
        return GateResult(
            decision=Decision.DEFER,
            reasons=("protected_habitat_requires_human_authority",),
            conditions=("obtain_authorised_human_clearance",),
            evidence_used=tuple(e.source for e in snapshot.evidence),
        )

    if snapshot.people_nearby and proposal.autonomous:
        return GateResult(
            decision=Decision.DEFER,
            reasons=("people_in_operating_envelope",),
            conditions=("human_operator_confirms_clear_zone",),
            evidence_used=tuple(e.source for e in snapshot.evidence),
        )

    if snapshot.wind_kph > MAX_AUTONOMOUS_WIND_KPH:
        return GateResult(
            decision=Decision.DENY,
            reasons=("wind_outside_operating_envelope",),
            evidence_used=tuple(e.source for e in snapshot.evidence),
        )

    if snapshot.visibility_m < MIN_VISIBILITY_M:
        return GateResult(
            decision=Decision.DENY,
            reasons=("visibility_outside_operating_envelope",),
            evidence_used=tuple(e.source for e in snapshot.evidence),
        )

    if proposal.action == "collect_debris":
        if proposal.target_mass_kg <= 0:
            return GateResult(
                decision=Decision.DENY,
                reasons=("invalid_collection_mass",),
            )

        if proposal.autonomous and proposal.target_mass_kg > MAX_AUTONOMOUS_MASS_KG:
            return GateResult(
                decision=Decision.CONDITIONAL,
                reasons=("mass_exceeds_autonomous_limit",),
                conditions=("human_operator_takes_control",),
                evidence_used=tuple(e.source for e in snapshot.evidence),
            )

        reasons.append("runtime_conditions_within_envelope")
        return GateResult(
            decision=Decision.APPROVE,
            reasons=tuple(reasons),
            evidence_used=tuple(e.source for e in snapshot.evidence),
        )

    if proposal.action in {"inspect", "map", "request_human_review"}:
        return GateResult(
            decision=Decision.APPROVE,
            reasons=("non_destructive_action_within_envelope",),
            evidence_used=tuple(e.source for e in snapshot.evidence),
        )

    return GateResult(
        decision=Decision.DENY,
        reasons=("action_not_allowlisted",),
    )
