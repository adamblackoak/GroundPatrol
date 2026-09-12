from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

from .models import Evidence, PatrolSnapshot


@dataclass(frozen=True)
class BeachProfile:
    beach_id: str
    latitude: float
    longitude: float


BEACHES = {
    # Synthetic operations identifier mapped to West Bay, Dorset for the demo.
    "west-bay-01": BeachProfile("west-bay-01", 50.7107, -2.7616),
}


class FixtureFeed:
    """Deterministic feed used for tests and reproducible judging demos."""

    def snapshot(self, beach_id: str) -> PatrolSnapshot:
        scenario = os.getenv("GROUNDPATROL_SCENARIO", "clear").strip().lower()
        now = datetime.now(timezone.utc)

        overrides: dict[str, object] = {}
        if scenario == "people_nearby":
            overrides["people_nearby"] = True
        elif scenario == "protected_habitat":
            overrides["protected_habitat"] = True
        elif scenario == "access_closed":
            overrides["access_open"] = False
        elif scenario == "high_wind":
            overrides["wind_kph"] = 52.0
        elif scenario == "low_visibility":
            overrides["visibility_m"] = 90
        elif scenario == "stale":
            now = now - timedelta(hours=2)
        elif scenario != "clear":
            raise ValueError(f"unknown GROUNDPATROL_SCENARIO: {scenario}")

        stamp = now.isoformat()
        values = {
            "beach_id": beach_id,
            "tide_state": "falling",
            "wind_kph": 18.0,
            "visibility_m": 1200,
            "access_open": True,
            "protected_habitat": False,
            "people_nearby": False,
            "debris_type": "mixed_plastic",
            "debris_mass_kg": 12.0,
        }
        values.update(overrides)

        return PatrolSnapshot(
            **values,
            evidence=(
                Evidence(
                    source="shore-camera-01",
                    observed_at=stamp,
                    claim="debris patch confirmed above strand line",
                    confidence=0.96,
                ),
                Evidence(
                    source=f"fixture-conditions:{scenario}",
                    observed_at=stamp,
                    claim="runtime operating conditions observed",
                    confidence=1.0,
                ),
            ),
        )


class OpenMeteoFeed:
    """Live-weather overlay with fixture operational facts.

    Access, habitat, people and debris observations stay explicit fixture inputs in v0;
    only weather is fetched live. This makes the source boundary visible instead of
    pretending every field came from a real sensor network.
    """

    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self.timeout_seconds = timeout_seconds
        self.fixture = FixtureFeed()

    def snapshot(self, beach_id: str) -> PatrolSnapshot:
        profile = BEACHES.get(beach_id)
        if profile is None:
            raise ValueError(f"no live profile configured for beach_id={beach_id}")

        base = self.fixture.snapshot(beach_id)
        query = urlencode(
            {
                "latitude": profile.latitude,
                "longitude": profile.longitude,
                "current": "wind_speed_10m,visibility",
                "wind_speed_unit": "kmh",
                "timezone": "UTC",
            }
        )
        url = f"https://api.open-meteo.com/v1/forecast?{query}"
        with urlopen(url, timeout=self.timeout_seconds) as response:  # nosec B310
            payload = json.load(response)

        current = payload.get("current") or {}
        wind = float(current["wind_speed_10m"])
        visibility = int(float(current["visibility"]))
        observed_at = str(current.get("time") or datetime.now(timezone.utc).isoformat())
        if observed_at.endswith("Z"):
            weather_stamp = observed_at
        elif "+" not in observed_at:
            weather_stamp = observed_at + "+00:00"
        else:
            weather_stamp = observed_at

        return PatrolSnapshot(
            beach_id=base.beach_id,
            tide_state=base.tide_state,
            wind_kph=wind,
            visibility_m=visibility,
            access_open=base.access_open,
            protected_habitat=base.protected_habitat,
            people_nearby=base.people_nearby,
            debris_type=base.debris_type,
            debris_mass_kg=base.debris_mass_kg,
            evidence=(
                base.evidence[0],
                Evidence(
                    source="open-meteo",
                    observed_at=weather_stamp,
                    claim=f"wind={wind:.1f}km/h visibility={visibility}m",
                    confidence=0.99,
                ),
                base.evidence[1],
            ),
        )


def get_feed():
    mode = os.getenv("GROUNDPATROL_FEED", "fixture").strip().lower()
    if mode == "fixture":
        return FixtureFeed()
    if mode == "live":
        return OpenMeteoFeed()
    raise ValueError(f"unknown GROUNDPATROL_FEED: {mode}")
