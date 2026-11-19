"""DhaaraSathi Phase 1 geospatial ETL service.

This service normalizes external environmental evidence. It is intentionally
provider-tolerant: credentials are optional, and missing providers return a
clear unavailable/stale response rather than fabricating measurements.
"""
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from etl.jobs import refresh_village
from etl.live_evidence import fetch_live_evidence
from hydro.aquifer import classify_aquifer
from hydro.recharge import scs_recharge_raster
from hydro.suitability import priority_surface, rank_interventions
from hydro.springshed import delineate_springshed
from etl.geology import ingest_geojson, fetch_gsi_bhukosh
from etl.lulc import fetch_worldcover
from hydro.terrain import terrain_derivatives
from models.recharge_model import train_and_predict

app = FastAPI(title="DhaaraSathi Geo Engine", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])


class VillageRequest(BaseModel):
    village_id: str = Field(min_length=1)
    polygon: list[list[float]] | None = None
    centroid: dict[str, float] | None = None
    start_date: str | None = None
    end_date: str | None = None


class RasterRequest(BaseModel):
    dem: list[list[float]] | None = None
    rainfall_mm: list[list[float]] | None = None
    curve_number: list[list[float]] | None = None
    evapotranspiration_mm: list[list[float]] | None = None
    slope_degrees: list[list[float]] | None = None
    lineament_density: list[list[float]] | None = None
    lulc: list[list[str]] | None = None
    cell_size_m: float = Field(default=30.0, gt=0)


class PredictionRequest(BaseModel):
    training_samples: list[dict[str, Any]] = Field(min_length=4)
    prediction_grid: list[dict[str, Any]] = Field(min_length=1)


class SuitabilityRequest(BaseModel):
    sites: list[dict[str, Any]] = Field(min_length=1)
    existing_structures: list[dict[str, Any]] = []


class PrioritySurfaceRequest(BaseModel):
    cells: list[dict[str, Any]] = Field(min_length=1)
    existing_structures: list[dict[str, Any]] = []


class GeoJSONRequest(BaseModel):
    payload: dict[str, Any]
    source: str = "uploaded-geojson"


class LulcRequest(BaseModel):
    bbox: list[float] = Field(min_length=4, max_length=4)


class LiveEvidenceRequest(BaseModel):
    lat: float
    lng: float


class SpringshedRequest(BaseModel):
    dem: list[list[float]] = Field(min_length=3)
    spring_row: int = Field(ge=0)
    spring_col: int = Field(ge=0)
    cell_size_m: float = Field(default=30.0, gt=0)
    accumulation_threshold: float = Field(default=20.0, gt=0)
    elevation_ceiling_m: float = Field(default=500.0, gt=0)
    aquifer_class: str | None = None
    gps_accuracy_m: float | None = Field(default=None, ge=0)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "geo-engine", "time": datetime.now(timezone.utc).isoformat()}


@app.post("/etl/village/{village_id}/refresh")
def refresh(village_id: str, request: VillageRequest | None = None) -> dict[str, Any]:
    payload = request.model_dump() if request else {"village_id": village_id}
    payload["village_id"] = village_id
    return refresh_village(payload)


@app.get("/etl/village/{village_id}/status")
def status(village_id: str) -> dict[str, Any]:
    # Phase 1 keeps cache metadata in the caller's database. This endpoint is
    # deliberately explicit until a shared artifact store is configured.
    return {"village_id": village_id, "status": "managed_by_orchestrator", "sources": []}


@app.post("/etl/village/{village_id}/{source}")
def refresh_source(village_id: str, source: str, request: VillageRequest | None = None) -> dict[str, Any]:
    if source not in {"sentinel-2", "chirps", "dem"}:
        raise HTTPException(status_code=404, detail="Unsupported ETL source")
    payload = request.model_dump() if request else {"village_id": village_id}
    payload["village_id"] = village_id
    result = refresh_village(payload)
    return {"village_id": village_id, "source": source, "result": result.get(source)}


@app.post("/hydro/terrain")
def hydro_terrain(request: RasterRequest) -> dict[str, Any]:
    if request.dem is None:
        raise HTTPException(status_code=422, detail="dem is required")
    return terrain_derivatives(request.dem, request.cell_size_m)


@app.post("/hydro/aquifer")
def hydro_aquifer(request: RasterRequest) -> dict[str, Any]:
    if request.slope_degrees is None or request.lineament_density is None:
        raise HTTPException(status_code=422, detail="slope_degrees and lineament_density are required")
    return classify_aquifer(request.slope_degrees, request.lineament_density, request.lulc)


@app.post("/hydro/recharge")
def hydro_recharge(request: RasterRequest) -> dict[str, Any]:
    if request.rainfall_mm is None or request.curve_number is None:
        raise HTTPException(status_code=422, detail="rainfall_mm and curve_number are required")
    return scs_recharge_raster(request.rainfall_mm, request.curve_number, request.evapotranspiration_mm)


@app.post("/predict-recharge")
def predict_recharge(request: PredictionRequest) -> dict[str, Any]:
    return train_and_predict(request.training_samples, request.prediction_grid)


@app.post("/suitability/interventions")
def suitability_interventions(request: SuitabilityRequest) -> dict[str, Any]:
    return rank_interventions(request.sites, request.existing_structures)


@app.post("/live-evidence")
def live_evidence(request: LiveEvidenceRequest) -> dict[str, Any]:
    return fetch_live_evidence(request.lat, request.lng)


@app.post("/hydro/springshed")
def hydro_springshed(request: SpringshedRequest) -> dict[str, Any]:
    return delineate_springshed(**request.model_dump())


@app.post("/suitability/priority-surface")
def suitability_priority_surface(request: PrioritySurfaceRequest) -> dict[str, Any]:
    return priority_surface(request.cells, request.existing_structures)


@app.post("/etl/geology/geojson")
def geology_geojson(request: GeoJSONRequest) -> dict[str, Any]:
    return ingest_geojson(request.payload, source=request.source)


@app.get("/etl/geology/gsi-bhukosh")
def geology_gsi_bhukosh(minx: float, miny: float, maxx: float, maxy: float) -> dict[str, Any]:
    return fetch_gsi_bhukosh({"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy})


@app.post("/etl/lulc/worldcover")
def lulc_worldcover(request: LulcRequest) -> dict[str, Any]:
    return fetch_worldcover(request.bbox)
