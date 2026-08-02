from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.banksys_sy_qiuyu.data import (
    MODEL_PATH,
    TARGET_COLUMN,
    available_datasets,
    categorical_columns,
    load_dataset,
    numeric_columns,
    summarize_dataset,
)
from src.banksys_sy_qiuyu.predict import load_model, predict_proba

st.set_page_config(
    page_title="Bank Marketing Analytics",
    layout="wide",
)

SERIES_COLORS = [
    "#2a78d6",
    "#1baf7a",
    "#eda100",
    "#008300",
    "#4a3aa7",
    "#e34948",
    "#e87ba4",
    "#eb6834",
]


@st.cache_data(show_spinner=False)
def _load_dataset(name: str) -> pd.DataFrame:
    return load_dataset(name)


@st.cache_resource(show_spinner=False)
def _load_model() -> dict | None:
    """Load the persisted training artifact (pipeline + metadata), if present."""
    return load_model(MODEL_PATH)


def _dataset_selector() -> tuple[str, pd.DataFrame]:
    datasets = available_datasets()
    if not datasets:
        st.error("No CSV datasets found in data/.")
        st.stop()

    options = [dataset.name for dataset in datasets]
    default_index = next(
        (index for index, dataset in enumerate(datasets) if dataset.has_target),
        0,
    )
    selected_name = st.sidebar.selectbox("Dataset", options, index=default_index)

    with st.sidebar.expander("Available files", expanded=False):
        st.dataframe(
            pd.DataFrame(
                {
                    "file": [dataset.name for dataset in datasets],
                    "rows": [dataset.rows for dataset in datasets],
                    "columns": [dataset.columns for dataset in datasets],
                    "has_target": [dataset.has_target for dataset in datasets],
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

    return selected_name, _load_dataset(selected_name)


def _render_kpis(frame: pd.DataFrame) -> None:
    summary = summarize_dataset(frame)
    cols = st.columns(4)
    cols[0].metric("Rows", f"{summary['rows']:,}")
    cols[1].metric("Columns", f"{summary['columns']:,}")
    cols[2].metric("Missing values", f"{summary['missing_values']:,}")
    cols[3].metric("Duplicate rows", f"{summary['duplicate_rows']:,}")


def _filtered_frame(frame: pd.DataFrame) -> pd.DataFrame:
    filtered = frame.copy()
    filter_columns = [column for column in categorical_columns(frame) if column != TARGET_COLUMN][
        :4
    ]
    if not filter_columns:
        return filtered

    with st.expander("Filters", expanded=True):
        filter_widgets = st.columns(len(filter_columns))
        for widget, column in zip(filter_widgets, filter_columns, strict=True):
            values = sorted(frame[column].dropna().unique().tolist())
            selected = widget.multiselect(column, values, default=[])
            if selected:
                filtered = filtered[filtered[column].isin(selected)]
    return filtered


def render_analysis_page(frame: pd.DataFrame) -> None:
    st.subheader("Data analysis")
    _render_kpis(frame)
    filtered = _filtered_frame(frame)

    st.caption(f"Showing {len(filtered):,} of {len(frame):,} rows after filters.")
    has_target = TARGET_COLUMN in filtered.columns
    if not has_target:
        st.warning("This dataset does not contain subscribe, so target comparisons are disabled.")

    left, right = st.columns(2)
    with left:
        if has_target:
            target_counts = (
                filtered[TARGET_COLUMN]
                .value_counts()
                .rename_axis(TARGET_COLUMN)
                .reset_index(name="count")
            )
            fig = px.bar(
                target_counts,
                x=TARGET_COLUMN,
                y="count",
                color=TARGET_COLUMN,
                color_discrete_sequence=SERIES_COLORS,
                text="count",
                title="Subscription outcome",
            )
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(showlegend=False, yaxis_title="Rows", xaxis_title="Outcome")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select a labeled dataset to see subscription outcomes.")

    with right:
        cats = [column for column in categorical_columns(filtered) if column != TARGET_COLUMN]
        if cats:
            selected_cat = st.selectbox("Categorical field", cats)
            if has_target:
                chart_data = (
                    filtered.groupby([selected_cat, TARGET_COLUMN]).size().reset_index(name="count")
                )
            else:
                chart_data = (
                    filtered[selected_cat]
                    .value_counts()
                    .rename_axis(selected_cat)
                    .reset_index(name="count")
                )
            fig = px.bar(
                chart_data,
                x=selected_cat,
                y="count",
                color=TARGET_COLUMN if has_target else None,
                barmode="group",
                color_discrete_sequence=SERIES_COLORS,
                title=f"{selected_cat} distribution",
            )
            fig.update_layout(yaxis_title="Rows", xaxis_title=selected_cat)
            st.plotly_chart(fig, use_container_width=True)

    nums = [column for column in numeric_columns(filtered) if column != "id"]
    if nums:
        selected_num = st.selectbox("Numeric field", nums)
        fig = px.histogram(
            filtered,
            x=selected_num,
            color=TARGET_COLUMN if has_target else None,
            nbins=30,
            color_discrete_sequence=SERIES_COLORS,
            title=f"{selected_num} distribution",
        )
        fig.update_layout(yaxis_title="Rows", xaxis_title=selected_num, bargap=0.08)
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(filtered.head(200), use_container_width=True, hide_index=True)


def render_prediction_page() -> None:
    st.subheader("Online prediction")
    artifact = _load_model()
    if artifact is None:
        st.warning(
            "No trained model artifact is available yet. Run the offline training module first."
        )
        return

    st.caption(f"Primary metric: {artifact['primary_metric']}")
    inputs: dict[str, object] = {}
    cols = st.columns(2)
    for index, column in enumerate(artifact["features"]):
        target_col = cols[index % 2]
        if column in artifact["categories"]:
            options = artifact["categories"][column]
            inputs[column] = target_col.selectbox(column, options)
        else:
            default = artifact["numeric_defaults"].get(column, 0.0)
            inputs[column] = target_col.number_input(column, value=float(default))

    if st.button("Predict", type="primary"):
        try:
            sample = pd.DataFrame([inputs])[artifact["features"]]
            prob_yes = float(predict_proba(artifact, sample)[0, 1])
        except Exception as exc:  # noqa: BLE001 - surface a friendly message, not a stack trace
            st.error(f"Prediction failed: {exc}")
            return
        if prob_yes >= 0.5:
            st.success(f"预测:会认购(概率 {prob_yes:.1%})")
        else:
            st.warning(f"预测:不会认购(概率 {1 - prob_yes:.1%})")


def main() -> None:
    st.title("Bank Marketing Analytics")
    dataset_name, frame = _dataset_selector()
    st.sidebar.caption(f"Loaded `{dataset_name}`")

    analysis_tab, prediction_tab = st.tabs(["Analysis", "Prediction"])
    with analysis_tab:
        render_analysis_page(frame)
    with prediction_tab:
        render_prediction_page()


if __name__ == "__main__":
    main()
