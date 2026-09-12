from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Decision(str, Enum):
    APPROVE = "APPROVE"
    CONDITIONAL = "CONDITIONAL"
    DEFER = "DEFER"
    DENY = "DENY"


@dataclass(frozen=True)
class Evidence:
    source: str
    observed_at: str
    claim: str
    confidence: float = 1.0

    def age_minutes(self, now: datetime | None = None) -> float:
        now = now or datetime.now(timezone.utc)
        stamp = datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))
        return max(0.0, (now - stamp).total_seconds() / 60.0)


@dataclass(frozen=True)
class PatrolSnapshot:
    beach_id: str
    tide_state: str
    wind_kph: float
    visibility_m: int
    access_open: bool
    protected_habitat: bool
    people_nearby: bool
    debris_type: str
    debris_mass_kg: float
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ActionProposal:
    action: str
    beach_id: str
    rationale: str
    autonomous: bool = False
    target_mass_kg: float = 0.0


@dataclass(frozen=True)
class GateResult:
    decision: Decision
    reasons: tuple[str, ...]
    conditions: tuple[str, ...] = field(default_factory=tuple)
    evidence_used: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["decision"] = self.decision.value
        return d
