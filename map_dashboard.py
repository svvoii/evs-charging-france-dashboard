import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static
import altair as alt

# Page configuration
st.set_page_config(
	page_title="Plug-in Progress",
	page_icon="🔌",
	layout="wide",
	initial_sidebar_state="expanded",
)

alt.themes.enable('dark')

def ft_sidebar(df):
	with st.sidebar:
		# st.sidebar.title("Plug-in Progress")
		st.sidebar.markdown(
			"""
			This dashboard shows the amount of electric vehicles and charging points in France.
			"""
		)
		# year_list =  ['All'] + sorted(df['year'].unique(), reverse=True)
		year_list = list(df['year'].unique())[::-1]
		year_list.insert(0, 'All')
		selected_year = st.radio('Select year', year_list)
		# df = df[df['year'] == selected_year]

		department_list = list(df['depart_code'].unique())[::-1]
		department_list.insert(0, 'All')
		selected_department = st.selectbox('Select department', department_list)
		# df = df[df['depart_code'] == selected_department]

	return selected_year, selected_department
	

# def create_choropleth(map, df, column, color, legend_name):
def create_choropleth(map, df, column, color, legend_name):
	# bins = list(df[column].quantile([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]))
	# bins = list(np.linspace(df[column].min(), df[column].max(), 10))
	# st.write(bins)

	choropleth = folium.Choropleth(
		geo_data="data/france_departments.geojson",
		name=legend_name,
		data=df,
		# columns=['depart_code', 'log_ratio'],
		columns=['depart_code', column],
		key_on='feature.properties.code',
		fill_color=color,
		fill_opacity=0.7,
		line_opacity=0.2,
		legend_name=legend_name,
		# bins=bins,
	).add_to(map)

	choropleth.geojson.add_child(
		folium.features.GeoJsonTooltip(['nom'])
	)

def calculate_ratio(df):
	df['num_epoints'] = df['num_epoints'].fillna(1)
	df['num_evs'] = df['num_evs'].fillna(1)

	df['ratio'] = df['num_evs'] / df['num_epoints']
	df['ratio'] = df['ratio'].astype(int)

	return df

# COLOR SCHEMES:
# 'BuGn', `BuPu`,`GnBu`,`OrRd`,`PuBu`,`PuBuGn`,`PuRd`,`RdPu`,`YlGn`,`YlGnBu`,`YlOrBr`,`YlOrRd`,
# `Blues`, `Greens`, `Greys`, `Oranges`, `Purples`, `Reds` 
# `Accent`, `Dark2`, `Paired`, `Pastel1`, `Pastel2`, `Set1`, `Set2`, `Set3`

# def render_map(df):
def render_map(df, selected_year, selected_department):
	if selected_year != 'All':
		df = df[df['year'] == selected_year]
	if selected_department != 'All':
		df = df[df['depart_code'] == selected_department]
	
	df = calculate_ratio(df)

	st.write(df)
	stats = df[['num_epoints', 'num_evs', 'ratio']].describe()
	st.write(stats)

	map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron', scrollWheelZoom=False)

	create_choropleth(map, df, 'ratio', 'Paired', 'NUMBER of EVs per charging point')
	create_choropleth(map, df, 'num_epoints', 'BuGn', 'Number of charging points')
	create_choropleth(map, df, 'num_evs', 'GnBu', 'Number of electric vehicles')

	folium.LayerControl().add_to(map)

	folium_static(map, width=800, height=800)

	total_epoints = df['num_epoints'].sum()
	total_evs = df['num_evs'].sum()
	ratio = total_evs / total_epoints # what if total_epoints is 0 ? < there is no way this value goes 0

	return total_epoints, total_evs, ratio

def show_map(df, selected_year, selected_department):

	e_points, evs, ratio = render_map(df, selected_year, selected_department)
	
	col1, col2, col3 = st.columns(3)

	with col1:
		st.metric("Total number of charging points", e_points)
	with col2:
		st.metric("Total number of electric vehicles", evs)
	with col3:
		st.metric("Ratio of electric vehicles per charging point", ratio)
  

def main():
	# Load the data
	df = pd.read_csv('data/voitures_epoints.csv')
	df = df.rename(columns={'nb_vp_rechargeables_el': 'num_evs'})

	selecetd_year, selected_department = ft_sidebar(df)

	show_map(df, selecetd_year, selected_department)	

if __name__ == "__main__":
    main()
