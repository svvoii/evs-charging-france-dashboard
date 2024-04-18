# This script is used to get the location data of the given latitude and longitude using Google Maps API.
# The function get_location_data takes a dataframe as input and returns 
# a new dataframe with the columns latitude, longitude, and location_data.

import requests
import pandas as pd
import os
from dotenv import load_dotenv
from tqdm import tqdm


def get_location_data(df):
	def get_data_from_api(lat, lon):
		if (lat, lon) in location_cache:
			return location_cache[(lat, lon)]
		response = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={API_KEY}')
		data = response.json()
		if 'results' in data and len(data['results']) > 0:
			location_cache[(lat, lon)] = data['results'][0]
			return data['results'][0]
		return None  # Handle cases where no results are found

	location_cache = {}
	new_location_data = []
	unique_rows = df.drop_duplicates(subset=['consolidated_latitude', 'consolidated_longitude'])
	for index, row in tqdm(unique_rows.iterrows(), total=unique_rows.shape[0]):
		location_data_row = get_data_from_api(row['consolidated_latitude'], row['consolidated_longitude'])
		if location_data_row:  # Only add data if API call succeeds
			new_location_data.append({
				'latitude': row['consolidated_latitude'],
				'longitude': row['consolidated_longitude'],
				'location_data': location_data_row
			})

	location_data = pd.DataFrame(new_location_data, columns=['latitude', 'longitude', 'location_data'])
	return location_data

if __name__ == "__main__":
	load_dotenv('data/.env')
	API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
	df = pd.read_csv("data/charging_points.csv", low_memory=False)
	location_data = get_location_data(df)
	location_data.to_csv("data/location_data.csv", index=False)
