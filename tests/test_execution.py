from dataclasses import replace

import pytest

from groundpatrol.execution import DispatchRejected, dispatch_collection_work_order
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
