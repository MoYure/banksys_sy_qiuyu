from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.banksys_sy_qiuyu.data import MODEL_PATH


def _validate_artifact(artifact: object) -> bool:
    """Return True when the loaded object is a usable model artifact dict."""
    if not isinstance(artifact, dict):
        return False
    model = artifact.get("model")
    features = artifact.get("features")
    return callable(getattr(model, "predict_proba", None)) and isinstance(features, list)


def load_model(path: Path = MODEL_PATH) -> dict | None:
    """Load the persisted artifact; return None when missing or corrupt."""
    if not path.exists():
        return None
    try:
        artifact = joblib.load(path)
    except Exception:
        return None
    if not _validate_artifact(artifact):
        return None
    return artifact


def predict_proba(artifact: dict, frame: pd.DataFrame) -> np.ndarray:
    """Return (n, 2) class probabilities in artifact['model'] class order."""
    return artifact["model"].predict_proba(frame[artifact["features"]])


def predict(artifact: dict, frame: pd.DataFrame) -> np.ndarray:
    """Return predicted class labels for each row."""
    return artifact["model"].predict(frame[artifact["features"]])
