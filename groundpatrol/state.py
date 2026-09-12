from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from threading import RLock

from .models import PatrolSnapshot


class SnapshotStore:
    """Thread-safe in-memory store for observed patrol state.

    A clearance request must reference the exact snapshot that was observed. This
    prevents a later tool call from silently evaluating a newly generated state.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._snapshots: dict[str, PatrolSnapshot] = {}

    @staticmethod
    def snapshot_id(snapshot: PatrolSnapshot) -> str:
        canonical = json.dumps(asdict(snapshot), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def put(self, snapshot: PatrolSnapshot) -> str:
        snapshot_id = self.snapshot_id(snapshot)
        with self._lock:
            self._snapshots[snapshot_id] = snapshot
        return snapshot_id

    def get(self, snapshot_id: str) -> PatrolSnapshot | None:
        with self._lock:
            return self._snapshots.get(snapshot_id)


SNAPSHOTS = SnapshotStore()
