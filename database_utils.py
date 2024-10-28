# database_utils.py
import psycopg2
from config import DB_CONFIG

def execute_query(query, params=()):
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results

def get_min_max_values(table_name, column_name):
    """Fetches the minimum and maximum values for a specific column."""
    query = f"SELECT MIN({column_name}), MAX({column_name}) FROM {table_name}"
    try:
        result = execute_query(query)
        min_val, max_val = result[0]
        return min_val, max_val
    except Exception as e:
        print(f"Error fetching min/max for {column_name}: {e}")
        return None, None

def get_unique_values(table_name, column_name):
    """Fetches unique values for a specific column."""
    query = f"SELECT DISTINCT {column_name} FROM {table_name} ORDER BY {column_name}"
    try:
        results = execute_query(query)
        unique_values = [row[0] for row in results]
        return unique_values
    except Exception as e:
        print(f"Error fetching unique values for {column_name}: {e}")
        return []

def get_groupable_fields(table_name):
    """Determine groupable fields based on the data type."""
    query = f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = '{table_name}'
    """
    results = execute_query(query)

    groupable_fields = []
    for column_name, data_type in results:
        # Categorical fields
        if data_type in ["varchar", "text", "boolean"]:
            groupable_fields.append(column_name)

        # Timestamp fields grouped by hour
        elif data_type == "timestamptz":
            groupable_fields.append(f"EXTRACT(HOUR FROM {column_name}) AS {column_name}_hour")

        # Optional: Numeric fields (only if you want to allow binning)
        elif data_type in ["int4", "int8", "bigint", "numeric", "float8"]:
            groupable_fields.append(column_name)  # Consider binning if included
    return groupable_fields
