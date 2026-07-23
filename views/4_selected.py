import streamlit as st
import pandas as pd
from parameters import Parameters
from cv_prompt import prompt

import os
import yaml

from dotenv import find_dotenv, load_dotenv
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI

def get_llm(**kwargs)-> ChatOpenAI:
    if kwargs.get("env") == "dev":
        dev_secrets = dotenv_values(".env-dev")
        api = dev_secrets["OPENROUTER_LLAMA4_MAVERICK_FREE"]
        api = dev_secrets["OPENROUTER_API_KEY"]
    elif kwargs.get("env") == "prod":
        dev_secrets = dotenv_values(".env")
        api = os.environ["OPENROUTER_LLAMA4_MAVERICK_FREE"]
        api = dev_secrets["OPENROUTER_API_KEY"]
    else:
        raise ValueError("Please set env to dev or prod")
    
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api,
        model=kwargs.get("model", "openrouter/quasar-alpha"),
        temperature=kwargs.get("temperature", 0.0),
        max_tokens=kwargs.get("max_tokens", 4096),
    )

## Read YAML file
#with open("config.yaml", 'r') as stream:
#    params = yaml.safe_load(stream)

# Function to handle button click
def button_click(title:str, company:str, description:str):
    #gemini2 = params['GEMINI2_MODEL']
    model_name = Parameters.GEMINI2_MODEL
    llm = get_llm(model=model_name, temperature=0.7, env="dev", max_tokens=8192) 

    system_prompt = """
                        You are a helpful assistant that generate a cover letter for a job application. The Job position was named \n
                        as {title} and the company name is {company}.
                        
                        Here is the job description: {description}

                        This generation should happen based on CV content given by the human as input. This generation should \n
                        be done in a professional way. The generated text should be in a formal tone and should be easy to read. \n
                        Do not copy the same content text by text. It should maintain some important keywords so that the ATS \n
                        should have a chance to pick the content and maintain similar context. Also try to give 2 sentences \n
                        about the company. Please consider the Profile or tasks, or Qualifications or Responsibilities \n
                        sections of the job description. Please ignore the unnecessary text in it. \n 
                        If the Job description is in German, then translate it to English and then generate the cover letter. \n\n             

                    """

    messages = [
        (
            "system",
            system_prompt.format(title=title, company=company, description=description),
        ),
        ("human", prompt),
    ]

    llm_message = llm.invoke(messages)

    st.write(f'Button clicked for {title}')
    #st.text_area(f"Here is the text created for {title}:", 
    #             value=f"Dear Hiring Manager,\n\nI am writing to express my interest in the {title} position. I believe my skills and experience make me a strong candidate for this role.\n\nBest regards,\nVamshi")
    st.text_area(
        f"Here is the text created for {title}:", 
        value = llm_message.text(),
        height=1000,
    )

def dataframe_with_selections(df: pd.DataFrame, init_value: bool = False) -> pd.DataFrame:
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", init_value)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        column_config={
            "Select": st.column_config.CheckboxColumn("Select", required=True),
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
        num_rows= "dynamic",
        disabled=["date", "site", "title", "company", "location", "lang", 
                  "job_url", "city", "state", "description", "search_term"],
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)  




st.title('Selected Jobs')

try:
    selected_jobs = pd.read_parquet("data/selected_jobs.parquet")    
    selected_jobs = selected_jobs[selected_jobs['status'] == 'OPEN']
    selected_jobs = selected_jobs[Parameters.JOBS_SELECTED_COLUMNS]
    selected_jobs = selected_jobs.sort_values(by='date', ascending=False)
    selected_jobs = selected_jobs.drop_duplicates(subset=['title', 'company', 'location'])

    if selected_jobs.shape[0] == 0:
        # write a markfown in a container streamlit component
        container = st.container(border=True)
        container.markdown("<h1 style='text-align: center; color: grey;'>Sorry</h1>", unsafe_allow_html=True)
        container.markdown("<h2 style='text-align: center; color: black;'>No Selected Jobs found 🙁</h2>", unsafe_allow_html=True)
        container.markdown("<h4 style='text-align: center; color: black;'>Please select some jobs from the Overview Page. 👈</h4>", unsafe_allow_html=True)
        # do the same for image center alignment
        container.markdown("<p style='text-align: center;'><img src='https://cdn.pixabay.com/photo/2020/04/22/18/22/excuse-me-5079442_1280.jpg' alt='Sorry' width='500' height='350'></p>", unsafe_allow_html=True)
    else: 
         # Get dataframe row-selections from user with st.data_editor
        selected_df = dataframe_with_selections(selected_jobs)

        st.write("### Your selection:")
        st.write(selected_df)
        

except:
    # write a markfown in a container streamlit component
    container = st.container(border=True)
    container.markdown("<h1 style='text-align: center; color: grey;'>Sorry</h1>", unsafe_allow_html=True)
    container.markdown("<h2 style='text-align: center; color: black;'>No Selected Jobs found 🙁</h2>", unsafe_allow_html=True)
    container.markdown("<h4 style='text-align: center; color: black;'>Please select some jobs from the Overview Page. 👈</h4>", unsafe_allow_html=True)
    # do the same for image center alignment
    container.markdown("<p style='text-align: center;'><img src='https://cdn.pixabay.com/photo/2020/04/22/18/22/excuse-me-5079442_1280.jpg' alt='Sorry' width='500' height='350'></p>", unsafe_allow_html=True)


if selected_df.shape[0] > 1:
    st.error(f"""
                You have selected {selected_df.shape[0]} jobs. Please select only 1 job. 🙁
                Please unselect {selected_df.shape[0]-1} jobs from the above table.
            """, icon="🚨")

else:
    for index, row in selected_df.iterrows():
        col1, col2, col3, col4 = st.columns([0.5, 0.5, 3.5, 1])
        col1.write(row['title'])
        col2.write(row['company'])
        #col3.write(row['description'])
        col3.text_area(
            'Description', row['description'], 
            height=100, disabled=True
        )
        if col4.button('Generate Cover Letter', key=index):
            button_click(row['title'], row['company'], row['description'])