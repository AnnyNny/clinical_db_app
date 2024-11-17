# database_utils.py
import psycopg2
from streamlit import cache_data
import polars as pl
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

@cache_data(max_entries=20)
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
            #df = pl.DataFrame(list_of_tuples, schema=column_names)
        return df

@cache_data(max_entries=5)
def get_min_max_values(table_name, column_name):
    """Fetch min and max values for a filter."""
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
    #query = f"SELECT DISTINCT (LOWER({column_name})) AS event_lowcase FROM {TABLE_NAME} ORDER BY event_lowcase"
    query = f"SELECT DISTINCT {column_name} FROM {TABLE_NAME}"
    try:
        results = execute_query(query)
        unique_values = [row[0] for row in results]
        return unique_values
    except Exception as e:
        print(f"Error fetching unique values for {column_name}: {e}")
        return []
