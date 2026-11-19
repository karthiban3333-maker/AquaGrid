"""Scheduled refresh entry point.

Deploy this command from cron, a container scheduler, or a managed job runner.
It intentionally receives village JSON rather than embedding project data.
"""
import json
import os
import sys
from pathlib import Path

from etl.jobs import refresh_village


def main() -> int:
    config_path = Path(os.getenv("GEO_ENGINE_VILLAGES_FILE", "villages.json"))
    if not config_path.exists():
        print(f"No village config at {config_path}; set GEO_ENGINE_VILLAGES_FILE", file=sys.stderr)
        return 2
    villages = json.loads(config_path.read_text())
    results = [refresh_village(village) for village in villages]
    print(json.dumps(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
