import os
import time
import pandas as pd
from typing import List
from jobspy import scrape_jobs
from parameters import Parameters
from datetime import datetime, timedelta
from get_companies import collect_companies

def get_jobs(source: str, search_term: str, location: str, results_wanted: int, country_indeed: str)->pd.DataFrame:
    """
    Collect the job from given source and returns to a dataframe.

    Args:
        source: str  -> Source name (Ex: indeed, glassdoor).
        search_term: str -> Search term (Ex: data engineer, marketing analyst).
        location: str -> City Location/Country (Ex: berlin, germany, munich).
        results_wanted: int -> Number of results to be collected (Ex: 40, 50).
        country_indeed: str -> Country (Ex: Germany, Ireland, France).

    Returns:
        pd.DataFrame: A DataFrame created from the data.9
    """
    try:
        # scrape the data
        jobs = scrape_jobs(
            site_name=[source],
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            country_indeed=country_indeed#,
            #google_search_term=search_term + "jobs near" + location + "yesterday"
        )  

        # adding a new column with the search term
        jobs['search_term'] = search_term

    except Exception as e:
        print(f"Error in collecting data from {source} for {search_term}: {e}")
        jobs = pd.DataFrame(
            columns=['id', 'site', 'job_url', 'job_url_direct', 'title', 'company', 'location', 'job_type', 
                     'date_posted', 'interval', 'min_amount', 'max_amount', 'currency', 'is_remote', 'job_function', 
                     'emails', 'description', 'company_url', 'company_url_direct', 'company_addresses',
                     'company_industry', 'company_num_employees', 'company_revenue', 'company_description', 'logo_photo_url', 
                     'banner_photo_url', 'ceo_name', 'ceo_photo_url']
        )

    return jobs


def collect_data(indeed_search_terms:List[str], search_terms: List[str] , location: str, results_wanted: int, country_indeed: str) -> None:
    """
    Collect the data from the sources and save it to a parquet file.

    Args:
        search_term: str -> Search term (Ex: data engineer, marketing analyst).
        location: str -> City Location/Country (Ex: berlin, germany, munich).
        results_wanted: int -> Number of results to be collected (Ex: 40, 50).
        country_indeed: str -> Country (Ex: Germany, Ireland, France).

    Returns:
        Save the result to parquet file with a date.
    """
    # Initialize the list to store the data
    jobs: list[pd.DataFrame] = []

    for indeed_search_term in indeed_search_terms:
        # Collecting the data from indeed
        indeed_jobs = get_jobs("indeed", indeed_search_term, location, results_wanted, country_indeed)
        time.sleep(10)
        jobs.append(indeed_jobs)

    # iterate through the search terms and collect the data
    for search_term in search_terms:
        #indeed_jobs = get_jobs("indeed", search_term, location, results_wanted, country_indeed)
        #time.sleep(10)
        linkedin_jobs = get_jobs("linkedin", search_term, location, results_wanted, country_indeed)
        time.sleep(10)
        glassdoor_jobs = get_jobs("glassdoor", search_term, location, results_wanted, country_indeed)
        time.sleep(10)
        #google_jobs = get_jobs("google", search_term, location, results_wanted, country_indeed)
        #time.sleep(10)

        # Concatenate the data from all the sources based on the search term
        #sources_list = [indeed_jobs, linkedin_jobs, glassdoor_jobs]
        #search_term_jobs = pd.concat([df for df in sources_list if not df.empty], ignore_index=True)
        search_term_jobs = pd.concat([linkedin_jobs, glassdoor_jobs], ignore_index=True)
        #search_term_jobs = pd.concat([indeed_jobs, linkedin_jobs, glassdoor_jobs, google_jobs], ignore_index=True)
        jobs.append(search_term_jobs)

    # Concatenate the data from all the search terms
    all_jobs = pd.concat(jobs, ignore_index=True)
    all_jobs = all_jobs.drop_duplicates()
    

    # Save the data to a parquet file
    current_local_timestamp: str = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join(os.getcwd(), 'daily_data', current_local_timestamp + '.parquet')
    all_jobs.to_parquet(file_path)

def delete_old_files():
    """
    Delete the files older than 60 days.
    """
    # get today date
    today = datetime.now().date()

    # delete files older than 60 days
    files = os.listdir('daily_data')
    for file in files:
        if file.endswith('.parquet'):
            file_date = datetime.strptime(file.split('.')[0], '%Y-%m-%d').date()
            if (today - file_date).days > 60:
                os.remove(os.path.join('daily_data', file))


def main():
    # Pipeline 1 Initializations
    indeed_search_terms =Parameters.INDEED_SEARCH_TERMS
    search_terms = Parameters.SEARCH_TERMS
    location = Parameters.LOCATION 
    results_wanted = Parameters.RESULTS_WANTED
    country_indeed = Parameters.COUNTRY_INDEED

    # PIPELINE 1
    # Collecting the data
    collect_data(indeed_search_terms, search_terms, location, results_wanted, country_indeed)

    # get companies list from the collected data
    collect_companies()

    # delete old files
    delete_old_files()


if __name__ == "__main__":
    main()