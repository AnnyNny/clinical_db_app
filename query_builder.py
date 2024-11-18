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



