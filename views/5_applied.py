import streamlit as st
import pandas as pd
from parameters import Parameters 

def dataframe_with_selections(df: pd.DataFrame, init_value: bool = False) -> pd.DataFrame:
    df_with_selections = df.copy()
    #df_with_selections.insert(0, "Select", init_value)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        column_config={
            #"Select": st.column_config.CheckboxColumn("Select", required=True),
            "date": st.column_config.DateColumn("Date", help="The date of the job posting"),
            "status": st.column_config.TextColumn("Status", help="The status of the job posting"),
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
        },
        hide_index=True,
        num_rows= "fixed", # "dynamic",
        disabled=["date", "site", "title", "company", "location", "lang", 
                  "job_url", "city", "state", "description", "search_term"],
    )

    # Filter the dataframe using the temporary column, then drop the column
    #selected_rows = edited_df[edited_df.Select]
    #return selected_rows.drop('Select', axis=1) 

    return edited_df 




st.title('Applied Jobs')

selected_jobs = pd.read_parquet("data/selected_jobs.parquet")
selected_jobs = selected_jobs[selected_jobs['status'] == 'APPLIED']
selected_jobs = selected_jobs[Parameters.JOBS_SELECTED_COLUMNS]
selected_jobs = selected_jobs.sort_values(by='date', ascending=False)
selected_jobs = selected_jobs.drop_duplicates(subset=['title', 'company', 'location'])

# Get dataframe row-selections from user with st.data_editor
selected_df = dataframe_with_selections(selected_jobs)

#st.write("### Your selection:")
#st.write(selected_df)