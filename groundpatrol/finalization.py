"""Receipt-bound finalization evidence for the local demo side-effect boundary.

A verified finalizer is necessary for dispatch; neither this locally stored
unkeyed digest nor its existence represents external operating authority.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .evaluator import verify_output_contract
from .receipts import load_receipt, verify_receipt
from .storage import runtime_state_directory


_RECEIPT_ID = re.compile(r"[a-f0-9]{64}\Z")


def _digest(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _file(receipt_id: str) -> Path:
    if not isinstance(receipt_id, str) or not _RECEIPT_ID.fullmatch(receipt_id):
        raise ValueError("invalid_receipt_id")
    return runtime_state_directory("finalizations") / f"{receipt_id}.json"


def load_finalization(receipt_id: str) -> dict | None:
    path = _file(receipt_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def verify_finalization(record: dict, *, receipt_id: str) -> bool:
    if not isinstance(record, dict) or record.get("receipt_id") != receipt_id:
        return False
    digest = record.get("finalization_sha256")
    if not isinstance(digest, str) or not _RECEIPT_ID.fullmatch(digest):
        return False
    body = {key: val for key, val in record.items() if key != "finalization_sha256"}
    return hmac.compare_digest(_digest(body), digest)


def _persist_finalization(
    receipt_id: str, *, status: str, reason: str, decision: str, next_action: str
) -> dict:
    body = {
        "receipt_id": receipt_id,
        "status": status,
        "reason": reason,
        "decision": decision,
        "next_action": next_action,
        "finalized_at": datetime.now(timezone.utc).isoformat(),
    }
    body["finalization_sha256"] = _digest(body)
    target = _file(receipt_id)
    fd, temp_name = tempfile.mkstemp(prefix=".finalization-", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(body, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return body


def finalize_receipt_decision(receipt_id: str, claimed_decision: str, next_action: str) -> dict:
    """Persist each evaluation, including rejected outcomes, superseding prior results."""
    try:
        receipt = load_receipt(receipt_id) if _RECEIPT_ID.fullmatch(receipt_id) else None
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        receipt = None

    if receipt is None:
        return {"status": "REJECTED", "reason": "receipt_not_found", "receipt_id": receipt_id}
    if not verify_receipt(receipt):
        return {"status": "REJECTED", "reason": "receipt_integrity_failure", "receipt_id": receipt_id}

    actual_decision = receipt["gate_result"]["decision"]
    result = verify_output_contract(
        receipt_decision=actual_decision,
        claimed_decision=claimed_decision,
        next_action=next_action,
    )
    status = "VERIFIED" if result.verified else "REJECTED"
    record = _persist_finalization(
        receipt_id,
        status=status,
        reason=result.reason,
        decision=actual_decision,
        next_action=next_action,
    )
    return {
        "status": status,
        "reason": result.reason,
        "receipt_id": receipt_id,
        "decision": actual_decision,
        "next_action": next_action,
        "finalization_sha256": record["finalization_sha256"],
    }
