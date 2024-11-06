# filters/duration_gap_filters.py
import streamlit as st
from database_utils import get_min_max_values
from config import TABLE_NAME


def add_duration_gap_filters():
    """Add filters for duration and gap-related fields."""
    duration_and_gaps = {
        "duration_pre": "numeric",
        "duration_post": "numeric",
        "gap_pre": "numeric",
        "gap_post": "numeric",
        "maxdurationtime": "int4",
        "maxdeltastart": "int4",
        "max_steady_percentage": "numeric"
    }

    filters = {}
    with st.sidebar.expander("Duration and Gaps", expanded=False):
        for field, datatype in duration_and_gaps.items():
            # Only apply min and max for numeric fields
            if datatype in ["numeric", "int4", "int8", "float8"]:
                # Fetch min and max values from the database
                min_val, max_val = get_min_max_values(TABLE_NAME, field)

                # Ensure min_val is less than max_val
                if min_val is not None and max_val is not None:
                    min_val, max_val = float(min_val), float(max_val)
                    if min_val > max_val:
                        min_val, max_val = max_val, min_val  # Swap values if min > max

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
                    min_val, max_val = 0.0, 100.0
                    default_range = (min_val, max_val)

                # Checkbox to enable or disable the filter
                enabled = st.checkbox(f"{field}", value=False)
                if enabled:
                    # Range slider for numeric range selection
                    selected_range = st.slider(
                        f"Filter by {field} range",
                        min_value=min_val,
                        max_value=max_val,
                        value=default_range
                    )
                    filters[field] = selected_range  # Store as a tuple (min, max)
                else:
                    filters[field] = None  # Set to None if not enabled

            else:
                # For non-numeric fields, use a standard input without range selection
                enabled = st.checkbox(f"{field}", value=False)
                if enabled:
                    filters[field] = st.text_input(f"Filter by {field}")
                else:
                    filters[field] = None  # Set to None if not enabled

    return filters
