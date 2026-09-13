from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .models import Decision
from .receipts import load_receipt, verify_receipt
from .storage import runtime_state_directory


class DispatchRejected(RuntimeError):
    pass


def _work_order_id(receipt_id: str) -> str:
    digest = hashlib.sha256(f"groundpatrol:{receipt_id}".encode("utf-8")).hexdigest()
    return f"GP-{digest[:12].upper()}"


def _execution_directory(directory: str) -> Path:
    if directory == "executions":
        return runtime_state_directory("executions")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    return root


def dispatch_collection_work_order(
    receipt_id: str,
    *,
    directory: str = "executions",
) -> dict:
    """Create one idempotent collection work order from an approved receipt.

    The local JSON queue is the hackathon adapter for a field-work system. The
    deterministic approval check remains here at the side-effect boundary, so a model
    cannot bypass it by calling the dispatch tool directly.
    """
    receipt = load_receipt(receipt_id)
    if receipt is None:
        raise DispatchRejected("receipt_not_found")
    if not verify_receipt(receipt):
        raise DispatchRejected("receipt_integrity_failure")

    decision = receipt.get("gate_result", {}).get("decision")
    if decision != Decision.APPROVE.value:
        raise DispatchRejected("gate_decision_not_approved")

    proposal = receipt.get("proposal", {})
    if proposal.get("action") != "collect_debris":
        raise DispatchRejected("unsupported_dispatch_action")

    work_order_id = _work_order_id(receipt_id)
    root = _execution_directory(directory)
    path = root / f"{work_order_id}.json"

    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        existing["idempotent_replay"] = True
        return existing

    body = {
        "work_order_id": work_order_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "QUEUED_FOR_COLLECTION",
        "receipt_id": receipt_id,
        "beach_id": proposal["beach_id"],
        "action": proposal["action"],
        "target_mass_kg": proposal.get("target_mass_kg", 0.0),
        "autonomous_requested": bool(proposal.get("autonomous", False)),
        "adapter": "local_demo_queue",
        "note": "Replace this adapter with the target field-work/robotics dispatch API in production.",
        "idempotent_replay": False,
    }
    path.write_text(json.dumps(body, indent=2), encoding="utf-8")
    return body
