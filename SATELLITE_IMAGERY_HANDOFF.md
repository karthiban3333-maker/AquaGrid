# Satellite imagery layer

DhaaraSathi now includes a satellite-ready map experience. In the map controls, choose **Satellite** to use the project’s provided Google Maps proxy with the satellite basemap. Spring markers are added from the selected area and remain selectable. If the proxy is unavailable, the terrain view remains the safe fallback.

The prototype also ships sample evidence for all 8 demo springs. Each spring includes a scene ID, acquisition date, cloud cover, NDVI, NDWI and a recharge-confidence label. These sample values are synthetic and are shown as supporting evidence only; they do not prove groundwater flow or a recharge boundary.

For production, the recommended pipeline is:

1. Search Sentinel-2 Level-2A scenes for the selected village/block geometry and a date range.
2. Filter scenes by cloud cover and create a cloud-masked composite.
3. Compute NDVI from `(B08 - B04) / (B08 + B04)` and NDWI from `(B03 - B08) / (B03 + B08)`.
4. Publish a clipped raster/COG or tile layer through Sentinel Hub, Microsoft Planetary Computer, or an approved state GIS service. Keep the service token server-side.
5. Store scene ID, acquisition date, processing date, cloud cover, spatial resolution, source URL, band recipe and confidence in `dataSources`.
6. Display vegetation and surface-water change as evidence alongside field readings. Never label the satellite layer as proof of underground recharge.
7. Keep the precomputed recharge polygon separate from the satellite layer and require technical validation before an intervention can be approved.

The current UI intentionally uses a sample Sentinel-2-style record: `S2A_20260914_KANDHAMAL`, 14 Sep 2026, 8% cloud cover, 10 m sample resolution. Replace these records with real scene metadata after connecting the chosen imagery provider.

## Sample fields

| Field | Example | Meaning |
|---|---|---|
| `satelliteScene` | `S2A_20260914_KANDHAMAL` | Provider scene or composite identifier |
| `sceneDate` | `14 Sep 2026` | Acquisition date |
| `cloudCover` | `8` | Scene cloud percentage |
| `ndvi` | `0.68` | Vegetation index, supporting land-cover evidence |
| `ndwi` | `0.31` | Surface-water/moisture indicator |
| `rechargeConfidence` | `High` | Planning confidence after combining terrain, imagery and field evidence |

## Guardrail

> Satellite imagery can show vegetation, surface moisture, land-cover change and visible water features. It cannot directly prove the underground path of water or guarantee an increase in spring discharge. Field measurements and expert validation remain mandatory.
