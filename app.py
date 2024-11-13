import streamlit as st
from database_utils import execute_query, execute_final_query, count_unique_combinations
from filters.time_filters import add_time_filters
from filters.trend_filters import add_trend_filters
from filters.slope_filters import add_slope_filters
from filters.duration_gap_filters import add_duration_gap_filters
from filters.event_filters import add_event_filters
from filters.general_filters import add_general_filters
from query_builder import build_where_clause, build_final_query, build_final_query_extract_hour, \
    build_final_query_extract_hour1, build_final_query1
from vis_with_polars import plot_result_with_binning_polars
from visualization import dynamic_trend_analysis, plot_result_with_binning, plot_result_with_binning1
from group_by_filters import group_by_filters as gr
from streamlit_sortables import sort_items

st.set_page_config(page_title="Trend-Event Pattern Analysis", layout="wide")
st.markdown( """ <style> .stDeployButton {display: none;} [data-testid="stStatusWidget"] {visibility: hidden;} </style> """, unsafe_allow_html=True)
st.title("Clinical Database Application")

if "reordered_columns" not in st.session_state:
    st.session_state["reordered_columns"] = None
try:
    results = execute_query("SELECT NOW();")
    st.success(f"Database connected. Current time: {results[0][0]}")
except Exception as e:
    st.error(f"Failed to connect to database: {e}")

st.sidebar.title("Filter Panel")
st.sidebar.write("Select your filters below.")

filters = []
filters.extend(add_time_filters())
filters.extend(add_duration_gap_filters())
filters.extend(add_event_filters())
filters.extend(add_general_filters())
filters.extend(add_trend_filters())
filters.extend(add_slope_filters())

#st.sidebar.write("Selected Filters:")
#for selected_filter in filters:
    #st.sidebar.write(f"- {selected_filter['description'], selected_filter['value']}")"""

where_query, params = build_where_clause(filters)
#st.write("Executed query", where_query, "with params", params, "total count", execute_query(where_query, params))

group_by_filters = st.sidebar.multiselect(
    "Choose how to group your data:",
    options=gr,
    format_func=lambda f: f["description"],
    default=None
)

st.sidebar.write("Selected groups:")
for i, selected_filter in enumerate(group_by_filters):
    st.sidebar.write(f"{i+1}) {selected_filter['description']}")

order_by_filters = st.sidebar.multiselect(
    "Choose order in which we will group:",
    options=group_by_filters,
    format_func=lambda f: f["description"],
    default=None
)

st.sidebar.write("Selected order:")
for selected_filter in order_by_filters:
    st.sidebar.write(f"- {selected_filter['description']}")

selected_group_columns = [f["column_name"] for f in group_by_filters]
selected_order_columns = [f["column_name"] for f in order_by_filters]

#if st.sidebar.button("Create final query:"):
    #final_query = build_final_query(where_query, selected_group_columns, selected_order_columns)
    #st.write("Final query 1", final_query)
    #final_query2 = build_final_query_extract_hour(where_query, selected_group_columns, selected_order_columns)
    #st.write("Final query 2", final_query2)
time_slice = st.selectbox("**choose time slice:**", options=[None, "hour", "month", "year"])
top_n = st.number_input("**choose how many most important counts you want (top_n)**", min_value=1, max_value=100, value=30, step=1)
max_bins = st.number_input("**choose how many bins you want (max_bins)**", min_value=1, max_value=25, step=1, value=10, placeholder="leave empty if you dont want any bins")
if st.button("Visualize plot"):
    final_query = build_final_query(where_query, selected_group_columns, selected_order_columns)
    if time_slice is not None:
        try:
            data = execute_final_query(final_query, params)
            if not data.is_empty():
                st.write("Query was executed")
                plot_result_with_binning_polars(data, time_slice=time_slice, top_n=top_n, max_bins=max_bins)
                print("outside of plot result with binning")
            else:
                st.write("Query was not executed")
        except Exception as e:
            st.write("Query was not executed because of the error: ", e)
    else:
        st.write("Problem with time slice choosing")

#st.write("Final query (after rerunning) is:", st.session_state.final_query1,
         #"\n\n\nother variant of query: ",st.session_state.final_query2)

"""if st.sidebar.button("Execute final query1:"):
    with st.spinner(text="Executing, wait 2-3 minutes..."):
        final_query = build_final_query(where_query, selected_group_columns, selected_order_columns)
        st.session_state.final_result1 = execute_final_query(final_query, params)
if st.sidebar.button("Execute final query2:"):
    with st.spinner(text="Executing, wait 2-3 minutes..."):
        st.session_state.final_result2 = execute_final_query(st.session_state.final_query2, params)

if st.session_state.final_result1 is not None:
    st.write("Final query", st.session_state.final_query1, "executed successfully.")

if st.session_state.final_result1 is not None:
    st.write("Final query", st.session_state.final_query2, "executed successfully.")"""

