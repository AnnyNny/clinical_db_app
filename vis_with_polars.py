from decimal import Decimal
import polars as pl
import streamlit as st
import plotly.express as px
import pandas as pd
import time
from group_by_filters import filter_map

def plot_result(result, chart_title=None, x_description_string=None):
    fig = px.bar(
        result,
        x=x_description_string,
        y="count",
        color=x_description_string,
        title=chart_title,
    )
    st.session_state["plot"] = fig
    st.plotly_chart(fig)

def apply_binning_to_decimal_p_value_columns(new_df, max_bins):
    new_df = new_df.to_pandas()
    """binning for p1-p4 values of vital parameters"""
    decimal_columns = [col for col in new_df.columns if isinstance(new_df[col].iloc[0], Decimal)]
    # st.write("after to_pandas() conversion data type is ", new_df.dtypes, new_df.dtypes)
    if max_bins > 0:
        for col in decimal_columns:
            new_df[col] = new_df[col].round(decimals=2)
            min_value = new_df[f"{col}"].min()
            max_value = new_df[f"{col}"].max()
            bin_width = (max_value - min_value) / max_bins
            bin_edges = [round(min_value + bin_width * i, 2) for i in range(max_bins + 1)]
            new_df[f"{col}"] = pd.cut(new_df[f"{col}"], bins=bin_edges,
                                             labels=[f"{bin_edges[i]}-{bin_edges[i + 1]}" for i in
                                                     range(len(bin_edges) - 1)], include_lowest=True)
            """new_df[f"{col}"] = pd.cut(new_df[f"{col}"],
                                             bins=bin_edges,
                                             labels=[f"{bin_edges[i]}-{bin_edges[i + 1]}" for i in
                                                     range(len(bin_edges) - 1)],
                                             include_lowest=True)"""
            #new_df = new_df.drop(columns=[col])
    return pl.from_pandas(new_df)

# I had to convert polars-pandas-polars because I don't know how to implement binning with polars, it gives POLARS ShapeError: provide len(quantiles) + 1 labels
"""def apply_binning_to_decimal_p_value_columns1(new_df, max_bins):
    decimal_columns = [col for col in new_df.columns if new_df.schema[col] == pl.Decimal]
    if max_bins > 0:
        for col in decimal_columns:
            min_value = new_df[col].min()
            max_value = new_df[col].max()
            bin_width = (max_value - min_value) / max_bins
            bin_edges = [min_value + bin_width * i for i in range(max_bins + 1)]
            labels = [f"{bin_edges[i]:.2f}-{bin_edges[i + 1]:.2f}" for i in range(len(bin_edges) - 1)]
            labels.append(f"{bin_edges[-2]:.2f}-{bin_edges[-1]:.2f}")

            s = new_df[col].cut(breaks=bin_edges, labels=labels, include_breaks=True).alias(f"{col}")

            # Add the binned column to the DataFrame
            new_df = new_df.with_columns(s)
            # Apply binning within Polars
            new_df = new_df.with_columns(
                pl.cut(pl.col(col), bins=bin_edges, labels=labels).alias(col)  # Replace column in place
            )

    return new_df"""




def plot_result_with_binning_polars(new_df, top_n=20, max_bins=3, time_slice=None):

    #print(new_df.dtypes)
    #st.write(df.schema)
    #st.write(df, "\n Total rows:", len(df), "type of df:", df.dtypes)
    #out = df.select(cs.numeric() - cs.by_name("count"))
    #st.write("out numeric columns:", out.columns, "type", out.dtypes)
    #possible_value_columns = ["p1_value", "p2_value", "p3_value", "p4_value"]
    for col in new_df.columns:
        if new_df[f"{col}"].dtype == pl.Datetime:
            time_slice_func = getattr(pl.col(col).dt, time_slice)
            new_df = new_df.with_columns(
                (
                    #time_slice_func().alias(f"{col}_{time_slice}")
                    time_slice_func().alias(f"{col}")
                )
            )
            #new_df = new_df.drop(f"{col}")
        else:
            pass
            #st.write(f"{col} is not a datetime column")
    #st.write(f"new_df after time slicing by {time_slice}", new_df, new_df.shape, new_df.dtypes)
    group_columns = [col for col in new_df.columns if col != "count"]
    if not group_columns:
        st.warning("Please select at least one column to group by before visualizing plot.")
        return

    new_df = new_df.group_by(group_columns).agg([
        pl.col("count").sum().alias("count"),
    ]).sort("count", descending=True)

    #st.write(f"DEBUGGING new_df after time slicing by {time_slice} and aggregating by count", new_df, new_df.shape)
    #new_df = new_df.to_pandas()
    #new_df = apply_binning_to_decimal_p_value_columns(new_df, max_bins)


    #st.write("###DEBUGGING new_df after binning p1,p2,p3,p4 values", new_df, len(new_df))

    group_columns = [col for col in new_df.columns if col != "count"]
    #st.write("###debugging: show group columns", group_columns)
    result = new_df.group_by(group_columns).agg([
        pl.col("count").sum()
    ]).sort("count", descending=True)

    #st.write("###DEBUGGING grouped data", result.shape, result)
    if top_n is not None:
        pass
        #result = result.head(top_n)
        #st.write(f"###Grouped data after limiting to top {top_n} groups", result.shape, result)

    grouped_columns = [pl.col(col).cast(str) for col in result.columns if col != "count"]
    grouped_columns_as_str = [expr.meta.output_name() for expr in grouped_columns]
    new_column_name = " — ".join(grouped_columns_as_str)

    result = result.with_columns(
        pl.concat_str(grouped_columns_as_str, separator="— ").alias(new_column_name)
    ).sort("count", descending=True)

    mapped_descriptions = [filter_map.get(col, col) for col in grouped_columns_as_str]
    mapped_descriptions_string = ' —  '.join(mapped_descriptions)

    chart_title = f"Top {top_n} Count groups by {mapped_descriptions_string}"
    st.write(result.head(top_n))
    plot_result(result, chart_title, new_column_name)





