from geopy.geocoders import Nominatim
import pickle
import os
from typing import Dict
import pandas as pd
from utils import load_city_mapping, get_state

df = pd.read_parquet("data/last_30_days.parquet")
cities = df['city'].unique().tolist()
# cities = ['Berlin', 'Munich', 'Hamburg', 'Weinheim', 'Darmstadt', 'Grasbrunn' ]
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
print(city_mappings)