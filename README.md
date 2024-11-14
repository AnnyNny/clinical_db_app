# Clinical Database Application
 This is my bachelor thesis app, dedicated to connecting to PostgreSQL database and visualizing trend-event pattern data, consisting of one table. It basically provides a graphical interface ad-hoc for medics to help them interrogate the specific table.
 The query is based on simple SELECT COUNT(*) FROM table WHERE params=params GROUP BY selected_filters_group_by.
 The data is converted to polars dataframe (but binning for parameters of is executed by pandas for now, since I couldn't fix the error with number of lables and bin groups) and then when users chooses the time slice they prefer
 (hour, month, year), the datetime columns are cut for the chosen option, the data is aggregated by count and sorted by count column in descending order. It will be seen both as a table and plot view with and without binning. 

## Features

- **Interactive Filters**: Filter data based on different parameters, including time, trends, slopes, duration gaps, events, and general filters.
- **Materialized View**: Added for smooth extracting of min, max values of the filters.
- **Group Options**: Allows users to select how data is grouped.
- **Top N Counts**: Allows users to choose how many most popular trends count to see.
- **Binned vs Non-Binned Views**: Allows users to compare binned and non-binned views.
- **Real-time Database Connection**: Connects to a database and shows the current connection time for verification.
- **Visualizations**: Uses Plotly to display data with bar plots.

## Setup Instructions
- Type in the terminal streamlit run app.py and it will open a local browser connection.

### Prerequisites

- **Python 3.7+**

### Dependencies

Install the required Python packages:
pip install streamlit polars pandas plotly psycopg2
