"""Transparent intervention suitability, risk, and priority-surface analysis."""
from typing import Any

CRITERIA_WEIGHTS = {"recharge_probability": 0.30, "slope": 0.15, "accessibility": 0.15, "land_ownership": 0.15, "contamination_risk": 0.10, "cost": 0.15}


def _structure_adjustment(site: dict[str, Any], existing_structures: list[dict[str, Any]]) -> tuple[float, list[str]]:
    adjustment, flags = 0.0, []
    for structure in existing_structures:
        distance = float(structure.get("distanceM", 999999))
        functioning = str(structure.get("condition", "")).lower() in {"good", "functioning", "verified"}
        if distance <= float(structure.get("influenceRadiusM", 100)):
            flags.append("existing_structure_influence_zone")
            if functioning:
                adjustment -= 0.20
                flags.append("duplicate_functioning_structure_penalty")
    return adjustment, sorted(set(flags))


def _band(score: float) -> str:
    return "very-high" if score >= 0.8 else "high" if score >= 0.6 else "medium" if score >= 0.4 else "low" if score >= 0.2 else "very-low"


def rank_interventions(sites: list[dict[str, Any]], existing_structures: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    existing_structures = existing_structures or []
    results = []
    for site in sites:
        score = sum(CRITERIA_WEIGHTS[key] * float(site.get(key, 0.0)) for key in CRITERIA_WEIGHTS)
        adjustment, structure_flags = _structure_adjustment(site, existing_structures)
        score = max(0.0, min(1.0, score + adjustment))
        risk_flags = list(structure_flags)
        if float(site.get("slope", 0)) < 0.15: risk_flags.append("low_slope_or_drainage_uncertainty")
        if float(site.get("slope", 0)) > 0.75: risk_flags.append("steep_slope_landslide_screen_required")
        if float(site.get("land_ownership", 0)) < 0.5: risk_flags.append("land_access_or_ownership_unconfirmed")
        if float(site.get("contamination_risk", 0)) < 0.5: risk_flags.append("contamination_screen_required")
        intervention = "spring-shed protection" if score >= 0.70 else "recharge pit" if score >= 0.50 else "check dam or monitoring"
        results.append({**site, "score": round(score, 6), "priorityBand": _band(score), "interventionType": intervention, "riskFlags": sorted(set(risk_flags)), "confidence": "medium" if not risk_flags else "low", "reasons": [f"{key} contributes {CRITERIA_WEIGHTS[key]:.0%} weight" for key in CRITERIA_WEIGHTS]})
    results.sort(key=lambda item: item["score"], reverse=True)
    return {"modelVersion": "phase4-ahp-baseline-v0.2", "criteriaWeights": CRITERIA_WEIGHTS, "sites": results, "caveat": "Indicative suitability ranking; technical, ownership, contamination, and field validation required."}


def priority_surface(cells: list[dict[str, Any]], existing_structures: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    ranked = rank_interventions(cells, existing_structures)
    features = []
    for cell in ranked["sites"]:
        geometry = cell.get("geometry")
        if not geometry:
            x, y, size = float(cell.get("x", 0)), float(cell.get("y", 0)), float(cell.get("cellSize", 30))
            geometry = {"type": "Polygon", "coordinates": [[[x, y], [x + size, y], [x + size, y + size], [x, y + size], [x, y]]]}
        features.append({"type": "Feature", "properties": {"band": cell["priorityBand"], "score": cell["score"], "criteria": {key: cell.get(key, 0) for key in CRITERIA_WEIGHTS}, "confidence": cell["confidence"]}, "geometry": geometry})
    return {"type": "FeatureCollection", "features": features, "modelVersion": ranked["modelVersion"], "caveat": "Priority surface is an indicative screening layer, not an engineering design."}
