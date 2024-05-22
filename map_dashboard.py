import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static
import altair as alt
import json

# Page configuration
st.set_page_config(
	page_title="Plug-in Progress",
	page_icon="🔌",
	layout="wide",
	initial_sidebar_state="expanded",
)

alt.themes.enable('dark')

# Uploading datasets
def load_datasets():
	# epoints_df = pd.read_csv('data/epoints_pivot.csv')
	epoints_df = pd.read_csv('data/epoints_pivot_cumsum.csv')
	epoints_df['dept_code_name'] = epoints_df['dept_code'] + ' - ' + epoints_df['dept_name']
	epoints_df.insert(2, '2020', 0)

	# evs_df = pd.read_csv('data/evs_pivot.csv')
	evs_df = pd.read_csv('data/evs_pivot_cumsum.csv')
	evs_df['dept_code_name'] = evs_df['dept_code'] + ' - ' + evs_df['dept_name']

	return epoints_df, evs_df

# def ft_sidebar(df):
def ft_sidebar(df_epoints, df_evs):
	with st.sidebar:
		# st.sidebar.title("Plug-in Progress")
		st.sidebar.markdown(
			"""
			Ce tableau de bord montre le nombre de véhicules électriques et de points de charge en France métropolitaine.
			"""
		)
		
		dept_list = list(df_epoints['dept_code_name'].unique())
		dept_list.insert(0, 'All Departments')
		selected_department = st.selectbox('Select department', dept_list)

		year_list = ['2024', '2023', '2022', '2021', '2020']
		selected_year = st.radio('Select year', year_list)

	return selected_year, selected_department
	

# def create_choropleth(map, df, column, color, legend_name):
def create_choropleth(map, df_points, df_evs, column, color, legend_name):
	# Converting the dataframe to a dictionarya to add a value to the GeoJSON file to use withthe tooltip
	df_points_dict = df_points.set_index('dept_code')[column].to_dict()
	df_evs_dict = df_evs.set_index('dept_code')[column].to_dict()

	with open('data/france_departments.geojson') as f:
		geojson_dict = json.load(f)
	
	for feature in geojson_dict['features']:
		feature['properties']['e_charge'] = df_points_dict.get(feature['properties']['code'], 'N/A')
		feature['properties']['vehicles'] = df_evs_dict.get(feature['properties']['code'], 'N/A')
		evs = df_evs_dict.get(feature['properties']['code'], 'N/A')
		points = df_points_dict.get(feature['properties']['code'], 'N/A')
		ratio = int(evs / points) if points != 0 else -1
		# ratio = int(df_evs_dict.get(feature['properties']['code'], 'N/A') / df_points_dict.get(feature['properties']['code'], 'N/A'))
		feature['properties']['vhs_per_epoint'] = ratio
	
	# Creating df with ratios of vehicles per charging point as values..
	df_ratio = df_points.copy()
	df_ratio[column] = (df_evs[column] / df_points[column]).fillna(0) # vehicles per charging point
	df_ratio = df_ratio[['dept_code', 'dept_code_name', column]]

	choropleth = folium.Choropleth(
		# geo_data="data/france_departments.geojson",
		geo_data=geojson_dict,
		name=legend_name,
		data=df_ratio,
		# columns=['depart_code', 'log_ratio'],
		columns=['dept_code', column],
		key_on='feature.properties.code',
		fill_color=color,
		fill_opacity=0.7,
		line_opacity=0.2,
		legend_name=legend_name,
		# bins=bins,
	).add_to(map)

	# DEBUG #
	st.write(f"df_ratio: {df_ratio.shape}")
	st.write(df_ratio)
	# # # # #

	choropleth.geojson.add_child(
		folium.features.GeoJsonTooltip(['code', 'nom', 'vhs_per_epoint', 'vehicles', 'e_charge'], aliases=['départ. code: ', 'département: ', 'vé par borne: ', 'véhicules él.: ', 'bornes: '])
	)

# COLOR SCHEMES:
# 'BuGn', `BuPu`,`GnBu`,`OrRd`,`PuBu`,`PuBuGn`,`PuRd`,`RdPu`,`YlGn`,`YlGnBu`,`YlOrBr`,`YlOrRd`,
# `Blues`, `Greens`, `Greys`, `Oranges`, `Purples`, `Reds` 
# `Accent`, `Dark2`, `Paired`, `Pastel1`, `Pastel2`, `Set1`, `Set2`, `Set3`

def render_map(df_epoints, df_evs, selected_year):

	map = folium.Map(
    	location=[46.603354, 1.8883344], 
    	zoom_start=6, 
    	tiles='CartoDB positron', 
    	scrollWheelZoom=False,
		control_scale=False
	)

	# df_ratio = df_epoints.copy()
	# df_ratio[selected_year] = df_ratio[selected_year].replace([np.inf, -np.inf], np.nan)

	# st.write(f"Ratio shape: {df_ratio.shape}")
	# st.write(df_ratio)

	create_choropleth(map, df_epoints, df_evs, selected_year, 'Set3', 'Véhicules électriques par borne de recharge')
	# create_choropleth(map, df_epoints, selected_year, 'BuGn', 'Number of charging points')
	# create_choropleth(map, df_evs, selected_year, 'OrRd', 'Number of electric vehicles')

	folium.LayerControl().add_to(map)
	folium_static(map, width=800, height=800)


def main():
	# Load the data
	df_epoints, df_evs = load_datasets()

	col = st.columns((5, 3), gap='small')

	selected_year, selected_department = ft_sidebar(df_epoints, df_evs)

	if selected_department != 'All Departments':
		df_epoints = df_epoints[df_epoints['dept_code_name'] == selected_department]
		df_evs = df_evs[df_evs['dept_code_name'] == selected_department]
	
	epoints = df_epoints[selected_year].sum() if selected_year in df_epoints.columns else 0
	evs = df_evs[selected_year].sum() if selected_year in df_evs.columns else 0

	with col[0]:
		mettric_col = st.columns(3)
		with mettric_col[0]:
			st.write(f"Charging Points")
			st.metric(label=selected_department, value='{:,}'.format(epoints), delta=0)
		with mettric_col[1]:
			st.write(f"Electric Vehicles")
			st.metric(label=selected_department, value='{:,}'.format(evs), delta=0)
		with mettric_col[2]:
			st.write(f"Vehicles per charging point")
			# ratio = int(evs/epoints)
			ratio = int(evs/epoints) if epoints != 0 else 0
			st.metric(label=selected_department, value=f'{ratio}', delta=0)

		render_map(df_epoints, df_evs, selected_year)

	with col[1]:
		st.write("Cumulative Charging Points")
		df_epoints_cum = pd.DataFrame(df_epoints.sum(numeric_only=True)).T
		st.write(df_epoints_cum)
		st.line_chart(df_epoints_cum.sum())

		st.write("Cumulative Electric Vehicles")
		df_evs_cum = pd.DataFrame(df_evs.sum(numeric_only=True)).T
		st.write(df_evs_cum)
		st.line_chart(df_evs_cum.sum())

	# DEBUG #
	st.write(df_epoints.shape)
	st.write(df_epoints)

	st.write(df_evs.shape)
	st.write(df_evs)
	# # # # #
	


if __name__ == "__main__":
    main()
