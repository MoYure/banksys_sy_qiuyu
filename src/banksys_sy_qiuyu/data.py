from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
TARGET_COLUMN = "subscribe"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "model.joblib"


@dataclass(frozen=True)
class DatasetInfo:
    name: str
    path: Path
    rows: int
    columns: int
    has_target: bool


def available_datasets(data_dir: Path = DATA_DIR) -> list[DatasetInfo]:
    """Return CSV datasets available to the app."""
    datasets: list[DatasetInfo] = []
    for path in sorted(data_dir.glob("*.csv")):
        frame = pd.read_csv(path, nrows=5)
        row_count = sum(1 for _ in path.open("r", encoding="utf-8")) - 1
        datasets.append(
            DatasetInfo(
                name=path.name,
                path=path,
                rows=max(row_count, 0),
                columns=len(frame.columns),
                has_target=TARGET_COLUMN in frame.columns,
            )
        )
    return datasets


def load_dataset(name: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Load a named CSV dataset from the project data directory."""
    path = (data_dir / name).resolve()
    root = data_dir.resolve()
    if not path.is_relative_to(root):
        msg = f"Dataset path escapes data directory: {name}"
        raise ValueError(msg)
    if not path.exists():
        msg = f"Dataset does not exist: {name}"
        raise FileNotFoundError(msg)
    return pd.read_csv(path)


def summarize_dataset(frame: pd.DataFrame) -> dict[str, int]:
    """Return compact dataset health metrics for display and tests."""
    return {
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "missing_values": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
    }


def categorical_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if frame[column].dtype == "object"]


def numeric_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if pd.api.types.is_numeric_dtype(frame[column])]


def feature_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if column not in {"id", TARGET_COLUMN}]


def require_target(frame: pd.DataFrame) -> None:
    if TARGET_COLUMN not in frame.columns:
        msg = f"Dataset must contain target column '{TARGET_COLUMN}'."
        raise ValueError(msg)
