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

def main():
    st.title('Analysis')
    
    # Set page layout to wide mode
    ##st.set_page_config(layout="wide")
    
    # Define the options for the dropdown
    options = [
        #"Option 1", "Option 2", 
        "Last 30 days"
    ]

    # Display filters in the sidebar
    st.sidebar.write("### Filters")


    # Create a dropdown (selectbox) in the sidebar. Index is the index of the list in the options list
    selected_option = st.sidebar.selectbox("Select the Data:", options, index=0)

    # Define the files corresponding to each option
    files = {
        #"Option 1": "data/last_7_days.parquet",
        #"Option 2": "data/last_14_days.parquet",
        "Last 30 days": "data/last_30_days.parquet"
    }

    ## Display the selected option
    #st.write(f"You selected: {selected_option}")

    # Get the corresponding file based on the selected option
    selected_file = files[selected_option]

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

    # Filter by source
    selected_site = st.sidebar.multiselect("Select the Job Site", df['site'].unique())

    # Filter by State
    selected_state = st.sidebar.multiselect("Select the State", df['state'].unique(), 
                                            default=['Bayern', 'Baden-Württemberg', 
                                                     'Nordrhein-Westfalen', 'Hamburg', 
                                                     'Hessen', 'Rheinland-Pfalz'])
    
    # Filter by City
    selected_city = st.sidebar.multiselect("Select the City", df['city'].unique())

    # Filter by categorical column (e.g., Gender)
    #selected_language = st.sidebar.multiselect("Select Language", df['language'].unique())
    selected_term= st.sidebar.multiselect("Select the Job Skill Term", df['search_term'].unique())

    # Filter by language
    selected_language = st.sidebar.multiselect("Select the Job Posting Language", df['lang'].unique())

    ## Filter by location
    #selected_location = st.sidebar.multiselect("Select Location", df['location'].unique())

    # Filter by Company
    companies = [company for company in df['company'].unique() if company is not None]
    selected_company = st.sidebar.multiselect("Select the Company", companies)

    

    # Filter the data based on the selected
    filtered_df = df

    #if selected_language:
    if selected_term:
        #filtered_df = df[df['language'].isin(selected_language)]
        filtered_df = df[df['search_term'].isin(selected_term)]
    
    if selected_site:
        filtered_df = filtered_df[filtered_df['site'].isin(selected_site)]

    if selected_language:
        filtered_df = filtered_df[filtered_df['lang'].isin(selected_language)]
    
    #if selected_location:
    #    filtered_df = filtered_df[filtered_df['location'].isin(selected_location)]
    
    if selected_state:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_state)]

    if selected_city:
        filtered_df = filtered_df[filtered_df['city'].isin(selected_city)]

    if selected_company:
        filtered_df = filtered_df[filtered_df['company'].isin(selected_company)]

    # Get number of records based on each category
    search_term_counts = filtered_df['search_term'].value_counts().reset_index()
    search_term_counts.columns = ['search_term', 'num_of_jobs']

    # Create Bar Plot for category_counts
    search_term_bar_chart = alt.Chart(search_term_counts).mark_bar().encode(
        #x='search_term:O',
        x=alt.X('search_term', sort='-y'), 
        y='num_of_jobs:Q',
        color='search_term:N'
    ).properties(
        title='Number of Jobs by given Keywords',
    )

    # Display Bar Plot
    st.subheader('Jobs by Keywords')
    st.altair_chart(search_term_bar_chart, use_container_width=True)

    # Get number of records based on date
    date_counts = filtered_df['date'].value_counts().reset_index()
    date_counts.columns = ['date', 'num_of_jobs']
    
    # Create Bar Plot for category_counts
    date_bar_chart = alt.Chart(date_counts).mark_bar().encode(
        x='monthdate(date):O',
        y='num_of_jobs:Q',
        color='monthdate(date):O'
    ).properties(
        title='Number of Jobs by given date',
    )

    # Display Bar Plot
    st.subheader('Jobs by Date')
    st.altair_chart(date_bar_chart, use_container_width=True)


    # Get number of records based on state
    state_counts = filtered_df['state'].value_counts().reset_index()
    state_counts.columns = ['state', 'num_of_jobs']
    state_counts = state_counts.sort_values(by='num_of_jobs', ascending=False).reset_index(drop=True)
    #print(state_counts)
    
    # Create Bar Plot for category_counts
    state_bar_chart = alt.Chart(state_counts).mark_bar().encode(
        x=alt.X('state', sort='-y'), 
        #x='state:O',
        y='num_of_jobs:Q',
        color='state:N'
    ).properties(
        title='Number of Jobs by given state',
    )

    # Display Bar Plot
    st.subheader('Jobs by state')
    st.altair_chart(state_bar_chart, use_container_width=True)



    st.write(f"Consists of {filtered_df.shape[0]} records and {filtered_df.shape[1]} columns.")
    st.dataframe(filtered_df, height=500, width=800)

if __name__ == '__main__':
    main()