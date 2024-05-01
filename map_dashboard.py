import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static

def create_choropleth(map, df, column, color, legend_name):
	choropleth = folium.Choropleth(
		geo_data="data/france_departments.geojson",
		name=legend_name,
		data=df,
		columns=['depart_code', column],
		key_on='feature.properties.code',
		fill_color=color,
		fill_opacity=0.7,
		line_opacity=0.2,
		legend_name=legend_name,
	).add_to(map)

	choropleth.geojson.add_child(
		folium.features.GeoJsonTooltip(['nom'])
	)

def render_map(df, year=None):
	
	if year is not None:
		df = df[df['year'] == year]

	df = df.groupby('depart_code').agg({'num_epoints': 'sum', 'nb_vp_rechargeables_el': 'sum'}).reset_index()
	df['num_epoints'] = df['num_epoints'].fillna(0.1)
	df['num_epoints'] = df['num_epoints'].replace(0, 0.1)
	df['ratio'] = np.where(df['num_epoints'] >= 1, df['nb_vp_rechargeables_el'] / df['num_epoints'], 500) # how to deal with outliers?
	
	# Just to check the calculaton results
	# df.to_csv('data/ratio_result_after.csv')

	Q1 = df['ratio'].quantile(0.25)
	Q3 = df['ratio'].quantile(0.75)
	IQR = Q3 - Q1
	filter = (df['ratio'] >= Q1 - 1.5 * IQR) & (df['ratio'] <= Q3 + 1.5 *IQR)
	df = df.loc[filter]
	
	total_epoints = df['num_epoints'].sum()
	total_evs = df['nb_vp_rechargeables_el'].sum()
	ratio = total_evs / total_epoints # what if total_epoints is 0 ? < there is no way this value goes 0

	map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron', scrollWheelZoom=False)

	create_choropleth(map, df, 'num_epoints', 'BuGn', 'Number of charging points')
	create_choropleth(map, df, 'nb_vp_rechargeables_el', 'OrRd', 'Number of electric vehicles')
	create_choropleth(map, df, 'ratio', 'PuRd', 'NUMBER of EVs per charging point')

	folium.LayerControl().add_to(map)

	folium_static(map, width=800, height=800)

	return total_epoints, total_evs, ratio

def show_map(df, selected_year):

	# Render the map. If `All` is selected, render the map for all years
	if selected_year == 'All':
		e_points, evs, ratio = render_map(df)
	else:
		e_points, evs, ratio = render_map(df, selected_year)

	col1, col2, col3 = st.columns(3)

	with col1:
		st.metric("Total number of charging points", e_points)
	with col2:
		st.metric("Total number of electric vehicles", evs)
	with col3:
		st.metric("Ratio of electric vehicles per charging point", ratio)
  

def main():
	# Load the data
	voitures_epoints = pd.read_csv('data/voitures_epoints.csv')

	# Getting the years form the DataFrame
	years =  ['All'] + sorted(voitures_epoints['year'].unique(), reverse=True)

	# Creating a column for each year
	columns = st.columns(len(years))

	# Add a select radio button in each column
	selected_year = st.radio('Select year', years)

	show_map(voitures_epoints, selected_year)	

if __name__ == "__main__":
    main()
