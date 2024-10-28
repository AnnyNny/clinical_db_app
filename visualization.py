import streamlit as st
import pandas as pd
import altair as alt
from database_utils import execute_query
from config import TABLE_NAME


def dynamic_trend_analysis(selected_groups, conditions, params, selected_event):
    trend_data = get_dynamic_trend_data(selected_groups, conditions, params)
    if trend_data:
        columns = selected_groups + ["count_events"]
        trend_df = pd.DataFrame(trend_data, columns=columns)

        # Set the title based on the selected event
        chart_title = f"Event Count Grouped by {', '.join(selected_groups)}"
        if selected_event:
            chart_title += f" (Event: {selected_event})"

        # Display dynamic grouping query
        st.write("Dynamic Grouping Query:", trend_data[1])  # Display the query for debugging

        # Bar chart to show event count by selected groups
        st.write(f"### {chart_title}")
        bar_chart = alt.Chart(trend_df).mark_bar().encode(
            x=alt.X(f"{selected_groups[0]}:O", title=selected_groups[0].capitalize()),
            y=alt.Y("count_events:Q", title="Event Count"),
            color=selected_groups[1] if len(selected_groups) > 1 else alt.value("steelblue"),
            tooltip=selected_groups + ["count_events"]
        ).properties(
            width=600,
            height=400,
            title=chart_title
        )
        st.altair_chart(bar_chart)
    else:
        st.warning("No data available for the selected grouping criteria.")


def get_dynamic_trend_data(groups, conditions, params, aggregation="count"):
    select_clause = ", ".join(groups)
    group_by_clause = ", ".join(groups)

    # Construct query with additional conditions
    query = f"SELECT {select_clause}, COUNT(*) AS count_events FROM {TABLE_NAME}"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" GROUP BY {group_by_clause} ORDER BY {group_by_clause};"

    # Execute query with params
    st.write("Dynamic Grouping Query:", query)  # Debug query
    return execute_query(query, params)
