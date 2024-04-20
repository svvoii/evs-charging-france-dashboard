import os # for using os.path.exists to check if a file exists
import streamlit as st # for creating the web app with streamlit framework
import pandas as pd # for data manipulation
import ast # for converting string to dictionary using ast.literal_eval
import json # for converting dictionary to string using json.dumps
import folium # for creating maps from GeoJSON data
import streamlit_folium as folium_static # for displaying maps in Streamlit
from streamlit_folium import st_folium # for displaying maps in Streamlit


APP_TITLE = "Map Dashboard"

@st.cache_data # Caching the data to avoid loading it multiple times
def load_dataset():
	charging_points = pd.read_csv("data/charging_points.csv", low_memory=False)
	location_data = pd.read_csv("data/location_data.csv")
	return charging_points, location_data

@st.cache_data # Caching the data to avoid loading it multiple times
def extract_postal_code(location_data): # This will extract postal code from the location_data file (received via google API)
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

# This will display the number of missing values in each column (missing in RED, no missing in GREEN)
@st.cache_data
def display_missing_values(charging_points):
	st.write(f"DEBUG: Missing values in :")
	for column in charging_points.columns:	
		missing_values = charging_points[column].isna().sum()
		if missing_values > 0:
			st.markdown(f"<font color='red'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)
		else:
			st.markdown(f"<font color='green'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)

# This function will display the map using `folium` library with GeoJSON data
def display_map(charging_points, geojson_file):
	# Extract the first two digits of the postal code to get the department
	charging_points['depart_code'] = charging_points['consolidated_code_postal'].str[:2]
    
	points_by_department = charging_points['depart_code'].value_counts().reset_index()
	points_by_department.columns = ['depart_code', 'count']

	# Load GeoJSON data
	with open(geojson_file) as f:
		france_departments_geo = json.load(f)

	# Create a map object
	m = folium.Map(location=[46.603354, 1.888334], zoom_start=5)

	# Create a choropleth map
	folium.Choropleth(
		geo_data=france_departments_geo,
		name='choropleth',
		data=points_by_department,
		columns=['depart_code', 'count'],
		key_on='feature.properties.code',
		fill_color='YlGn',
		fill_opacity=0.7,
		line_opacity=0.2,
		legend_name='Number of charging points by department'
	).add_to(m)

	return m

def render_map(df, geojson_file):
	map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron')

	points_by_department = df['depart_code'].value_counts().reset_index()
	points_by_department.columns = ['depart_code', 'count']

	choropleth = folium.Choropleth(
		geo_data="data/france_departments.geojson",
		data=points_by_department,
		columns=['depart_code', 'count'],
		key_on='feature.properties.code',	
		line_opacity=0.8,
		line_color='black',
		highlight=True,
	)
	choropleth.geojson.add_to(map)
	choropleth.geojson.add_child(
		folium.features.GeoJsonTooltip(['nom'], labels=False)
	)

	st_map = st_folium(map, width=800, height=600)
 
	st.write(df.shape)
	st.write(df.head())
	st.write(df.columns)

def main():
	st.set_page_config(APP_TITLE)
	st.title(APP_TITLE)
	st.caption("A simple dashboard to display maps and data tables. made by: `Serge` and `Nammi`. `Plug-In Progress`")

	charging_points, location_data = load_dataset() # Loading data from CSV files
	location_data = extract_postal_code(location_data) # Extracting postal_code from location_data

	# Renaming columns in location_data to correspond with the charging_points data
	location_data = location_data.rename(columns={'longitude': 'consolidated_longitude', 'latitude': 'consolidated_latitude'})
	location_data.to_csv("data/location_data.csv", index=False) # Saving to the same file

	# Merge postal code data into charging points data (after this still 832 missing values in code_postal column, which is less than 1% of the total data)
	charging_points = pd.merge(charging_points, location_data[['consolidated_longitude', 'consolidated_latitude', 'code_postal']], on=['consolidated_longitude', 'consolidated_latitude'], how='left')
	charging_points['consolidated_code_postal'] = charging_points['consolidated_code_postal'].fillna(charging_points['code_postal']) # Fill missing values in 'consolidated_code_postal' with 'code_postal'	

	# to fill missing 832 values we use the `adresse_station` column and extract it from there with regex and fill the missing values in `consolidated_code_postal`
	charging_points['extracted_code_postal'] = charging_points['adresse_station'].str.extract(r"(\d{5})")
	charging_points['consolidated_code_postal'] = charging_points['consolidated_code_postal'].fillna(charging_points['extracted_code_postal']) # Fill missing values in 'consolidated_code_postal' with 'extracted_code_postal'

	# After this last extraction and merging the missing values in `consolidated_code_postal` are 12 (6 unique) which is negligible) !
	# Now we can use the `consolidated_code_postal` column to break down the data by regions and display it on the map !!
	# ##### #

	# Now we can use the `consolidated_code_postal` column to break down the data by regions and display it on the map
	charging_points['depart_code'] = charging_points['consolidated_code_postal'].str[:2] # Extract the first two digits of the postal code to get the commune
 
	# We can also use the `consolidated_longitude` and `consolidated_latitude` columns to display the data on the map

	# Filters
	postal_code = "consolidated_code_postal"
	missing_postal_code = charging_points[charging_points[postal_code].isna()]
	commune = "consolidated_commune"
	charging_points_by_department = charging_points['depart_code'].value_counts()

	# charging_points = charging_points[(charging_points[postal_code].astype(str).str[0] == '7')] # Filter by postal code starting with 7

	# display_missing_values(charging_points) # This will display the number of missing values in each column (missing in RED, no missing in GREEN)
	
	st.write(f"DEBUG: Number of rows where [{postal_code}] is missing, TOTAL (with duplicates) [{missing_postal_code.shape[0]}], list without duplicates :")
	st.write(missing_postal_code[['adresse_station', 'consolidated_code_postal', 'consolidated_commune', 'extracted_code_postal']].drop_duplicates())
	# st.write(missing_postal_code['adresse_station'].unique())

	st.write(f"Charging points. TOTAL (rows, columns):")
	st.write(charging_points.shape)
	st.write(charging_points.head())
	st.write(charging_points.columns)
	
	st.write(f"Charging points by department. TOTAL (rows, columns):")
	st.write(charging_points_by_department.shape)
	st.write(charging_points_by_department)

	# has_postal_code = check_postal_code(location_data)
	# st.write(f"DEBUG: There is postal code in the location data: {has_postal_code}")

	# Displaying filters and map

	st.write(f"DEBUG: Displaying map with charging points data")
	m = display_map(charging_points, "data/france_departments.geojson")
	folium_static.folium_static(m)

	render_map(charging_points, "data/france_departments.geojson")
 
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
