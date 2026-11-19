from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def unavailable(source: str, reason: str, *, last_good: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return an explicit stale result; never replace missing data with fake values."""
    return {
        "source": source,
        "status": "stale" if last_good else "unavailable",
        "stale": True,
        "fetchedAt": now_iso(),
        "error": reason,
        "usingLastGoodValue": bool(last_good),
        "payload": last_good.get("payload") if last_good else None,
    }


def ready(source: str, payload: dict[str, Any], **metadata: Any) -> dict[str, Any]:
    return {
        "source": source,
        "status": "ready",
        "stale": False,
        "fetchedAt": now_iso(),
        "payload": payload,
        **metadata,
    }
