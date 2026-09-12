from __future__ import annotations

from datetime import datetime, timezone

from .models import Evidence, PatrolSnapshot


def demo_snapshot(beach_id: str = "west-bay-01") -> PatrolSnapshot:
    now = datetime.now(timezone.utc).isoformat()
    return PatrolSnapshot(
        beach_id=beach_id,
        tide_state="falling",
        wind_kph=18.0,
        visibility_m=1200,
        access_open=True,
        protected_habitat=False,
        people_nearby=False,
        debris_type="mixed_plastic",
        debris_mass_kg=12.0,
        evidence=(
            Evidence(
                source="shore-camera-01",
                observed_at=now,
                claim="debris patch confirmed above strand line",
                confidence=0.96,
            ),
            Evidence(
                source="local-conditions-feed",
                observed_at=now,
                claim="operating conditions within configured envelope",
                confidence=0.99,
            ),
        ),
    )
