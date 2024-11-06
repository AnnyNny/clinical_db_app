# database_utils.py
import psycopg2
from config import DB_CONFIG
import streamlit as st

@st.cache_data(show_spinner=False)
def execute_query(query, params=()):
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results

def get_min_max_values(table_name, column_name):
    """Fetches the minimum and maximum values for a specific column from the materialized view."""
    query = f"SELECT min_value, max_value FROM matteo_tef.min_max_view WHERE column_name = '{column_name}'"
    try:
        result = execute_query(query)
        min_val, max_val = result[0]
        return min_val, max_val
    except Exception as e:
        print(f"Error fetching min/max for {column_name}: {e}")
        return None, None

def get_unique_values(table_name, column_name):
    """Fetches unique values for a specific column."""
    query = f"SELECT DISTINCT INITCAP (LOWER({column_name})) AS event_normalized FROM {table_name} ORDER BY event_normalized"
    try:
        results = execute_query(query)
        unique_values = [row[0] for row in results]
        return unique_values
    except Exception as e:
        print(f"Error fetching unique values for {column_name}: {e}")
        return []


# database_utils.py
def get_groupable_fields(table_name):
    """Determine groupable fields based on the data type."""
    # Split schema and table name if the table includes schema (e.g., matteo_tef.tep_divided_results)
    if "." in table_name:
        schema, table = table_name.split(".")
    else:
        schema, table = None, table_name

    query = f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = '{table}'
    """

    if schema:
        query += f" AND table_schema = '{schema}'"

    # Execute the query and fetch results
    results = execute_query(query)

    groupable_fields = []
    for column_name, data_type in results:
        # Only consider columns suitable for grouping
        if data_type in ["varchar", "text", "boolean", "integer", "bigint", "numeric", "character varying"]:
            groupable_fields.append(column_name)

        # Handle timestamp fields to allow grouping by hour
        elif data_type == "timestamp with time zone" or data_type == "timestamptz":
            groupable_fields.append(f"EXTRACT(HOUR FROM {column_name})")
        """elif data_type == "timestamp with time zone" or data_type == "timestamptz":
            groupable_fields.append(f" {column_name} ")"""
            #groupable_fields.append(f" {column_name} HOUR")

    # Debugging to verify what fields are detected as groupable
    print("Groupable fields:", groupable_fields)
    return groupable_fields


def add_binning_to_query(column, bin_size=5):
    """Создаёт SQL выражение для бинирования числового столбца."""
    return f"FLOOR({column} / {bin_size}) * {bin_size} AS {column}_binned"
