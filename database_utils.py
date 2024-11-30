"""import psycopg2
from streamlit import cache_data
from config import DB_CONFIG, TABLE_NAME
import pandas as pd
import streamlit as st


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def check_db_status():
    try:
        results = execute_query("SELECT NOW();")
        st.success(f"Database connected. Current time: {results[0][0]}")
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")


def execute_query(query, params=()):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results


def execute_final_query(query, params=()):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            column_names = [desc[0] for desc in cursor.description]
            list_of_tuples = cursor.fetchall()
            df = pd.DataFrame(list_of_tuples, columns=column_names)
        return df

@cache_data(max_entries=5)
def get_min_max_values(table_name, column_name):

    query = f"SELECT min_value, max_value FROM matteo_tef.min_max_view WHERE column_name = '{column_name}'"
    try:
        result = execute_query(query)
        min_val, max_val = result[0]
        return min_val, max_val
    except Exception as e:
        print(f"Error fetching min/max for {column_name}: {e}")
        return None, None

@cache_data(max_entries=33)
def get_unique_values(table_name, column_name):

    query = f"SELECT DISTINCT {column_name} FROM {TABLE_NAME}"
    try:
        results = execute_query(query)
        unique_values = [row[0] for row in results]
        return unique_values
    except Exception as e:
        print(f"Error fetching unique values for {column_name}: {e}")
        return []
"""

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from streamlit import cache_data
from config import DB_CONFIG, TABLE_NAME
import pandas as pd
import streamlit as st

# Initialize connection pool
POOL = SimpleConnectionPool(
    minconn=1,
    maxconn=10,  # Adjust based on expected concurrency
    **DB_CONFIG
)


def get_db_connection():
    """
    Retrieve a database connection from the pool.
    """
    try:
        return POOL.getconn()
    except Exception as e:
        st.error(f"Failed to get database connection: {e}")
        raise


def release_db_connection(conn):
    """
    Return a database connection back to the pool.
    """
    try:
        POOL.putconn(conn)
    except Exception as e:
        st.error(f"Failed to release database connection: {e}")


def check_db_status():
    """
    Check the database connection status.
    """
    try:
        results = execute_query("SELECT NOW();")
        st.success(f"Database connected. Current time: {results[0][0]}")
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")


def execute_query(query, params=()):
    """
    Execute a query and return results.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        raise
    finally:
        release_db_connection(conn)


def execute_final_query(query, params=()):
    """
    Execute a query and return results as a Pandas DataFrame.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            column_names = [desc[0] for desc in cursor.description]
            list_of_tuples = cursor.fetchall()
            df = pd.DataFrame(list_of_tuples, columns=column_names)
            return df
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        raise
    finally:
        release_db_connection(conn)


@cache_data(max_entries=5)
def get_min_max_values(table_name, column_name):
    """
    Get min and max values for a filter slider.
    """
    query = f"SELECT min_value, max_value FROM matteo_tef.min_max_view WHERE column_name = %s"
    try:
        result = execute_query(query, (column_name,))
        min_val, max_val = result[0]
        return min_val, max_val
    except Exception as e:
        st.error(f"Error fetching min/max for {column_name}: {e}")
        return None, None


@cache_data(max_entries=33)
def get_unique_values(table_name, column_name):
    """
    Get unique values for a specific column.
    """
    query = f"SELECT DISTINCT {column_name} FROM {table_name}"
    try:
        results = execute_query(query)
        unique_values = [row[0] for row in results]
        return unique_values
    except Exception as e:
        st.error(f"Error fetching unique values for {column_name}: {e}")
        return []
