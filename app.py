# app.py
import streamlit as st
from config import TABLE_NAME
from database_utils import execute_query, get_unique_values
from filters.time_filters import add_time_filter_with_hour
from filters.trend_filters import add_trend_filters
from filters.slope_filters import add_slope_filters
from filters.duration_gap_filters import add_duration_gap_filters
from filters.event_filters import add_event_filters
from filters.general_filters import add_general_filters

# Title for the Streamlit app
st.title("Clinical Database Application")

# Check and display the database connection status
try:
    results = execute_query("SELECT NOW();")
    st.success(f"Database connected. Current time: {results[0][0]}")
except Exception as e:
    st.error(f"Failed to connect to database: {e}")

# Sidebar for filter selection
st.sidebar.title("Filters")
st.sidebar.write("Select your filters below.")

# Collect filters from each filter function
filters = {}
filters.update(add_time_filter_with_hour())        # Time-based filters (e.g., hour selection)
filters.update(add_trend_filters())                # Trend-related filters
filters.update(add_slope_filters())                # Slope-related filters
filters.update(add_duration_gap_filters())         # Duration and gap-related filters
filters.update(add_event_filters())                # Event-related filters
filters.update(add_general_filters())              # General filters

# Build the query dynamically based on selected filters
query = f"SELECT * FROM {TABLE_NAME}"
conditions = []
params = []

# Define timestamp fields for hour extraction
timestamp_fields = ["vt_start_pre", "vt_end_pre", "vt_start_post", "vt_end_post", "vt"]

# Apply filters dynamically
for field, value in filters.items():
    if value is not None:
        # Check if the value is a range (tuple) for numeric range filters
        if isinstance(value, tuple) and len(value) == 2:
            conditions.append(f"{field} BETWEEN %s AND %s")
            params.extend(value)  # Add both min and max values to params

        # Apply hour extraction only for timestamp fields
        elif field in timestamp_fields and isinstance(value, int):
            conditions.append(f"EXTRACT(HOUR FROM {field}) = %s")
            params.append(value)

        # Case-insensitive comparison for the 'event' field (and other varchar fields if needed)
        elif field == "event" and isinstance(value, str):
            conditions.append(f"LOWER({field}) = LOWER(%s)")
            params.append(value)

        # Apply direct comparison for string-based filters
        elif isinstance(value, str) and value != "":
            conditions.append(f"{field} = %s")
            params.append(value)

        # Numeric filters (single values)
        elif isinstance(value, (float, int)) and not isinstance(value, bool):
            conditions.append(f"{field} = %s")
            params.append(value)

        # Boolean filters
        elif isinstance(value, bool):
            if value:
                conditions.append(f"{field} IS TRUE")
            else:
                conditions.append(f"{field} IS FALSE")

# Combine conditions into the query if there are any
if conditions:
    query += " WHERE " + " AND ".join(conditions)

# Display query and parameters for debugging
st.write("Executing query:", query)
st.write("With parameters:", params)

# Execute and display the results
try:
    results = execute_query(query, params)
    if results:
        st.dataframe(results)  # Display results in a table
    else:
        st.warning("No results match the selected filters.")
        st.write("Query executed but no results were found. Debugging information:")
        st.write("Query:", query)
        st.write("Parameters:", params)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.write("Query:", query)
    st.write("Parameters:", params)
