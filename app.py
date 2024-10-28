# app.py
import streamlit as st
import pandas as pd
import altair as alt
from config import TABLE_NAME
from database_utils import execute_query, get_groupable_fields
from filters.time_filters import add_time_filter_with_hour
from filters.trend_filters import add_trend_filters
from filters.slope_filters import add_slope_filters
from filters.duration_gap_filters import add_duration_gap_filters
from filters.event_filters import add_event_filters
from filters.general_filters import add_general_filters
from query_builder import build_query
from visualization import dynamic_trend_analysis

# Title for the Streamlit app
st.title("Clinical Database Application")

# Check and display the database connection status
try:
    results = execute_query("SELECT NOW();")
    st.success(f"Database connected. Current time: {results[0][0]}")
except Exception as e:
    st.error(f"Failed to connect to database: {e}")

# Sidebar for filter selection
st.sidebar.title("Filters")
st.sidebar.write("Select your filters below.")

# Collect filters from each filter function
filters = {}
filters.update(add_time_filter_with_hour())  # Time-based filters
filters.update(add_trend_filters())          # Trend-related filters
filters.update(add_slope_filters())          # Slope-related filters
filters.update(add_duration_gap_filters())   # Duration and gap-related filters
filters.update(add_event_filters())          # Event-related filters
filters.update(add_general_filters())        # General filters

# Build and execute the main query
conditions, params, selected_event = build_query(filters)
query = f"SELECT * FROM {TABLE_NAME}"
if conditions:
    query += " WHERE " + " AND ".join(conditions)

st.write("Executing main query:", query)
st.write("With parameters:", params)

# Execute and display the main query results
try:
    results = execute_query(query, params)
    if results:
        st.dataframe(results)
    else:
        st.warning("No results match the selected filters.")
except Exception as e:
    st.error(f"Error fetching data: {e}")

# Dynamic Grouping and Visualization Section
st.sidebar.write("### Dynamic Trend Analysis")
groupable_fields = get_groupable_fields(TABLE_NAME)
if groupable_fields:
    selected_groups = st.sidebar.multiselect("Choose up to 2 fields to group by:", groupable_fields, max_selections=2)
    if selected_groups:
        dynamic_trend_analysis(selected_groups, conditions, params, selected_event)
else:
    st.sidebar.write("No groupable fields available in the database.")
