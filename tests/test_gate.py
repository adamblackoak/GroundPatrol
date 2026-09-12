from datetime import datetime, timedelta, timezone

from groundpatrol.gate import evaluate_action
from groundpatrol.models import ActionProposal, Decision, Evidence, PatrolSnapshot


def snap(**overrides):
    now = datetime.now(timezone.utc).isoformat()
    base = dict(
        beach_id="b1",
        tide_state="falling",
        wind_kph=10,
        visibility_m=1000,
        access_open=True,
        protected_habitat=False,
        people_nearby=False,
        debris_type="plastic",
        debris_mass_kg=5,
        evidence=(Evidence("cam", now, "confirmed"),),
    )
    base.update(overrides)
    return PatrolSnapshot(**base)


def proposal(**overrides):
    base = dict(
        action="collect_debris",
        beach_id="b1",
        rationale="clear confirmed debris",
        autonomous=True,
        target_mass_kg=5,
    )
    base.update(overrides)
    return ActionProposal(**base)


def test_safe_collection_is_approved():
    assert evaluate_action(snap(), proposal()).decision == Decision.APPROVE


def test_people_nearby_forces_defer():
    assert evaluate_action(
        snap(people_nearby=True), proposal()
    ).decision == Decision.DEFER


def test_protected_habitat_forces_human_authority():
    result = evaluate_action(snap(protected_habitat=True), proposal())
    assert result.decision == Decision.DEFER
    assert "obtain_authorised_human_clearance" in result.conditions


def test_bad_weather_denied():
    assert evaluate_action(
        snap(wind_kph=80), proposal()
    ).decision == Decision.DENY


def test_large_autonomous_collection_is_conditional():
    result = evaluate_action(snap(), proposal(target_mass_kg=40))
    assert result.decision == Decision.CONDITIONAL


def test_stale_evidence_defers():
    old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    snapshot = snap(evidence=(Evidence("cam", old, "old observation"),))
    assert evaluate_action(snapshot, proposal()).decision == Decision.DEFER


def test_unknown_action_denied():
    assert evaluate_action(
        snap(), proposal(action="excavate")
    ).decision == Decision.DENY
