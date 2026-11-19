"""OpenTopography DEM metadata/download adapter."""
import os
from typing import Any

import requests

from .common import ready, unavailable


def fetch_dem(village: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("OPENTOPOGRAPHY_API_KEY")
    bounds = village.get("bounds")
    if not api_key or not bounds:
        missing = "OPENTOPOGRAPHY_API_KEY" if not api_key else "village bounds"
        return unavailable("dem", f"{missing} is required for DEM retrieval")
    url = os.getenv("OPENTOPOGRAPHY_URL", "https://portal.opentopography.org/API/globaldem")
    params = {"demtype": os.getenv("OPENTOPOGRAPHY_DEM", "SRTMGL1"), "outputFormat": "GTiff", "API_Key": api_key, **bounds}
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return ready("dem", {"contentType": response.headers.get("content-type"), "bytes": len(response.content), "terrain": ["elevation", "slope", "aspect"]}, provider="OpenTopography")
    except Exception as exc:
        return unavailable("dem", f"OpenTopography request failed: {exc}")
