"""Terrain derivatives used by the Phase 2 transparent baseline.

The lineament-density output is a reproducible DEM-derived proxy based on
second-derivative edges. It is not a substitute for mapped faults/fractures;
field/geological validation remains required.
"""
from typing import Any

import numpy as np


def terrain_derivatives(dem: list[list[float]], cell_size_m: float = 30.0) -> dict[str, Any]:
    elevation = np.asarray(dem, dtype=float)
    if elevation.ndim != 2 or min(elevation.shape) < 2:
        raise ValueError("DEM must be a 2D grid with at least 2 rows and columns")
    gy, gx = np.gradient(elevation, cell_size_m, cell_size_m)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    aspect = (np.degrees(np.arctan2(-gx, gy)) + 360.0) % 360.0
    curvature_x = np.gradient(gx, cell_size_m, axis=1)
    curvature_y = np.gradient(gy, cell_size_m, axis=0)
    curvature = curvature_x + curvature_y
    # Local edge intensity is used only as a lineament-density indicator.
    edge = np.abs(curvature)
    threshold = float(np.percentile(edge, 75))
    lineament_density = (edge >= threshold).astype(float)
    return {
        "elevation_m": elevation.tolist(),
        "slope_degrees": slope.tolist(),
        "aspect_degrees": aspect.tolist(),
        "curvature": curvature.tolist(),
        "lineament_density_proxy": lineament_density.tolist(),
        "metadata": {
            "cellSizeM": cell_size_m,
            "lineamentMethod": "DEM curvature edge proxy; mapped geological structures required for validation",
        },
    }
