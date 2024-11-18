from decimal import Decimal
import polars as pl
import streamlit as st
import plotly.express as px
import pandas as pd
import time

from streamlit_sortables import sort_items

from group_by_filters import filter_map

def is_in_pandas(df):
    if isinstance(df, pl.DataFrame):  # Check if it's a Polars DataFrame
        return df.to_pandas()
    elif isinstance(df, pd.DataFrame):  # If it's already a Pandas DataFrame
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

def apply_binning_to_decimal_p_value_columns(new_df, max_bins):
    #new_df = new_df.to_pandas()
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
                                             labels=[f"range {bin_edges[i]}-{bin_edges[i + 1]}" for i in
                                                     range(len(bin_edges) - 1)], include_lowest=True)
    return new_df


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

def apply_time_slicing(new_df, time_slice=None):
    """dynamically slices the df columns of type datetime based on chosen by user time slice: hour, month or year"""
    polars_df = pl.from_pandas(new_df)
    if time_slice is None:
        return polars_df

    for col in polars_df.columns:
        if polars_df[col].dtype == pl.Datetime:
            time_slice_func = getattr(pl.col(col).dt, time_slice, None)
            if time_slice_func:
                polars_df = polars_df.with_columns(
                    time_slice_func().alias(col)
                )
            else:
                st.warning(f"Invalid time slicing option: {time_slice} for column {col}")
    return polars_df



def plot_result_with_binning_polars(new_df, top_n=20, max_bins=3, time_slice=None):
    start_time = time.time()
    new_df = pl.from_pandas(new_df)

    for col in new_df.columns:
        if new_df[f"{col}"].dtype == pl.Datetime:
            time_slice_func = getattr(pl.col(col).dt, time_slice)
            new_df = new_df.with_columns(
                (
                    time_slice_func().alias(f"{col}")
                )
            )
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
    if not group_columns:
        st.warning("Add the filters you want to group by before visualizing plot.")
        return
    sorted_group_columns = sort_items(group_columns)
    #st.write("###debugging: show group columns", group_columns)
    #result = new_df.group_by(group_columns).agg([
        #pl.col("count").sum()
    #]).sort("count", descending=True)
    result = new_df.group_by(sorted_group_columns).agg([
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

    plotting_start_time = time.time()
    plot_result(result, chart_title, new_column_name)
    plotting_end_time = time.time()
    elapsed_plotting_time = plotting_end_time - plotting_start_time
    st.info(f"️⏱️ Total plotting time: {elapsed_plotting_time:.2f} seconds ")
    with st.expander("View Table", expanded=False):
        st.write(result.head(top_n))
    elapsed_time = time.time() - start_time
    st.info(f"⏱️ Total execution time: {elapsed_time:.2f} seconds.")

"""def plot_result_with_binning_polars_lazy(new_df, top_n=20, max_bins=3, time_slice=None):
    start_time = time.time()
    lazy_df = pl.from_pandas(new_df).lazy()
    print("lazy schema", lazy_df.schema)
    schema = lazy_df.collect_schema()

    for col, dtype in schema.items():
        if dtype == pl.Datetime:  # Check if column is datetime
            # Get the time slicing function (e.g., hour, month, etc.)
            time_slice_func = getattr(pl.col(col).dt, time_slice, None)
            if time_slice_func:
                # Apply the time slicing operation
                lazy_df = lazy_df.with_columns(time_slice_func().alias(col))
            else:
                print(f"Time slicing operation '{time_slice}' is not supported for column '{col}'.")
        else:
            print(f"Skipping column '{col}' as it is not a datetime column.")

    group_columns = [col for col in new_df.columns if col != "count"]
    if not group_columns:
        st.warning("Please select at least one column to group by before visualizing plot.")
        return

    lazy_df = lazy_df.group_by(group_columns).agg([
        pl.col("count").sum().alias("count"),
    ]).sort("count", descending=True)


    result = lazy_df.collect()

    sorted_group_columns = sort_items(group_columns)

    result = result.group_by(sorted_group_columns).agg([
        pl.col("count").sum()
    ]).sort("count", descending=True)

    grouped_columns = [pl.col(col).cast(str) for col in result.columns if col != "count"]
    grouped_columns_as_str = [expr.meta.output_name() for expr in grouped_columns]
    new_column_name = " — ".join(grouped_columns_as_str)

    result = result.with_columns(
        pl.concat_str(grouped_columns_as_str, separator="— ").alias(new_column_name)
    ).sort("count", descending=True)

    mapped_descriptions = [filter_map.get(col, col) for col in grouped_columns_as_str]
    mapped_descriptions_string = ' —  '.join(mapped_descriptions)

    chart_title = f"Top {top_n} Count groups by {mapped_descriptions_string}"

    plotting_start_time = time.time()
    plot_result(result, chart_title, new_column_name)
    plotting_end_time = time.time()
    elapsed_plotting_time = plotting_end_time - plotting_start_time
    st.info(f"️⏱️ Lazy Total plotting time: {elapsed_plotting_time:.2f} seconds ")
    with st.expander("View Table", expanded=False):
        st.write(result.head(top_n))
    elapsed_time = time.time() - start_time
    st.info(f"⏱️ Lazy Total execution time: {elapsed_time:.2f} seconds.")"""






