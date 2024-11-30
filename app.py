import asyncio
import time
import streamlit as st
from database_utils import execute_final_query, check_db_status
from filters.time_filters import add_time_filters
from filters.trend_filters import add_trend_filters
from filters.slope_filters import add_slope_filters
from filters.duration_gap_filters import add_duration_gap_filters
from filters.event_filters import add_event_filters
from filters.general_filters import add_general_filters
from query_builder import build_where_clause, build_final_query
from vis_with_polars import apply_binning_to_decimal, apply_time_slicing, plot_unbinned, plot_binned
from group_by_filters import group_by_filters as gr

import cProfile
import pstats
import io
from contextlib import redirect_stdout


def profile_function(func, *args, **kwargs):
    """
    Profiles the execution of a given function and prints the profiling results.

    Parameters:
        func (callable): The function to profile.
        *args: Arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The return value of the profiled function.
    """
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    # Generate profiling stats
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats(pstats.SortKey.TIME)  # Sort by time
    stats.print_stats(20)  # Show top 20 slowest operations

    # Print profiling results to Streamlit app
    with redirect_stdout(stream):
        st.text("Profiling Results:\n" + stream.getvalue())

    return result


# Utility to measure execution time
def measure_time(label, func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    elapsed_time = time.time() - start_time
    st.info(f"{label} took {elapsed_time:.2f} seconds.")
    return result


@st.cache_data
def load_legend_content():
    """Load legend content for explanations."""
    with open("./texts/legend.md", "r") as file:
        return file.read()


def setup_page():
    """Set up the Streamlit page configuration and layout."""
    st.set_page_config(page_title="Trend-Event Pattern Analysis", layout="wide")
    st.markdown(
        """
        <style>
        header {visibility: hidden;}
        .stApp {margin-top: -50px;}
        .stDeployButton {display: none;}
        [data-testid="stStatusWidget"] {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Clinical Database Application")
    markdown_content = load_legend_content()
    with st.expander("🖼️ Figure of Trend-Event Pattern", expanded=True):
        st.image("./screenshots/trend_event_img.png")
    with st.expander("ℹ️ Parameters explanations", expanded=False):
        st.markdown(markdown_content, unsafe_allow_html=True)


def create_filter_panel():
    """Create the filter panel on the sidebar."""
    st.sidebar.title("Filter Panel")
    st.sidebar.write("Select your filters below.")
    filters = []
    filters.extend(add_time_filters())
    filters.extend(add_duration_gap_filters())
    filters.extend(add_event_filters())
    filters.extend(add_general_filters())
    filters.extend(add_trend_filters())
    filters.extend(add_slope_filters())
    return filters


def select_group_by_filters():
    """Allow users to select group-by filters."""
    group_by_selection = st.sidebar.multiselect(
        "Choose how to group your data:",
        options=gr,
        format_func=lambda f: f["description"],
        default=[g for g in gr if g["column_name"] in ["trend_pre", "trend_post"]],
    )
    st.sidebar.write("Selected groups:")
    for i, selected_filter in enumerate(group_by_selection):
        st.sidebar.write(f"{i + 1}) {selected_filter['description']}")
    return [f["column_name"] for f in group_by_selection]


def get_bins_and_top_n_configuration():
    """Get user configuration for bins and Top-N selection."""
    with st.expander("**Configuration**"):
        left_top_n, right_max_bins = st.columns(2)
    with left_top_n:
        top = st.number_input(
            "**Choose Top-N:**",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            help="Will choose the most popular N combinations.",
        )
    with right_max_bins:
        bins = st.number_input(
            "**Choose number of bins:**",
            min_value=0,
            max_value=25,
            value=5,
            step=1,
            help="Set to 0 if you don't want any binning.",
        )
    return bins, top


@st.cache_data
def execute_cached_query(final_query, params):
    """Execute and cache query results."""
    return execute_final_query(final_query, params)


@st.cache_data
def apply_cached_time_slicing(data, time_slice):
    """Apply time slicing and cache results."""
    return apply_time_slicing(data, time_slice)


@st.cache_data
def apply_cached_binning(data, max_bins):
    """Apply binning and cache results."""
    return apply_binning_to_decimal(data, max_bins)


def visualize_data(unbinned_data, binned_data, top_n=None):
    toggle_label = (
        "View Non-Binned Data"
        if st.session_state.show_binned
        else "View Binned Data (Recommended if you choose many groups)"
    )
    if st.button(toggle_label):
        st.session_state.show_binned = not st.session_state.show_binned

    if st.session_state.show_binned:
        st.subheader("Current: Binned Data View")
        plot_binned(binned_data, top_n=top_n)
        st.session_state.show_binned = not st.session_state.show_binned
    else:
        st.subheader("Current: Non-Binned Data View")
        plot_unbinned(unbinned_data)
        st.session_state.show_binned = not st.session_state.show_binned




def main():
    setup_page()
    check_db_status()

    where_filters = create_filter_panel()
    where_query, params = build_where_clause(where_filters)
    selected_group_columns = select_group_by_filters()

    time_slice = st.selectbox(
        "**Choose time slice:**", options=[None, "hour", "month", "year"]
    )
    if not time_slice:
        st.error("No time slice selected.")
        return

    max_bins, top_n = get_bins_and_top_n_configuration()
    st.write("Number of bins:", max_bins)
    st.write("Top Events:", top_n)


    my_bar = st.progress(0, text="Executing query and plotting may take 2-3 minutes.")
    st.session_state.setdefault("visualize_clicked", False)
    #st.session_state.setdefault("show_binned", True)


    # Visualization button logic
    if st.button("Visualize plot") or st.session_state.visualize_clicked:
        st.session_state.visualize_clicked = True


        # Build and execute the query
        final_query = build_final_query(where_query, selected_group_columns)
        try:
            data = measure_time(
                "Query execution", execute_cached_query, final_query, params
            )


            if data.empty:
                st.warning("No data available. Try adjusting filter parameters.")
                return

            # Apply time slicing and binning with caching
            data = measure_time(
                "Time slicing", apply_cached_time_slicing, data, time_slice
            )
            binned_data = measure_time(
                "Binning", apply_cached_binning, data, max_bins
            )

            # Display cardinality
            st.sidebar.write("Column Cardinality:")
            cardinality = {col: data[col].nunique() for col in data.columns}
            for col, unique_values in cardinality.items():
                st.sidebar.write(f"{col}: {unique_values} unique values")

            # Render visualizations
            measure_time("Visualization rendering", visualize_data, data, binned_data, top_n)

        except Exception as e:
            st.error(f"Query execution failed: {e}")


if __name__ == "__main__":
    main()
