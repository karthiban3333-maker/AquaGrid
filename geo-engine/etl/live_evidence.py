"""Fetch real public evidence for a point without fabricating field measurements."""
from datetime import datetime, timezone
from typing import Any

import requests

from .common import now_iso, unavailable

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_live_evidence(lat: float, lng: float) -> dict[str, Any]:
    weather: dict[str, Any]
    scenes: list[dict[str, Any]] = []
    try:
        params = {
            "latitude": lat, "longitude": lng,
            "current": "precipitation,soil_moisture_0_to_1cm",
            "daily": "rain_sum",
            "past_days": 7, "forecast_days": 1,
            "timezone": "Asia/Kolkata",
        }
        payload = requests.get(OPEN_METEO_URL, params=params, timeout=20).json()
        weather = {
            "provider": "Open-Meteo / ERA5-derived weather",
            "elevationM": payload.get("elevation"),
            "currentPrecipitationMm": payload.get("current", {}).get("precipitation"),
            "soilMoistureM3M3": payload.get("current", {}).get("soil_moisture_0_to_1cm"),
            "dailyRainMm": payload.get("daily", {}).get("rain_sum", []),
            "sourceUrl": OPEN_METEO_URL,
        }
    except Exception as exc:
        weather = unavailable("open-meteo", f"Weather request failed: {exc}")

    try:
        body = {
            "collections": ["sentinel-2-l2a"],
            "bbox": [lng - 0.08, lat - 0.08, lng + 0.08, lat + 0.08],
            "limit": 5,
            "query": {"eo:cloud_cover": {"lt": 40}},
        }
        response = requests.post(STAC_URL, json=body, timeout=30)
        response.raise_for_status()
        for item in response.json().get("features", []):
            props = item.get("properties", {})
            scenes.append({
                "id": item.get("id"),
                "date": props.get("datetime"),
                "cloudCover": props.get("eo:cloud_cover"),
                "provider": "Microsoft Planetary Computer / Sentinel-2 L2A",
                "sourceUrl": f"https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/{item.get('id')}",
                "indices": "Not computed: raster bands require signed asset processing",
            })
    except Exception as exc:
        scenes = [{"status": "unavailable", "error": f"Sentinel-2 request failed: {exc}"}]

    return {
        "status": "ready" if weather.get("provider") and scenes else "partial",
        "fetchedAt": now_iso(),
        "coordinates": {"lat": lat, "lng": lng},
        "weather": weather,
        "sentinel2": {"scenes": scenes, "fieldMeasurements": "not available from satellite"},
        "uncertainty": "Live environmental evidence only; spring flow, household dependence, and intervention impact require field/community records.",
    }
