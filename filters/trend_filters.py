# filters/trend_filters.py
import streamlit as st


def add_trend_filters():
    trend_parameters = {
        "trend_pre": "varchar",
        "trend_post": "varchar"
    }

    filters = {}
    with st.sidebar.expander("Trend Parameters", expanded=True):
        for field in trend_parameters:
            filters[field] = st.selectbox(f"Filter by {field}", options=["", "INCREASING", "DECREASING", "STEADY"],
                                          index=0)
    return filters
