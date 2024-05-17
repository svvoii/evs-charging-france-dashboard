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
		year_list = [col for col in df.columns if col.isdigit()]
		year_list.sort(reverse=True)
		year_list.insert(0, 'All')
		selected_year = st.radio('Select year', year_list)
		
		department_list = list(df['dept_code_name'].unique())[::-1]
		department_list.insert(0, 'All')
		selected_department = st.selectbox('Select department', department_list)

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
		columns=['dept_code', column],
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

# COLOR SCHEMES:
# 'BuGn', `BuPu`,`GnBu`,`OrRd`,`PuBu`,`PuBuGn`,`PuRd`,`RdPu`,`YlGn`,`YlGnBu`,`YlOrBr`,`YlOrRd`,
# `Blues`, `Greens`, `Greys`, `Oranges`, `Purples`, `Reds` 
# `Accent`, `Dark2`, `Paired`, `Pastel1`, `Pastel2`, `Set1`, `Set2`, `Set3`

# def render_map(df):
def render_map(df, selected_year, selected_department):
	if selected_year != 'All':
		column = selected_year
	else:
		column = 'total'
	
	if selected_department != 'All':
		df = df[df['dept_code_name'] == selected_department]
		# df = df[df['dept_code'] == selected_department]
	
	st.write(df)

	map = folium.Map(location=[46.603354, 1.8883344], zoom_start=6, tiles='CartoDB positron', scrollWheelZoom=False)

	create_choropleth(map, df, column, 'BuGn', 'Number of charging points')

	folium.LayerControl().add_to(map)

	folium_static(map, width=800, height=800)

	total_epoints = df[column].sum()

	return total_epoints

def show_map(df, selected_year, selected_department):

	e_points = render_map(df, selected_year, selected_department)
	
	col1 = st.columns(1)[0]

	with col1:
		st.metric("Total number of charging points", e_points)
	# with col2:
	# 	st.metric("Total number of electric vehicles", evs)
	# with col3:
	# 	st.metric("Ratio of electric vehicles per charging point", ratio)
  

def main():
	# Load the data
	df = pd.read_csv('data/epoints_pivot.csv')
	df['dept_code_name'] = df['dept_code'] + ' - ' + df['dept_name']

	selecetd_year, selected_department = ft_sidebar(df)

	show_map(df, selecetd_year, selected_department)	

if __name__ == "__main__":
    main()
