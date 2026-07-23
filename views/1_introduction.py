import streamlit as st



st.write('# Introduction')

st.write("\n")
st.write(
        '''
            This app gives you the ability to understand the job market for Data Analyst/Scientist in the Germany. 
            The app is divided into the following sections:
        '''
)
st.write("\n")



st.write('### Overview Page')
container1 = st.container(border=True)

container1.write(
        '''
            - This shows the raw data acquired from the Job Sites. And it allows the user to do the following tasks:
                - **Filtering** :Filter the data based on several filters. Upon selecting the necessary filters, the results were displayed in a table.
                - **Selection**: Select the Job Postings for the next stage of creating a Cover Letter using GenAI.
                - **Saving**: We can also see the selected Job Postings in the Result Table. You can save any number of Job Postings for the next stage.
        '''
)
st.write("\n")

st.write('### Job Insights Page')
container2 = st.container(border=True)
container2.write(
        '''
            - Here we can see the insights of the data. And it allows the user to do the following tasks:
                - **Filtering**: Filter the data based on several filters. Upon selecting the necessary filters, get the relevant KPIs get populated.
                - **Insights**: The insights are displayed in the form of graphs/table.
        '''
)
st.write("\n")

st.write('### Selected Jobs Page')
container3 = st.container(border=True)
container3.write(
        '''
            - Here, we will see all the selected Job Postings. And it allows the user to do the following tasks:
                - **TODO**: For each Job Posting, we should be able to create a cover letter using GenAI as pieces. 
                - **Ex**: About Company, User Technical and Soft Skills, Language Skills etc. according to the job posting.
                - **TODO**: The user should be able to see the relevancy score of the selected job posting against the user profile.
        '''
)    



#script = """<div id = 'chat_outer'></div>"""
#st.markdown(script, unsafe_allow_html=True)
#st.text("Random outer text")

#plh = st.container()
#with plh:
#    script = """<div id = 'chat_inner'></div>"""
#    st.markdown(script, unsafe_allow_html=True)
#    st.text("Random inner text")



## applying style
#chat_plh_style = """<style>
#div[data-testid='stVerticalBlock']:has(div#chat_inner):not(:has(div#chat_outer)) {background-color: #E4F2EC};
#</style>
#"""

#st.markdown(chat_plh_style, unsafe_allow_html=True) 



import pandas as pd



# Initialize data (you can load from a file or database)
if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({
                'Name': ['Alice', 'Bob', 'Charlie'],
                'Age': [25, 30, 28],
                'City': ['New York', 'London', 'Tokyo']
        })

# Display the data editor
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic")

# Save button
if st.button("Save Changes"):
        st.session_state.data = edited_df  # Update session state
        # Here, you would typically save the edited_df to a file or database
        # For example, to save to a CSV:
        # edited_df.to_csv("edited_data.csv", index=False)
        st.success("Changes saved!")

# Display the updated data (optional)
st.subheader("Current Data:")
st.dataframe(st.session_state.data)

