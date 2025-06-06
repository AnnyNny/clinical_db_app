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
- in the file docker-compose.yml you need to insert your own database connection variables.

### Prerequisites
for installing on Windows
- **Python 3.12**
- **PostgreSQL** 17 https://www.postgresql.org/download/
- **Docker Desktop** https://docs.docker.com/desktop/setup/install/windows-install/

### Dependencies
1) Navigate to project folder in terminal
2) docker-compose up --build
3) http://localhost:8501


## Screenshots

### Main Page
![Main Page](screenshots/main_page.png)

### Filter Panel
![Filter Panel](screenshots/filter_panel1.png)
![Filter Panel](screenshots/filter_panel2.png)

### Comparison of Binned and Non-Binned Views
![Comparison View](screenshots/binned_table_and_plot.png)
![Comparison View](screenshots/unbinned_plot.png)

### Sequence Diagram
![Sequence Diagram](screenshots/sequence_diagram.png)
### Use Case Diagram
![USe Case Diagram](screenshots/use_case.png)
