# filters/event_filters.py
import streamlit as st
from database_utils import get_unique_values
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
                else:
                    # For numeric fields, use a number input
                    filters[field] = st.number_input(f"Filter by {field}", value=0, step=1)
            else:
                filters[field] = None  # Set to None if not enabled
    return filters
