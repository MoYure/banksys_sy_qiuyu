from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.banksys_sy_qiuyu.data import MODEL_PATH, TARGET_COLUMN
from src.banksys_sy_qiuyu.predict import load_model, predict, predict_proba
from src.banksys_sy_qiuyu.training import save_model, train_model

CATEGORICAL = ["job", "marital"]
NUMERIC = ["age", "duration"]
FEATURES = CATEGORICAL + NUMERIC


def _sample_frame(rows: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    return pd.DataFrame(
        {
            "id": range(rows),
            "job": rng.choice(["admin.", "blue-collar", "services"], size=rows),
            "marital": rng.choice(["married", "single", "divorced"], size=rows),
            "age": rng.integers(18, 90, size=rows),
            "duration": rng.integers(10, 3000, size=rows),
            TARGET_COLUMN: rng.choice(["yes", "no"], size=rows, p=[0.3, 0.7]),
        }
    )


@pytest.fixture()
def artifact(tmp_path):
    frame = _sample_frame()
    trained = train_model(frame)
    path = save_model(trained, tmp_path / "model.joblib")
    return load_model(path)


def test_load_model_returns_artifact(artifact):
    assert artifact is not None
    assert artifact["model"] is not None
    assert artifact["features"] == FEATURES


def test_load_model_missing_file_returns_none(tmp_path):
    assert load_model(tmp_path / "nope.joblib") is None


def test_load_model_corrupt_file_returns_none(tmp_path):
    path = tmp_path / "corrupt.joblib"
    path.write_text("not a joblib payload", encoding="utf-8")

    assert load_model(path) is None


def test_predict_matches_training_pipeline(artifact, tmp_path):
    frame = _sample_frame(10)
    x = frame[FEATURES]
    trained = train_model(_sample_frame())
    saved = save_model(trained, tmp_path / "model.joblib")

    loaded = load_model(saved)
    # AC4: predictions from the persisted pipeline equal the training-side ones.
    np.testing.assert_array_equal(loaded["model"].predict(x), trained["model"].predict(x))


def test_predict_proba_shape_and_range(artifact):
    frame = _sample_frame(10)
    proba = predict_proba(artifact, frame)

    assert proba.shape == (10, 2)
    np.testing.assert_allclose(proba.sum(axis=1), 1.0)
    assert (proba >= 0.0).all() and (proba <= 1.0).all()


def test_predict_returns_labels(artifact):
    frame = _sample_frame(10)
    labels = predict(artifact, frame)

    assert labels.shape == (10,)
    assert set(labels.tolist()).issubset({0, 1})


def test_predict_ignores_unknown_category(artifact):
    frame = _sample_frame(1)
    frame["job"] = "never-seen-job"

    proba = predict_proba(artifact, frame)

    assert proba.shape == (1, 2)


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="committed model not present")
def test_committed_model_loads_and_predicts():
    artifact = load_model()

    assert artifact is not None
    frame = pd.read_csv(MODEL_PATH.parents[1] / "data" / "train.csv", nrows=20)
    proba = predict_proba(artifact, frame)

    assert proba.shape == (20, 2)
