import re
import time
import streamlit as st
from database_utils import execute_query, execute_final_query, check_db_status
from filters.time_filters import add_time_filters
from filters.trend_filters import add_trend_filters
from filters.slope_filters import add_slope_filters
from filters.duration_gap_filters import add_duration_gap_filters
from filters.event_filters import add_event_filters
from filters.general_filters import add_general_filters
from query_builder import build_where_clause, build_final_query
from vis_with_polars import plot_result_with_binning_polars, apply_binning_to_decimal_p_value_columns, \
    plot_result_with_binning_polars_lazy
from group_by_filters import group_by_filters as gr

def measure_time(label, func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    elapsed_time = time.time() - start_time
    st.info(f"⏱️ {label} took {elapsed_time:.2f} seconds.")
    return result

def setup_page():
    st.set_page_config(page_title="Trend-Event Pattern Analysis", layout="wide")
    st.markdown("""
        <style>
        header {visibility: hidden;}
        .stApp {margin-top: -50px;}
        </style>
        """, unsafe_allow_html=True)
    st.markdown( """ <style> .stDeployButton {display: none;} [data-testid="stStatusWidget"] {visibility: hidden;} </style> """, unsafe_allow_html=True)
    st.title("Clinical Database Application")

def get_filters():
    filters = []
    filters.extend(add_time_filters())
    filters.extend(add_duration_gap_filters())
    filters.extend(add_event_filters())
    filters.extend(add_general_filters())
    filters.extend(add_trend_filters())
    filters.extend(add_slope_filters())
    return filters

if "reordered_columns" not in st.session_state:
    st.session_state["reordered_columns"] = None

setup_page()
check_db_status()

st.sidebar.title("Filter Panel")
st.sidebar.write("Select your filters below.")

filters = get_filters()
where_query, params = build_where_clause(filters)
#st.write("Executed query", where_query, "with params", params, "total count", execute_query(where_query, params))

group_by_filters = st.sidebar.multiselect(
    "Choose how to group your data:",
    options=gr,
    format_func=lambda f: f["description"],
    default=[g for g in gr if g["column_name"] in ["trend_pre", "trend_post"]]
)
selected_group_columns = [f["column_name"] for f in group_by_filters]
st.sidebar.write("Selected groups:")
for i, selected_filter in enumerate(group_by_filters):
    st.sidebar.write(f"{i+1}) {selected_filter['description']}")

order_by_filters = st.sidebar.multiselect(
    "Choose order in which we will group:",
    options=group_by_filters,
    format_func=lambda f: f["description"],
    default=group_by_filters
)

st.sidebar.write("Selected order:")
for selected_filter in order_by_filters:
    st.sidebar.write(f"- {selected_filter['description']}")


selected_order_columns = [f["column_name"] for f in order_by_filters]


time_slice = st.selectbox("**Choose time slice: (must always be chosen)\***", options=[None, "hour", "month", "year"])
if not time_slice:
    st.error("No time slice selected")

with st.expander("**Configuration**"):
    left_top_n, right_max_bins = st.columns(2)
with left_top_n:
    top_n = st.number_input(
    "**Choose how many most important counts you want (top_n). Important: top may be smaller than n than you expect if there is not enough unique combinations of groups**",
    min_value=1,
    max_value=100,
    value=20,
    step=1,
    help="Will choose most popular n combinations"
)
with right_max_bins:
    max_bins = st.number_input(
        "**Choose how many bins you want (vital parameters of P1, P2, P3, P4 will be divided by n intervals. 0 bins if you want to see each value separately. Recommended for optimization purposes: less bins)**",
        min_value=0,
        max_value=25,
        value=7,
        step=1,
        help="Set to 0 if you don't want any binning."
    )
st.write("Number of bins:", max_bins)
st.write(f"Top Events:", top_n)
my_bar = st.progress(0, text="Executing query and plotting may take 2-3 minutes.")


if 'visualize_clicked' not in st.session_state:
    st.session_state.visualize_clicked = False
if 'show_binned' not in st.session_state:
    st.session_state.show_binned = True

def visualize_callback():
    st.session_state.visualize_clicked = True

def toggle_view():
    st.session_state.show_binned = not st.session_state.show_binned

if (
    st.button("Visualize plot", on_click=visualize_callback())
    or st.session_state.visualize_clicked
) and time_slice:

    final_query = build_final_query(where_query, selected_group_columns, selected_order_columns)
    try:
        data = execute_final_query(final_query, params)
        cardinality = {col: data[col].nunique() for col in data.columns}
        st.sidebar.write("Column Cardinality:")
        for col, unique_values in cardinality.items():
            st.sidebar.write(f"{col}: {unique_values} unique values")
        #data = measure_time("Executing final query", execute_final_query, final_query, params)
        if not data.empty:

            unbinned_data = data.copy()
            binned_data = apply_binning_to_decimal_p_value_columns(data, max_bins)
            #binned_data = measure_time("Applying binning to data", apply_binning_to_decimal_p_value_columns, data,max_bins)

            toggle_label = "View Non-Binned Data" if st.session_state.show_binned else "View Binned Data"
            if st.button(toggle_label, on_click=toggle_view):
                pass

            if st.session_state.show_binned:
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1)
                time.sleep(1)
                st.subheader("Binned Data View")
                plot_result_with_binning_polars(binned_data, top_n=top_n, max_bins=max_bins, time_slice=time_slice)
                st.divider()
                #plot_result_with_binning_polars_lazy(binned_data, top_n=top_n, max_bins=max_bins,time_slice=time_slice)

            else:
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1)
                time.sleep(1)
                st.subheader("Non-Binned Data View (keeps vital parameters P1-P4 separated, can become very slow)")
                plot_result_with_binning_polars(unbinned_data, top_n=top_n, max_bins=max_bins, time_slice=time_slice)
                st.divider()
                #plot_result_with_binning_polars_lazy(unbinned_data, top_n=top_n, max_bins=max_bins, time_slice=time_slice)


            st.divider()
        else:
            st.warning("** There is no such data. Try to change filter parameters **")
    except Exception as e:
        st.write("Query was not executed because of the error: ", e)


