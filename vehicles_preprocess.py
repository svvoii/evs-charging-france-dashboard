# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Description: This script preprocesses the vehicles dataset `data/vehicules.csv` 
# The final datasets are saved as `evs_pivot.csv` and `evs_pivot_cumsum.csv` in the `data` folder
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import pandas as pd
import numpy as np
import streamlit as st

# Load the dataset
def load_dataset():
	df = pd.read_csv('data/voitures.csv', sep=';', dtype=str)
	df = df.rename(columns={
        'CODGEO': 'codgeo',
        'LIBGEO': 'libgeo',
        'EPCI': 'epci',
        'LIBEPCI': 'libepci',
        'DATE_ARRETE': 'date_arrete',
        'NB_VP_RECHARGEABLES_EL': 'nb_evs',
        # 'nb_vp_rechargeables_el': 'nb_evs',
    })	
	return df

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

# This function adds a new columns with department code and name
def adding_department(df):
	# Creating new column with department code
	dept_code = df['codgeo'].str[:2]
	df.insert(0, 'dept_code', dept_code)	

	dept_code_filter = [str(i).zfill(2) for i in range(1, 96)] + ['2A', '2B']
	df = df[df['dept_code'].isin(dept_code_filter)].copy()

	# Creating new column with department name
	fr_dep_df = pd.read_csv('data/fr-ref-geo.csv', sep=';', dtype=str)
	dep_to_name = fr_dep_df.set_index('DEP_CODE')['DEP_NOM'].to_dict()
	df['dept_name'] = df['dept_code'].map(dep_to_name)

	# Creating new `year` column
	df['year'] = df['date_arrete'].str.slice(0, 4)
	df = df[['dept_code', 'dept_name', 'year', 'nb_evs']]

	return df

# THis function will transform the dataset to a pivot table with the following columns:
# ['dept_code', 'dept_name', '2020', '2021', '2022', '2023', '2024', 'total']
def transform_to_pivot(df):
	df['nb_evs'] = pd.to_numeric(df['nb_evs'], errors='coerce')
	pivot_df = pd.pivot_table(df, index=['dept_code', 'dept_name'], columns='year', values='nb_evs', aggfunc='sum', fill_value=0)
	# pivot_df['total'] = pivot_df.iloc[:, 2:].sum(axis=1)
	pivot_df['total'] = pivot_df.loc[:, '2020':'2025'].sum(axis=1)

	return pivot_df


def main():
	evs_df = load_dataset() 
	
	df = adding_department(evs_df)

	# df_pivot = transform_to_pivot(df)

	# df_pivot.to_csv('data/evs_pivot.csv')

	# Saving the cumulative sum of the number of EVs as well
	# df_pivot_cumsum = df_pivot.loc[:, '2020':'2025'].cumsum(axis=1)
	# df_pivot_cumsum.to_csv('data/evs_pivot_cumsum.csv')

	# print('The final datasets `evs_pivot.csv` and `evs_pivot_cumsum.csv` have been saved in the `data` folder')

	# DEBUG #
	# TO RUN THE FOLLOWING CODE THE STREAMLIT APP NEEDS TO BE LAUNCHED FIRST
	st.write(evs_df.shape)
	st.write(evs_df)
	display_missing_values(df)
	st.write(df.shape)
	st.write(df)

	# # filter_df = df.drop_duplicates(subset=['year'])
	# st.write(df_pivot.shape)
	# st.write(df_pivot)
	# st.write(f'The final dataset has been saved as `evs_pivot.csv` in the `data` folder')

	# st.write(df_pivot_cumsum.shape)
	# st.write(df_pivot_cumsum)
	# st.write(f'The final dataset has been saved as `evs_pivot_cumsum.csv` in the `data` folder')
	# # # # #


if __name__ == '__main__':
	main()
