import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(
	page_title="Data Clean",
	layout="wide",
)

@st.cache_data
def load_dataset():
	epoints = pd.read_csv('data/charging_points.csv', dtype=str)
	geo_ref = pd.read_csv('data/fr-ref-geo.csv', sep=';', dtype=str)
	return epoints, geo_ref

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

# This will extract the postal code from `adresse_station` and store it in `postal_code`, new column
def extract_postal_code(df):
	def find_postal_code(s):
		for i in range(len(s)):
			if s[i:i+5].isdigit() and len(s[i:i+5]) == 5:
				return s[i:i+5]
		return None

	df['postal_code'] = df['adresse_station'].apply(find_postal_code)
	return df

# This will return the new coord column in a format: `x, y` with one decimal place to group by the coordinates and fill missing values in the postal code..
# `coord` example: `[4.352516, 50.8467]` will be formatted as `50.84, 4.35`
def format_coordinates(df):
	def format_coord(coord):
		parts = coord.replace('[', '').replace(']', '').split(',')	
		# formatted_parts = [str(round(float(part), 1)) for part in parts]
		formatted_parts = [part[:part.index('.')+3] if '.' in part else part for part in parts]
		formatted_parts = formatted_parts[::-1] # Reverse the order of the parts
		return ', '.join(formatted_parts)

	df['lat_long'] = df['coordonneesXY'].apply(format_coord)
	return df

# This will fill missing values in the 'consolidated_code_postal' and 'postal_code' columns..
def fill_missing_values(df):
	# Grouping by 'lat_long' and fill missing values in 'postal_code'
	df['postal_code'] = df.groupby('lat_long')['postal_code'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else np.nan))

	# Convert 'postal_code' back to string and replace 'nan' with empty string (None)
	df['postal_code'] = df['postal_code'].astype(str)
	df['postal_code'] = df['postal_code'].replace('nan', None)

	# Fill missing values in 'postal_code' from 'consolidated_code_postal' if found
	df['postal_code'] = df['postal_code'].fillna(df['consolidated_code_postal'])
	return df

def convert_column_to_upper(df, column, new_column):
	df[new_column] = df[column].str.upper()
	return df

def is_substring(larger, smaller):
	return smaller in larger

# This will add the postal code to the epoints DataFrame by matching the commune name in the 'adresse_station' with the 'COM_NOM_MAJ' in the geo_ref DataFrame
def add_postal_code(search_in, search_for):
	progress_bar = st.progress(0)
	# Create a dictionary where the keys are the commune names and the values are the postal codes
	postal_codes = search_for.set_index('COM_MAJ')['COM_CODE'].to_dict()
	# Create a new column 'postal_code' and initialize it with None
	search_in['postal_code'] = None
	# Iterate over the items in the postal_codes dictionary
	for commune_name, postal_code in postal_codes.items():
		progress_bar.progress((list(postal_codes.keys()).index(commune_name) + 1) / len(postal_codes))
		# Find the rows where the commune name is in the 'ADR_MAJ' string
		mask = search_in['ADR_MAJ'].apply(lambda x: commune_name in x)
		# Assign the corresponding postal code to the 'postal_code' column for those rows
		search_in.loc[mask, 'postal_code'] = postal_code

	return search_in

def main():
	epoints, geo_ref = load_dataset()
	# st.write(epoints.shape)
	# st.write(epoints)
	# display_missing_values(epoints)

	epoints_copy = epoints[['adresse_station', 'coordonneesXY', 'consolidated_code_postal']].copy()
	new_df = convert_column_to_upper(epoints_copy, 'adresse_station', 'ADR_MAJ')
	new_df['postal_code'] = None

	# st.write(new_df.shape)
	# st.write(new_df)

	geo_ref_cp = geo_ref[['COM_NOM', 'COM_CODE', 'COM_NOM_MAJ']].copy()
	geo_ref_cp = convert_column_to_upper(geo_ref_cp, 'COM_NOM', 'COM_MAJ')

	new_df = add_postal_code(new_df, geo_ref_cp)

	# new_df = extract_postal_code(epoints_copy) # Extract postal code from `adresse_station` and store it in `postal_code`, new column
	# new_df = format_coordinates(new_df) # Format the coordinates into new column `lat_long` (`[4.352516, 50.8467]` will be `50.84, 4.35`)
	# new_df = fill_missing_values(new_df) # Fill missing values in the `postal_code` by grouping `lat_long` and from 'consolidated_code_postal'

	# missing_values = new_df[new_df['consolidated_code_postal'].isnull() | new_df['postal_code'].isnull()]
	missing_values = new_df[new_df['postal_code'].isnull()]
	st.write(f'Missing values: {missing_values.shape[0]}')
	st.write(missing_values.shape)
	st.write(missing_values)

	st.write(f'geo_ref: {geo_ref.shape[0]}')
	st.write(geo_ref_cp.shape)
	st.write(geo_ref_cp.sort_values('COM_NOM'))
	# display_missing_values(geo_ref)



if __name__ == '__main__':
    main()
