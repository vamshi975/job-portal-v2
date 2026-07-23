class Parameters:
    # Initializations
    LOCATION:str = "Germany" 
    RESULTS_WANTED:int = 50
    COUNTRY_INDEED:str = "Germany"
    LEV_ONE_RECENT_DAYS:int = 7
    LEV_TWO_RECENT_DAYS:int = 14
    LEV_THREE_RECENT_DAYS:int = 30
    GEMINI2_MODEL= "deepseek/deepseek-chat-v3-0324:free"

    INDEED_SEARCH_TERMS: list[str] = [
        "'(machine+learning+engineer)'", '"(ai+engineer)"', '"ai-engineer"', # >100
        "'(ai+research+engineer)'",  '"(ai+scientist)"', # 1
        '(("data modelling") and -student and -praktikant)', # >25
        "'(ml+engineer)'", '"analytics+engineer"', # > 50
        '(("data+analysis") and -student and -praktikant and -werkstudent and -internship and -intern and -Duales and -Praktikum and -Masterarbeit)', # > 800
        '(("data analyst") and -student and -praktikant and -werkstudent and -internship and -intern and -Duales and -Praktikum and -Masterarbeit)',  # > 400
        '(("data+analytics") and -student and -praktikant and -werkstudent and -internship and -intern and -Duales and -Praktikum and -Masterarbeit)', # >1000
        '(("machine+learning") and -student and -praktikant and -werkstudent and -internship and -intern and -Duales and -Praktikum and -Masterarbeit)', # >2000
        "'(("'(ai+developer)'" or "'(ai+specialist)'") and -werkstudent)'", # > 50
        "(('NLP' + 'machine learning') and -student and -praktikant and -werkstudent and -internship and -intern and -Duales and -Praktikum and -Masterarbeit)"
        '"rag" or "mcp"', '"data scientist"', '"data engineer"', '"artificial intelligence engineer"'
    ]

    SEARCH_TERMS: list[str] = [
        "data scientist", "data engineer", "machine learning engineer", "ai engineer",
        "analytics engineer", "data analyst", "data analytics", "machine learning", 
        "ai developer", "ai specialist", "nlp machine learning", "rag"
    ]

    STREAMLIT_FILTERS: list[str] = [ 
        'site', 'state', 'city', 'company', 'lang', 'search_term'
    ]

    JOBS_SELECTED_COLUMNS: list[str] = ['date', 'uuid', 'status', 'title', 'company', 'location', 'lang', 'job_url', 'description']
    
    ROWS_FILTER: list[str] = [
        'praktikant', 'working student', 'werkstudent', 'abschlussarbeit', 'thesis', 
        'praktika', 'intern','internship', 'praktikum', 'dualer student', 'duales studium',
        'ausbildung', 'apprenticeship', 'student', 'aushilfe', 'Masterarbeit', 'bachelorarbeit', 
        'Minijob', 'Masterand', 'bachelorand', 'hilfskraft', 'studentische hilfskraft',
    ]

    COLUMNS_FILTER: list[str] = [
        'date', 'title', 'job_url', 'company', 'location', 'site', 'lang',  # 'job_type', 'job_url_direct',
        'city', 'state', 'description', 'search_term', 'uuid'
    ]

    COMPANY_FILTER: list[str] = [
        'BearingPoint', 'Michael Page', 'adesso SE', 'BridgingIT GmbH', 
        'indivHR', 'Lawrence Harvey', 'indivHR - We 💚 IT Recruiting',
        'univativ GmbH', 'The Stepstone Group', 'ALTEN Consulting Services',
        'SAP', 'Mayflower GmbH', 'Optimus Search', 'Crossover', 'The Recruitment 2.0 Group',
        'Cologne Intelligence', 'Cologne Intelligence GmbH', 'Mayflower',
        'The StepStone Group GmbH', 'TrioTech Recruitment', 'IntaPeople: STEM Recruitment',
        'IntaPeople', 'TrioTech', 'Optimus Search Limited', 'ALTEN Technology',
        'Yellow Brick Road', 'Goodman Masson Deutschland', 'diconium group', 'diconium',
        'U.S. Army', 'ControlExpert GmbH', 'ControlExpert', 'Manning Global AG', 
        'Alexander Thamm GmbH', 'Alexander Thamm', 'Alexander Thamm Consulting',
        'TechBiz Global GmbH', 'TechStarter', 'Mindrift', 
    ]
    
    


    # ALDI Süd
    # merck
    # NielsenIQ
    # Südzucker
    # Haufe Group
    # https://www.linkedin.com/jobs/view/4001979963
    # Döhler Group
    # Deufol SE
    # BAUR-Gruppe
    # DEKRA Germany
    # Grünenthal Group
    # Graf Hardenberg
    


#- Researching, defining and testing the data model to set up our data quality validation pipeline, via intense communication with experts of SAP/CRM systems and product owners. 
#- Data Engineering: developing our in house data engineering and data quality python package (Azure, PySpark, Git, Databricks) 
#- Data Quality Validation through business defined rules (python)
#- Data Visualisation of results (PowerBI) and maintenance of our dashboards
#- Coordinating activities with stakeholders in absence of our PO