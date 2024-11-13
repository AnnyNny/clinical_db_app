from math import floor

import numpy as np
import streamlit as st
import pandas as pd
from database_utils import execute_query, get_min_max_values
from config import TABLE_NAME
import plotly.express as px
import plotly as plt
import plotly.figure_factory as ff
import scipy
import polars as pl


def plot_result_with_binning1(data, top_n=10, max_bins=24):
    df = data.copy()
    columns_list = df.columns.values.tolist()
    st.write(df.head(), "\n Total rows:", len(df), "Shape", df.shape, "Data types: ", df.dtypes)

    """#possible_timestamp_columns = ["vt", "vt_end_pre", "vt_end_post", "vt_start_pre", "vt_start_post"]
    possible_value_columns = ["p1_value", "p2_value", "p3_value", "p4_value"]
    new_df = df.copy()
    new_df_agg_by = df.copy()
    for col in columns_list:
        if col in possible_value_columns:
            df[col] = df[col].astype(int)
            if pd.api.types.is_any_real_numeric_dtype(df[col]):
                st.write(f"Обработка колонки: {col} min_p_value {df[col].min()} max_p_value {df[col].max()}")
                min_p_value = df[col].min()
                max_p_value = df[col].max()
                bin_length = floor((max_p_value - min_p_value) / max_bins)
                labels = []
                current_min = min_p_value
                for i in range(1, max_bins + 1):
                    current_max = current_min + bin_length
                    labels.append(f"Group {i} for {col}: ({current_min}-{current_max})")
                    current_min = current_max + 1
                st.write(f"Interval of one bin: {bin_length}, labels: {labels}")
                new_df[col+"_binned"] = pd.cut(df[col], bins=max_bins, labels=labels)
                st.write("Inside col binninf:", new_df[col+"_binned"])
                #new_df_agg_by_col = new_df.groupby([col+"_binned"]).agg({"count":"sum"}).reset_index()
                #new_df.drop(col, axis=1, inplace=True)

            else:
                st.warning(f"Column {col} is not in numeric format but in {col}.")"""

    """agg_dict = {}
    for col in new_df.columns:
        if col == 'count':
            agg_dict[col] = 'sum'  # Суммируем 'count'
        elif col in possible_value_columns:
            continue  # Игнорируем колонки, которые были обработаны для бинов
        elif col.endswith("_binned"):
            continue  # Игнорируем новые колонки с бинами, т.к. по ним группируем
        else:
            agg_dict[col] = lambda x: ', '.join(map(str, x.unique()))"""

    """grouped_df = new_df.copy()
    bin_columns = [col for col in new_df.columns if col.endswith("_binned")]
    if bin_columns:
        grouped_df = new_df.groupby(list(new_df.columns.difference(['count']))).agg({'count': 'sum'}).reset_index()

    else:
        st.warning("Нет колонок для биннинга, группировка не выполнена.")
        grouped_df = new_df
        
    grouped_df_sorted = grouped_df.sort_values(by='count', ascending=False).head(top_n)
    st.write("after processing points",new_df.head())
    st.write("after grouping by col points", grouped_df.head())

    columns_to_combine = grouped_df.drop(columns=["count"]).columns
    combined_names = ' - '.join(columns_to_combine)

    grouped_df["combined"] = grouped_df.drop(columns=["count"]).astype(str).agg('-'.join, axis=1)


    st.write(combined_names)
    st.write("df combined", grouped_df["combined"])

    fig = px.bar(
        grouped_df_sorted,
        x='combined',
        y='count',
        title=f"25 bins with Trend and Time (Grouped)",

    )

    st.plotly_chart(fig)"""

