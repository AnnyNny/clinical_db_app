from decimal import Decimal
import polars as pl
import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_sortables import sort_items
from group_by_filters import filter_map



def is_in_pandas(df):
    if isinstance(df, pl.DataFrame):
        return df.to_pandas()
    elif isinstance(df, pd.DataFrame):
        return df
    else:
        raise TypeError("Input must be either a Pandas or Polars DataFrame.")


def plot_result(df, chart_title=None, x_description_string=None):
    df = is_in_pandas(df)
    placeholder = st.empty()
    fig = px.bar(
        df,
        x=x_description_string,
        y="count",
        color=x_description_string,
        category_orders={x_description_string: df[x_description_string].unique()},
        title=chart_title,
        template="plotly_white"
    )
    fig.update_layout(
        xaxis_title=x_description_string,
        yaxis_title="Count",
        barmode="relative",
        bargap=0.2,
        height=800,
    )
    placeholder.plotly_chart(fig, use_container_width=True)


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


def apply_time_slicing(df, time_slice):
    """
    Dynamically slices the DataFrame columns of type datetime
    based on a user-selected time slice: hour, month, or year.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        time_slice (str): The time slice option, e.g., "hour", "month", "year".

    Returns:
        pd.DataFrame: The updated DataFrame with sliced datetime columns.
    """
    if time_slice is None:
        st.warning("No time slice. Please choose one.")
        return df

    for col in df.select_dtypes(include=['datetime64[ns, UTC]']).columns:
        print(f"{col}: {df[col].dtype}")
        if time_slice in ["hour", "month", "year"]:
            df[col] = getattr(df[col].dt, time_slice)
        else:
            print(f"Invalid time slicing option: {time_slice} for column {col}")

    return df

def plot_binned(df, top_n):
    df = pl.from_pandas(df)

    on = st.toggle("Sort by the number of trends")
    result = None
    new_column_name = None
    chart_title = None
    if on:
        result, new_column_name, group_columns = sort_by_trend_count(df)
        chart_title = generate_binned_chart_title(group_columns, top_n)
    else:
        result, new_column_name, sorted_group_columns = sort_by_sortable_items(df)
        chart_title = generate_binned_chart_title(sorted_group_columns,top_n)

    if result is not None:
        result = result.head(top_n)
        plot_result(result, chart_title, new_column_name)
    else:
        st.warning("No data available to plot.")


def plot_unbinned(df):
    df = pl.from_pandas(df)

    on = st.toggle("Sort by the number of trends")
    if on:
        result, new_column_name, group_columns = sort_by_trend_count(df)
        chart_title = generate_chart_title(group_columns)
        plot_result(result, chart_title, new_column_name)
    else:
        result, new_column_name, sorted_group_columns = sort_by_sortable_items(df)
        chart_title = generate_chart_title(sorted_group_columns)
        plot_result(result, chart_title, new_column_name)




def sort_by_trend_count(df):
    """
        Groups data by all columns except 'count', aggregates by count, and
        adds a new column that combines the grouped columns into a single string.

        Parameters:
            df (pl.DataFrame): Input Polars DataFrame.

        Returns:
            pl.DataFrame: Aggregated DataFrame with a new combined column.
        """
    group_columns = [col for col in df.columns if col != "count"]
    result = df.group_by(group_columns).agg([
        pl.col("count").sum().alias("count"),
    ]).sort("count", descending=True)

    combined_column_name = "-".join(group_columns)
    result = result.with_columns(
        pl.concat_str([pl.col(col).cast(str) for col in group_columns], separator=" — ").alias(combined_column_name)
    ).sort("count", descending=True)

    #st.write(result.head(5))

    return result, combined_column_name, group_columns

def sort_by_sortable_items(df):
    group_columns = [col for col in df.columns if col != "count"]

    sorted_group_columns = sort_items(group_columns)
    result = df.group_by(sorted_group_columns).agg([
        pl.col("count").sum().alias("count"),
    ])

    combined_column_name = "-".join(sorted_group_columns)
    result = result.with_columns(
        pl.concat_str([pl.col(col).cast(str) for col in sorted_group_columns], separator=" — ").alias(combined_column_name)
    ).sort(by=sorted_group_columns, descending=True)
    #st.write(result.head(5))
    return result, combined_column_name, sorted_group_columns

def generate_chart_title(group_columns):
    """
    Generates a chart title based on the group columns and filter map.

    Parameters:
        group_columns (list): List of columns used for grouping.

    Returns:
        str: Descriptive chart title.
    """
    mapped_descriptions = [filter_map.get(col, col) for col in group_columns]
    mapped_descriptions_string = " — ".join(mapped_descriptions)
    chart_title = f"Groups by {mapped_descriptions_string}"
    return chart_title

def generate_binned_chart_title(group_columns, top_n):
    mapped_descriptions = [filter_map.get(col, col) for col in group_columns]
    mapped_descriptions_string = " — ".join(mapped_descriptions)
    binned_chart_title = f"Top {top_n} Groups by {mapped_descriptions_string}"
    return binned_chart_title