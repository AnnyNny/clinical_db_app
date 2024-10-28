from filters.time_filters import add_time_filter_with_hour
from filters.trend_filters import add_trend_filters
from filters.slope_filters import add_slope_filters
from filters.duration_gap_filters import add_duration_gap_filters
from filters.event_filters import add_event_filters
from filters.general_filters import add_general_filters
from config import TABLE_NAME


def collect_filters():
    filters = {}
    filters.update(add_time_filter_with_hour())
    filters.update(add_trend_filters())
    filters.update(add_slope_filters())
    filters.update(add_duration_gap_filters())
    filters.update(add_event_filters())
    filters.update(add_general_filters())
    return filters


def build_query(filters):
    query = f"SELECT * FROM {TABLE_NAME}"
    conditions, params = [], []
    timestamp_fields = ["vt_start_pre", "vt_end_pre", "vt_start_post", "vt_end_post", "vt"]
    selected_event = None

    for field, value in filters.items():
        if value is not None:
            if isinstance(value, tuple) and len(value) == 2:
                conditions.append(f"{field} BETWEEN %s AND %s")
                params.extend(value)
            elif field in timestamp_fields and isinstance(value, int):
                conditions.append(f"EXTRACT(HOUR FROM {field}) = %s")
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

    return conditions, params, selected_event
