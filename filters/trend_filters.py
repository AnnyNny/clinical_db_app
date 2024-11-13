
import streamlit as st

trend_constraints = [
    {
        "column_name": "trend_pre",
        "description": "Trend before event",
        "filter_group": "trend_constraints",
        "value": None,
        "type": "varchar",
        "options": [None,"INCREASING", "DECREASING", "STEADY"]
    },
    {
        "column_name": "trend_post",
        "description": "Trend after event",
        "filter_group": "trend_constraints",
        "value": None,
        "type": "varchar",
        "options": [None,"INCREASING", "DECREASING", "STEADY"]
    }
]


def add_trend_filters():
    with st.sidebar.expander("Trend Parameters", expanded=False):
        for constraint in trend_constraints:
            constraint["value"] = st.selectbox(
                f"Filter by {constraint['description']}",
                options=constraint["options"],
                index=0
            )
    return trend_constraints
