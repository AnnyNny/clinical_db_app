# filters/event_filters.py
import streamlit as st
from database_utils import get_unique_values, get_min_max_values
from config import TABLE_NAME


def add_event_filters():
    """Add filters for event-related fields."""
    event_related = {
        "event": "varchar",
        "influenced_by_event": "boolean",
        "deltax": "int4",
        "deltay": "numeric",
        "measure": "varchar"
    }

    filters = {}
    with st.sidebar.expander("Event-Related Parameters", expanded=True):
        for field, datatype in event_related.items():
            # Checkbox to enable or disable the filter
            enabled = st.checkbox(f"Enable filter for {field}", value=False)
            if enabled:
                if datatype == "varchar":
                    # Retrieve unique values for varchar fields and use a selectbox
                    options = get_unique_values(TABLE_NAME, field)
                    if options:
                        filters[field] = st.selectbox(f"Filter by {field}", options=options)
                    else:
                        st.warning(f"No options available for {field} in the database.")

                elif datatype == "boolean":
                    # For boolean, create a selectbox with True/False options
                    filters[field] = st.selectbox(f"Filter by {field}", options=[None, True, False], index=0)

                elif datatype in ["int4", "int8", "numeric", "float8"]:
                    # For numeric fields, use a range slider
                    min_val, max_val = get_min_max_values(TABLE_NAME, field)  # Fetch min and max from DB

                    # Ensure min_val is less than max_val
                    if min_val is not None and max_val is not None:
                        min_val, max_val = float(min_val), float(max_val)
                        if min_val > max_val:
                            min_val, max_val = max_val, min_val  # Swap values if min > max

                        # Check if min_val equals max_val
                        if min_val == max_val:
                            st.write(f"{field} has a fixed value of {min_val}. No range available.")
                            filters[field] = min_val  # Store the single value
                        else:
                            # Range slider for numeric range selection
                            filters[field] = st.slider(
                                f"Filter by {field} range",
                                min_value=min_val,
                                max_value=max_val,
                                value=(min_val, max_val)  # Set the default range
                            )
                    else:
                        st.warning(f"Could not retrieve min/max for {field}. Using default range.")
                        filters[field] = st.slider(
                            f"Filter by {field} range",
                            min_value=0.0,
                            max_value=100.0,
                            value=(0.0, 100.0)
                        )
            else:
                filters[field] = None  # Set to None if not enabled
    return filters
