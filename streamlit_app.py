import os
import streamlit as st
import pandas as pd
import ast
import json


APP_TITLE = "Map Dashboard"

# def check_postal_code(location_data):
# 	for index, row in location_data.iterrows():
# 		location_dict = ast.literal_eval(row['location_data'])
# 		if 'address_components' in location_dict:
# 			for component in location_dict['address_components']:
# 				if 'postal_code' in component['types']:
# 					return True
# 	return False


def main():
	st.set_page_config(APP_TITLE)
	st.title(APP_TITLE)
	st.caption("A simple dashboard to display maps and data tables. made by: `Serge` and `Nammi`. `Plug-In Progress`")

	# Loading data
	df = pd.read_csv("data/charging_points.csv", low_memory=False)
	location_data = pd.read_csv("data/location_data.csv")

	# Extracting postal_code from location_data
	location_data_list = []
	postal_codes = []
	for index, row in location_data.iterrows():
		location_data_dict = ast.literal_eval(row["location_data"])
		location_data_list.append(location_data_dict)

		# Extract address components and find postal code
		postal_code = None # thre still some missing values so we add None
		address_components = location_data_dict["address_components"]
		for component in address_components:
			if "postal_code" in component["types"]:
				postal_code = component["long_name"]
				break
		postal_codes.append(postal_code)
	
	# Adding new column to location_data
	location_data["code_postal"] = postal_codes
	
	# Saving to the same file
	location_data.to_csv("data/location_data.csv", index=False)
	
	# new_location_data = pd.DataFrame({
	# 	"latitude": location_data["latitude"],
	# 	"longitude": location_data["longitude"],
	# 	# "location_data": location_data_list,
	# 	"code_postal": postal_codes
	# })
 
	# new_location_data.to_csv('processed_location_data.csv', index=False)

	# DEBUG # Adding new column for postal code by extracting it from the address..
	# df["code_postal_extracted"] = df["adresse_station"].str.extract(r"(\d{5})")
	# df['adresse_station'].to_excel('data/adresse_station.xlsx', index=False)
	# df['adresse_station'].to_csv('data/adresse_station.csv', index=False)
	# if os.path.exists('data/missing_code_postal_adresse.csv'):
	# 	df_missing_code_postal = pd.read_csv('data/missing_code_postal_adresse.csv')
	# else:
	# 	df_missing_code_postal = df[df["code_postal_extracted"].isna()]["adresse_station"]
	# 	df_missing_code_postal.to_csv('data/missing_code_postal_adresse.csv', index=False)
	# uniques_values_missing_code = df_missing_code_postal['adresse_station'].unique()
	# st.write(f"UNIQUE values of missing code postal in [adresse_station], total: {len(uniques_values_missing_code)}")
	# stations_unique = df['adresse_station'].unique()
	# percentage_missing_code = (len(uniques_values_missing_code) / len(stations_unique)) * 100
	# st.write(f"Percentage of missing code postal in [adresse_station]: {percentage_missing_code}") 

	# ##### #

	# Filters
	postal_code = "consolidated_code_postal"
	commune = "consolidated_commune"

	# df = df[(df[postal_code].astype(str).str[0] == '7')]

	st.write(f"DEBUG: Missing values in :")
	for column in df.columns:	
		missing_values = df[column].isna().sum()
		# st.write(f"{column}: {missing_values}")
		if missing_values > 0:
			st.markdown(f"<font color='red'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)
		else:
			st.markdown(f"<font color='green'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)
	
	# common_missing = df[(df[postal_code].isna()) & (df[commune].isna())].shape[0]
	# st.write(f"DEBUG: Number of rows where both [{postal_code}] and [{commune}] are missing: [ {common_missing} ]")


	st.write(f"Charging points. TOTAL (rows, columns):")
	st.write(df.shape)
	st.write(df.head())
	st.write(df.columns)

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
