from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import ActionProposal, GateResult, PatrolSnapshot
from .storage import runtime_state_directory


def _receipt_hash(body: dict) -> str:
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def make_receipt(
    snapshot: PatrolSnapshot,
    proposal: ActionProposal,
    result: GateResult,
    *,
    snapshot_id: str,
) -> dict:
    body = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_id": snapshot_id,
        "snapshot": asdict(snapshot),
        "proposal": asdict(proposal),
        "gate_result": result.as_dict(),
    }
    body["receipt_sha256"] = _receipt_hash(body)
    return body


def _receipt_directory(directory: str) -> Path:
    if directory == "receipts":
        return runtime_state_directory("receipts")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    return root


def persist_receipt(receipt: dict, directory: str = "receipts") -> str:
    root = _receipt_directory(directory)
    path = root / f"{receipt['receipt_sha256']}.json"
    path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return str(path)


def load_receipt(receipt_id: str, directory: str = "receipts") -> dict | None:
    root = _receipt_directory(directory)
    path = root / f"{receipt_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def verify_receipt(receipt: dict) -> bool:
    supplied = receipt.get("receipt_sha256")
    if not isinstance(supplied, str):
        return False
    body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    return _receipt_hash(body) == supplied
