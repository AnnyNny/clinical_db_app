# filters/time_filters.py
import streamlit as st


def add_time_filter_with_hour():
    time_constraints = {
        "vt_start_pre": "timestamptz",
        "vt_end_pre": "timestamptz",
        "vt_start_post": "timestamptz",
        "vt_end_post": "timestamptz"
    }

    filters = {}
    with st.sidebar.expander("Time Constraints", expanded=True):
        for field in time_constraints:
            enabled = st.checkbox(f"Enable {field} hour filter", value=False)
            if enabled:
                selected_hour = st.slider(f"Select hour for {field}", min_value=0, max_value=23, value=9)
                filters[field] = selected_hour
            else:
                filters[field] = None
    return filters
