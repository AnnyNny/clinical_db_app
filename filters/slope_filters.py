# filters/slope_filters.py
import streamlit as st

def add_slope_filters():
    """Add filters for slope-related fields."""
    slope_parameters = {
        "slope_pre": "numeric",
        "slope_pre_normalized": "numeric",
        "slope_post": "numeric"
    }

    filters = {}
    with st.sidebar.expander("Slope Parameters", expanded=False):
        for field, datatype in slope_parameters.items():
            enabled = st.checkbox(f"{field}", value=False)
            if enabled:
                filters[field] = st.number_input(f"Filter by {field}", value=0.0, step=0.1)
            else:
                filters[field] = None  # Set to None if not enabled
    return filters