def plot_result_with_binning(data, top_n=10, max_bins=25):
    df = data.copy()
    columns_list = df.columns.values.tolist()
    st.write(df.head(), "\n Total rows:", len(df))

    possible_timestamp_columns = ["vt", "vt_end_pre", "vt_end_post", "vt_start_pre", "vt_start_post"]
    possible_value_columns = ["p1_value", "p2_value", "p3_value", "p4_value"]

    for col in columns_list:
        if col in possible_timestamp_columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                st.write(f"Обработка колонки: {col}")
                df[col] = df[col].dt.tz_localize(None)
                df[col] = df[col].dt.hour
                st.write(f"Часы для {col}:", df[col].head())
            else:
                st.warning(f"Column {col} is not in datetime format.")

    columns_to_combine = df.drop(columns=["count"]).columns
    df['combined_names'] = '-'.join(columns_to_combine)

    df["combined"] = df.drop(columns=["count"]).astype(str).agg('-'.join, axis=1)

    st.write(df['combined_names'])
    st.write("df combined", df["combined"])


    """# Биннинг значений для p1_value
    for col in columns_list:
        if col in possible_value_columns:
            # Преобразование в числовой формат для корректного выполнения биннинга
            df[col] = pd.to_numeric(df[col], errors='coerce')

            if pd.api.types.is_numeric_dtype(df[col]):
                # Создаем биннинг на 25 групп с равными интервалами
                df[col + "_binned"] = pd.cut(df[col], bins=max_bins)

                # Сгруппируем данные по нескольким столбцам для построения группированного графика
                grouped_df = df.groupby(['trend_pre', 'vt_start_pre_hour', col + '_binned']).size().reset_index(name='count')

                # Преобразование интервалов в строки для корректной сериализации
                grouped_df[col + "_binned"] = grouped_df[col + "_binned"].astype(str)

                # Используем plotly express для построения графика
                fig = px.bar(
                    grouped_df,
                    x=col + "_binned",
                    y='count',
                    color='trend_pre',
                    facet_col='vt_start_pre_hour',
                    title=f"Distribution of {col} across 25 bins with Trend and Time (Grouped)",
                    labels={col + "_binned": f"{col} (Binned into 25 equal groups)", "count": "Count", "trend_pre": "Trend", "vt_start_pre_hour": "Hour"}
                )

                st.plotly_chart(fig)
                break  # Достаточно построить график для одной колонки, если нужно больше, уберите break
            else:
                st.warning(f"Column {col} is not numeric and cannot be binned.")"""
    # Remove timezone information if necessary
    #df[timestamp_column] = df[timestamp_column].dt.tz_localize(None)

    """# User selection for time binning interval"""


    # Initial binning based on user choice


    # Calculate the number of unique bins
    """unique_bins = df['time_bin'].nunique()

    # Dynamically reduce the number of bins if necessary
    if unique_bins > max_bins:
        # Determine the appropriate aggregation level within the chosen interval
        if time_bin == "Hour":
            aggregation_freq = f"{max(unique_bins // max_bins, 1)}H"  # e.g., 6H for 6-hour bins
            df['time_bin'] = df[timestamp_column].dt.to_period(aggregation_freq).astype(str)
            st.info(f"Aggregating by {aggregation_freq} to reduce the number of hourly bins.")

        elif time_bin == "Month":
            aggregation_freq = f"{max(unique_bins // max_bins, 1)}M"  # e.g., every 3 months
            df['time_bin'] = df[timestamp_column].dt.to_period(aggregation_freq).astype(str)
            st.info(f"Aggregating by {aggregation_freq} to reduce the number of monthly bins.")

        elif time_bin == "Year":
            aggregation_freq = f"{max(unique_bins // max_bins, 1)}Y"  # e.g., every 5 years
            df['time_bin'] = df[timestamp_column].dt.to_period(aggregation_freq).astype(str)
            st.info(f"Aggregating by {aggregation_freq} to reduce the number of yearly bins.")

    # Calculate the count for each trend and select top N trends
    trend_counts = df[trend_column].value_counts().nlargest(top_n)
    top_trends = trend_counts.index.tolist()

    # Filter the data for top trends
    filtered_df = df[df[trend_column].isin(top_trends)]

    # Group by time_bin and trend column, count occurrences
    grouped_df = filtered_df.groupby(['time_bin', trend_column]).size().reset_index(name='count')

    # Sort by time_bin to keep bins in chronological order
    grouped_df = grouped_df.sort_values(by="time_bin")

    # Plot the data with Plotly
    fig = px.bar(
        grouped_df,
        x='time_bin',
        y='count',
        color=trend_column,
        barmode="group",
        title=f"Top {top_n} Trends Over Time (Binned by {time_bin}, Aggregated as Necessary)"
    )
    fig.update_layout(
        xaxis_title="Time (Binned by selected interval)",
        yaxis_title="Count",
        legend_title_text="Trend",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig)
"""





    """x_label = df.copy().drop(columns=["count"]).astype(str).agg(' - '.join, axis=1)
    st.write(x_label.head())  # Display the first few rows for reference

    fig = px.bar(
        df,
        x=x_label,
        y='count',
        barmode="group",
        title="Trend Combinations Over Time"
    )
    st.plotly_chart(fig)"""
    """# Display available columns for debugging and dynamic checking
    columns_list = df.columns.to_list()
    st.write("Available columns:", columns_list)

    # Define possible timestamp and trend columns
    possible_timestamp_columns = ["vt", "vt_end_pre", "vt_end_post", "vt_start_pre", "vt_start_post"]
    possible_trend_columns = ["trend_pre", "trend_post"]

    # Find an available timestamp column for binning
    timestamp_column = next((col for col in possible_timestamp_columns if col in columns_list), None)
    if not timestamp_column:
        st.error("No valid timestamp column found in the dataset.")
        return

    # Find available trend columns for grouping
    trend_columns = [col for col in possible_trend_columns if col in columns_list]

    # User selection for time binning
    time_bin = st.selectbox("Choose Time Bin", options=["Hour", "Month", "Year"])

    # Remove timezone if necessary to avoid warnings
    if pd.api.types.is_datetime64tz_dtype(df[timestamp_column]):
        df[timestamp_column] = df[timestamp_column].dt.tz_localize(None)

    # Apply time binning based on user selection
    if time_bin == "Month":
        df['time_bin'] = df[timestamp_column].dt.to_period('M')
    elif time_bin == "Year":
        df['time_bin'] = df[timestamp_column].dt.to_period('Y')
    elif time_bin == "Hour":
        df['time_bin'] = df[timestamp_column].dt.to_period('h')  # Use lowercase 'h' to avoid future deprecation

    # Convert the 'time_bin' Period column to a string format for compatibility
    df['time_bin'] = df['time_bin'].astype(str)

    # Group by 'time_bin' and trend columns (if available)
    groupby_columns = ['time_bin'] + trend_columns
    grouped_df = df.groupby(groupby_columns).size().reset_index(name='count')

    # Plot the data with Plotly for interactivity
    fig = px.bar(
        grouped_df,
        x='time_bin',
        y='count',
        color=trend_columns[0] if trend_columns else None,  # Use the first trend column if available
        barmode="group",
        title="Trend Combinations Over Time"
    )

    # Update layout for better appearance
    fig.update_layout(
        xaxis_title="Time (Binned by selected interval)",
        yaxis_title="Count",
        legend_title_text="Trend" if trend_columns else None
    )

    # Display the plot
    st.plotly_chart(fig)"""


