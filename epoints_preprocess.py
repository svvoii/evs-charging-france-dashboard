# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# The goal of this script is to preprocess the dataset `charging_points.csv`.
# The end goal is have the dataset grouped by department. 
# Therefore, the missing postal codes in the dataset need to be filled in.
#
# Steps to preprocess the dataset:
# 1. Load the datasets (charging_points.csv, fr-ref-geo.csv) `load_dataset()` -> (epoints, geo_ref) and examin the data `display_missing_values()`
# 2. Isolate the columns needed for the preprocessing `select_columns()` (the goal to fill in the missing postal codes)
# 3. Process the missing postal codes `process_missing_postal_codes()`:
#	- Extract postal code from `adresse_station` string and store it in `postal_code`, new column `extract_postal_code_from_str()`
# 	- Fill in the postal code based on similar GPS coordinates in new `lat_lon` column `map_coordinates_to_postal_code()`
#	- Some manual fixes (about 600 rows with around 150 unique locations) for the remaining missing postal codes `postal_code_manual_fixes()`
# 4. Grouping the dataset by department in `adding_department()`
#	- Fixing the postal codes for Corsica (20) to 2A and 2B`
#	- Drop the rows with empty `department` values as well as all that is not in the range of 1-95 + 2A + 2B
#	- Mappping the department codes to department names `dep_to_name`
#	- Saving dataset with following columns: ('dept_code', 'dept_name', 'year')
# 5. Transforming the dataset into a pivot table withthe follwong columns:
# 	['dept_code', 'dept_name', '2021', '2022', '2023', '2024', 'total']

import streamlit as st
import pandas as pd
import numpy as np
from unidecode import unidecode


st.set_page_config(
	page_title="Data Clean",
	layout="wide",
)

