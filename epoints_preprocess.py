import streamlit as st
import pandas as pd
import numpy as np
from unidecode import unidecode


st.set_page_config(
	page_title="Data Clean",
	layout="wide",
)

@st.cache_data
def load_dataset():
	epoints = pd.read_csv('data/charging_points.csv', dtype=str)
	geo_ref = pd.read_csv('data/fr-ref-geo.csv', sep=';', dtype=str)
	return epoints, geo_ref
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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

def convert_column_to_upper(df, column, new_column):
	df[new_column] = df[column].str.upper().apply(unidecode)
	return df
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# This will add the postal code to the epoints DataFrame by matching the commune name in the 'adresse_station' with the 'COM_NOM_MAJ' in the geo_ref DataFrame
def add_postal_code(df, geo_ref_cp, key_col):
	progress_bar = st.progress(0)
	progress_text = st.empty()
	# Create a dictionary where the keys are the commune names and the values are the postal codes
	postal_codes = geo_ref_cp.set_index(key_col)['COM_CODE'].to_dict()
	# Iterate over the items in the postal_codes dictionary
	for i, (commune_name, postal_code) in enumerate(postal_codes.items()):
		progress = (i + 1) / len(postal_codes)
		progress_bar.progress(progress)
		text = 'Processing and matching postal code from `fr-ref-geo.csv` dataset into charging points (epoints) data frame.'
		progress_text.text(f'{text}\nProcessed {i + 1} of {len(postal_codes)} rows with empty postal code.')

		# Find the rows where the commune name is in the 'ADR_MAJ' string
		mask = df['ADR_MAJ'].apply(lambda x: commune_name in x)
		# Assign the corresponding postal code to the 'postal_code' column for those rows
		df.loc[mask, 'postal_code'] = postal_code

	return df
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def postal_code_manual_fixes(df):
	# Fill in the missing postal codes manually based GPS coordinates `coordonneesXY`
	df.loc[df['coordonneesXY'] == '[2.05,48.77]', 'postal_code'] = '78180'
	df.loc[df['coordonneesXY'] == '[2.537134, 49.009377]', 'postal_code'] = '95700'
	df.loc[df['coordonneesXY'] == '[1.51,43.54]', 'postal_code'] = '31670'
	df.loc[df['coordonneesXY'] == '[4.81745, 45.751829]', 'postal_code'] = '69005'
	df.loc[df['coordonneesXY'] == '[4.042399692989961, 44.140507984691325]', 'postal_code'] = '30480'
	df.loc[df['coordonneesXY'] == '[5.115036, 43.398722]', 'postal_code'] = '13220'
	df.loc[df['coordonneesXY'] == '[0.163932, 49.513496]', 'postal_code'] = '76600'
	df.loc[df['coordonneesXY'] == '[1.15170464,49.4665534]', 'postal_code'] = '76160'
	df.loc[df['coordonneesXY'] == '[5.49,45.67]', 'postal_code'] = '38510'
	df['postal_code'] = df['postal_code'].astype(str)
	return df
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def select_columns(df, columns):
	new_df = df[columns].copy()
	return new_df

def process_missing_postal_codes(df_epoints, df_geo_ref):
	df_epoints = select_columns(df_epoints, ['adresse_station', 'coordonneesXY', 'consolidated_code_postal'])
	df_geo_ref = select_columns(df_geo_ref, ['COM_NOM', 'COM_CODE', 'COM_NOM_MAJ'])

	df_epoints = convert_column_to_upper(df_epoints, 'adresse_station', 'ADR_MAJ')
	df_geo_ref = convert_column_to_upper(df_geo_ref, 'COM_NOM', 'COM_MAJ')

	df_epoints['postal_code'] = None
	df_epoints = extract_postal_code_from_str(df_epoints) # Extract postal code from `adresse_station` string and store it in `postal_code`, new column
	df_epoints['postal_code'] = df_epoints['postal_code'].fillna(df_epoints['consolidated_code_postal']) # Copy the code from 'consolidated_code_postal' to 'postal_code' if it's not null

	# isolating the rows with missing postal codes
	missing_codes_df = df_epoints[df_epoints['postal_code'].isnull()]
	missing_codes_df = add_postal_code(missing_codes_df, df_geo_ref, 'COM_MAJ') # Fills in the missing postal codes form the geo_ref DataFrame based on the commune name
	df_epoints.update(missing_codes_df) # Update the original DataFrame with extracted postal codes 

	# Some manual fixes (about 60 rows with 9 unique locations) for the remaining missing postal codes
	df_epoints = postal_code_manual_fixes(df_epoints)

	return df_epoints, df_geo_ref
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def main():
	epoints, geo_ref = load_dataset()
	# st.write(f'epoints: {epoints.shape[0]}')
	# st.write(epoints.shape)
	# st.write(epoints)
	# display_missing_values(epoints)

	## PREPROCESSING DATASET ##
	missing_values = epoints[epoints['consolidated_code_postal'].isnull()]
	st.write(f'Missing values in `postal_code` column: `{missing_values.shape[0]}` in dataset `epoints`')

	df_epoints, df_geo_ref = process_missing_postal_codes(epoints, geo_ref)

	columns_to_drop = ['consolidated_code_postal', 'ADR_MAJ']
	df_epoints.drop(columns=columns_to_drop, inplace=True)

	st.write(f'Dataframe `df_epoints`, rows count: `{df_epoints.shape[0]}`')
	st.write(df_epoints.shape)
	st.write(df_epoints)

	missing_values = df_epoints[df_epoints['postal_code'].isnull()]
	st.write(f'Missing values in `postal_code` column: `{missing_values.shape[0]}`, in dataframe `df_epoints`')
	st.write(missing_values.shape)
	st.write(missing_values)

	# st.write(f'Dataframe `df_geo_ref`, rows count: `{df_geo_ref.shape[0]}`')
	# st.write(df_geo_ref.shape)
	# st.write(df_geo_ref)

	## GROUPING DATASET BY DEPATRMENT ##


if __name__ == '__main__':
    main()