def prepare_x_label(df, exclude_column='count'):
    """
    Prepares the x_label by formatting datetime columns and concatenating them.

    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - exclude_column (str): Column name to exclude from concatenation (e.g., 'count').

    Returns:
    - pd.Series: A Series with concatenated x_labels.
    """
    formatted_df = df.copy()

    # Convert all datetime columns to a formatted string (e.g., only date part)
    for col in formatted_df.columns:
        if pd.api.types.is_datetime64_any_dtype(formatted_df[col]):
            formatted_df[col] = formatted_df[col].dt.strftime('%m')  # Adjust the format as needed

    # Concatenate all columns except the exclude_column
    x_label = formatted_df.drop(columns=[exclude_column]).astype(str).agg(' - '.join, axis=1)

    return x_label


def dynamic_trend_analysis(selected_groups, conditions, params, selected_event, enable_binning, bin_threshold=25, max_combinations=30):
    trend_data = get_dynamic_trend_data(selected_groups, conditions, params)
    points = ["p1_value", "p2_value", "p3_value", "p4_value"]

    if trend_data:

        columns = selected_groups + ["count_events"]
        trend_df = pd.DataFrame(trend_data, columns=columns)

        # Create a 'combined' column with all selected group values for readability
        trend_df['combined'] = trend_df[selected_groups].astype(str).agg(', '.join, axis=1)
        unique_combinations_count = trend_df['combined'].nunique()

        if unique_combinations_count > max_combinations:
            # Warning message explaining the situation
            st.warning(
                f"The number of unique combinations ({unique_combinations_count}) exceeds {max_combinations}. "
                "Displaying all of them might make the chart difficult to interpret. You can adjust filters in the Filter Panel to reduce combinations."
            )

            # Checkbox to confirm proceeding with the plot
            proceed = st.checkbox(
                "I understand the chart may be complex, and I still want to proceed with all combinations.\n Use 'Zoom' if you want to see a particluar part better",
                value=False
            )

            if not proceed:
                st.info("Please adjust filters in the Filter Panel to reduce the number of combinations.")
                return  # Stop here if the user does not want to proceed
        """total_rows = len(trend_df)
        print("total_rows", total_rows)
        target_groups = 25
        bin_size = max(1, total_rows // target_groups)
        trend_df['group_id'] = (np.arange(total_rows) // bin_size)

        grouped_df = trend_df.groupby(['group_id']).agg({
            group_column: 'p1_value',
            x_column: 'mean',
            y_column: 'mean'
        }).reset_index()"""
        #st.write("grouped_df",grouped_df.columns)
        # Set a dynamic title based on selected events
        chart_title = f"Event Count Grouped by {', '.join(selected_groups)}"
        if selected_event:
            chart_title += f" (Event: {selected_event})"

        # Generate the plot with Plotly Express
        st.write(f"### {chart_title}")

        fig = px.bar(trend_df,
                     x="combined",
                     y="count_events",
                     color="combined",  # Use the combination of groups as color
                     title=chart_title,
                     labels={"combined": "Combinations", "count_events": "Event Count"},
                     text="count_events"  # Show count above each bar
                     )
        """fig = px.line(grouped_df,
                     x=x_column,
                     y="count_events",
                     color="combined",  # Use the combination of groups as color
                     title=chart_title,
                     labels={"combined": "Combinations", "count_events": "Event Count"},
                     text="count_events"  # Show count above each bar
                     )"""
        # Set layout to maximize space usage
        fig.update_layout(
            width=1800,  # Increase width for larger display
            height=800,  # Increase height
            xaxis_title=" - ".join([col.capitalize() for col in selected_groups]),
            yaxis_title="Event Count",
            xaxis_tickangle=-90,  # Rotate x-axis labels for readability
            font=dict(size=12),  # Increase font size
            hovermode="closest",
            xaxis={'tickmode': 'array', 'tickvals': trend_df.index, 'automargin': True},
            margin=dict(l=20, r=20, t=40, b=100)
        )

        # Display count text on top of bars
        fig.update_traces(textposition='outside', textfont_size=12)

        # Display the chart in Streamlit with full container width
        st.plotly_chart(fig, use_container_width=True)

        # Success message after plot is displayed
        st.success("Plot generated successfully!")
    else:
        st.warning("No data available for the selected grouping criteria.")