# @st.cache_data
def load_dataset():
	epoints = pd.read_csv('data/charging_points.csv', dtype=str)
	return epoints
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def postal_code_manual_fixes(df):
	# Fill in the missing postal codes manually based GPS coordinates `coordonneesXY`
	df.loc[df['lat_lon'] == '43.95, 4.76', 'postal_code'] = '30133'
	df.loc[df['lat_lon'] == '43.96, 4.75', 'postal_code'] = '30133'
	df.loc[df['lat_lon'] == '44.02, 4.79', 'postal_code'] = '30150'
	df.loc[df['lat_lon'] == '47.50, 0.49', 'postal_code'] = '37360'
	df.loc[df['lat_lon'] == '48.79, 2.15', 'postal_code'] = '78000'
	df.loc[df['lat_lon'] == '48.80, 2.15', 'postal_code'] = '78000'
	df.loc[df['lat_lon'] == '43.33, 6.54', 'postal_code'] = '83120'
	df.loc[df['lat_lon'] == '43.32, 6.62', 'postal_code'] = '83120'
	df.loc[df['lat_lon'] == '43.27, 6.52', 'postal_code'] = '83310'
	df.loc[df['lat_lon'] == '43.22, 6.66', 'postal_code'] = '83350'
	df.loc[df['lat_lon'] == '43.23, 6.58', 'postal_code'] = '83580'
	df.loc[df['lat_lon'] == '43.26, 6.58', 'postal_code'] = '83580'
	df.loc[df['lat_lon'] == '43.27, 6.63', 'postal_code'] = '83990'
	df.loc[df['lat_lon'] == '43.95, 4.83', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.92, 4.82', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.93, 4.79', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.93, 4.80', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.92, 4.81', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.94, 4.87', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.94, 4.82', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.94, 4.79', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.94, 4.84', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.95, 4.79', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.95, 4.82', 'postal_code'] = '84000'
	df.loc[df['lat_lon'] == '43.94, 4.89', 'postal_code'] = '84310'
	df.loc[df['lat_lon'] == '43.82, 5.40', 'postal_code'] = '84400'
	df.loc[df['lat_lon'] == '43.94, 4.93', 'postal_code'] = '84470'
	df.loc[df['lat_lon'] == '48.79, 2.26', 'postal_code'] = '92140'
	df.loc[df['lat_lon'] == '48.85, 2.20', 'postal_code'] = '92380'
	df.loc[df['lat_lon'] == '48.83, 2.18', 'postal_code'] = '92410'
	df.loc[df['lat_lon'] == '43.92, 4.87', 'postal_code'] = '84140'
	df.loc[df['lat_lon'] == '48.81, 2.46', 'postal_code'] = '94340'
	df.loc[df['lat_lon'] == '48.82, 2.47', 'postal_code'] = '94340'
	df.loc[df['lat_lon'] == '43.53, 5.30', 'postal_code'] = '13122'
	df.loc[df['lat_lon'] == '43.53, 5.29', 'postal_code'] = '13122'
	df.loc[df['lat_lon'] == '44.97, 0.43', 'postal_code'] = '24400'
	df.loc[df['lat_lon'] == '48.34, 1.18', 'postal_code'] = '28120'
	df.loc[df['lat_lon'] == '47.86, 1.68', 'postal_code'] = '45130'
	df.loc[df['lat_lon'] == '43.28, 6.58', 'postal_code'] = '83310'
	df.loc[df['lat_lon'] == '43.28, 6.59', 'postal_code'] = '83310'
	df.loc[df['lat_lon'] == '43.27, 6.58', 'postal_code'] = '83310'
	df.loc[df['lat_lon'] == '43.22, 6.65', 'postal_code'] = '83350'
	df.loc[df['lat_lon'] == '43.25, 6.63', 'postal_code'] = '83350'
	df.loc[df['lat_lon'] == '43.22, 6.64', 'postal_code'] = '83350'
	df.loc[df['lat_lon'] == '43.16, 6.46', 'postal_code'] = '83820'
	df.loc[df['lat_lon'] == '43.93, 4.87', 'postal_code'] = '84140'
	df.loc[df['lat_lon'] == '43.75, 5.34', 'postal_code'] = '84160'
	df.loc[df['lat_lon'] == '43.97, 4.90', 'postal_code'] = '84270'
	df.loc[df['lat_lon'] == '43.98, 4.89', 'postal_code'] = '84270'
	df.loc[df['lat_lon'] == '44.00, 4.92', 'postal_code'] = '84320'
	df.loc[df['lat_lon'] == '48.80, 2.26', 'postal_code'] = '92140'
	df.loc[df['lat_lon'] == '48.78, 2.23', 'postal_code'] = '92140'
	df.loc[df['lat_lon'] == '48.78, 2.28', 'postal_code'] = '92290'
	df.loc[df['lat_lon'] == '48.79, 2.27', 'postal_code'] = '92350'
	df.loc[df['lat_lon'] == '48.77, 2.25', 'postal_code'] = '92290'
	df.loc[df['lat_lon'] == '48.84, 2.18', 'postal_code'] = '92380'
	df.loc[df['lat_lon'] == '48.84, 2.19', 'postal_code'] = '92380'
	df.loc[df['lat_lon'] == '48.77, 2.05', 'postal_code'] = '78180'
	df.loc[df['lat_lon'] == '48.15, -1.59', 'postal_code'] = '35510'
	df.loc[df['lat_lon'] == '44.77, 0.40', 'postal_code'] = '24240'
	df.loc[df['lat_lon'] == '48.38, 4.34', 'postal_code'] = '10220'
	df.loc[df['lat_lon'] == '46.08, 5.81', 'postal_code'] = '01200'
	df.loc[df['lat_lon'] == '46.26, 5.36', 'postal_code'] = '01370'
	df.loc[df['lat_lon'] == '45.46, 4.49', 'postal_code'] = '42400'
	df.loc[df['lat_lon'] == '4.96, 4.57', 'postal_code'] = '' # error in coords ?!
	df.loc[df['lat_lon'] == '43.43, 5.51', 'postal_code'] = '13120'
	df.loc[df['lat_lon'] == '47.17, 1.48', 'postal_code'] = '36600'
	df.loc[df['lat_lon'] == '43.54, 1.40', 'postal_code'] = '31120'
	df.loc[df['lat_lon'] == '47.87, -3.93', 'postal_code'] = '29900'
	df.loc[df['lat_lon'] == '48.53, 2.15', 'postal_code'] = '91580'
	df.loc[df['lat_lon'] == '48.06, -0.79', 'postal_code'] = '53000'
	df.loc[df['lat_lon'] == '44.14, 5.06', 'postal_code'] = '84190'
	df.loc[df['lat_lon'] == '43.14, 5.84', 'postal_code'] = '83190'
	df.loc[df['lat_lon'] == '43.47, 6.66', 'postal_code'] = '83480'
	df.loc[df['lat_lon'] == '43.12, 5.83', 'postal_code'] = '83140'
	df.loc[df['lat_lon'] == '44.14, 4.04', 'postal_code'] = '30480'
	df.loc[df['lat_lon'] == '50.60, 5.48', 'postal_code'] = '' # Belgium
	df.loc[df['lat_lon'] == '43.69, 7.22', 'postal_code'] = '06200'
	df.loc[df['lat_lon'] == '51.01, 2.37', 'postal_code'] = '59180'
	df.loc[df['lat_lon'] == '46.14, 3.41', 'postal_code'] = '03700'
	df.loc[df['lat_lon'] == '49.73, 4.75', 'postal_code'] = '08000'
	df.loc[df['lat_lon'] == '47.80, 7.31', 'postal_code'] = '68270'
	df.loc[df['lat_lon'] == '46.66, -1.33', 'postal_code'] = '85310'
	df.loc[df['lat_lon'] == '48.33, 4.11', 'postal_code'] = '10150'
	df.loc[df['lat_lon'] == '48.30, 4.14', 'postal_code'] = '10410'
	df.loc[df['lat_lon'] == '50.64, 3.19', 'postal_code'] = '59510'
	df.loc[df['lat_lon'] == '51.00, 2.33', 'postal_code'] = '59380'
	df.loc[df['lat_lon'] == '49.86, 4.42', 'postal_code'] = '08260'
	df.loc[df['lat_lon'] == '49.42, 4.95', 'postal_code'] = '08240'
	df.loc[df['lat_lon'] == '49.88, 4.84', 'postal_code'] = '08800'
	df.loc[df['lat_lon'] == '49.35, 4.49', 'postal_code'] = '08310'
	df.loc[df['lat_lon'] == '49.87, 4.80', 'postal_code'] = '08800'
	df.loc[df['lat_lon'] == '49.89, 4.62', 'postal_code'] = '08500'
	df.loc[df['lat_lon'] == '49.52, 4.47', 'postal_code'] = '08300'
	df.loc[df['lat_lon'] == '49.90, 4.27', 'postal_code'] = '08380'
	df.loc[df['lat_lon'] == '49.39, 4.69', 'postal_code'] = '08400'
	df.loc[df['lat_lon'] == '49.85, 4.76', 'postal_code'] = '08120'
	df.loc[df['lat_lon'] == '49.78, 4.49', 'postal_code'] = '08150'
	df.loc[df['lat_lon'] == '49.92, 4.52', 'postal_code'] = '08230'
	df.loc[df['lat_lon'] == '49.51, 4.76', 'postal_code'] = '08390'
	df.loc[df['lat_lon'] == '49.85, 4.74', 'postal_code'] = '08120'
	df.loc[df['lat_lon'] == '49.17, 1.35', 'postal_code'] = '27940'
	df.loc[df['lat_lon'] == '48.94, 0.66', 'postal_code'] = '27410'
	df.loc[df['lat_lon'] == '49.01, 0.70', 'postal_code'] = '27410'
	df.loc[df['lat_lon'] == '49.15, 0.67', 'postal_code'] = '27300'
	df.loc[df['lat_lon'] == '48.89, 0.93', 'postal_code'] = '27160'
	df.loc[df['lat_lon'] == '48.83, 0.96', 'postal_code'] = '27160'
	df.loc[df['lat_lon'] == '48.86, 1.07', 'postal_code'] = '27240'
	df.loc[df['lat_lon'] == '48.87, 1.08', 'postal_code'] = '27240'
	df.loc[df['lat_lon'] == '49.06, 1.41', 'postal_code'] = '27950'
	df.loc[df['lat_lon'] == '49.15, 1.60', 'postal_code'] = '27630'
	df.loc[df['lat_lon'] == '49.19, 1.22', 'postal_code'] = '27400'
	df.loc[df['lat_lon'] == '49.26, 0.93', 'postal_code'] = '27370'
	df.loc[df['lat_lon'] == '49.18, 1.54', 'postal_code'] = '27510'
	df.loc[df['lat_lon'] == '48.75, 1.54', 'postal_code'] = '28410'
	df.loc[df['lat_lon'] == '48.74, 0.92', 'postal_code'] = '27130'
	df.loc[df['lat_lon'] == '48.73, 0.92', 'postal_code'] = '27130'
	df.loc[df['lat_lon'] == '48.97, 0.78', 'postal_code'] = '27190'
	df.loc[df['lat_lon'] == '49.29, 1.47', 'postal_code'] = '27150'
	df.loc[df['lat_lon'] == '49.26, 0.97', 'postal_code'] = '27370'
	df.loc[df['lat_lon'] == '47.06, 0.73', 'postal_code'] = '37240'
	df.loc[df['lat_lon'] == '49.13, 4.53', 'postal_code'] = '51600'
	df.loc[df['lat_lon'] == '48.97, 4.46', 'postal_code'] = '51460'
	df.loc[df['lat_lon'] == '48.97, 4.34', 'postal_code'] = '51000'
	df.loc[df['lat_lon'] == '48.96, 4.31', 'postal_code'] = '51510'
	df.loc[df['lat_lon'] == '49.09, 4.89', 'postal_code'] = '51800'
	df.loc[df['lat_lon'] == '48.94, 4.88', 'postal_code'] = '51330'
	df.loc[df['lat_lon'] == '48.78, 4.91', 'postal_code'] = '51250'
	df.loc[df['lat_lon'] == '48.76, 4.84', 'postal_code'] = '51340'
	df.loc[df['lat_lon'] == '48.90, 4.00', 'postal_code'] = '51130'
	df.loc[df['lat_lon'] == '49.17, 4.22', 'postal_code'] = '51360'
	df.loc[df['lat_lon'] == '49.13, 4.36', 'postal_code'] = '51400'
	df.loc[df['lat_lon'] == '49.14, 4.16', 'postal_code'] = '51380'
	df.loc[df['lat_lon'] == '49.22, 4.05', 'postal_code'] = '51350'
	df.loc[df['lat_lon'] == '43.90, 2.27', 'postal_code'] = '81430'
	df.loc[df['lat_lon'] == '43.89, 2.42', 'postal_code'] = '81430'
	df.loc[df['lat_lon'] == '43.89, 1.97', 'postal_code'] = '81150'
	df.loc[df['lat_lon'] == '43.80, 2.36', 'postal_code'] = '81120'
	df.loc[df['lat_lon'] == '43.51, 2.35', 'postal_code'] = '81200'
	df.loc[df['lat_lon'] == '50.79, 4.30', 'postal_code'] = '' # Belgium
	df.loc[df['lat_lon'] == '49.43, 2.70', 'postal_code'] = '60190'
	df.loc[df['lat_lon'] == '49.48, 0.13', 'postal_code'] = '76600'
	df.loc[df['lat_lon'] == '49.49, 0.17', 'postal_code'] = '76600'
	df.loc[df['lat_lon'] == '49.52, 0.11', 'postal_code'] = '76620'
	df.loc[df['lat_lon'] == '49.64, 0.15', 'postal_code'] = '76280'
	df.loc[df['lat_lon'] == '49.50, 0.17', 'postal_code'] = '76600'
	df.loc[df['lat_lon'] == '49.51, 0.16', 'postal_code'] = '76610'
	df.loc[df['lat_lon'] == '49.51, 0.09', 'postal_code'] = '76620'
	df.loc[df['lat_lon'] == '49.51, 0.11', 'postal_code'] = '76620'
	df.loc[df['lat_lon'] == '49.50, 0.10', 'postal_code'] = '76600'
	df.loc[df['lat_lon'] == '49.50, 0.11', 'postal_code'] = '76600'
	df.loc[df['lat_lon'] == '47.70, 2.94', 'postal_code'] = '89220'
	df.loc[df['lat_lon'] == '47.70, 2.95', 'postal_code'] = '89220'
	df.loc[df['lat_lon'] == '48.18, 1.63', 'postal_code'] = '28150'
	df.loc[df['lat_lon'] == '43.36, -1.72', 'postal_code'] = '64122'
	df.loc[df['lat_lon'] == '45.67, 5.49', 'postal_code'] = '38510'
	df.loc[df['lat_lon'] == '46.71, 4.39', 'postal_code'] = '71450'

	df.loc[df['lat_lon'] == '41.93, 8.75', 'postal_code'] = '20090'

	return df
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# This will display the number of missing values in each column (missing in RED, no missing in GREEN)
# @st.cache_data
def display_missing_values(charging_points):
	st.write(f"DEBUG: Missing values in :")
	for column in charging_points.columns:	
		missing_values = charging_points[column].isna().sum()
		if missing_values > 0:
			st.markdown(f"<font color='red'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)
		else:
			st.markdown(f"<font color='green'>**{column}: {missing_values}**</font>", unsafe_allow_html=True)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# This will extract the postal code from `adresse_station` and store it in `postal_code`, new column
def extract_postal_code_from_str(df):
	def find_postal_code(s):
		for i in range(len(s)):
			if s[i:i+5].isdigit() and len(s[i:i+5]) == 5:
				return s[i:i+5]
		return None

	df['postal_code'] = df['adresse_station'].apply(find_postal_code)
	return df
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def select_columns(df, columns):
	new_df = df[columns].copy()
	return new_df

def map_coordinates_to_postal_code(df):
	# Converting the GPS coordinates to a specific format (e.g. from  `[-0.056488 , 48.723084]` to `48.723,-0.056`)
	def process_coordinates(str):
		coords = str.replace(' ', '').replace('[', '').replace(']', '')
		coord_list = coords.split(',')
		reverse_coords = reversed(coord_list)
		formatted_list = [coord[:coord.index('.')+3] if '.' in coord else coord for coord in reverse_coords]
		modified_coords = ', '.join(formatted_list)
		return modified_coords

	df['lat_lon'] = df['coordonneesXY'].apply(process_coordinates)

	# Mapping the GPS coordinates form `lat_lon` to `postal_code` values
	coord_to_code = df[df['postal_code'].notnull()].set_index('lat_lon')['postal_code'].to_dict()
	# Fill in the missing postal codes based on the GPS coordinates mapping
	df.loc[df['postal_code'].isnull(), 'postal_code'] = df['lat_lon'].map(coord_to_code)

	return df

def process_missing_postal_codes(df_epoints):
	df_epoints = select_columns(df_epoints, ['adresse_station', 'coordonneesXY', 'consolidated_code_postal', 'created_at'])

	df_epoints = extract_postal_code_from_str(df_epoints) # Extract postal code from `adresse_station` string and store it in `postal_code`, new column
	df_epoints['postal_code'] = df_epoints['postal_code'].fillna(df_epoints['consolidated_code_postal']) # Copy the code from 'consolidated_code_postal' to 'postal_code' if it's not null

	# This will fill in the postal code based on similar GPS coordinates in new `lat_lon` column
	df_epoints = map_coordinates_to_postal_code(df_epoints)

	# Some manual fixes (around 600 rows with 150 unique locations) for the remaining missing postal codes
	df_epoints = postal_code_manual_fixes(df_epoints)

	# This will convert the postal codes to string and set/keep the missing values to None
	df_epoints['postal_code'] = df_epoints['postal_code'].where(df_epoints['postal_code'].isnull(), df_epoints['postal_code'].astype(str))

	return df_epoints
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def adding_department(df):
	df['dept_code'] = df['postal_code'].str[:2]
	# Fix the postal codes for Corsica (20) to 2A and 2B
	df_corse = pd.read_csv('data/code-postal-corse.csv', sep=';', dtype=str)
	# st.write(df_corse)
	# Replace `20` with `2A` and `2B` for Corsica in `department` column. Using mapping from `code-postal-corse.csv`
	df['dept_code'] = df['dept_code'].replace('20', np.nan)
	code_to_dep = df_corse.set_index('Code_postal')['CODE_DEPT'].to_dict()
	df['dept_code'] = df['dept_code'].fillna(df['postal_code'].map(code_to_dep))

	# This will drop the rows with empty `department` values as well as all that is not in the range of 1-95 + 2A + 2B
	mask_empty = df['dept_code'] == ''
	mask_not_in_range = ~df['dept_code'].isin([str(i).zfill(2) for i in range(0, 96)] + ['2A', '2B'])
	df = df[~(mask_empty | mask_not_in_range)].copy()

	# Load the `fr-ref-geo.csv` file to map the department codes to department names
	df_fr_dep = pd.read_csv('data/fr-ref-geo.csv', sep=';', dtype=str)
	# st.write(df_fr_dep)
	dep_to_name = df_fr_dep.set_index('DEP_CODE')['DEP_NOM'].to_dict()
	df['dept_name'] = df['dept_code'].map(dep_to_name)

	# Extract the year from the `created_at` into `year` column and keep only the `dept_code`, `dept_name` and `year` columns in the DataFrame
	df['year'] = df['created_at'].str.slice(0, 4)
	df = df[['dept_code', 'dept_name', 'year']]
	return df
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def transform_data(df):
	df['epoints'] = 1
	pivot_df = pd.pivot_table(df, index=['dept_code', 'dept_name'], columns='year', values='epoints', aggfunc='sum', fill_value=0)
	# pivot_df = pd.pivot_table(df, index=['dept_code', 'dept_name'], columns='year', aggfunc='sum', fill_value=0)
	# pivot_df.reset_index(inplace=True)
	# pivot_df.columns = ['_'.join(str(col)).strip('_') for col in pivot_df.columns.values]
	# pivot_df.columns = ['dept_code', 'dept_name', '2021', '2022', '2023', '2024']
	# pivot_df['total'] = pivot_df.iloc[:, 2:].sum(axis=1)
	pivot_df['total'] = pivot_df[['2021', '2022', '2023', '2024', '2025']].sum(axis=1)
	return pivot_df
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def main():
	# epoints, geo_ref = load_dataset()
	epoints = load_dataset()

	## PREPROCESSING DATASET ##

	# DEBUG #
	# missing_values = epoints[epoints['consolidated_code_postal'].isnull()]
	# st.write(f'Initislly missing values in `consolidated_code_postal` column: `{missing_values.shape[0]}` in dataset `epoints`')
	# # # # #

	df_epoints = process_missing_postal_codes(epoints)

	df_epoints = adding_department(df_epoints)
	# st.write(f'Preprocessed dataset `df_epoints`, rows count: `{df_epoints.shape[0]}`')
	# st.write(df_epoints)

	pivot_df = transform_data(df_epoints)

	pivot_df.to_csv('data/epoints_pivot.csv')

	# Saving the cumulative sum of the pivot table as well
	pivot_df_cumsum = pivot_df.loc[:, '2021':'2025'].cumsum(axis=1)
	pivot_df_cumsum.to_csv('data/epoints_pivot_cumsum.csv')

	print('The final datasets have been saved to `data/epoints_pivot.csv` and `data/epoints_pivot_cumsum.csv`')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# TO RUN THE FOLLOWING CODE THE STREAMLIT APP NEEDS TO BE LAUNCHED FIRST
	# # DEBUG # #
	# st.write(f'Pivot table `pivot_df`, rows count: `{pivot_df.shape[0]}`')
	# st.write(pivot_df)
	# st.write(f'Pivot table saved to `data/epoints_pivot.csv`')

	# st.write(f'Pivot table `pivot_df_cumsum`, rows count: `{pivot_df_cumsum.shape[0]}`')
	# st.write(pivot_df_cumsum)
	# st.write(f'Pivot table saved to `data/epoints_pivot_cumsum.csv`')

	# st.write(f'Original Dataframe `epoints`, rows count: `{epoints.shape[0]}`')
	# st.write(epoints.shape)
	# st.write(epoints)

	# st.write(f'Filtered dataframe `df_epoints`, rows count (with '' empty string): `{filtered_df.shape[0]}`: ')
	# if filtered_df.shape[0] > 0:
	# 	st.write(filtered_df)

	# filtered_df_unique = filtered_df.drop_duplicates(subset='postal_code')
	# st.write(f'Filtered dataframe unique postal codes starting with `20`: `{filtered_df_unique.shape[0]}`')
	# if filtered_df_unique.shape[0] > 0:
	# 	st.write(filtered_df_unique)

	# missing_values = df_epoints[df_epoints['postal_code'].isnull()]
	# missing_values = df_epoints[df_epoints['department'].isnull()]
	# st.write(f'Missing values in `department` column: `{missing_values.shape[0]}`, in dataframe `df_epoints`')
	# if missing_values.shape[0] > 0:
	# 	st.write(missing_values.shape)
	# 	st.write(missing_values)
	
	# missing_values_unique_coords = missing_values.drop_duplicates(subset='coordonneesXY')
	# missing_values_unique_coords = missing_values.drop_duplicates(subset='lat_lon')
	# if missing_values_unique_coords.shape[0] > 0:
	# 	st.write(f'Missing values with unique GPS coordinates (shape): `{missing_values_unique_coords.shape[0]}`')
		# st.write(missing_values_unique_coords)
	# # # # # # #

	## GROUPING DATASET BY DEPATRMENT ##


if __name__ == '__main__':
    main()
