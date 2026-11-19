# Geotagged map QA

Live browser verification confirmed that Satellite mode now renders a real Google satellite basemap through the shared proxy. Spring markers are Google map markers with coordinate-based positions, so they move with map zoom/pan instead of remaining fixed in the card. The satellite map exposes a Street View control button, and Google’s native Pegman/Street View controls are also present.

Build, typecheck and tests passed after the update.

Interactive verification: clicking a spring marker changed the selected detail card from Kundapani Upper Spring to Sikata Community Spring and the map zoomed from the area view to a close local view. The Street View action is visible for the selected spring and is wired to the selected coordinates through the Google Maps panorama API; imagery availability depends on Google coverage at the demo coordinate.
