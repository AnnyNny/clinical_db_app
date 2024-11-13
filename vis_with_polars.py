from decimal import Decimal

import polars as pl
import streamlit as st
import plotly.express as px
import polars.selectors as cs
import pandas as pd
from streamlit_sortables import sort_items

from group_by_filters import filter_map


def reorder_columns(columns):
    print("inside reorder_columns")
    print(st.session_state["reordered_columns"])
    if "reordered_columns" not in st.session_state:
        st.write("DEbugging..,inside reorder_columns if not session_state")
        st.session_state["reordered_columns"] = [col for col in columns if col not in ["count", "combined"]]

    st.write("Drag and drop to reorder columns for grouping:")
    reordered_columns = sort_items(st.session_state["reordered_columns"], key="sortable-columns-key")
    if reordered_columns != st.session_state["reordered_columns"]:
        st.session_state["reordered_columns"] = reordered_columns
    st.write("Reordered columns:", st.session_state["reordered_columns"])

    return st.session_state["reordered_columns"]


def plot_result(result, chart_title=None):
    fig = px.bar(
        result,
        x="combined",
        y="count",
        color="combined",
        title=chart_title,
    )
    st.session_state["plot"] = fig
    st.plotly_chart(fig)



def plot_result_with_binning_polars(data, top_n=10, max_bins=3, time_slice=None):
    df = data
    st.write(df.schema)
    st.write(df, "\n Total rows:", len(df), "type of df:", df.dtypes)
    out = df.select(cs.numeric() - cs.by_name("count"))
    #st.write("out numeric columns:", out.columns, "type", out.dtypes)
    #possible_value_columns = ["p1_value", "p2_value", "p3_value", "p4_value"]
    new_df = df
    for col in new_df.columns:
        if new_df[f"{col}"].dtype == pl.Datetime:
            time_slice_func = getattr(pl.col(col).dt, time_slice)
            new_df = new_df.with_columns(
                (
                    time_slice_func().alias(f"{col}_{time_slice}")
                    #time_slice_func().alias(f"{col}")
                )
            )
            new_df = new_df.drop(f"{col}")
        else:
            st.write(f"{col} is not a datetime column")
    st.write(f"new_df after time slicing by {time_slice}", new_df, new_df.shape, new_df.dtypes)
    group_columns = [col for col in new_df.columns if col != "count"]

    new_df = new_df.group_by(group_columns).agg([
        pl.col("count").sum().alias("count"),
    ]).sort("count", descending=True)

    st.write(f"new_df after time slicing by {time_slice} and aggregating by count", new_df, new_df.shape)
    new_df = new_df.to_pandas()

    # binning for p1-p4 values of vital parameters
    decimal_columns = [col for col in new_df.columns if isinstance(new_df[col].iloc[0], Decimal)]
    #st.write("after to_pandas() conversion data type is ", new_df.dtypes, new_df.dtypes)
    for col in decimal_columns:
        new_df[col] = new_df[col].round(decimals=2)
        min_value = new_df[f"{col}"].min()
        max_value = new_df[f"{col}"].max()
        bin_width = (max_value - min_value) / max_bins
        bin_edges = [round(min_value + bin_width * i,2) for i in range(max_bins + 1)]
        new_df[f"{col}_binned"] = pd.cut(new_df[f"{col}"], bins=bin_edges,labels=[f"{bin_edges[i]}-{bin_edges[i + 1]}" for i in range(len(bin_edges) - 1)], include_lowest=True)
        """new_df[f"{col}"] = pd.cut(new_df[f"{col}"],
                                         bins=bin_edges,
                                         labels=[f"{bin_edges[i]}-{bin_edges[i + 1]}" for i in
                                                 range(len(bin_edges) - 1)],
                                         include_lowest=True)"""
        new_df = new_df.drop(columns=[col])

    #st.write("###new_df after binning p1,p2,p3,p4 values", new_df, len(new_df))
    new_df = pl.from_pandas(new_df)
    group_columns = [col for col in new_df.columns if col != "count"]
    st.write("###debugging: show group columns", group_columns)
    result = new_df.group_by(group_columns).agg([
        pl.col("count").sum()
    ]).sort("count", descending=True)

    st.write("###grouped data", result.shape, result)
    if top_n is not None:
        result = result.head(top_n)
        st.write(f"###Grouped data after limiting to top {top_n} groups", result.shape, result)
    grouped_columns_as_str = [pl.col(col).cast(str) for col in result.columns if col != "count"]
    result = result.with_columns(
        pl.concat_str(grouped_columns_as_str, separator=", ").alias("combined")
    ).sort("count", descending=True)
    char_cols = [col for col in result.columns if col != "count" and col != "combined"]
    mapped_descriptions = [filter_map.get(col, col) for col in char_cols]
    chart_title = f"Top {top_n} Count Grouped by \"{'", "'.join(mapped_descriptions)}"
    st.write(chart_title, result)

    plot_result(result, chart_title)





