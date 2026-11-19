"""Geological structure and lithology ingestion with provenance."""
import json
import os
from pathlib import Path
from typing import Any

import requests

from .common import now_iso, unavailable


def ingest_geojson(payload: dict[str, Any], *, source: str = "uploaded-geojson") -> dict[str, Any]:
    if payload.get("type") not in {"FeatureCollection", "Feature"}:
        return unavailable("geology", "Expected GeoJSON Feature or FeatureCollection")
    features = payload.get("features", [payload] if payload.get("type") == "Feature" else [])
    structures, lithology = [], []
    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry")
        if not geometry:
            continue
        if properties.get("rockType") or properties.get("formation"):
            lithology.append({"rockType": properties.get("rockType", "unknown"), "formationName": properties.get("formation"), "geometry": geometry, "source": source})
        elif properties.get("structureType") in {"fault", "fracture", "joint", "contact", "bedding"}:
            structures.append({"structureType": properties["structureType"], "strike": properties.get("strike"), "dip": properties.get("dip"), "dipDirection": properties.get("dipDirection"), "geometry": geometry, "source": source, "confidence": properties.get("confidence", "low"), "observedDate": properties.get("observedDate")})
    return {"source": source, "status": "ready", "fetchedAt": now_iso(), "structures": structures, "lithology": lithology, "lineamentPath": "mapped-geological-structures" if structures else "dem-proxy-fallback", "confidence": "medium" if structures else "low"}


def ingest_file(path: str) -> dict[str, Any]:
    file_path = Path(path)
    if file_path.suffix.lower() in {".json", ".geojson"}:
        try:
            return ingest_geojson(json.loads(file_path.read_text()), source=str(file_path))
        except Exception as exc:
            return unavailable("geology", f"GeoJSON parse failed: {exc}")
    if file_path.suffix.lower() in {".shp", ".zip"}:
        try:
            import fiona
            features = {"type": "FeatureCollection", "features": [dict(feature) for feature in fiona.open(path)]}
            return ingest_geojson(features, source=str(file_path))
        except Exception as exc:
            return unavailable("geology", f"Shapefile ingestion unavailable: {exc}")
    return unavailable("geology", "Only GeoJSON or shapefile uploads are supported")


def fetch_gsi_bhukosh(bounds: dict[str, float]) -> dict[str, Any]:
    endpoint = os.getenv("GSI_BHUKOSH_URL")
    if not endpoint:
        return unavailable("gsi-bhukosh", "GSI_BHUKOSH_URL is not configured")
    try:
        response = requests.get(endpoint, params=bounds, timeout=30)
        response.raise_for_status()
        return ingest_geojson(response.json(), source="GSI Bhukosh")
    except Exception as exc:
        return unavailable("gsi-bhukosh", f"GSI Bhukosh request failed: {exc}")
