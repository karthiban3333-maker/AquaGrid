import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from etl.geology import ingest_geojson
from etl.lulc import reclassify_worldcover
from hydro.springshed import delineate_springshed
from hydro.suitability import priority_surface, rank_interventions


def test_springshed_returns_geojson_and_confidence():
    dem = [[10, 9, 8, 7, 6], [11, 10, 9, 8, 7], [12, 11, 10, 9, 8], [13, 12, 11, 10, 9], [14, 13, 12, 11, 10]]
    result = delineate_springshed(dem, 0, 4, cell_size_m=30, accumulation_threshold=2, gps_accuracy_m=3)
    assert result["catchment"]["geometry"]["type"] == "Polygon"
    assert result["catchment"]["properties"]["confidence"] in {"medium", "high"}
    assert result["streamNetwork"]["type"] == "FeatureCollection"


def test_geology_uses_mapped_structures_path():
    result = ingest_geojson({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"structureType": "fault", "strike": 90, "confidence": "high"}, "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}}]})
    assert result["lineamentPath"] == "mapped-geological-structures"
    assert result["structures"][0]["structureType"] == "fault"


def test_lulc_reclassification_is_explicit():
    assert reclassify_worldcover(10) == "forest"
    assert reclassify_worldcover(80) == "water"
    assert reclassify_worldcover(999) == "unknown"


def test_existing_functioning_structure_is_penalised():
    result = rank_interventions([{"id": "a", "recharge_probability": 0.8, "slope": 0.4, "accessibility": 0.8, "land_ownership": 0.8, "contamination_risk": 0.8, "cost": 0.8, "distanceM": 20}], [{"condition": "functioning", "distanceM": 20}])
    assert "duplicate_functioning_structure_penalty" in result["sites"][0]["riskFlags"]


def test_priority_surface_is_geojson():
    result = priority_surface([{"x": 0, "y": 0, "cellSize": 30, "recharge_probability": 0.9, "slope": 0.4, "accessibility": 0.8, "land_ownership": 0.8, "contamination_risk": 0.8, "cost": 0.8}])
    assert result["type"] == "FeatureCollection"
    assert result["features"][0]["properties"]["band"] in {"very-high", "high", "medium", "low", "very-low"}
