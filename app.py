import time
import streamlit as st
from database_utils import execute_query, execute_final_query
from filters.time_filters import add_time_filters
from filters.trend_filters import add_trend_filters
from filters.slope_filters import add_slope_filters
from filters.duration_gap_filters import add_duration_gap_filters
from filters.event_filters import add_event_filters
from filters.general_filters import add_general_filters
from query_builder import build_where_clause, build_final_query
from vis_with_polars import plot_result_with_binning_polars, apply_binning_to_decimal_p_value_columns
from group_by_filters import group_by_filters as gr

st.set_page_config(page_title="Trend-Event Pattern Analysis", layout="wide")
st.markdown("""
    <style>
    /* Hide the Streamlit header and menu */
    header {visibility: hidden;}
    .stApp {margin-top: -50px;} /* Adjusts layout after hiding header */
    </style>
    """, unsafe_allow_html=True)
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
    default=[g for g in gr if g["column_name"] in ["trend_pre", "trend_post", "p1_value"]]
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


time_slice = st.selectbox("**Choose time slice: (must always be chosen)\***", options=[None, "hour", "month", "year"])
if not time_slice:
    st.error("No time slice selected")
top_n = st.number_input(
    "**Choose how many most important counts you want (top_n). Important: top may be smaller than n than you expect if there is not enough unique combinations of groups**",
    min_value=1,
    max_value=1000,
    value=30,
    step=1,
    help="Will choose most popular n combinations"
)
max_bins = st.number_input(
    "**Choose how many bins you want (vital parameters of P1, P2, P3, P4 will be divided by n intervals. 0 bins if you want to see each value separately. Recommended for optimization purposes: 10 bins)**",
    min_value=0,
    max_value=25,
    value=10,
    step=1,
    help="Set to 0 if you don't want any binning."
)
my_bar = st.progress(0, text="Executing query and plotting may take 2-3 minutes. Please wait after clicking 'Visualize plot' button")
if st.button("Visualize plot"):
    final_query = build_final_query(where_query, selected_group_columns, selected_order_columns)
    if time_slice is not None:
        try:
            data = execute_final_query(final_query, params)
            if not data.is_empty():
                #st.write("DEBUGGING Query was executed")
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1)
                time.sleep(1)
                unbinned_data = data.clone()
                binned_data = apply_binning_to_decimal_p_value_columns(data, max_bins)

                st.subheader("Non-Binned Data View")
                plot_result_with_binning_polars(unbinned_data, top_n=top_n, max_bins=max_bins,time_slice=time_slice)
                st.divider()
                st.subheader("Binned Data View")
                plot_result_with_binning_polars(binned_data, top_n=top_n, max_bins=max_bins, time_slice=time_slice)

                #print("DEBUGGIN outside of plot result with binning")
            else:
                st.warning("** There is no such data. Try to change filter parameters **")
        except Exception as e:
            st.write("Query was not executed because of the error: ", e)
    else:
        st.write("Problem with time slice choosing")

