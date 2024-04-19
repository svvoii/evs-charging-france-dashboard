import os # for using os.path.exists to check if a file exists
import streamlit as st # for creating the web app with streamlit framework
import pandas as pd # for data manipulation
import ast # for converting string to dictionary using ast.literal_eval
import json # for converting dictionary to string using json.dumps


APP_TITLE = "Map Dashboard"

@st.cache_data # Caching the data to avoid loading it multiple times
def load_dataset():
	charging_points = pd.read_csv("data/charging_points.csv", low_memory=False)
	location_data = pd.read_csv("data/location_data.csv")
	return charging_points, location_data

@st.cache_data # Caching the data to avoid loading it multiple times
def extract_postal_code(location_data):
	location_data_list = []
	postal_codes = []
	for index, row in location_data.iterrows():
		location_data_dict = ast.literal_eval(row["location_data"])
		location_data_list.append(location_data_dict)

		# Extract address components and find postal code
		postal_code = None # there still some missing values so we add None
		address_components = location_data_dict["address_components"]
		for component in address_components:
			if "postal_code" in component["types"]:
				postal_code = component["long_name"]
				break
		postal_codes.append(postal_code)
	
	# Adding new column to location_data
	location_data["code_postal"] = postal_codes
	return location_data


def main():
	st.set_page_config(APP_TITLE)
	st.title(APP_TITLE)
	st.caption("A simple dashboard to display maps and data tables. made by: `Serge` and `Nammi`. `Plug-In Progress`")

	# Loading data
	charging_points, location_data = load_dataset()

	# Extracting postal_code from location_data
	location_data = extract_postal_code(location_data)

	# Renaming columns in location_data to correspond with the charging_points data
	location_data = location_data.rename(columns={'longitude': 'consolidated_longitude', 'latitude': 'consolidated_latitude'})
	
	# Saving to the same file
	location_data.to_csv("data/location_data.csv", index=False)

	# Merge postal code data into charging points data 
	charging_points = pd.merge(charging_points, location_data[['consolidated_longitude', 'consolidated_latitude', 'code_postal']], on=['consolidated_longitude', 'consolidated_latitude'], how='left')
	charging_points['consolidated_code_postal'].fillna(charging_points['code_postal'], inplace=True)

	# ##### #

	# Filters
	postal_code = "consolidated_code_postal"
	missing_postal_code = charging_points[charging_points[postal_code].isna()]
	commune = "consolidated_commune"

	# charging_points = charging_points[(charging_points[postal_code].astype(str).str[0] == '7')] # Filter by postal code starting with 7

	st.write(f"DEBUG: Missing values in :")
	for column in charging_points.columns:	
		missing_values = charging_points[column].isna().sum()
		# st.write(f"{column}: {missing_values}")
		if missing_values > 0:
			st.markdown(f"<font color='red'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)
		else:
			st.markdown(f"<font color='green'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)
	
	# common_missing = charging_points[(charging_points[postal_code].isna()) & (charging_points[commune].isna())].shape[0]
	# st.write(f"DEBUG: Number of rows where both [{postal_code}] and [{commune}] are missing: [ {common_missing} ]")
	st.write(f"DEBUG: Number of rows where [{postal_code}] is missing, TOTAL [{missing_postal_code.shape[0]}] :")
	# st.write(missing_postal_code['adresse_station'].unique())
	st.write(missing_postal_code[['adresse_station', 'consolidated_code_postal', 'consolidated_commune']].drop_duplicates())


	st.write(f"Charging points. TOTAL (rows, columns):")
	st.write(charging_points.shape)
	st.write(charging_points.head())
	st.write(charging_points.columns)

	st.write(f"Location data. TOTAL (rows, columns):")
	st.write(location_data.shape)
	st.write(location_data.head())
	st.write(location_data.columns)
 
	# has_postal_code = check_postal_code(location_data)
	# st.write(f"DEBUG: There is postal code in the location data: {has_postal_code}")

	# Displaying filters and map
 
	# Displaying data tables and metrics
 

if __name__ == "__main__":
    main()


# def check_postal_code(location_data):
# 	for index, row in location_data.iterrows():
# 		location_dict = ast.literal_eval(row['location_data'])
# 		if 'address_components' in location_dict:
# 			for component in location_dict['address_components']:
# 				if 'postal_code' in component['types']:
# 					return True
# 	return False

	# DEBUG # Adding new column for postal code by extracting / parsing it from the address string in `adresse_station`..
	# charging_points["code_postal_extracted"] = charging_points["adresse_station"].str.extract(r"(\d{5})")
	# charging_points['adresse_station'].to_excel('data/adresse_station.xlsx', index=False)
	# charging_points['adresse_station'].to_csv('data/adresse_station.csv', index=False)
	# if os.path.exists('data/missing_code_postal_adresse.csv'):
	# 	charging_points_missing_code_postal = pd.read_csv('data/missing_code_postal_adresse.csv')
	# else:
	# 	charging_points_missing_code_postal = charging_points[charging_points["code_postal_extracted"].isna()]["adresse_station"]
	# 	charging_points_missing_code_postal.to_csv('data/missing_code_postal_adresse.csv', index=False)
	# uniques_values_missing_code = charging_points_missing_code_postal['adresse_station'].unique()
	# st.write(f"UNIQUE values of missing code postal in [adresse_station], total: {len(uniques_values_missing_code)}")
	# stations_unique = charging_points['adresse_station'].unique()
	# percentage_missing_code = (len(uniques_values_missing_code) / len(stations_unique)) * 100
	# st.write(f"Percentage of missing code postal in [adresse_station]: {percentage_missing_code}") 
