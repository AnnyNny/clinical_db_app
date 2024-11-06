from datetime import time
import streamlit as st
import pandas as pd
from database_utils import execute_query
from config import TABLE_NAME
import plotly.express as px


# Main function to handle dynamic trend analysis and plotting
# Main function to handle dynamic trend analysis and plotting
def dynamic_trend_analysis(selected_groups, conditions, params, selected_event, enable_binning, bin_threshold=25, max_combinations=30):
    with st.spinner("Generating your plot... This may take a few moments."):
        # Retrieve data for the dynamic query
        trend_data = get_dynamic_trend_data(selected_groups, conditions, params)

    # Check if data is available
    if trend_data:
        # Construct the DataFrame with the selected columns and count_events
        columns = selected_groups + ["count_events"]
        trend_df = pd.DataFrame(trend_data, columns=columns)

        # Create a 'combined' column with all selected group values for readability
        trend_df['combined'] = trend_df[selected_groups].astype(str).agg(', '.join, axis=1)

        # Count unique combinations
        unique_combinations_count = trend_df['combined'].nunique()

        # If the number of unique combinations exceeds max_combinations, prompt the user
        if unique_combinations_count > max_combinations:
            if not st.checkbox(f"The number of unique combinations ({unique_combinations_count}) exceeds {max_combinations}. "
                               "The plot might be difficult to read. Proceed anyway?"):
                st.info("Adjust filters from the panel to reduce the number of combinations.")
                return  # Stop here if the user does not want to proceed

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

        # Set layout to maximize space usage
        fig.update_layout(
            width=1800,  # Increase width for larger display
            height=800,  # Increase height
            xaxis_title=" - ".join([col.capitalize() for col in selected_groups]),
            yaxis_title="Event Count",
            xaxis_tickangle=-45,  # Rotate x-axis labels for readability
            font=dict(size=14),  # Increase font size
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

    print("Debug: Starting to build SELECT and GROUP BY clauses...")  # Debug start message

    for group in groups:
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

    print("Generated Query:", query)  # Final query debugging statement

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
