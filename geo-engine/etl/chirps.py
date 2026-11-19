"""CHIRPS rainfall adapter.

Google Earth Engine credentials are deployment-specific. This adapter exposes
that dependency clearly and supports a configured export endpoint, while never
inventing rainfall values when Earth Engine is unavailable.
"""
import os
from typing import Any

import requests

from .common import ready, unavailable


def fetch_chirps(village: dict[str, Any]) -> dict[str, Any]:
    endpoint = os.getenv("CHIRPS_EXPORT_URL")
    if not endpoint:
        return unavailable("chirps", "CHIRPS_EXPORT_URL is not configured; connect Google Earth Engine for historical rainfall")
    try:
        response = requests.post(endpoint, json={"village": village}, timeout=30)
        response.raise_for_status()
        return ready("chirps", response.json(), provider="Google Earth Engine CHIRPS")
    except Exception as exc:
        return unavailable("chirps", f"CHIRPS request failed: {exc}")
