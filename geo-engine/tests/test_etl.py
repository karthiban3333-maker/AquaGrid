import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from api import health
from etl.chirps import fetch_chirps
from etl.jobs import refresh_village
from etl.planetary_computer import fetch_sentinel


def test_health_is_explicit():
    assert health()["status"] == "ok"


def test_sentinel_requires_polygon():
    result = fetch_sentinel({"village_id": "demo"})
    assert result["status"] == "unavailable"
    assert result["stale"] is True


def test_chirps_does_not_fabricate_without_provider(monkeypatch):
    monkeypatch.delenv("CHIRPS_EXPORT_URL", raising=False)
    result = fetch_chirps({"village_id": "demo"})
    assert result["status"] == "unavailable"
    assert result["payload"] is None


def test_refresh_returns_all_sources(monkeypatch):
    monkeypatch.delenv("CHIRPS_EXPORT_URL", raising=False)
    monkeypatch.delenv("OPENTOPOGRAPHY_API_KEY", raising=False)
    result = refresh_village({"village_id": "demo"})
    assert set(result) == {"village_id", "sentinel-2", "chirps", "dem"}