# Cache the data retrieval to avoid repeated database calls
@st.cache_data(show_spinner=False)
def get_dynamic_trend_data(groups, conditions, params):
    select_parts = []
    group_by_parts = []
    #points = ["p1_value", "p2_value", "p3_value", "p4_value"]
    print("Debug: Starting to build SELECT and GROUP BY clauses...")  # Debug start message

    for group in groups:
        """if group in points:
            min_binned_points, max_binned_points = get_min_max_values(None, group)
            num_bins_step = (max_binned_points - min_binned_points)//25
            print("num_bins_step", num_bins_step)"""
        """# Custom handling for vt_hour to group by time of day
        if group == "vt_hour":
            # Use CASE WHEN to categorize vt_hour into time-of-day ranges
            time_of_day_case = 
                CASE
                    WHEN vt_hour BETWEEN 6 AND 11 THEN 'Morning'
                    WHEN vt_hour BETWEEN 12 AND 17 THEN 'Day'
                    WHEN vt_hour BETWEEN 18 AND 23 THEN 'Evening'
                    ELSE 'Night'
                END
            
            select_parts.append(f"{time_of_day_case} AS time_of_day")  # Alias as `time_of_day`
            group_by_parts.append(time_of_day_case)  # Use CASE directly in GROUP BY
            print(f"Debug: Added custom time-of-day grouping for {group}")  # Debugging line
        elif is_numeric_column(group):
            # Apply binning for other numeric fields if needed
            binned_expression = f"FLOOR({group} / 5) * 5"
            select_parts.append(f"{binned_expression} AS {group}_binned")
            group_by_parts.append(binned_expression)
            print(f"Debug: Added binned expression for {group}: {binned_expression}")  # Debugging line
        else:
            # Non-binned group"""
        select_parts.append(group)
        group_by_parts.append(group)
        print(f"Debug: Added non-binned group: {group}")  # Debugging line

    # Construct the SELECT and GROUP BY clauses
    select_clause = ", ".join(select_parts)
    group_by_clause = ", ".join(group_by_parts)

    print("Debug: SELECT clause ->", select_clause)  # Debugging the SELECT clause
    print("Debug: GROUP BY clause ->", group_by_clause)  # Debugging the GROUP BY clause

    # Construct the final query with conditions
    query = f"SELECT {select_clause}, COUNT(*) AS count_events FROM {TABLE_NAME}"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" GROUP BY {group_by_clause} ORDER BY {group_by_clause};"

    st.write("Generated Query:", query)  # Final query debugging statement

    # Execute query with params
    return execute_query(query, params)


# Cache the numeric column check to avoid repeated database calls
@st.cache_data(show_spinner=False)
def is_numeric_column(column_name):
    """Determine if a column is numeric based on predefined criteria or query metadata."""
    numeric_columns_query = f"""
    SELECT att.attname
    FROM pg_catalog.pg_attribute AS att
    JOIN pg_catalog.pg_class AS cls ON att.attrelid = cls.oid
    JOIN pg_catalog.pg_type AS typ ON att.atttypid = typ.oid
    WHERE cls.relname = '{TABLE_NAME.split('.')[-1]}' 
      AND typ.typcategory = 'N' 
      AND att.attname = '{column_name}';
    """
    # Execute query to check if column is numeric
    result = execute_query(numeric_columns_query)
    return len(result) > 0
