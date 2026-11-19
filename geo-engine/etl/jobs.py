from typing import Any

from .chirps import fetch_chirps
from .opentopography import fetch_dem
from .planetary_computer import fetch_sentinel


def refresh_village(village: dict[str, Any]) -> dict[str, Any]:
    """Refresh all Phase 1 sources for one village.

    The Node orchestration layer persists each result and applies last-good-value
    retention. Keeping this function stateless makes scheduled jobs repeatable.
    """
    return {
        "village_id": village["village_id"],
        "sentinel-2": fetch_sentinel(village),
        "chirps": fetch_chirps(village),
        "dem": fetch_dem(village),
    }
