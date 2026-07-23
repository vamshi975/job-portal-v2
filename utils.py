import time
from typing import List, Dict
from jobspy import scrape_jobs
import pandas as pd
from parameters import Parameters
import os
import langid
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import pickle


def detect_language(text: str)->str:
    """
    Detect the language of the text.

    Args:
        text: str -> Text to be detected.

    Returns:
        str: Language of the text.
    """
    try:
        lang, _ = langid.classify(text)
        return lang
    except:
        return 'not_detected'
    
def extract_city_from_location(location: str)-> str:
    """
    Extract the state from the location.

    Args:
        location: str -> Location from which state is to be extracted.

    Returns:
        str: State extracted from the location.
    """
    if pd.isnull(location):
        return 'DE'
    
    try:
        geolocator = Nominatim(user_agent="google")
        text_parts = location.split(',')
        city_name = text_parts[0].strip()
        
        """
        location = geolocator.geocode(city_name + ', Germany', addressdetails=True)
        # 
        
        if location:
            state = location.raw['address']['state']
            #print(city_name, state)
            return city_name, state
        else:
            return 'DE', 'DE'
        """

        return city_name
        
    except Exception as e:
        return 'DE'

def truncate_text(text: str, max_length: int=30):
    """
    Truncate the text.
    
    Args:
        text: str -> Text to be truncated.
        max_length: int -> Maximum length of the text.

    Returns:
        str: Truncated text.
    """
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    else:
        return text

def format_url(url:str)->str:
    """
    Format the URL as clickable link.

    Args:
        url: str -> URL to be formatted.

    Returns:
        str: Formatted URL.    
    """    
    return f'<a href="{url}" target="_blank">{url}</a>'

def get_last_n_dates(since_days: int)->List[datetime.date]:
    """
    Get the last n dates from today.

    Args:
        since_days: int -> Last n number of considered days.
    
    Returns:
        List[datetime.date]: A list of last n dates from today.  
    """

    # Get today's date
    end_date = datetime.now().date()
    
    # Calculate n days ago
    start_date = end_date - timedelta(days=since_days - 1)
    
    # Generate list of dates from start_date to end_date
    date_list = [start_date + timedelta(days=day) for day in range(since_days)]
    
    return date_list

def get_full_data(last_n_dates: List[datetime.date])->None:
    """
    Get the full data from the last n dates and save it to a parquet file.

    Args:
        last_n_dates: List[datetime.date] -> List of last n dates.
    
    Returns:
        Save the result to parquet file with a date.
    """
    # Initialize the list to store the data
    jobs: list[pd.DataFrame] = []

    for date in last_n_dates:
        file_path = os.path.join(os.getcwd(), 'daily_data', date.strftime('%Y-%m-%d') + '.parquet')
        daily_data = pd.read_parquet(file_path)
        jobs.append(daily_data)

    # Concatenate all DataFrames into a single DataFrame
    all_jobs = pd.concat(jobs, ignore_index=True)
    all_jobs = all_jobs.drop_duplicates()

    # Save the data to a parquet file
    current_local_timestamp: str = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join(
            os.getcwd(), 'data', 
            "last_" + str(last_n_dates) + "_" + current_local_timestamp + '.parquet')
    all_jobs.to_parquet(file_path)


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
        pd.DataFrame: A DataFrame created from the data.
    """
    # scrape the data
    jobs = scrape_jobs(
        site_name=[source],
        search_term=search_term,
        location=location,
        results_wanted=results_wanted,
        country_indeed=country_indeed
    )  

    # adding a new column with the search term
    jobs['search_term'] = search_term

    return jobs


def collect_data(search_terms: List[str] , location: str, results_wanted: int, country_indeed: str) -> None:
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

    # iterate through the search terms and collect the data
    for search_term in search_terms:
        indeed_jobs = get_jobs("indeed", search_term, location, results_wanted, country_indeed)
        time.sleep(10)
        linkedin_jobs = get_jobs("linkedin", search_term, location, results_wanted, country_indeed)
        time.sleep(10)
        glassdoor_jobs = get_jobs("glassdoor", search_term, location, results_wanted, country_indeed)
        time.sleep(10)

        # Concatenate the data from all the sources based on the search term
        search_term_jobs = pd.concat([indeed_jobs, linkedin_jobs, glassdoor_jobs], ignore_index=True)
        jobs.append(search_term_jobs)

    # Concatenate the data from all the search terms
    all_jobs = pd.concat(jobs, ignore_index=True)
    all_jobs = all_jobs.drop_duplicates()

    # Save the data to a parquet file
    current_local_timestamp: str = datetime.now().strftime('%Y-%m-%d')
    file_path = os.path.join(os.getcwd(), 'daily_data', current_local_timestamp + '.parquet')
    all_jobs.to_parquet(file_path)

def exclude_consultancy_jobs(df: pd.DataFrame)->pd.DataFrame:
    """
    Exclude the consultancy jobs from the data.

    Args:
        df: pd.DataFrame -> Dataframe to be filtered.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    company_filter = Parameters.COMPANY_FILTER
    #not_interested_company = ['Michael Page', 'adesso SE']
    return df[~df['company'].isin(company_filter)]


def load_city_mapping()->Dict[str, str]:
    """
    Load the city mapping dictionary.

    Returns:
        Dict[str, str]: City mapping dictionary.
    """
    city_mapping = pickle.load(open(os.path.join("data", "city_mapping.pkl"), "rb"))
    return city_mapping


def dump_city_mapping(city_mapping:Dict[str, str])->None:
    """
    Dump the city mapping dictionary.

    Args:
        city_mapping: Dict[str, str] -> City mapping dictionary.
    """
    pickle.dump(city_mapping, open(os.path.join("data", "city_mapping.pkl"), "wb"))

def get_state(city:str, mapping: Dict[str, str])->Dict[str, str]:
    """
    Get the state based on the city.

    Args:
        city: str -> City name.

    Returns:
        str: State name.
    """

    try:
        # Get the state based on the city
        geolocator = Nominatim(user_agent="google")
        location = geolocator.geocode(city + ', Germany', addressdetails=True)
        
        if location:
            address = location.raw['address']
            state = address.get(
                'state', 
                address.get(
                    'city', 
                    address.get(
                        'town', 
                        address.get('village', 'DE')
                    )
                )
            )

            mapping[city] = state
            return mapping
        else:
            return mapping

    except Exception as e:
        return mapping


def main():
    # Pipeline 1 Initializations
    search_terms = Parameters.SEARCH_TERMS
    location = Parameters.LOCATION 
    results_wanted = Parameters.RESULTS_WANTED
    country_indeed = Parameters.COUNTRY_INDEED

    # Pipeline 2 Initializations
    level_one_days = Parameters.LEV_ONE_RECENT_DAYS
    level_two_days = Parameters.LEV_TWO_RECENT_DAYS
    level_three_days = Parameters.LEV_THREE_RECENT_DAYS


    # PIPELINE 1
    # Collecting the data
    collect_data(search_terms, location, results_wanted, country_indeed)

    # PIPELINE 2
    # Get level-wise data
    level_one_dates = get_last_n_dates(level_one_days)
    level_two_dates = get_last_n_dates(level_two_days)
    level_three_dates = get_last_n_dates(level_three_days)

    get_full_data(level_one_dates)
    get_full_data(level_two_dates)
    get_full_data(level_three_dates)

    # PIPELINE 3
    # Streamlit App

    

if __name__ == "__main__":
    main()