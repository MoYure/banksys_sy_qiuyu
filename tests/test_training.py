from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.banksys_sy_qiuyu.data import TARGET_COLUMN
from src.banksys_sy_qiuyu.training import (
    RANDOM_SEED,
    build_pipeline,
    main,
    save_model,
    train_model,
)

CATEGORICAL = ["job", "marital"]
NUMERIC = ["age", "duration"]


def _sample_frame(rows: int = 60) -> pd.DataFrame:
    """Small synthetic frame so tests never depend on the real dataset."""
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


def test_build_pipeline_structure():
    frame = _sample_frame()
    pipeline = build_pipeline(CATEGORICAL, NUMERIC)
    pipeline.fit(frame[CATEGORICAL + NUMERIC], (frame[TARGET_COLUMN] == "yes").astype(int))

    assert isinstance(pipeline, Pipeline)
    assert list(pipeline.named_steps) == ["preprocessor", "classifier"]
    assert isinstance(pipeline["classifier"], LogisticRegression)

    preprocessor = pipeline["preprocessor"]
    assert isinstance(preprocessor, ColumnTransformer)
    encoder = preprocessor.named_transformers_["cat"]
    scaler = preprocessor.named_transformers_["num"]
    assert isinstance(encoder, OneHotEncoder)
    assert encoder.handle_unknown == "ignore"
    assert encoder.sparse_output is False
    assert isinstance(scaler, StandardScaler)


def test_build_pipeline_handles_unknown_category():
    pipeline = build_pipeline(CATEGORICAL, NUMERIC)
    frame = _sample_frame()
    pipeline.fit(frame[CATEGORICAL + NUMERIC], (frame[TARGET_COLUMN] == "yes").astype(int))

    known = frame.iloc[[0]][CATEGORICAL + NUMERIC]
    unknown = known.copy()
    unknown["job"] = "never-seen-job"

    # AC2: predicting a category unseen in training must not raise.
    pipeline.predict(unknown)


def test_train_model_returns_metrics_and_metadata():
    frame = _sample_frame()
    artifact = train_model(frame)

    for key in (
        "model",
        "features",
        "categorical_features",
        "categories",
        "numeric_features",
        "numeric_defaults",
        "metrics",
        "primary_metric",
    ):
        assert key in artifact

    assert artifact["features"] == CATEGORICAL + NUMERIC
    assert artifact["categories"]["job"] == ["admin.", "blue-collar", "services"]
    assert artifact["primary_metric"] == "roc_auc"
    for value in artifact["metrics"].values():
        assert np.isfinite(value)
        assert 0.0 <= value <= 1.0


def test_train_model_reproducible_with_fixed_seed():
    frame = _sample_frame()

    first = train_model(frame, seed=RANDOM_SEED)
    second = train_model(frame, seed=RANDOM_SEED)

    x = frame[first["features"]]
    proba_first = first["model"].predict_proba(x)
    proba_second = second["model"].predict_proba(x)
    # AC5: fixed seed must give bit-identical predictions.
    np.testing.assert_array_equal(proba_first, proba_second)


def test_train_model_missing_target_raises():
    frame = _sample_frame().drop(columns=[TARGET_COLUMN])

    with pytest.raises(ValueError, match=TARGET_COLUMN):
        train_model(frame)


def test_train_model_target_with_missing_values_raises():
    frame = _sample_frame()
    frame.loc[0, TARGET_COLUMN] = None

    with pytest.raises(ValueError, match="missing values"):
        train_model(frame)


def test_save_model_roundtrip(tmp_path):
    artifact = train_model(_sample_frame())
    path = save_model(artifact, tmp_path / "model.joblib")

    import joblib

    loaded = joblib.load(path)
    assert loaded["features"] == artifact["features"]
    assert loaded["metrics"] == artifact["metrics"]


def test_main_cli_end_to_end(tmp_path):
    output = tmp_path / "model.joblib"

    status = main(["--data", "train.csv", "--output", str(output), "--seed", "42"])

    assert status == 0
    assert output.exists()

    import joblib

    artifact = joblib.load(output)
    for key in ("metrics", "primary_metric", "features"):
        assert key in artifact
