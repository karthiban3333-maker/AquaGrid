# DhaaraSathi: project guide and complete usage workflow

## What this project is

DhaaraSathi is a spring-shed planning and field-verification application for local facilitators, technical officers, administrators, and community users. It combines public environmental datasets with transparent hydrogeological calculations, explainable pilot modelling, intervention suitability screening, and field observations. The application is a **decision-support prototype**: it helps teams decide what to inspect and validate, but it does not claim that a satellite image proves underground recharge or that a model replaces hydrogeological expertise.

## What data is original and what is demo data

The dashboard now uses live provider-backed values for coordinate-based environmental evidence. Elevation, recent rainfall, soil moisture, and Sentinel-2 scene metadata are fetched from public services at runtime. The provider, scene ID, cloud cover, source URL, and fetch time are retained in the response and can be persisted in the `dataSources` table.

Some domain fields cannot be obtained from those datasets. Spring discharge in litres per minute, household dependence, community use, field water quality, maintenance status, and intervention impact require field or community records. The current UI shows clearly labelled demo placeholders for those unavailable fields, while keeping the live environmental values unchanged. Demo labels must never be interpreted as measurements.

The spring registry names, pilot IDs, and demo coordinate set in `client/src/pages/Home.tsx` are also prototype seed records until a verified spring inventory is supplied. Replace them with an official CSV/GeoJSON or field-verified registry before pilot deployment.

## End-to-end architecture

```text
Public data providers
  ├─ Open-Meteo: elevation, precipitation, recent rainfall, soil moisture
  ├─ Planetary Computer STAC: Sentinel-2 L2A scene metadata
  ├─ CHIRPS / Google Earth Engine: configurable rainfall history
  └─ OpenTopography: configurable DEM retrieval
          ↓
FastAPI geo-engine (geo-engine/)
  ├─ live evidence fetch
  ├─ terrain derivatives
  ├─ DEM drainage and probable springshed delineation
  ├─ mapped geology, lithology, and ESA WorldCover inputs
  ├─ SCS Curve Number recharge
  ├─ aquifer screening rules
  ├─ Random Forest pilot prediction + spatial validation + SHAP
  └─ intervention suitability and risk flags
          ↓
Node/tRPC orchestration (server/)
  ├─ source provenance and stale-last-good-value persistence
  ├─ assessments and recommendations
  └─ protected prediction and ranking routes
          ↓
React dashboard
  ├─ live environmental evidence card
  ├─ springshed/stream/priority-surface overlay contract
  ├─ explicit demo placeholders for unavailable field data
  └─ field observation and issue capture workflows
```

## How to run locally

### React and Node application

```bash
pnpm install --frozen-lockfile
pnpm dev
```

The app normally runs on port `3000`.

### Geo-engine

```bash
python3 -m pip install -r geo-engine/requirements.txt
cd geo-engine
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
docker compose up --build
```

The Compose file starts the Node app and FastAPI geo-engine. Provider credentials must be supplied through environment variables or a secret manager; never commit them to the repository.

## How to use the project

Open the React preview or local application. Choose a role, continue to location selection, select a pilot block, and open the Overview screen. Select a spring card. The **Live datasets** panel displays provider-backed elevation, recent rainfall, Sentinel-2 scene ID, cloud cover, fetch state, and provider metadata. If a provider is unavailable, the application must show unavailable/stale state rather than invent a number.

Use the Field Capture workflow to enter original observations. A facilitator can record observed time, discharge, water presence, ground condition, intervention status, notes, photo paths, and location accuracy. These records are separate from environmental evidence and are the correct source for field-only values.

Use the Registry to inspect spring records, the Action Plans view for transparent intervention ranking, and Monitoring for dated observations. Technical officers should review the input snapshot, model version, risk flags, and confidence before approving an intervention.

## Important API routes

| Route | Use |
|---|---|
| `GET /health` | Check the geo-engine |
| `POST /live-evidence` | Fetch live weather/elevation and Sentinel-2 metadata for latitude/longitude |
| `POST /etl/village/{id}/refresh` | Run configured Phase 1 source refreshes |
| `POST /hydro/terrain` | Calculate DEM derivatives |
| `POST /hydro/springshed` | Calculate D8 drainage, streams, and probable springshed GeoJSON |
| `POST /hydro/aquifer` | Run transparent aquifer screening rules |
| `POST /hydro/recharge` | Calculate SCS Curve Number recharge/runoff |
| `POST /predict-recharge` | Train the limited-pilot Random Forest and return probabilities/SHAP explanations |
| `POST /suitability/interventions` | Rank intervention sites and return risk flags |
| `POST /suitability/priority-surface` | Return a five-band GeoJSON suitability surface |
| `POST /etl/geology/geojson` | Ingest mapped geology/lithology GeoJSON |
| `GET /etl/geology/gsi-bhukosh` | Query optional configured GSI source |
| `POST /etl/lulc/worldcover` | Discover ESA WorldCover scenes and map classes |

## Credentials and provider configuration

Sentinel-2 scene discovery uses the public Microsoft Planetary Computer STAC endpoint. The current implementation retrieves scene metadata; signed raster-band processing is required before displaying NDVI or NDWI. ESA WorldCover discovery uses the same STAC service. Mapped structures from GeoJSON/shapefile uploads take precedence over DEM lineament proxies; absent sources remain unavailable and are never fabricated.

Open-Meteo is used for the live coordinate-based weather/elevation evidence route. CHIRPS historical rainfall requires `CHIRPS_EXPORT_URL` connected to a Google Earth Engine deployment. OpenTopography requires `OPENTOPOGRAPHY_API_KEY` and bounds. `GEO_ENGINE_URL` configures the Node server’s FastAPI target. Database persistence requires `DATABASE_URL`.

## Accuracy, safety, and validation rules

Never treat a scene ID or rainfall total as measured spring discharge. Never treat a model probability as a forecast accuracy claim. The Phase 3 model uses limited pilot points and deterministic pseudo-absences; spatial GroupKFold and SHAP explanations improve transparency but do not create ground truth. The Phase 4 suitability score is a weighted screening baseline, not an engineering design.

Before approving an intervention, verify spring location, discharge series, land access, contamination risk, slope stability, local geology, community consent, cost, existing conservation structures, and post-intervention monitoring. Keep the field-validation and uncertainty labels visible in every deployment. A springshed is a probable DEM contributing area, not proof of groundwater flow; confidence falls with coarse DEM resolution or inaccurate GPS.

## Testing

```bash
pnpm check
pnpm test
pnpm build
pytest -q geo-engine
```

The project’s current validation includes TypeScript checking, the existing Node test suite, Python ETL tests, terrain/recharge tests, model tests, and suitability tests.
