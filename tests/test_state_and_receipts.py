from groundpatrol.gate import evaluate_action
from groundpatrol.models import ActionProposal
from groundpatrol.receipts import make_receipt, verify_receipt
from groundpatrol.scenarios import demo_snapshot
from groundpatrol.state import SnapshotStore


def test_snapshot_id_is_stable_for_same_snapshot():
    snapshot = demo_snapshot("b1")
    store = SnapshotStore()
    assert store.put(snapshot) == store.put(snapshot)


def test_receipt_binds_snapshot_and_detects_tampering():
    snapshot = demo_snapshot("b1")
    store = SnapshotStore()
    snapshot_id = store.put(snapshot)
    proposal = ActionProposal(
        action="collect_debris",
        beach_id="b1",
        rationale="test",
        autonomous=True,
        target_mass_kg=5,
    )
    gate = evaluate_action(snapshot, proposal)
    receipt = make_receipt(snapshot, proposal, gate, snapshot_id=snapshot_id)
    assert verify_receipt(receipt) is True

    receipt["proposal"]["target_mass_kg"] = 500
    assert verify_receipt(receipt) is False
