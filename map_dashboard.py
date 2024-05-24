import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static
import altair as alt
import json
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
	page_title="Plug-in Progress",
	# page_icon="🔌",
	page_icon="🚘",
	layout="wide",
	initial_sidebar_state="expanded",
)

alt.themes.enable('dark')
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Uploading datasets
@st.cache_data
def load_datasets():
	epoints_actual = pd.read_csv('data/epoints_pivot.csv')
	epoints_actual['dept_code_name'] = epoints_actual['dept_code'] + ' - ' + epoints_actual['dept_name']
	epoints_actual.insert(2, '2020', 0)

	epoints_cum = pd.read_csv('data/epoints_pivot_cumsum.csv')
	epoints_cum['dept_code_name'] = epoints_cum['dept_code'] + ' - ' + epoints_cum['dept_name']
	epoints_cum.insert(2, '2020', 0)

	# evs_cum = pd.read_csv('data/evs_pivot.csv')
	evs_actual = pd.read_csv('data/evs_pivot.csv')
	evs_actual['dept_code_name'] = evs_actual['dept_code'] + ' - ' + evs_actual['dept_name']

	evs_cum = pd.read_csv('data/evs_pivot_cumsum.csv')
	evs_cum['dept_code_name'] = evs_cum['dept_code'] + ' - ' + evs_cum['dept_name']

	ratio_cum = evs_cum.copy()
	for column in evs_cum.columns:
		if column not in ['dept_code', 'dept_name', 'dept_code_name']:
			ratio_cum[column] = evs_cum[column].div(epoints_cum[column]).replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
	
	# DEBUG #
	# st.write(f"ratio_cum shape: {ratio_cum.shape}")
	# st.write(ratio_cum)
	# # # # #
	return epoints_actual, evs_actual, epoints_cum, evs_cum, ratio_cum
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# def ft_sidebar(df):
def ft_sidebar(df_epoints, df_evs):
	with st.sidebar:
		# st.sidebar.header("Ce tableau de bord montre le nombre de véhicules électriques et de points de charge en France métropolitaine.")
		# st.title("🇫🇷, :fr:")
		# st.title("🔋, :battery:")
		# st.title("🔌, :electric_plug:")
		# st.title("🚗, :car:")
		# st.title("🚙, \U0001F699")
		# st.title("⚡, :zap:")
		# st.title("Ce Dashboard montre le nombre de véhicules électriques et de points de charge en France métropolitaine.")

		# st.sidebar.markdown(
		# 	"""
		# 	# Ce tableau de bord montre le nombre de véhicules électriques et de points de charge en France métropolitaine.
		# 	"""
		# )

		year_list = ['2024', '2023', '2022', '2021', '2020']
		selected_year = st.selectbox('Select year', year_list)
		# year_list = ['2020', '2021', '2022', '2023', '2024']
		# selected_year = st.radio('Select year', year_list)
		
		dept_list = list(df_epoints['dept_code_name'].unique())
		dept_list.insert(0, 'All Departments')
		selected_department = st.radio(':fr: Select department :fr:', dept_list)
		# selected_department = st.selectbox(':fr: Select department :fr:', dept_list)

	return selected_year, selected_department
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# def create_choropleth(map, df, column, color, legend_name):
def create_choropleth(map, df_points, df_evs, ratio_cum, column, color, legend_name):
	# Converting the dataframe to a dictionarya to add a value to the GeoJSON file to use withthe tooltip
	df_points_dict = df_points.set_index('dept_code')[column].to_dict()
	df_evs_dict = df_evs.set_index('dept_code')[column].to_dict()
	df_ratio_cum_dict = ratio_cum.set_index('dept_code')[column].to_dict()

	with open('data/france_departments.geojson') as f:
		geojson_dict = json.load(f)
	
	for feature in geojson_dict['features']:
		feature['properties']['e_charge'] = df_points_dict.get(feature['properties']['code'], 'N/A')
		feature['properties']['vehicles'] = df_evs_dict.get(feature['properties']['code'], 'N/A')
		feature['properties']['ratio'] = df_ratio_cum_dict.get(feature['properties']['code'], 'N/A')
	
	choropleth = folium.Choropleth(
		# geo_data="data/france_departments.geojson",
		geo_data=geojson_dict,
		name=legend_name,
		data=ratio_cum,
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
	# st.write(f"df_ratio_cum: {df_ratio_cum.shape}")
	# st.write(df_ratio_cum)
	# # # # #

	choropleth.geojson.add_child(
		folium.features.GeoJsonTooltip(['code', 'nom', 'ratio', 'vehicles', 'e_charge'], aliases=['départ. code: ', 'département: ', 'vé par départ: ', 'véhicules él.: ', 'bornes: '])
	)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# COLOR SCHEMES FOR CHOROPLETH MAPS:
# 'BuGn', `BuPu`,`GnBu`,`OrRd`,`PuBu`,`PuBuGn`,`PuRd`,`RdPu`,`YlGn`,`YlGnBu`,`YlOrBr`,`YlOrRd`,
# `Blues`, `Greens`, `Greys`, `Oranges`, `Purples`, `Reds` 
# `Accent`, `Dark2`, `Paired`, `Pastel1`, `Pastel2`, `Set1`, `Set2`, `Set3`
def render_map(df_epoints, df_evs, ratio_cum, selected_year):

	map = folium.Map(
    	location=[46.603354, 1.8883344], 
    	zoom_start=6, 
    	tiles='CartoDB positron', 
    	scrollWheelZoom=False,
		control_scale=False
	)

	create_choropleth(map, df_epoints, df_evs, ratio_cum, selected_year, 'Set3', 'Véhicules électriques par borne de recharge')

	folium.LayerControl().add_to(map)
	folium_static(map, width=800, height=800)

def plot_barchart(df, title):
	years = ['2020', '2021', '2022', '2023', '2024']
	data = []
	for year in years:
		data.append(go.Bar(name=year, x=df['dept_code_name'], y=df[year]))
	fig = go.Figure(data=data)
	fig.update_layout(barmode='stack', title=title)
	st.plotly_chart(fig, use_container_width=True, height=600)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def main():
	# Load the data
	df_epoints, df_evs, df_epoints_cum, df_evs_cum, df_ratio_cum = load_datasets()

	st.title("DASHBOARD")
	st.header(":electric_plug: Bornes de recharge et Véhicules électriques en France :car:")

	selected_year, selected_department = ft_sidebar(df_epoints_cum, df_evs_cum)

	plot_barchart(df_epoints, 'Bornes de recharge par département, cumulatif.')

	if selected_department != 'All Departments':
		df_epoints_cum = df_epoints_cum[df_epoints_cum['dept_code_name'] == selected_department]
		df_evs_cum = df_evs_cum[df_evs_cum['dept_code_name'] == selected_department]
		df_ratio_cum = df_ratio_cum[df_ratio_cum['dept_code_name'] == selected_department]
	
	epoints = df_epoints_cum[selected_year].sum()
	evs = df_evs_cum[selected_year].sum()
	ratio = int(evs/epoints) if epoints != 0 else evs

	st.header("Véhicules électriques par borne de rechargei cumulatif:")

	mettric_col = st.columns(3)
	with mettric_col[0]:
		st.markdown("### Bornes de recharge")
		st.metric(label=selected_department, value='{:,}'.format(epoints), delta=0)
	with mettric_col[1]:
		st.markdown(f"### Véhicules électriques")
		st.metric(label=selected_department, value='{:,}'.format(evs), delta=0)
	with mettric_col[2]:
		st.markdown("### VÉ par borne")
		st.metric(label=selected_department, value='{:,}'.format(ratio), delta=0)

	render_map(df_epoints_cum, df_evs_cum, df_ratio_cum, selected_year)

	st.header("Bornes de recharge")


	# st.write("Cumulative Charging Points")
	# df_epoints_cum = pd.DataFrame(df_epoints.sum(numeric_only=True)).T
	# st.write(df_epoints_cum)
	# st.line_chart(df_epoints_cum.sum())

	# st.write("Cumulative Electric Vehicles")
	# df_evs_cum = pd.DataFrame(df_evs.sum(numeric_only=True)).T
	# st.write(df_evs_cum)
	# st.line_chart(df_evs_cum.sum())

	# df_chart_epoints = df_epoints[['dept_code', selected_year]].copy()
	# st.bar_chart(df_chart_epoints.set_index('dept_code'))
	st.bar_chart(data=df_epoints, x='dept_code', y=selected_year, color="#008000", width=0, height=0, use_container_width=True)

	


	# DEBUG #
	st.write(df_epoints.shape)
	st.write(df_epoints)

	st.write(df_evs.shape)
	st.write(df_evs)

	st.write(df_ratio_cum.shape)
	st.write(df_ratio_cum)
	# # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	


if __name__ == "__main__":
    main()

# Calculate delta between years !!!