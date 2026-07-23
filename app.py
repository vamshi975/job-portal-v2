import streamlit as st
from PIL import Image

st.set_page_config(
    layout="wide",
    page_title="Jobs Board",
    page_icon="👋",
)

image1 = Image.open("assets/job1.jpg")
image2 = Image.open("assets/job2.jpg")

# ----------PAGE SETUP------- 
home_page = st.Page(
    page="views/1_introduction.py",
    title="Introduction",
    icon=":material/home:",
    default=True,
)

overview_page = st.Page(
    page="views/2_overview.py",
    title="Overview",
    icon=":material/overview:",
)	

search_insights_page = st.Page(
    page="views/3_trends.py",
    title="Job Insights",
    icon=":material/insert_chart:",
)

selected_jobs_page = st.Page(
    page="views/4_selected.py",
    title="Selected Jobs",
    icon=":material/checklist:",
)

applied_jobs_page = st.Page(
    page="views/5_applied.py",
    title="Applied Jobs",
    icon=":material/check_circle_outline:",
)

# ----------NAVIGATION SETUP (WITHOUT SECTIONS)-------
# pg = st.navigation(pages=[home_page, search_insights_page, selected_jobs_page])


# ----------NAVIGATION SETUP (WITH SECTIONS)-------
pg = st.navigation(
    {
        "Home": [home_page],
        "Modules": [overview_page, search_insights_page, selected_jobs_page, applied_jobs_page, ],
    }
)

st.sidebar.image(image1)
st.sidebar.image(image2)
st.logo("assets/icon.jpg", size="large")
st.sidebar.text("Made with ❤️ by Vamshi")


# ----------PG RUN-------
pg.run()