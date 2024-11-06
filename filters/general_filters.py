# filters/general_filters.py
import streamlit as st
from database_utils import get_min_max_values
from config import TABLE_NAME

def add_general_filters():
    """Add filters for general fields."""
    general = {
        "rows_pre": "int8",
        "rows_post": "int8",
        "p1_value": "numeric",
        "p2_value": "numeric",
        "p3_value": "numeric",
        "p4_value": "numeric",
        "minnumberoftuples": "int4",
        "maxdeltavt": "int4"
    }

    filters = {}
    with st.sidebar.expander("General Parameters", expanded=False):
        for field, datatype in general.items():
            # Only apply min and max for numeric fields
            if datatype in ["numeric", "int4", "int8", "float8", "bigint"]:
                # Fetch min and max values from the database
                min_val, max_val = get_min_max_values(TABLE_NAME, field)

                # Ensure min_val is less than max_val
                if min_val is not None and max_val is not None:
                    # Convert to appropriate type based on datatype
                    if datatype in ["int4", "int8", "bigint"]:
                        min_val, max_val = int(min_val), int(max_val)
                    else:
                        min_val, max_val = float(min_val), float(max_val)

                    # If min_val equals max_val, display a single-value filter
                    if min_val == max_val:
                        enabled = st.checkbox(f" {field}", value=False)
                        if enabled:
                            st.write(f"{field} has a fixed value of {min_val}. No range available.")
                            filters[field] = min_val  # Store the single value
                        else:
                            filters[field] = None
                        continue  # Skip to the next field

                    # Set the default range for sliders
                    default_range = (min_val, max_val)
                else:
                    # Fallback values if min/max are not available
                    if datatype in ["int4", "int8", "bigint"]:
                        min_val, max_val = 0, 100
                        default_range = (min_val, max_val)
                    else:
                        min_val, max_val = 0.0, 100.0
                        default_range = (min_val, max_val)

                # Checkbox to enable or disable the filter
                enabled = st.checkbox(f" {field}", value=False)
                if enabled:
                    # Range slider with appropriate integer or float type
                    selected_range = st.slider(
                        f"Filter by {field} range",
                        min_value=min_val,
                        max_value=max_val,
                        value=default_range,
                        step=1 if datatype in ["int4", "int8", "bigint"] else 0.1  # Integer step for int types
                    )
                    filters[field] = selected_range  # Store as a tuple (min, max)
                else:
                    filters[field] = None  # Set to None if not enabled

            else:
                # For non-numeric fields, use a standard input without range selection
                enabled = st.checkbox(f" {field}", value=False)
                if enabled:
                    filters[field] = st.text_input(f"Filter by {field}")
                else:
                    filters[field] = None  # Set to None if not enabled

    return filters