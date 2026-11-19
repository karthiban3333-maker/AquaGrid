"""Sentinel-2 access through the public Microsoft Planetary Computer STAC API.

The adapter returns scene metadata and processing parameters. Raster processing
is kept deterministic and can be enabled with rasterio in a deployment that
has the required assets available.
"""
import os
from typing import Any

import requests

from .common import ready, unavailable

STAC_URL = os.getenv("PLANETARY_COMPUTER_STAC_URL", "https://planetarycomputer.microsoft.com/api/stac/v1/search")


def fetch_sentinel(village: dict[str, Any]) -> dict[str, Any]:
    polygon = village.get("polygon")
    if not polygon:
        return unavailable("sentinel-2", "A village polygon is required for scene search")
    body: dict[str, Any] = {
        "collections": ["sentinel-2-l2a"],
        "intersects": {"type": "Polygon", "coordinates": [polygon]},
        "limit": 5,
        "query": {"eo:cloud_cover": {"lt": float(os.getenv("SENTINEL_MAX_CLOUD", "30"))}},
    }
    if village.get("start_date") and village.get("end_date"):
        body["datetime"] = f"{village['start_date']}/{village['end_date']}"
    try:
        response = requests.post(STAC_URL, json=body, timeout=20)
        response.raise_for_status()
        features = response.json().get("features", [])
        scenes = [
            {
                "id": item.get("id"),
                "datetime": item.get("properties", {}).get("datetime"),
                "cloudCover": item.get("properties", {}).get("eo:cloud_cover"),
                "assets": sorted(item.get("assets", {}).keys()),
            }
            for item in features
        ]
        return ready("sentinel-2", {"scenes": scenes, "indices": ["NDVI", "NDWI"], "processing": "L2A surface reflectance"})
    except Exception as exc:  # provider outage must become stale, not synthetic data
        return unavailable("sentinel-2", f"Planetary Computer request failed: {exc}")
