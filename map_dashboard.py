import pandas as pd
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
	total_epoints = df['num_epoints'].sum()
	total_evs = df['nb_vp_rechargeables_el'].sum()

	map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron', scrollWheelZoom=False)

	create_choropleth(map, df, 'num_epoints', 'BuGn', 'Number of charging points')
	create_choropleth(map, df, 'nb_vp_rechargeables_el', 'OrRd', 'Number of electric vehicles')

	folium.LayerControl().add_to(map)

	folium_static(map, width=800, height=800)

	return total_epoints, total_evs

def show_map(df, selected_year):

	# Render the map. If `All` is selected, render the map for all years
	if selected_year == 'All':
		e_points, evs = render_map(df)
	else:
		e_points, evs = render_map(df, selected_year)

	col1, col2 = st.columns(2)

	with col1:
		st.metric("Total number of charging points", e_points)
	with col2:
		st.metric("Total number of electric vehicles", evs)
  

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
