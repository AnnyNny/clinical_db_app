
import streamlit as st
from database_utils import get_min_max_values
from config import TABLE_NAME

duration_constraints = [
    {"column_name" : "duration_pre",
     "description" : "Duration of trend before event",
     "filter_group" : "duration_constraints",
     "value": None,
     "min_value" : None,
     "max_value" : None,
     "type": "numeric"},
{"column_name" : "duration_post",
     "description" : "Duration of trend after event",
     "filter_group" : "duration_constraints",
     "value": None,
 "min_value": None,
 "max_value": None,
 "type": "numeric"
 },
{"column_name" : "gap_pre",
     "description" : "p2_value - p1_value (gap_pre)",
     "filter_group" : "duration_constraints",
     "value": None,
 "min_value": None,
 "max_value": None,
 "type": "numeric"
 },
{"column_name" : "gap_post",
     "description" : "p4_value - p3_value (gap_post)",
     "filter_group" : "duration_constraints",
     "value": None,
 "min_value": None,
 "max_value": None,
 "type": "numeric"
 },
{"column_name" : "maxdurationtime",
     "description" : "Max Duration Time",
     "filter_group" : "duration_constraints",
     "value": None,
 "min_value": None,
 "max_value": None,
 "type": "int4"
 },
{"column_name" : "max_steady_percentage",
     "description" : "Max Steady Percentage",
     "filter_group" : "duration_constraints",
     "value": None,
 "min_value": None,
 "max_value": None,
 "type": "int4"
 },

]

"""duration_and_gaps = {
        "duration_pre": "numeric",
        "duration_post": "numeric",
        "gap_pre": "numeric",
        "gap_post": "numeric",
        "maxdurationtime": "int4",
        "maxdeltastart": "int4",
        "max_steady_percentage": "numeric"
    }"""

def add_duration_gap_filters():

    with st.sidebar.expander("Duration and Gaps", expanded=False):
        for i, constraint in enumerate(duration_constraints):
            enabled = st.checkbox(f"{constraint['description']}", value=False, key=f"{constraint['column_name']}_checkbox_{i}")
            min_val, max_val = get_min_max_values(TABLE_NAME, constraint["column_name"])
            if min_val is not None and max_val is not None:
                constraint["min_value"] = min_val
                constraint["max_value"] = max_val
                if min_val == max_val:
                    if enabled:
                        st.write(f"{constraint['description']} has a fixed value of {min_val}. No range available.")

                default_range = (int(min_val), int(max_val))
                if enabled:
                    selected_range = st.slider(
                        f"Filter by {constraint["description"]} range",
                        min_value=int(min_val),
                        max_value=int(max_val),
                        value=default_range,
                        key=f"{constraint['column_name']}_slider_{i}"
                    )
                    constraint["value"] = selected_range
                else:
                    constraint["value"] = None
    return duration_constraints