#if st.sidebar.button("Visualize plot"):
    #plot_result_with_binning1(st.session_state.final_result2)
"""group_by_filters = st.sidebar.multiselect(
    "Choose fields to group by:",
    options=filters,
    format_func=lambda f: f["description"] + (" " + f["granularity"] if "granularity" in f else ""),
    default=None
)
selected_group_by_columns = [
    {"column_name": g["column_name"], "granularity": g.get("granularity")}
    for g in group_by_filters
]
st.sidebar.write("Selected fields to group by:")
for selected_filter in group_by_filters:
    st.sidebar.write(f"- {selected_filter['description']} ({selected_filter.get('granularity', 'No granularity specified')})")

order_by_filters = st.sidebar.multiselect(
    "Choose order in which we will group:",
    options=group_by_filters,
    format_func=lambda f: f["description"] + (" " + f["granularity"] if "granularity" in f else ""),
    default=None
)
#selected_order_by_columns = [o["column_name"] for o in order_by_filters]
selected_order_by_columns = [
    {"column_name": o["column_name"], "granularity": o.get("granularity")}
    for o in order_by_filters
]
with st.spinner("Wait 2-3 minutes for catching result from the table"):
    if st.sidebar.button("Build query that is processed in sql (dynamically extracts chosen granularity and bins p1-p4)"):
        st.session_state.final_query[0] = build_final_query_extract_hour1(where_query, selected_group_by_columns, selected_order_by_columns)
        st.write("Query 1 (sql processed):", st.session_state.final_query[0])
    # problem with this query is that if user chooses when grouping e.g. pre_trend in month and pre_trend in hour, it is not reflected in query
    if st.sidebar.button("Build simple query that will be processed with pandas later"):
        st.session_state.final_query[1] = build_final_query1(where_query, selected_group_by_columns, selected_order_by_columns)
        st.write("Query 2 (simple):", st.session_state.final_query[1])
    if st.session_state.final_query[0] is not None:
        if st.sidebar.button("execute Query 1: SQL processed"):
            st.session_state.final_result[0] = execute_final_query(st.session_state.final_query[0], params)
            if st.session_state.final_result[0] is not None:
                st.write("caught results of query 1")
                unique_combinations = count_unique_combinations(st.session_state.final_result[0])
                st.write("Count of unique combinations: ", unique_combinations)

    if st.session_state.final_query[1] is not None:
        if st.sidebar.button("execute Query 2: Simple query (will be Pandas processed)"):
            st.session_state.final_result[1] = execute_final_query(st.session_state.final_query[1], params)
            if st.session_state.final_result[1] is not None:
                st.write("caught results of query 2")
                unique_combinations = count_unique_combinations(st.session_state.final_result[1])
                st.write("Count of unique combinations: ", unique_combinations)


st.sidebar.write("### Dynamic Trend Analysis")
#enable_binning = st.sidebar.checkbox("Enable Binning for Numeric Fields")
#if enable_binning:
    #num_bins = st.sidebar.slider("Number of bins", 1, 100, 10)
    #st.session_state.num_bins = num_bins

if st.sidebar.button("Calculate combinations with query sql"):
    plot_result_with_binning(st.session_state.final_result[0])

if st.sidebar.button("Calculate combinations with query (pandas will process)"):
    plot_result_with_binning(st.session_state.final_result[1])"""

"""# Dynamic Grouping and Visualization Section
st.sidebar.write("### Dynamic Trend Analysis")
# Checkbox to enable optional binning
#enable_binning = st.sidebar.checkbox("Enable Binning for Numeric Fields")
groupable_fields = filters.keys()
if groupable_fields:
    selected_groups = st.sidebar.multiselect("Choose fields to group by:", groupable_fields, max_selections=4)
    with st.sidebar.expander("ℹ️ ***Hint: Is the order of how I group important?***"):
        st.write(
            "The order in which you select fields to group by can change the visualization. " 
            "\n\nExperiment with different order to see how it changes the analysis."
        )
    order_by = st.sidebar.selectbox("Order by", [it for it in selected_groups])
    # Dynamic Trend Analysis with binning option
    if selected_groups:
        with st.spinner("Generating your plot... This may take a few moments."):
            dynamic_trend_analysis(selected_groups, conditions, params, selected_event, enable_binning=False)
    else:
        st.sidebar.write("No groupable fields selected yet.")"""
