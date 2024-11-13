import streamlit as st
from config import TABLE_NAME

def build_where_clause(filters):
    query = f"SELECT COUNT(*) FROM {TABLE_NAME}"
    conditions, params = [], []
    for filter in filters:
        column_name = filter["column_name"]
        value = filter["value"]
        if value is not None:
            if filter["filter_group"] == "time_constraints":
                granularity = filter.get("granularity", "").upper()
                conditions.append(f"EXTRACT({granularity} FROM {column_name}) = %s")
                params.append(value)
            elif isinstance(value, tuple) and len(value) == 2:
                conditions.append(f"{column_name} BETWEEN %s AND %s")
                params.extend(value)
            else:
                conditions.append(f"{column_name} = %s")
                params.append(value)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    return query, params

def build_final_query(where_query, selected_group_by_columns= None, order_by_filters=None):
    final_query = ""

    if selected_group_by_columns:
        select_columns = ', '.join(selected_group_by_columns) + ", COUNT(*)"
        final_query = where_query.replace("COUNT(*)", select_columns)
    else:
        final_query = where_query
    if selected_group_by_columns:
        final_query = group_by_clause(final_query, selected_group_by_columns)
    if order_by_filters:
        final_query = order_by_clause(final_query, order_by_filters)
    print("final final query", final_query)
    return final_query

def group_by_clause(query, selected_group_by_filters_columns):
    query += " GROUP BY " + ', '.join(selected_group_by_filters_columns)
    return query
def order_by_clause(query, order_by_filters = None):
    query += " ORDER BY " + ', '.join(order_by_filters)
    return query

def build_final_query1(where_query, selected_group_by_columns=None, selected_order_by_columns:list[dict[str, str | None]]=None):
    final_query = ""
    select_columns = []
    if selected_group_by_columns:
        for column in selected_group_by_columns:
            col = column["column_name"]
            granularity = column.get("granularity")
            if granularity:
                alias = f"{col}_extract_{granularity.lower()}"
                select_columns.append(f"{alias}")
            else:
                select_columns.append(col)

        select_clause = ', '.join(select_columns) + ", COUNT(*) AS total_count"
        final_query = where_query.replace("COUNT(*)", select_clause)
    else:
        final_query = where_query

    if selected_group_by_columns:
        group_by_columns = [
            f"{column['column_name']}_extract_{col_info['granularity'].lower()}" if col_info.get("granularity") else
            col_info["column_name"]
            for col_info in selected_group_by_columns
        ]
        final_query = group_by_clause(final_query, group_by_columns)

    if selected_order_by_columns:
        order_by_columns = [
            f"{col_info['column_name']}_extract_{col_info['granularity'].lower()}" if col_info.get("granularity") else
            col_info["column_name"]
            for col_info in selected_group_by_columns if col_info["column_name"] in selected_order_by_columns
        ]
        final_query = order_by_clause(final_query, order_by_columns)

    print("final final query", final_query)
    return final_query

def build_final_query_extract_hour(where_query, selected_group_by_columns:list[str | None] = None, order_by_filters=None):
    final_query = where_query
    select_clause = "SELECT "
    to_truncate = ["vt_start_pre","vt_end_pre","vt_start_post","vt_end_post"]
    points = ["p1_value", "p2_value", "p3_value", "p4_value"]
    group_by_columns = []
    order_by_columns = []

    if selected_group_by_columns:
        for col in selected_group_by_columns:
            if col in to_truncate:
                    alias = f"{col}_extract_hour"
                    select_clause += f"EXTRACT(HOUR FROM {col}) AS {alias}, "
                    group_by_columns.append(alias)
                    order_by_columns.append(alias) if col in order_by_filters else None
                    """elif col in points:
                alias = f"{col}_binned"
                select_clause += f"FLOOR({col}/5) * 5 AS {alias}, "
                group_by_columns.append(alias)
                order_by_columns.append(alias) if col in order_by_filters else None"""
            else:
                select_clause += f"{col}, "
                group_by_columns.append(col)
                if col in order_by_filters:
                    order_by_columns.append(col)
        select_clause += "COUNT(*) AS count"
        final_query = where_query.replace("SELECT COUNT(*)", select_clause)
        final_query = group_by_clause(final_query, group_by_columns)
    if order_by_filters:
        final_query = order_by_clause(final_query, order_by_columns)

    return final_query


def build_final_query_extract_hour1(where_query, selected_group_by_columns: list[dict] = None, order_by_filters=None):
    final_query = where_query
    select_clause = "SELECT "
    points = ["p1_value", "p2_value", "p3_value", "p4_value"]
    group_by_columns = []
    order_by_columns = []

    if selected_group_by_columns:
        for col_info in selected_group_by_columns:
            col = col_info["column_name"]
            granularity = col_info.get("granularity")

            if granularity:  # Если выбрана гранулярность
                alias = f"{col}_extract_{granularity.lower()}"
                select_clause += f"EXTRACT({granularity.upper()} FROM {col}) AS {alias}, "
                group_by_columns.append(alias)
                if col in order_by_filters:
                    order_by_columns.append(alias)
            elif col in points:  # Биннинг для числовых полей
                alias = f"{col}_binned"
                select_clause += f"FLOOR({col}/5) * 5 AS {alias}, "
                group_by_columns.append(alias)
                if col in order_by_filters:
                    order_by_columns.append(alias)
            else:  # Обычные поля без гранулярности
                select_clause += f"{col}, "
                group_by_columns.append(col)
                if col in order_by_filters:
                    order_by_columns.append(col)

        # Добавляем выражение COUNT(*) для итогового подсчета
        select_clause += "COUNT(*) AS total_count"
        final_query = where_query.replace("SELECT COUNT(*)", select_clause)

        # Генерация секции GROUP BY и ORDER BY
        final_query = group_by_clause(final_query, group_by_columns)

    if order_by_filters:
        final_query = order_by_clause(final_query, order_by_columns)

    print("final final_extract_granularity_and_binned query", final_query)
    return final_query


"""def build_query(filters):
    query = f"SELECT * FROM {TABLE_NAME}"
    conditions, params = [], []
    timestamp_fields = ["vt_start_pre", "vt_end_pre", "vt_start_post", "vt_end_post", "vt"]
    selected_event = None

    for field, value in filters.items():
        print(f"building query {field}: {value}")
        if value is not None:
            if isinstance(value, tuple) and len(value) == 2:
                conditions.append(f"{field} BETWEEN %s AND %s")
                params.extend(value)
            elif field in timestamp_fields and isinstance(value, int):
                conditions.append(f"EXTRACT({filter_time_type} FROM {field}) = %s")
                params.append(value)
            elif field == "event" and isinstance(value, str):
                conditions.append(f"LOWER({field}) = LOWER(%s)")
                params.append(value)
                selected_event = value
            elif isinstance(value, str) and value != "":
                conditions.append(f"{field} = %s")
                params.append(value)
            elif isinstance(value, (float, int)) and not isinstance(value, bool):
                conditions.append(f"{field} = %s")
                params.append(value)
            elif isinstance(value, bool):
                conditions.append(f"{field} IS {'TRUE' if value else 'FALSE'}")

    return conditions, params, selected_event"""
