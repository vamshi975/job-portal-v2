import streamlit as st
import pandas as pd
import numpy as np
import subprocess
from datetime import datetime, timedelta
from parameters import Parameters
from utils import detect_language
import altair as alt
from utils import exclude_consultancy_jobs
from streamlit_dynamic_filters import DynamicFilters
from streamlit_extras.switch_page_button import switch_page  # streamlit-extras-0.5.5

def dataframe_with_selections(df: pd.DataFrame, init_value: bool = False) -> pd.DataFrame:
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", init_value)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        column_config={
            "Select": st.column_config.CheckboxColumn("Select", required=True),
            "date": st.column_config.DateColumn("Date", help="The date of the job posting"),
            "site": st.column_config.TextColumn("Site", help="The website where the job was posted"),
            "title": st.column_config.TextColumn("Title", help="The title of the job posting"),
            "company": st.column_config.TextColumn("Company", help="The company offering the job"),
            "location": st.column_config.TextColumn("Location", help="The location of the job"),
            #"job_type": st.column_config.TextColumn("Job Type", help="The type of job"),
            "lang": st.column_config.TextColumn("Language", help="The language of the job posting"),
            "job_url": st.column_config.LinkColumn("Job URL", help="The URL of the job posting"),
            "city": st.column_config.TextColumn("City", help="The city of the job"),
            "state": st.column_config.TextColumn("State", help="The state of the job"),
            "description": st.column_config.TextColumn("Description", help="The description of the job"),
            "search_term": st.column_config.TextColumn("Search Term", help="The search term used to find the job"),
            "uuid": st.column_config.TextColumn("UUID", help="The UUID of the job posting"),
        },
        hide_index=True,
        num_rows= "dynamic",
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows


st.title('Jobs Board')

# Define the options for the dropdown
options = [
    #"Option 1", "Option 2", 
    "Last 30 days"
]

# Display filters in the sidebar
#st.sidebar.write("### Filters")

selected_file = "data/last_30_days.parquet"

# Create the main content area using columns
left_pane, rest_pane = st.columns([1, 2])

# Use col2 for displaying the table
with rest_pane:
    # Read and display the content of the selected Parquet file

    try:
        df = pd.read_parquet(selected_file)
        df = df[df['search_term']!="AI"]
        #print(df.columns)

        #st.write(f"Consists of {df.shape[0]} records and {df.shape[1]} columns.")
        #st.dataframe(df, height=600, width=800)
    except FileNotFoundError:
        st.error(f"The file {selected_file} was not found.")
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")

# Filter the data based on the selected columns list
columns_filter = Parameters.COLUMNS_FILTER
df = df[columns_filter]


rows_filter = Parameters.ROWS_FILTER
# Create a regular expression pattern that matches any of the substrings
pattern = '|'.join(rows_filter)
df = df[~df['title'].str.lower().str.contains(pattern, case=False, na=False)]
df = df.sort_values(by='date', ascending=False)

# Filter the consultancy jobs
df = exclude_consultancy_jobs(df)

# cleaning nan values
df['state'] = df['state'].replace(np.nan, 'Unknown') 
df['company'] = df['company'].replace(np.nan, 'Unknown') 

dynamic_filters = DynamicFilters(df, Parameters.STREAMLIT_FILTERS)
dynamic_filters.display_filters(location='columns', num_columns=3, gap='large')
#dynamic_filters.display_filters(location='sidebar')

filtered_df = dynamic_filters.filter_df()

#dynamic_filters.display_df(height=650, width=1800)

# reset button for dynamic filters all at once
if st.button("Reset Filters"):
    dynamic_filters.reset_filters()

st.info(f"Consists of {filtered_df.shape[0]} records and {filtered_df.shape[1]} columns.")

# Get dataframe row-selections from user with st.data_editor
selected_df = dataframe_with_selections(filtered_df)

col1, col2 = st.columns([1, 1])
col2.button("Remove Selection", type="primary", use_container_width=True)
if col1.button("Save Selection", use_container_width=True):
    # check if parquet already exists or not
    try:
        selected_archived_jobs = pd.read_parquet("data/selected_jobs.parquet")
        selected_df['status'] = 'OPEN'
        selected_df = selected_df.drop('Select', axis=1)  
        selected_archived_jobs = pd.concat([selected_archived_jobs, selected_df], ignore_index=True)
        selected_archived_jobs.to_parquet("data/selected_jobs.parquet", index=False)

    except FileNotFoundError:
        selected_df['status'] = 'OPEN'
        selected_df = selected_df.drop('Select', axis=1)
        selected_jobs = selected_df.to_parquet("data/selected_jobs.parquet", index=False)

    st.write("### Your selection:")
    st.write(selected_df)
    st.info("Selection saved successfully.")

else:
    selected_df['Select'] = False
    selected_df = pd.DataFrame()
    st.info("Selection removed successfully.")

# st.write("### Your selection:")
# st.write(selected_df)




