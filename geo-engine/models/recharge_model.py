"""Explainable pilot recharge prediction.

This is a decision-support baseline trained on limited pilot points. It must not
be presented as measured accuracy or validated ground truth.
"""
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_val_score

FEATURES = ["slope", "lineament_density", "rainfall", "ndvi", "ndwi", "recharge", "rock_type", "proximity_to_contact"]
MODEL_VERSION = "phase3-random-forest-pilot-v0.1"


def generate_pseudo_absences(points: list[dict[str, Any]], count: int | None = None) -> list[dict[str, Any]]:
    """Create deterministic pseudo-absence samples by shifting coordinates.

    Pseudo-absence labels are modelling assumptions, not surveyed absence.
    """
    count = count or len(points)
    generated: list[dict[str, Any]] = []
    for index, point in enumerate(points[:count]):
        sample = dict(point)
        sample["lat"] = float(point.get("lat", 0)) + 0.01 + (index % 3) * 0.002
        sample["lng"] = float(point.get("lng", 0)) + 0.01 + (index % 2) * 0.002
        sample["label"] = 0
        generated.append(sample)
    return generated


def _matrix(samples: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([[float(sample.get(feature, 0.0)) if feature != "rock_type" else float(sample.get("rock_type_score", 0.0)) for feature in FEATURES] for sample in samples], dtype=float)


def _groups(samples: list[dict[str, Any]]) -> np.ndarray:
    # Spatial bins avoid random CV leakage between nearby points.
    return np.asarray([f"{float(s.get('lat', 0)):.2f}:{float(s.get('lng', 0)):.2f}" for s in samples])


def _top_shap(model: RandomForestClassifier, X: np.ndarray, feature_names: list[str]) -> tuple[list[dict[str, Any]], str]:
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        values = explainer.shap_values(X[:1])
        raw = values[1] if isinstance(values, list) else values
        row = np.asarray(raw)[0]
        ranked = sorted(({"feature": name, "contribution": round(float(value), 6)} for name, value in zip(feature_names, row)), key=lambda item: abs(item["contribution"]), reverse=True)
        return ranked[:5], "shap.TreeExplainer"
    except Exception as exc:
        return [], f"unavailable: {type(exc).__name__}"


def train_and_predict(samples: list[dict[str, Any]], prediction_grid: list[dict[str, Any]]) -> dict[str, Any]:
    if len(samples) < 4:
        raise ValueError("At least four pilot samples are required for a prediction")
    positives = [sample for sample in samples if int(sample.get("label", 1)) == 1]
    if not positives:
        raise ValueError("At least one spring presence point is required")
    labelled = samples + generate_pseudo_absences(positives, max(1, len(positives)))
    X = _matrix(labelled)
    y = np.asarray([int(sample.get("label", 1)) for sample in labelled])
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced", min_samples_leaf=1)
    model.fit(X, y)
    groups = _groups(labelled)
    unique_groups = np.unique(groups)
    validation: dict[str, Any] = {"method": "spatial GroupKFold", "status": "not_run", "scores": []}
    if len(unique_groups) >= 2:
        folds = min(5, len(unique_groups))
        scores = cross_val_score(model, X, y, cv=GroupKFold(n_splits=folds), groups=groups, scoring="balanced_accuracy")
        validation.update({"status": "computed", "folds": folds, "scores": [round(float(score), 4) for score in scores]})
    grid_probabilities = model.predict_proba(_matrix(prediction_grid))[:, 1].round(6).tolist()
    explanations, explanation_method = _top_shap(model, _matrix(prediction_grid), FEATURES)
    return {
        "modelVersion": MODEL_VERSION,
        "probability": grid_probabilities,
        "topFeatureContributions": explanations,
        "explanationMethod": explanation_method,
        "validation": validation,
        "training": {
            "presencePoints": len(positives),
            "pseudoAbsencePoints": len(labelled) - len(positives),
            "caveat": "Trained on limited pilot data and pseudo-absences; designed to improve as field data grows. No measured accuracy is claimed.",
        },
    }
