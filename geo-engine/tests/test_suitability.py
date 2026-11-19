import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from hydro.suitability import rank_interventions


def test_suitability_ranks_and_flags_risk():
    result = rank_interventions([
        {"id": "good", "recharge_probability": 0.9, "slope": 0.4, "accessibility": 0.8, "land_ownership": 0.9, "contamination_risk": 0.9, "cost": 0.7},
        {"id": "risky", "recharge_probability": 0.5, "slope": 0.95, "accessibility": 0.2, "land_ownership": 0.2, "contamination_risk": 0.2, "cost": 0.2},
    ])
    assert result["sites"][0]["id"] == "good"
    assert result["sites"][1]["riskFlags"]
    assert result["modelVersion"].startswith("phase4-")
