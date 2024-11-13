import streamlit as st
from database_utils import get_min_max_values
from config import TABLE_NAME


general_constraints = [
    {"column_name": "rows_pre", "description": "Rows before event", "filter_group": "general", "extract_period": None,
     "value": None, "min_value": None, "max_value": None, "type": "int8"},
    {"column_name": "rows_post", "description": "Rows after event", "filter_group": "general", "extract_period": None,
     "value": None, "min_value": None, "max_value": None, "type": "int8"},
    {"column_name": "p1_value", "description": "Parameter 1 Value", "filter_group": "general", "extract_period": None,
     "value": None, "min_value": None, "max_value": None, "type": "numeric"},
    {"column_name": "p2_value", "description": "Parameter 2 Value", "filter_group": "general", "extract_period": None,
     "value": None, "min_value": None, "max_value": None, "type": "numeric"},
    {"column_name": "p3_value", "description": "Parameter 3 Value", "filter_group": "general", "extract_period": None,
     "value": None, "min_value": None, "max_value": None, "type": "numeric"},
    {"column_name": "p4_value", "description": "Parameter 4 Value", "filter_group": "general", "extract_period": None,
     "value": None, "min_value": None, "max_value": None, "type": "numeric"},
    {"column_name": "minnumberoftuples", "description": "Minimum Number of Tuples", "filter_group": "general",
     "extract_period": None, "value": None, "min_value": None, "max_value": None, "type": "int4"},
    {"column_name": "maxdeltavt", "description": "Max Delta VT", "filter_group": "general", "extract_period": None,
     "value": None, "min_value": None, "max_value": None, "type": "int4"},
]


def add_general_filters():

    with st.sidebar.expander("General Parameters", expanded=False):
        for constraint in general_constraints:
            min_val, max_val = get_min_max_values(TABLE_NAME, constraint["column_name"])
            if min_val is not None and max_val is not None:
                constraint["min_value"] = min_val
                constraint["max_value"] = max_val
            enabled = st.checkbox(f" {constraint['description']}", value=False)
            if enabled:
                if min_val == max_val:
                    st.write(f"{constraint['description']} has a fixed value of {int(min_val)}. No range available.")
                    constraint["value"] = min_val
                else:
                    default_range = (int(min_val), int(max_val))
                    step = 1
                    selected_range = st.slider(
                        f"Filter by {constraint['description']} range",
                        min_value=int(min_val),
                        max_value=int(max_val),
                        value=default_range,
                        step=step
                    )
                    constraint["value"] = selected_range
            else:
                constraint["value"] = None

    return general_constraints
