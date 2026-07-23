import os
import pandas as pd
from typing import List, Dict
from utils import detect_language, extract_city_from_location, load_city_mapping, get_state
from parameters import Parameters
from datetime import datetime, timedelta
import pickle
import uuid


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

    #print("**************")
    for date in last_n_dates:
        #print(date)
        file_path = os.path.join(os.getcwd(), 'daily_data', date.strftime('%Y-%m-%d') + '.parquet')
        if os.path.exists(file_path):
            daily_data = pd.read_parquet(file_path)
            daily_data['date'] = date
            if daily_data.shape[0] > 0:
                jobs.append(daily_data)
            else:
                print(f"File {file_path} is empty.")
                continue
        else:
            #print(f"File {file_path} not found.")
            continue

    # Concatenate all DataFrames into a single DataFrame
    if len(jobs) == 0:
        print("No data found.")
        return None
    else:
        all_jobs = pd.concat(jobs, ignore_index=True)
        all_jobs = all_jobs.drop_duplicates(subset=['title', 'company', 'location', 'search_term'])
        all_jobs = all_jobs.drop_duplicates(subset=['title', 'company', 'location', 'description'])
        all_jobs['lang'] = all_jobs['description'].apply(lambda x: detect_language(x))

        # Apply function to create new columns
        all_jobs['location'] = all_jobs['location'].fillna('DE')
        #print('Extracting state from location...')
        all_jobs['city'] = all_jobs['location'].apply(lambda x: pd.Series(extract_city_from_location(x)))
        #print(all_jobs.columns)

        # create an unique identifier(uuid) for each record in the dataset
        all_jobs['uuid'] = all_jobs.apply(lambda x: str(uuid.uuid4()), axis=1)


        if len(last_n_dates)>15:
            cities = all_jobs['city'].unique().tolist()

            city_mappings: Dict[str, str] = {"DE": "DE"}

            if os.path.exists(os.path.join("data", "city_mapping.pkl")):
                city_mappings = load_city_mapping()

            for city in cities:
                # check if mappings already exist using os
                if city in city_mappings.keys():
                    continue
                else:   
                    city_mappings = get_state(city, city_mappings)

            # saving the mapping dictionary to a pickle file
            pickle.dump(city_mappings, open(os.path.join("data", "city_mapping.pkl"), "wb"))

            all_jobs['state'] = all_jobs['city'].map(city_mappings)
        
        else:
            city_mappings = load_city_mapping()
            all_jobs['state'] = all_jobs['city'].map(city_mappings)

        # Save the data to a parquet file
        current_local_timestamp: str = datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(
                os.getcwd(), 'data', 
                "last_" + str(len(last_n_dates)) + "_days" + '.parquet')
        all_jobs.to_parquet(file_path)


def main():
    # Pipeline 2 Initializations
    #level_one_days = Parameters.LEV_ONE_RECENT_DAYS
    #level_two_days = Parameters.LEV_TWO_RECENT_DAYS
    level_three_days = Parameters.LEV_THREE_RECENT_DAYS

    # PIPELINE 2
    # Get level-wise data
    #level_one_dates = get_last_n_dates(level_one_days)
    #level_two_dates = get_last_n_dates(level_two_days)
    level_three_dates = get_last_n_dates(level_three_days)

    print("Collecting data...")
    get_full_data(level_three_dates)    
    print("Level 3 data collected.")
    #get_full_data(level_two_dates)
    #print("Level 2 data collected.")
    #get_full_data(level_one_dates)
    #print("Level 1 data collected.")

if __name__ == "__main__":
    main()