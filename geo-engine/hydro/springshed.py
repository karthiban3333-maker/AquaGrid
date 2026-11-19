"""Transparent DEM drainage and probable springshed delineation.

This lightweight implementation uses a priority-flood-style iterative
 depression fill, D8 steepest-descent routing, recursive flow accumulation,
and a configurable stream threshold. The returned catchment is a bounding
GeoJSON polygon around contributing DEM cells; production deployments should
replace it with a raster-to-vector polygonizer for exact boundaries.

A springshed is a probable contributing area, not proof of groundwater flow.
Confidence decreases for coarse cells and low-accuracy spring coordinates.
"""
from typing import Any

import numpy as np


def _fill_depressions(dem: np.ndarray) -> np.ndarray:
    filled = dem.astype(float).copy()
    for _ in range(max(filled.shape) * 2):
        changed = False
        for r in range(1, filled.shape[0] - 1):
            for c in range(1, filled.shape[1] - 1):
                neighbours = filled[r - 1:r + 2, c - 1:c + 2].copy().ravel()
                neighbours = np.delete(neighbours, 4)
                target = max(filled[r, c], float(np.min(neighbours)))
                if target > filled[r, c] + 1e-9:
                    filled[r, c] = target
                    changed = True
        if not changed:
            break
    return filled


def _d8_flow(filled: np.ndarray) -> np.ndarray:
    directions = np.full(filled.shape, -1, dtype=int)
    neighbours = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for r in range(1, filled.shape[0] - 1):
        for c in range(1, filled.shape[1] - 1):
            drops = [(filled[r, c] - filled[r + dr, c + dc], i) for i, (dr, dc) in enumerate(neighbours)]
            best_drop, best = max(drops, key=lambda pair: pair[0])
            if best_drop > 0:
                directions[r, c] = best
    return directions


def _accumulation(directions: np.ndarray) -> np.ndarray:
    result = np.ones(directions.shape, dtype=float)
    neighbours = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    memo: dict[tuple[int, int], float] = {}

    def visit(r: int, c: int, trail: set[tuple[int, int]]) -> float:
        key = (r, c)
        if key in memo:
            return memo[key]
        if key in trail:
            return 1.0
        total = 1.0
        for rr in range(1, directions.shape[0] - 1):
            for cc in range(1, directions.shape[1] - 1):
                direction = directions[rr, cc]
                if direction < 0:
                    continue
                dr, dc = neighbours[direction]
                if (rr + dr, cc + dc) == key:
                    total += visit(rr, cc, trail | {key})
        memo[key] = total
        return total

    for r in range(directions.shape[0]):
        for c in range(directions.shape[1]):
            result[r, c] = visit(r, c, set())
    return result


def _polygon_for_cells(cells: np.ndarray, cell_size_m: float) -> list[list[float]]:
    rows, cols = np.where(cells)
    if len(rows) == 0:
        return []
    min_r, max_r, min_c, max_c = int(rows.min()), int(rows.max()) + 1, int(cols.min()), int(cols.max()) + 1
    return [[min_c * cell_size_m, min_r * cell_size_m], [max_c * cell_size_m, min_r * cell_size_m], [max_c * cell_size_m, max_r * cell_size_m], [min_c * cell_size_m, max_r * cell_size_m], [min_c * cell_size_m, min_r * cell_size_m]]


def delineate_springshed(
    dem: list[list[float]],
    spring_row: int,
    spring_col: int,
    *,
    cell_size_m: float = 30.0,
    accumulation_threshold: float = 20.0,
    elevation_ceiling_m: float = 500.0,
    aquifer_class: str | None = None,
    gps_accuracy_m: float | None = None,
) -> dict[str, Any]:
    grid = np.asarray(dem, dtype=float)
    if grid.ndim != 2 or min(grid.shape) < 3:
        raise ValueError("DEM must be a 2D grid with at least 3 rows and columns")
    if not (0 <= spring_row < grid.shape[0] and 0 <= spring_col < grid.shape[1]):
        raise ValueError("spring coordinate is outside the DEM")
    filled = _fill_depressions(grid)
    directions = _d8_flow(filled)
    accumulation = _accumulation(directions)
    neighbours = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    contributing = np.zeros(grid.shape, dtype=bool)
    for r in range(grid.shape[0]):
        for c in range(grid.shape[1]):
            current = (r, c)
            seen: set[tuple[int, int]] = set()
            while current not in seen and 0 <= current[0] < grid.shape[0] and 0 <= current[1] < grid.shape[1]:
                seen.add(current)
                if current == (spring_row, spring_col):
                    if grid[r, c] <= grid[spring_row, spring_col] + elevation_ceiling_m:
                        contributing[r, c] = True
                    break
                direction = directions[current]
                if direction < 0:
                    break
                dr, dc = neighbours[direction]
                current = (current[0] + dr, current[1] + dc)
    stream_mask = accumulation >= accumulation_threshold
    stream_lines = []
    for r, c in zip(*np.where(stream_mask)):
        direction = directions[r, c]
        if direction >= 0:
            dr, dc = neighbours[direction]
            stream_lines.append({"type": "Feature", "properties": {"accumulation": float(accumulation[r, c])}, "geometry": {"type": "LineString", "coordinates": [[c * cell_size_m, r * cell_size_m], [(c + dc) * cell_size_m, (r + dr) * cell_size_m]]}})
    confidence = "high"
    if cell_size_m > 30 or (gps_accuracy_m is not None and gps_accuracy_m > 10):
        confidence = "low"
    elif cell_size_m > 10 or (gps_accuracy_m is not None and gps_accuracy_m > 5):
        confidence = "medium"
    if aquifer_class not in {None, "weathered", "fractured", "alluvial"}:
        confidence = "low"
    polygon = _polygon_for_cells(contributing, cell_size_m)
    area_ha = float(contributing.sum() * cell_size_m * cell_size_m / 10000)
    return {
        "catchment": {"type": "Feature", "properties": {"areaHa": round(area_ha, 4), "confidence": confidence, "aquiferClass": aquifer_class}, "geometry": {"type": "Polygon", "coordinates": [polygon]}},
        "streamNetwork": {"type": "FeatureCollection", "features": stream_lines},
        "flowAccumulation": accumulation.tolist(),
        "flowDirection": directions.tolist(),
        "metadata": {"method": "iterative depression fill + D8 routing + recursive accumulation", "cellSizeM": cell_size_m, "accumulationThreshold": accumulation_threshold, "elevationCeilingM": elevation_ceiling_m, "caveat": "Probable DEM contributing area; not a hydrogeological proof."},
    }
