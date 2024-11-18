import streamlit as st

time_constraints = [
    {"column_name": "vt_start_pre", "description": "Start of Pre-Trend", "filter_group": "time_constraints",
     "granularity": "hour", "value": None},
    {"column_name": "vt_start_pre", "description": "Start of Pre-Trend", "filter_group": "time_constraints",
     "granularity": "month", "value": None},
    {"column_name": "vt_start_pre", "description": "Start of Pre-Trend", "filter_group": "time_constraints",
     "granularity": "year", "value": None},

    {"column_name": "vt_end_pre", "description": "End of Pre-Trend", "filter_group": "time_constraints",
     "granularity": "hour", "value": None},
    {"column_name": "vt_end_pre", "description": "End of Pre-Trend", "filter_group": "time_constraints",
     "granularity": "month", "value": None},
    {"column_name": "vt_end_pre", "description": "End of Pre-Trend", "filter_group": "time_constraints",
     "granularity": "year", "value": None},

    {"column_name": "vt_start_post", "description": "Start of Post-Trend", "filter_group": "time_constraints",
     "granularity": "hour", "value": None},
    {"column_name": "vt_start_post", "description": "Start of Post-Trend", "filter_group": "time_constraints",
     "granularity": "month", "value": None},
    {"column_name": "vt_start_post", "description": "Start of Post-Trend", "filter_group": "time_constraints",
     "granularity": "year", "value": None},

    {"column_name": "vt_end_post", "description": "End of Post-Trend", "filter_group": "time_constraints",
     "granularity": "hour", "value": None},
    {"column_name": "vt_end_post", "description": "End of Post-Trend", "filter_group": "time_constraints",
     "granularity": "month", "value": None},
    {"column_name": "vt_end_post", "description": "End of Post-Trend", "filter_group": "time_constraints",
     "granularity": "year", "value": None},

    {"column_name": "vt", "description": "Time of event", "filter_group": "time_constraints", "granularity": "hour",
     "value": None},
    {"column_name": "vt", "description": "Time of event", "filter_group": "time_constraints", "granularity": "month",
     "value": None},
    {"column_name": "vt", "description": "Time of event", "filter_group": "time_constraints", "granularity": "year",
     "value": None}
]

def add_time_filters():
    months = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    with st.sidebar.expander("Time Constraints (Hour)", expanded=False):
        for i, constraint in enumerate(time_constraints):
            if constraint["granularity"] == "hour":
                description = constraint['description']
                enabled = st.checkbox(f"{description} (Hour)", value=False,
                                      key=f"{constraint['column_name']}_hour_checkbox_{i}")
                if enabled:
                    constraint["value"] = st.slider(f"Select hour for {description}", min_value=0, max_value=23,
                                                    value=9, key=f"{constraint['column_name']}_hour_slider_{i}")
                else:
                    constraint["value"] = None


    with st.sidebar.expander("Time Constraints (Month)", expanded=False):
        for i, constraint in enumerate(time_constraints):
            if constraint["granularity"] == "month":
                description = constraint['description']
                enabled = st.checkbox(f"{description} (Month)", value=False,key=f"{constraint['column_name']}_month_checkbox_{i}")
                if enabled:
                    selected_month = st.select_slider(f"Select month for {description}", options=months.keys(), key=f"{constraint['column_name']}_month_slider_{i}")
                    constraint["value"] = months[selected_month]

                else:
                    constraint["value"] = None


    with st.sidebar.expander("Time Constraints (Year)", expanded=False):
        for i, constraint in enumerate(time_constraints):
            if constraint["granularity"] == "year":
                description = constraint['description']
                enabled = st.checkbox(f"{description} (Year)", value=False,key=f"{constraint['column_name']}_year_checkbox_{i}")
                if enabled:
                    constraint["value"] = st.slider(f"Select year for {description}", min_value=2110, max_value=2211,
                                                    value=2110, key=f"{constraint['column_name']}_year_slider_{i}")
                else:
                    constraint["value"] = None

    return time_constraints


