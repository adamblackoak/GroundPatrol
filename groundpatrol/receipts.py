from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import ActionProposal, GateResult, PatrolSnapshot


def make_receipt(
    snapshot: PatrolSnapshot,
    proposal: ActionProposal,
    result: GateResult,
) -> dict:
    body = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "snapshot": asdict(snapshot),
        "proposal": asdict(proposal),
        "gate_result": result.as_dict(),
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    body["receipt_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return body


def persist_receipt(receipt: dict, directory: str = "receipts") -> str:
    Path(directory).mkdir(parents=True, exist_ok=True)
    path = Path(directory) / f"{receipt['receipt_sha256'][:16]}.json"
    path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return str(path)
