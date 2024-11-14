# database_utils.py
import psycopg2
from streamlit import cache_data
import polars as pl
from config import DB_CONFIG, TABLE_NAME


@cache_data
def execute_query(query, params=()):
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results

@cache_data
def execute_final_query(query, params=()):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            column_names = [desc[0] for desc in cursor.description]
            list_of_tuples = cursor.fetchall()
            #df = pd.DataFrame(list_of_tuples, columns=column_names)
            df = pl.DataFrame(list_of_tuples, schema=column_names)
        return df

@cache_data
def get_min_max_values(table_name, column_name):
    """Fetch min and max values for a filter."""
    query = f"SELECT min_value, max_value FROM {TABLE_NAME} WHERE column_name = '{column_name}'"
    try:
        result = execute_query(query)
        min_val, max_val = result[0]
        return min_val, max_val
    except Exception as e:
        print(f"Error fetching min/max for {column_name}: {e}")
        return None, None

@cache_data
def get_unique_values(table_name, column_name):
    query = f"SELECT DISTINCT (LOWER({column_name})) AS event_lowcase FROM {TABLE_NAME} ORDER BY event_lowcase"
    try:
        results = execute_query(query)
        unique_values = [row[0] for row in results]
        return unique_values
    except Exception as e:
        print(f"Error fetching unique values for {column_name}: {e}")
        return []
