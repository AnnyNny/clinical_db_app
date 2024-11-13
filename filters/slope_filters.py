import streamlit as st
from database_utils import get_min_max_values
from config import TABLE_NAME

slope_constraints = [
    {"column_name": "slope_pre",
     "description": "Slope before event",
     "filter_group": "slope_constraints",
     "value": None,
     "min_value": None,
     "max_value": None,
     "type": "numeric"},

    {"column_name": "slope_pre_normalized",
     "description": "Normalized slope before event",
     "filter_group": "slope_constraints",
     "value": None,
     "min_value": None,
     "max_value": None,
     "type": "numeric"},

    {"column_name": "slope_post",
     "description": "Slope after event",
     "filter_group": "slope_constraints",
     "value": None,
     "min_value": None,
     "max_value": None,
     "type": "numeric"}
]


def add_slope_filters():
    with st.sidebar.expander("Slope Parameters", expanded=False):
        for constraint in slope_constraints:
            min_val, max_val = get_min_max_values(TABLE_NAME, constraint["column_name"])
            if min_val is not None and max_val is not None:
                constraint["min_value"] = min_val
                constraint["max_value"] = max_val
            enabled = st.checkbox(f" {constraint['description']}", value=False)
            if enabled:
                if min_val == max_val:
                    st.write(f"{constraint['description']} has a fixed value of {float(min_val)}. No range available.")
                    constraint["value"] = min_val
                else:
                    default_range = (float(min_val), float(max_val))
                    step = 1

                    selected_range = st.slider(
                        f"Filter by {constraint['description']} range",
                        min_value=float(min_val),
                        max_value=float(max_val),
                        value=default_range,
                        step=float(step)
                    )
                    constraint["value"] = selected_range
            else:
                constraint["value"] = None

    return slope_constraints