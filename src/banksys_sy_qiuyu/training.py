from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.banksys_sy_qiuyu.data import (
    MODEL_PATH,
    TARGET_COLUMN,
    categorical_columns,
    feature_columns,
    load_dataset,
    numeric_columns,
    require_target,
)

RANDOM_SEED = 42
DEFAULT_TEST_SIZE = 0.2


def build_pipeline(
    categorical_cols: Sequence[str],
    numeric_cols: Sequence[str],
    *,
    seed: int = RANDOM_SEED,
) -> Pipeline:
    """Build the preprocessor + classifier pipeline (unfitted).

    The full pipeline is persisted to the model artifact so prediction always
    reuses the exact same preprocessing as training (AC2/AC4).
    """
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(categorical_cols),
            ),
            ("num", StandardScaler(), list(numeric_cols)),
        ]
    )
    classifier = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed)
    return Pipeline([("preprocessor", preprocessor), ("classifier", classifier)])


def _feature_split(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Split feature columns by dtype, excluding id and the target column."""
    features = feature_columns(frame)
    cat_cols = [column for column in categorical_columns(frame) if column in features]
    num_cols = [column for column in numeric_columns(frame) if column in features]
    return cat_cols, num_cols


def train_model(
    frame: pd.DataFrame,
    *,
    test_size: float = DEFAULT_TEST_SIZE,
    seed: int = RANDOM_SEED,
) -> dict:
    """Validate target, split, fit, evaluate and assemble the model artifact (AC1)."""
    require_target(frame)
    if frame[TARGET_COLUMN].isna().any():
        msg = f"Target column '{TARGET_COLUMN}' contains missing values."
        raise ValueError(msg)

    cat_cols, num_cols = _feature_split(frame)
    pipeline = build_pipeline(cat_cols, num_cols, seed=seed)
    features = cat_cols + num_cols
    x = frame[features]
    y = (frame[TARGET_COLUMN] == "yes").astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=seed, stratify=y
    )
    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)
    y_prob = pipeline.predict_proba(x_test)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
    }

    return {
        "model": pipeline,
        "features": features,
        "categorical_features": cat_cols,
        "categories": {
            column: sorted(frame[column].dropna().unique().tolist()) for column in cat_cols
        },
        "numeric_features": num_cols,
        "numeric_defaults": {column: float(frame[column].median()) for column in num_cols},
        "metrics": metrics,
        "primary_metric": "roc_auc",
        "seed": seed,
        "trained_at": datetime.now(UTC).isoformat(),
    }


def save_model(artifact: dict, path: Path = MODEL_PATH) -> Path:
    """Persist the artifact dict (pipeline + metadata) with joblib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, path)
    return path


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the bank subscription classifier.")
    parser.add_argument("--data", default="train.csv", help="labeled CSV name in data/")
    parser.add_argument("--output", default=str(MODEL_PATH))
    parser.add_argument("--test-size", type=float, default=DEFAULT_TEST_SIZE)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    frame = load_dataset(args.data)
    artifact = train_model(frame, test_size=args.test_size, seed=args.seed)
    path = save_model(artifact, Path(args.output))

    print(
        f"[train] rows={len(frame)} features={len(artifact['features'])} "
        f"primary_metric={artifact['primary_metric']}"
    )
    print("[train] " + " ".join(f"{key}={value:.4f}" for key, value in artifact["metrics"].items()))
    print(f"[train] saved={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
