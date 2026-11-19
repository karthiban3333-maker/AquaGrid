# DhaaraSathi geo-engine

The FastAPI service in `geo-engine/` provides a staged, explainable geospatial decision-support pipeline. It is designed for pilot planning and field validation; it is not validated ground truth and does not claim measured model accuracy.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `/health` | Service health |
| `/etl/village/{id}/refresh` | Sentinel-2, CHIRPS, and DEM refresh |
| `/hydro/terrain` | DEM slope, aspect, curvature, and lineament proxy |
| `/hydro/aquifer` | Rules-first weathered/fractured/alluvial classification |
| `/hydro/recharge` | SCS curve-number runoff/recharge raster |
| `/hydro/springshed` | DEM depression fill, D8 flow, accumulation, streams, and probable catchment GeoJSON |
| `/predict-recharge` | Random Forest probability with spatial validation and SHAP explanations |
| `/suitability/interventions` | Weighted AHP-style intervention ranking and risk flags |
| `/suitability/priority-surface` | Five-band gridded priority GeoJSON surface |
| `/etl/geology/geojson` | Ingest mapped faults, fractures, joints, contacts, bedding, and lithology |
| `/etl/geology/gsi-bhukosh` | Optional configured GSI Bhukosh ingestion |
| `/etl/lulc/worldcover` | ESA WorldCover scene discovery and vocabulary mapping |

## Provenance and credentials

Sentinel-2 scene discovery uses Microsoft Planetary Computer STAC. Historical CHIRPS rainfall requires a configured Google Earth Engine export endpoint (`CHIRPS_EXPORT_URL`). DEM retrieval uses OpenTopography and requires `OPENTOPOGRAPHY_API_KEY` plus village bounds. ESA WorldCover scene discovery uses the Planetary Computer STAC endpoint; Bhuvan/GSI endpoints are optional configuration. Credentials are server-side only.

ETL failures never create synthetic environmental values. The server persists a source response in `dataSources`; failed refreshes are marked stale and retain the last successful payload when available.

## Modelling assumptions

Terrain derivatives use the supplied DEM cell size. The lineament-density value is a curvature-edge proxy and must be replaced or validated against mapped faults, fractures, joints, strike, and dip. The aquifer classifier uses explicit slope, lineament, and LULC thresholds. Recharge uses the SCS Curve Number equation with an initial-abstraction ratio of 0.2 and subtracts supplied evapotranspiration.

The springshed method performs iterative depression filling, D8 steepest-descent routing, recursive flow accumulation, and stream extraction at a configurable threshold. It returns a probable DEM contributing area, constrained by an elevation ceiling and optional aquifer label. Confidence degrades for coarse DEM cells and low-accuracy GPS points. Exact hydrogeological boundaries require a validated DEM and field/geological evidence.

Mapped geological structures take precedence over the DEM curvature proxy when supplied. Uploaded GeoJSON/shapefile records preserve structure type, strike, dip, dip direction, geometry, source, confidence, and observed date. Lithology preserves rock type, formation, geometry, and source. When no mapped structures exist, the API exposes `dem-proxy-fallback` and lower confidence rather than presenting the proxy as a mapped fault or fracture.

ESA WorldCover classes are reclassified into the aquifer classifier vocabulary. Existing functioning conservation structures within their influence radius reduce suitability and add a duplicate/influence risk flag. The priority surface converts ranked cells into five bands: very-low, low, medium, high, and very-high.

The Phase 3 Random Forest is trained on limited pilot presence points and deterministic pseudo-absences. It uses spatial GroupKFold when enough geographic groups exist. SHAP TreeExplainer outputs are returned when the SHAP dependency is available. No measured accuracy is claimed. More field-confirmed observations should be used before any operational decision.

Phase 4 uses a transparent weighted multi-criteria baseline. It flags steep slopes, uncertain land access, low-slope/drainage uncertainty, and contamination-screen requirements. All recommendations remain pending technical and field validation.

## Run locally

```bash
pip install -r geo-engine/requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000
```

The multi-service development layout is described in `docker-compose.yml`. Provider secrets should be supplied through environment variables or a managed secret store, never committed to the repository.

The React `MapView` loader now uses the direct Google Maps JavaScript URL and `VITE_GOOGLE_MAPS_API_KEY`; the old forge map proxy is no longer used. The custom satellite map continues to use ArcGIS imagery for its no-key preview mode.
