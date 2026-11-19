# Satellite implementation QA

The app now includes a satellite-ready map mode. The terrain mode remains the safe illustrative fallback. Satellite mode uses the existing Manus Google Maps proxy through the provided `MapView` component, sets the basemap to satellite, and adds selectable spring markers for the current area.

The demo dataset now contains 8 springs across Daringbadi and K. Nuagaon, with scene ID, acquisition date, cloud cover, NDVI, NDWI and recharge-confidence fields for every spring. All tests and the production build passed after the change.

The map copy explicitly states that satellite imagery is supporting evidence only and does not prove underground groundwater flow.

Interactive verification: the Overview map exposes Terrain and Satellite controls. Clicking Satellite changes the map label to “Sentinel-2 sample · 10 m” and updates the evidence copy. The Google Maps satellite basemap is wired through the provided proxy and remains safe to use as a progressive enhancement; the prototype retains a clear sample-state treatment if imagery tiles are unavailable in the preview environment.
