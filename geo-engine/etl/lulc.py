"""Land-use/land-cover ingestion with explicit provider provenance."""
import os
from typing import Any

import requests

from .common import now_iso, unavailable

WORLD_COVER_STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"

ESA_CLASS_TO_TOKEN = {
    10: "forest", 20: "forest", 30: "grassland", 40: "cropland", 50: "built-up",
    60: "bare", 70: "snow", 80: "water", 90: "wetland", 95: "mangrove", 100: "moss",
}


def reclassify_worldcover(class_code: int) -> str:
    return ESA_CLASS_TO_TOKEN.get(int(class_code), "unknown")


def fetch_worldcover(bbox: list[float]) -> dict[str, Any]:
    endpoint = os.getenv("LULC_STAC_URL", WORLD_COVER_STAC)
    try:
        response = requests.post(endpoint, json={"collections": ["esa-worldcover"], "bbox": bbox, "limit": 5}, timeout=30)
        response.raise_for_status()
        features = response.json().get("features", [])
        if not features:
            return unavailable("esa-worldcover", "No WorldCover scenes returned for the requested bounds")
        return {"source": "ESA WorldCover", "status": "ready", "fetchedAt": now_iso(), "scenes": [{"id": item.get("id"), "assets": sorted(item.get("assets", {}).keys())} for item in features], "vocabulary": sorted(set(ESA_CLASS_TO_TOKEN.values())), "reclassification": ESA_CLASS_TO_TOKEN}
    except Exception as exc:
        return unavailable("esa-worldcover", f"WorldCover request failed: {exc}")
