"""SCS curve-number water balance for an indicative recharge raster."""
from typing import Any


def scs_recharge_raster(
    rainfall_mm: list[list[float]],
    curve_number: list[list[float]],
    evapotranspiration_mm: list[list[float]] | None = None,
) -> dict[str, Any]:
    if len(rainfall_mm) != len(curve_number) or any(len(a) != len(b) for a, b in zip(rainfall_mm, curve_number)):
        raise ValueError("rainfall and curve-number grids must have the same shape")
    recharge: list[list[float]] = []
    runoff: list[list[float]] = []
    for r, (rain_row, cn_row) in enumerate(zip(rainfall_mm, curve_number)):
        recharge_row: list[float] = []
        runoff_row: list[float] = []
        for c, (rain, cn_value) in enumerate(zip(rain_row, cn_row)):
            cn = min(100.0, max(1.0, float(cn_value)))
            storage = 25400.0 / cn - 254.0
            initial_abstraction = 0.2 * storage
            precipitation = max(0.0, float(rain))
            q = 0.0 if precipitation <= initial_abstraction else (precipitation - initial_abstraction) ** 2 / (precipitation + 0.8 * storage)
            et = max(0.0, float(evapotranspiration_mm[r][c])) if evapotranspiration_mm else 0.0
            runoff_row.append(round(q, 4))
            recharge_row.append(round(max(0.0, precipitation - q - et), 4))
        runoff.append(runoff_row)
        recharge.append(recharge_row)
    return {
        "recharge_potential_mm": recharge,
        "runoff_mm": runoff,
        "metadata": {
            "method": "SCS Curve Number: P - Q - ET",
            "initialAbstractionRatio": 0.2,
            "units": "mm per model period",
            "caveat": "Indicative raster; calibration and field validation required.",
        },
    }
