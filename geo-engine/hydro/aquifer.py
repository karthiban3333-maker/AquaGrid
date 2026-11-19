"""Rules-first aquifer classification; thresholds are explicit and inspectable."""
from typing import Any


def classify_aquifer(
    slope_degrees: list[list[float]],
    lineament_density: list[list[float]],
    lulc: list[list[str]] | None = None,
) -> dict[str, Any]:
    if len(slope_degrees) != len(lineament_density) or any(len(a) != len(b) for a, b in zip(slope_degrees, lineament_density)):
        raise ValueError("slope and lineament grids must have the same shape")
    classes: list[list[str]] = []
    confidence: list[list[str]] = []
    for row_index, (slope_row, line_row) in enumerate(zip(slope_degrees, lineament_density)):
        class_row: list[str] = []
        confidence_row: list[str] = []
        for col_index, (slope, lineament) in enumerate(zip(slope_row, line_row)):
            land = (lulc[row_index][col_index].lower() if lulc else "unknown")
            if any(token in land for token in ("alluvial", "floodplain", "valley")):
                label, certainty = "alluvial", "medium"
            elif float(lineament) >= 0.5 and float(slope) <= 35:
                label, certainty = "fractured", "medium"
            elif float(slope) <= 25:
                label, certainty = "weathered", "low" if land == "unknown" else "medium"
            else:
                label, certainty = "fractured", "low"
            class_row.append(label)
            confidence_row.append(certainty)
        classes.append(class_row)
        confidence.append(confidence_row)
    return {
        "class": classes,
        "confidence": confidence,
        "thresholds": {
            "fracturedLineamentDensity": 0.5,
            "fracturedMaxSlopeDegrees": 35,
            "weatheredMaxSlopeDegrees": 25,
            "alluvialLulcTokens": ["alluvial", "floodplain", "valley"],
        },
        "metadata": "Rules-first screening model; not validated ground truth.",
    }
