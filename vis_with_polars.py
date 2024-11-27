from decimal import Decimal
import polars as pl
import streamlit as st
import plotly.express as px
import pandas as pd
import time
from streamlit_sortables import sort_items
from group_by_filters import filter_map

COUNT_COLUMN = "count"
SEPARATOR = " — "


def is_in_pandas(df):
    if isinstance(df, pl.DataFrame):
        return df.to_pandas()
    elif isinstance(df, pd.DataFrame):
        return df
    else:
        raise TypeError("Input must be either a Pandas or Polars DataFrame.")


def plot_result(df, chart_title=None, x_description_string=None):
    result = is_in_pandas(df)
    fig = px.bar(
        result,
        x=x_description_string,
        y="count",
        color=x_description_string,
        title=chart_title,
    )
    fig.update_layout(
        xaxis_title=x_description_string,
        yaxis_title="Count",
        barmode="relative",
        bargap=0.2,
        height=800,
    )
    st.session_state["plot"] = fig
    st.plotly_chart(fig)


"""def apply_binning_to_decimal_p_value_columns(df, max_bins):

    decimal_columns = [col for col in df.columns if isinstance(df[col].iloc[0], Decimal)]
    if not decimal_columns or max_bins <= 0:
        return df

    for col in decimal_columns:
        df[col] = df[col].round(decimals=2)
        min_value = df[f"{col}"].min()
        max_value = df[f"{col}"].max()
        if min_value == max_value:
            continue

            
        bin_width = (max_value - min_value) / max_bins
        bin_edges = [round(min_value + bin_width * i, 2) for i in range(max_bins + 1)]
        df[f"{col}"] = pd.cut(df[f"{col}"],
                              bins=bin_edges,
                              labels=[f"range {bin_edges[i]}-{bin_edges[i + 1]}" for i in
                                                 range(len(bin_edges) - 1)],
                              include_lowest=True,
                              duplicates='drop'
                              )
    return df
"""


def apply_binning_to_decimal(df, max_bins):
    decimal_columns = [col for col in df.columns if isinstance(df[col].iloc[0], Decimal)]
    if not decimal_columns or max_bins <= 0:
        return df

    for col in decimal_columns:
        df[col] = df[col].round(decimals=2)
        min_value = df[f"{col}"].min()
        max_value = df[f"{col}"].max()
        if min_value == max_value:
            continue

        bin_width = (max_value - min_value) / max_bins
        bin_edges = [round(min_value + bin_width * i, 2) for i in range(max_bins + 1)]
        df[f"{col}"] = pd.cut(df[f"{col}"],
                              bins=bin_edges,
                              labels=[f"range {bin_edges[i]}-{bin_edges[i + 1]}" for i in
                                      range(len(bin_edges) - 1)],
                              include_lowest=True,
                              duplicates='drop'
                              )
    return df


def apply_time_slicing(df, time_slice=None):
    """dynamically slices the df columns of type datetime based on chosen by user time slice: hour, month or year"""

    if time_slice is None:
        return df

    for col in df.columns:
        if df[col].dtype == pl.Datetime:
            time_slice_func = getattr(pl.col(col).dt, time_slice, None)
            if time_slice_func:
                df = df.with_columns(
                    time_slice_func().alias(col)
                )
            else:
                st.warning(f"Invalid time slicing option: {time_slice} for column {col}")
    return df


def cast_decimals_to_float_for_grouping(df):
    """
    Convert Decimal columns to float for grouping/sorting (otherwise for unbinned data it throws `arg_sort_multiple` operation not supported for dtype `decimal[*,0].
    """
    decimal_columns = [col for col in df.columns if df.schema[col] == pl.Decimal]
    for col in decimal_columns:
        df = df.with_columns(pl.col(col).cast(pl.Float64).alias(col))
    return df


def plot_result_polars(df, top_n=20, time_slice=None):
    start_time = time.time()

    df = pl.from_pandas(df)
    df = cast_decimals_to_float_for_grouping(df)
    df = apply_time_slicing(df, time_slice=time_slice)

    group_columns = [col for col in df.columns if col != COUNT_COLUMN]

    sorted_group_columns = sort_items(group_columns)

    result = df.group_by(sorted_group_columns).agg([
        pl.col(COUNT_COLUMN).sum()
    ])

    grouped_columns = [pl.col(col).cast(str) for col in result.columns if col != COUNT_COLUMN]
    grouped_columns_as_str = [expr.meta.output_name() for expr in grouped_columns]
    new_column_name = SEPARATOR.join(grouped_columns_as_str)

    result = result.with_columns(
        pl.concat_str(grouped_columns_as_str, separator=SEPARATOR).alias(new_column_name)
    ).top_k(top_n, by=[pl.col(col) for col in sorted_group_columns]).sort(by=sorted_group_columns)


    mapped_descriptions = [filter_map.get(col, col) for col in grouped_columns_as_str]
    mapped_descriptions_string = SEPARATOR.join(mapped_descriptions)

    chart_title = f"Top {top_n} Count groups by {mapped_descriptions_string}"

    plotting_start_time = time.time()

    plot_result(result, chart_title, new_column_name)


    plotting_end_time = time.time()
    elapsed_plotting_time = plotting_end_time - plotting_start_time

    st.info(f"️ Total plotting time: {elapsed_plotting_time:.2f} seconds ")

    with st.expander("View Table", expanded=False):
        st.write(result.head(top_n))

    elapsed_time = time.time() - start_time
    st.info(f" Total execution time: {elapsed_time:.2f} seconds.")
