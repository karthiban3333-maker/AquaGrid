import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

import pytest

from hydro.aquifer import classify_aquifer
from hydro.recharge import scs_recharge_raster
from hydro.terrain import terrain_derivatives


def test_terrain_derivatives_return_same_shape():
    result = terrain_derivatives([[100, 101, 102], [100, 101, 102], [100, 101, 102]])
    assert len(result["slope_degrees"]) == 3
    assert len(result["slope_degrees"][0]) == 3
    assert result["metadata"]["cellSizeM"] == 30.0


def test_aquifer_classifier_is_explicit():
    result = classify_aquifer([[10, 40]], [[0.8, 0.1]], [["forest", "alluvial valley"]])
    assert result["class"] == [["fractured", "alluvial"]]
    assert result["thresholds"]["fracturedLineamentDensity"] == 0.5


def test_recharge_never_exceeds_rainfall_and_subtracts_et():
    result = scs_recharge_raster([[100]], [[50]], [[10]])
    assert 0 <= result["recharge_potential_mm"][0][0] <= 90
    assert result["runoff_mm"][0][0] > 0


def test_recharge_rejects_mismatched_grids():
    with pytest.raises(ValueError):
        scs_recharge_raster([[100]], [[50, 60]])
