import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from models.recharge_model import generate_pseudo_absences, train_and_predict


def samples():
    return [
        {"lat": 19.90, "lng": 84.10, "label": 1, "slope": 10, "lineament_density": 0.8, "rainfall": 1000, "ndvi": 0.7, "ndwi": 0.3, "recharge": 80},
        {"lat": 19.92, "lng": 84.12, "label": 1, "slope": 12, "lineament_density": 0.7, "rainfall": 950, "ndvi": 0.6, "ndwi": 0.2, "recharge": 70},
        {"lat": 19.94, "lng": 84.14, "label": 1, "slope": 8, "lineament_density": 0.9, "rainfall": 1100, "ndvi": 0.8, "ndwi": 0.4, "recharge": 90},
        {"lat": 19.96, "lng": 84.16, "label": 1, "slope": 15, "lineament_density": 0.6, "rainfall": 900, "ndvi": 0.5, "ndwi": 0.2, "recharge": 60},
    ]


def test_pseudo_absences_are_deterministic():
    generated = generate_pseudo_absences(samples(), 2)
    assert len(generated) == 2
    assert all(point["label"] == 0 for point in generated)


def test_prediction_returns_probability_and_caveat():
    result = train_and_predict(samples(), samples()[:2])
    assert len(result["probability"]) == 2
    assert all(0 <= value <= 1 for value in result["probability"])
    assert result["modelVersion"].startswith("phase3-")
    assert "limited pilot data" in result["training"]["caveat"]
    assert result["validation"]["method"] == "spatial GroupKFold"
