
import streamlit as st
from database_utils import get_unique_values, get_min_max_values
from config import TABLE_NAME

event_constraints = [
    {"column_name": "event", "description": "Event Type", "filter_group": "event_related", "type": "varchar", "value": None},
    {"column_name": "influenced_by_event", "description": "Influenced by Event", "filter_group": "event_related", "type": "boolean", "value": None},
    {"column_name": "deltax", "description": "Delta X", "filter_group": "event_related", "type": "int4", "value": None, "min_value": None, "max_value": None},
    {"column_name": "deltay", "description": "Delta Y", "filter_group": "event_related", "type": "numeric", "value": None, "min_value": None, "max_value": None},
    {"column_name": "measure", "description": "Measurement", "filter_group": "event_related", "type": "varchar", "value": None}
]

def add_event_filters():
    with st.sidebar.expander("Event-Related Parameters", expanded=False):
        for constraint in event_constraints:
            enabled = st.checkbox(f" {constraint['description']}", value=False)
            if enabled:
                if constraint["type"] == "varchar":
                    options = get_unique_values(TABLE_NAME, constraint["column_name"])
                    if options:
                        constraint["value"] = st.selectbox(f"Filter by {constraint['description']}", options=options)
                    else:
                        st.warning(f"No options available for {constraint['description']} in the database.")

                elif constraint["type"] == "boolean":
                    constraint["value"] = st.selectbox(f"Filter by {constraint['description']}", options=[None, True, False], index=0)

                elif constraint["type"] in ["int4", "numeric"]:
                    min_val, max_val = get_min_max_values(TABLE_NAME, constraint["column_name"])
                    if min_val is not None and max_val is not None:
                        min_val, max_val = float(min_val), float(max_val)
                        constraint["min_value"] = min_val
                        constraint["max_value"] = max_val
                        if min_val == max_val:
                            st.write(f"{constraint['description']} has a fixed value of {min_val}. No range available.")
                            constraint["value"] = min_val
                        else:
                            constraint["value"] = st.slider(
                                f"Filter by {constraint['description']} range",
                                min_value=min_val,
                                max_value=max_val,
                                value=(min_val, max_val),
                                step=1.0
                            )
            else:
                constraint["value"] = None  # Set to None if not enabled

    return event_constraints
