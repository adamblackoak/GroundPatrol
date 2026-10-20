from dataclasses import replace

import pytest

from groundpatrol.execution import DispatchRejected, dispatch_collection_work_order
from groundpatrol.finalization import finalize_receipt_decision
from groundpatrol.gate import evaluate_action
from groundpatrol.models import ActionProposal
from groundpatrol.receipts import make_receipt, persist_receipt
from groundpatrol.scenarios import demo_snapshot
from groundpatrol.state import SnapshotStore


def _receipt(snapshot, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    proposal = ActionProposal(
        action="collect_debris",
        beach_id=snapshot.beach_id,
        rationale="test collection",
        autonomous=True,
        target_mass_kg=5,
    )
    gate = evaluate_action(snapshot, proposal)
    snapshot_id = SnapshotStore().put(snapshot)
    receipt = make_receipt(snapshot, proposal, gate, snapshot_id=snapshot_id)
    persist_receipt(receipt)
    if gate.decision.value == "APPROVE":
        assert finalize_receipt_decision(receipt["receipt_sha256"], "APPROVE", "execute")["status"] == "VERIFIED"
    return receipt


def test_approved_receipt_creates_idempotent_work_order(monkeypatch, tmp_path):
    receipt = _receipt(demo_snapshot("b1"), monkeypatch, tmp_path)
    first = dispatch_collection_work_order(receipt["receipt_sha256"])
    second = dispatch_collection_work_order(receipt["receipt_sha256"])

    assert first["status"] == "QUEUED_FOR_COLLECTION"
    assert first["work_order_id"] == second["work_order_id"]
    assert second["idempotent_replay"] is True


def test_non_approved_receipt_cannot_dispatch(monkeypatch, tmp_path):
    snapshot = replace(demo_snapshot("b1"), people_nearby=True)
    receipt = _receipt(snapshot, monkeypatch, tmp_path)

    with pytest.raises(DispatchRejected, match="gate_decision_not_approved"):
        dispatch_collection_work_order(receipt["receipt_sha256"])

def test_old_approval_cannot_dispatch_after_evidence_expires(monkeypatch, tmp_path):
    from datetime import datetime, timedelta, timezone

    snapshot = demo_snapshot("b1")
    receipt = _receipt(snapshot, monkeypatch, tmp_path)
    latest_observation = max(
        datetime.fromisoformat(e.observed_at.replace("Z", "+00:00"))
        for e in snapshot.evidence
    )
    with pytest.raises(DispatchRejected, match="clearance_no_longer_valid:stale_evidence"):
        dispatch_collection_work_order(
            receipt["receipt_sha256"],
            now=latest_observation + timedelta(minutes=46),
        )
    assert not (tmp_path / "executions").exists() or not list((tmp_path / "executions").glob("*.json"))


def test_future_dated_evidence_is_not_an_approval_shortcut(monkeypatch, tmp_path):
    from datetime import datetime, timedelta, timezone

    snapshot = demo_snapshot("b1")
    receipt = _receipt(snapshot, monkeypatch, tmp_path)
    latest_observation = max(
        datetime.fromisoformat(e.observed_at.replace("Z", "+00:00"))
        for e in snapshot.evidence
    )
    with pytest.raises(DispatchRejected, match="invalid_evidence_timestamp"):
        dispatch_collection_work_order(
            receipt["receipt_sha256"],
            now=latest_observation - timedelta(seconds=1),
        )


def test_replay_requires_current_clearance_even_for_existing_work_order(monkeypatch, tmp_path):
    from datetime import datetime, timedelta, timezone

    snapshot = demo_snapshot("b1")
    receipt = _receipt(snapshot, monkeypatch, tmp_path)
    latest_observation = max(
        datetime.fromisoformat(e.observed_at.replace("Z", "+00:00"))
        for e in snapshot.evidence
    )
    fresh_now = latest_observation + timedelta(minutes=1)
    result = dispatch_collection_work_order(receipt["receipt_sha256"], now=fresh_now)
    assert result["status"] == "QUEUED_FOR_COLLECTION"
    with pytest.raises(DispatchRejected, match="clearance_no_longer_valid:stale_evidence"):
        dispatch_collection_work_order(
            receipt["receipt_sha256"], now=latest_observation + timedelta(hours=2)
        )


def test_naive_dispatch_clock_is_rejected(monkeypatch, tmp_path):
    from datetime import datetime

    receipt = _receipt(demo_snapshot("b1"), monkeypatch, tmp_path)
    with pytest.raises(DispatchRejected, match="invalid_dispatch_clock"):
        dispatch_collection_work_order(
            receipt["receipt_sha256"], now=datetime(2026, 9, 13, 12, 0)
        )


def test_direct_dispatch_before_finalizer_refused(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    snapshot = demo_snapshot("b1")
    proposal = ActionProposal("collect_debris", "b1", "test", autonomous=True, target_mass_kg=5)
    gate = evaluate_action(snapshot, proposal)
    receipt = make_receipt(snapshot, proposal, gate, snapshot_id=SnapshotStore().put(snapshot))
    persist_receipt(receipt)
    with pytest.raises(DispatchRejected, match="finalization_missing"):
        dispatch_collection_work_order(receipt["receipt_sha256"])


def test_rejected_finalization_supersedes_earlier_approval(monkeypatch, tmp_path):
    receipt = _receipt(demo_snapshot("b1"), monkeypatch, tmp_path)
    rid = receipt["receipt_sha256"]
    finalization = finalize_receipt_decision(rid, "APPROVE", "stop")
    assert finalization["status"] == "VERIFIED"
    with pytest.raises(DispatchRejected, match="finalization_not_authorized"):
        dispatch_collection_work_order(rid)
    finalization = finalize_receipt_decision(rid, "DENY", "execute")
    assert finalization["status"] == "REJECTED"
    with pytest.raises(DispatchRejected, match="finalization_not_authorized"):
        dispatch_collection_work_order(rid)


def test_finalization_integrity_failure_refuses_dispatch(monkeypatch, tmp_path):
    import json
    from pathlib import Path
    receipt = _receipt(demo_snapshot("b1"), monkeypatch, tmp_path)
    rid = receipt["receipt_sha256"]
    path = Path("finalizations") / (rid + ".json")
    body = json.loads(path.read_text())
    body["next_action"] = "stop"
    path.write_text(json.dumps(body))
    with pytest.raises(DispatchRejected, match="finalization_integrity_failure"):
        dispatch_collection_work_order(rid)
