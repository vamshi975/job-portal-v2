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
import plotly.express as px # version : plotly-6.0.0


# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme, range_min, range_max):
    choropleth = px.choropleth(
        input_df, locations=input_id, color=input_column, locationmode="USA-states",
        color_continuous_scale=input_color_theme,
        range_color=(range_min, range_max),
        scope="usa",
        labels={'population':'Population'}
    )

    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )

    return choropleth

alt.themes.enable("dark")
st.title('Job Trends')

# Define the options for the dropdown
options = [
    #"Option 1", "Option 2", 
    "Last 30 days"
]

selected_file = "data/last_30_days.parquet"

# Create the main content area using columns
left_pane, rest_pane = st.columns([1, 2])

# Use col2 for displaying the table
with rest_pane:
    # Read and display the content of the selected Parquet file
    try:
        df = pd.read_parquet(selected_file)
        df = df[df['search_term']!="AI"]

    except FileNotFoundError:
        st.error(f"The file {selected_file} was not found.")

    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")

# Filter the data based on the selected columns list
columns_filter = Parameters.COLUMNS_FILTER
df = df[columns_filter]

# Create a regular expression pattern that matches any of the substrings
rows_filter = Parameters.ROWS_FILTER
pattern = '|'.join(rows_filter)
df = df[~df['title'].str.lower().str.contains(pattern, case=False, na=False)]
df = df.sort_values(by='date', ascending=False)

# Filter the consultancy jobs
df = exclude_consultancy_jobs(df)

# cleaning nan values
df['state'] = df['state'].replace(np.nan, 'Unknown') 
df['company'] = df['company'].replace(np.nan, 'Unknown') 

# Creating the dynamic filters
dynamic_filters = DynamicFilters(df, Parameters.STREAMLIT_FILTERS)
dynamic_filters.display_filters(location='columns', num_columns=3, gap='large')
#dynamic_filters.display_filters(location='sidebar')
filtered_df = dynamic_filters.filter_df()

# reset button for dynamic filters all at once
if st.button("Reset Filters"):
    dynamic_filters.reset_filters()

# st.write(filtered_df)

## Widgets for Site Counts
st.subheader('Jobs by Scraping Sites')
row_col1, row_col2, row_col3 = st.columns(3)

site_counts = filtered_df[['date', 'site']].value_counts().reset_index()
site_counts = filtered_df.groupby(['date', 'site']).size().reset_index(name='num_of_jobs')

# Convert the 'Date' column to datetime
site_counts['date'] = pd.to_datetime(site_counts['date'])

# get number of sites
unique_sites = len(site_counts['site'].unique().tolist())

# Get the last 2 different dates
last_two_dates = site_counts['date'].drop_duplicates().nlargest(2).tolist()

# Filter the DataFrame to get all rows with the last 2 different dates
site_counts = site_counts[site_counts['date'].isin(last_two_dates)]

# Display the number of jobs in Indeed
with row_col1:
    try : 
        indeed_count = str(site_counts[(site_counts.site=="indeed") & (site_counts.date==last_two_dates[0])]["num_of_jobs"].values[0])
        indeed_diff = str(
            site_counts[(site_counts.site=="indeed") & (site_counts.date==last_two_dates[0])]["num_of_jobs"].values[0]
            - site_counts[(site_counts.site=="indeed") & (site_counts.date==last_two_dates[1])]["num_of_jobs"].values[0]
        )

    except IndexError:
        indeed_count = '0'
        indeed_diff = '0'

    row_col1.metric("Indeed", indeed_count, indeed_diff + ' (compared to previous run)', border=True)

# Display the number of jobs in Linkedin
with row_col2:
    try : 
        linkedin_count = str(site_counts[(site_counts.site=="linkedin") & (site_counts.date==last_two_dates[0])]["num_of_jobs"].values[0])
        linkedin_diff = str(
            site_counts[(site_counts.site=="linkedin") & (site_counts.date==last_two_dates[0])]["num_of_jobs"].values[0]
            - site_counts[(site_counts.site=="linkedin") & (site_counts.date==last_two_dates[1])]["num_of_jobs"].values[0]
        )
    except IndexError:
        linkedin_count = '0'
        linkedin_diff = '0'

    row_col2.metric("Linkedin", linkedin_count, linkedin_diff + ' (compared to previous run)', border=True)

# Display the number of jobs in Glassdoor
with row_col3:
    try: 
        glassdoor_count = site_counts[(site_counts.site=="glassdoor") & (site_counts.date==last_two_dates[0])]["num_of_jobs"]
        #if glassdoor_count.shape[0] == 0:
        #    glassdoor_count = '0'
        #    glassdoor_diff = '0'
        #else:
        glassdoor_count = str(glassdoor_count.values[0])
    
        glassdoor_diff = str(
            site_counts[(site_counts.site=="glassdoor") & (site_counts.date==last_two_dates[0])]["num_of_jobs"].values[0]
            - site_counts[(site_counts.site=="glassdoor") & (site_counts.date==last_two_dates[1])]["num_of_jobs"].values[0]
        )
    except IndexError:
        glassdoor_count = '0'
        glassdoor_diff = '0'

    row_col3.metric("Glassdoor", glassdoor_count, glassdoor_diff + ' (compared to previous run)', border=True)


# Get number of records based on date
date_counts = filtered_df['date'].value_counts().reset_index()
date_counts.columns = ['date', 'num_of_jobs']

# Create Bar Plot for category_counts
date_bar_chart = alt.Chart(date_counts).mark_bar().encode(
    x='monthdate(date):O',
    y='num_of_jobs:Q',
    color='monthdate(date):O'
).properties(
    title='Number of Jobs by given date', height=400,
)

# Display Bar Plot
st.subheader('Jobs by Date')
st.altair_chart(date_bar_chart, use_container_width=True)

# Creating Columns for Alignment
row1_left_column, row1_right_column = st.columns([2, 2], gap="small", border=True)

# Create a Plot for the popular job keywords
with row1_left_column:
    st.markdown("### Popular Job Keywords")

    # Get number of records based on each category
    search_term_counts = filtered_df['search_term'].value_counts().reset_index()
    search_term_counts.columns = ['search_term', 'num_of_jobs']

    st.dataframe(
        search_term_counts.head(15),
        column_order=("search_term", "num_of_jobs"),
        hide_index=True,
        width=800,
        height=570,
        column_config={
            "search_term": st.column_config.TextColumn("Keyword", help="The keyword used to search for jobs"),
            "num_of_jobs": st.column_config.ProgressColumn(
                "No. of Jobs",
                help="Total number of jobs for the given keyword",
                format="%f",
                min_value=0,
                max_value=max(search_term_counts.num_of_jobs),
            )
        }
    )

# Create a Plot for the Popular Job States
with row1_right_column:
    st.markdown('### Popular Job Postings (by State)')

    # Get number of records based on state
    state_counts = filtered_df['state'].value_counts().reset_index()
    state_counts.columns = ['state', 'num_of_jobs']
    state_counts = state_counts.sort_values(by='num_of_jobs', ascending=False).reset_index(drop=True)
    
    st.dataframe(
        state_counts.head(15),
        column_order=("state", "num_of_jobs"),
        hide_index=True,
        width=500,
        height=570,
        column_config={
            "state": st.column_config.TextColumn("State", help="The state of the job posting"),
            "num_of_jobs": st.column_config.ProgressColumn(
                "No. of Jobs",
                help="Total number of jobs for the given state",
                format="%f",
                min_value=0,
                max_value=max(state_counts.num_of_jobs),
            )
        }
    )



