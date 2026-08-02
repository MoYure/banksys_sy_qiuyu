from __future__ import annotations

import pandas as pd
import pytest

from src.banksys_sy_qiuyu.data import (
    TARGET_COLUMN,
    available_datasets,
    feature_columns,
    load_dataset,
    require_target,
    summarize_dataset,
)


def test_available_datasets_reports_csv_files():
    datasets = available_datasets()

    names = {dataset.name for dataset in datasets}

    assert {"train.csv", "test.csv"}.issubset(names)


def test_train_dataset_contains_subscription_target():
    frame = load_dataset("train.csv")
    require_target(frame)

    assert TARGET_COLUMN in frame.columns
    assert set(frame[TARGET_COLUMN].unique()).issubset({"yes", "no"})


def test_test_dataset_target_status_is_explicit():
    frame = load_dataset("test.csv")

    with pytest.raises(ValueError, match=TARGET_COLUMN):
        require_target(frame)


def test_summarize_dataset_counts_shape_and_quality_metrics():
    frame = pd.DataFrame({"a": [1, 1, None], "b": ["x", "x", "y"]})

    summary = summarize_dataset(frame)

    assert summary == {
        "rows": 3,
        "columns": 2,
        "missing_values": 1,
        "duplicate_rows": 1,
    }


def test_feature_columns_excludes_id_and_target():
    frame = pd.DataFrame({"id": [1], "age": [30], TARGET_COLUMN: ["yes"]})

    assert feature_columns(frame) == ["age"]
