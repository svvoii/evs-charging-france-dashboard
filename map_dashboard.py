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

	evs_actual = pd.read_csv('data/evs_pivot.csv')
	evs_actual['dept_code_name'] = evs_actual['dept_code'] + ' - ' + evs_actual['dept_name']

	evs_cum = pd.read_csv('data/evs_pivot_cumsum.csv')
	evs_cum['dept_code_name'] = evs_cum['dept_code'] + ' - ' + evs_cum['dept_name']

	# Calculating the ratio of electric vehicles per charging point as the new dataframe
	ratio_cum = evs_cum.copy()
	for column in evs_cum.columns:
		if column not in ['dept_code', 'dept_name', 'dept_code_name']:
			ratio_cum[column] = evs_cum[column].div(epoints_cum[column]).replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
	
	return epoints_actual, evs_actual, epoints_cum, evs_cum, ratio_cum
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# def ft_sidebar(df):
def ft_sidebar(df_epoints, df_evs):
	with st.sidebar:
		year_list = ['2024', '2023', '2022', '2021', '2020']
		selected_year = st.selectbox('Select year', year_list)
		# year_list = ['2020', '2021', '2022', '2023', '2024']
		# selected_year = st.radio('Select year', year_list)
		
		dept_list = list(df_epoints['dept_code_name'].unique())
		dept_list.insert(0, 'France entière')
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
		geo_data=geojson_dict,
		name=legend_name,
		data=ratio_cum,
		columns=['dept_code', column],
		key_on='feature.properties.code',
		fill_color=color,
		fill_opacity=0.7,
		line_opacity=0.2,
		legend_name=legend_name,
	).add_to(map)

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
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@st.cache_data
def plot_barchart(df, title):
	years = ['2020', '2021', '2022', '2023', '2024']
	data = []
	for year in years:
		data.append(go.Bar(name=year, x=df['dept_code_name'], y=df[year]))
	fig = go.Figure(data=data)
	fig.update_layout(barmode='stack', title=title)
	st.plotly_chart(fig, use_container_width=True, height=600)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# This function calculates the change in values between the selected year and the previous year
def calculate_delta(df_epoints_cum, df_evs_cum, selected_year):
	# Calculating the values for the selected year
	epoints_current = df_epoints_cum[selected_year].sum()
	evs_current = df_evs_cum[selected_year].sum()
	ratio_current = int(evs_current/epoints_current) if epoints_current != 0 else evs_current

	# Calculating the values for the previous year
	previous_year = str(int(selected_year) - 1)
	epoints_previous = df_epoints_cum[previous_year].sum() if previous_year in df_epoints_cum.columns else 0
	evs_previous = df_evs_cum[previous_year].sum() if previous_year in df_evs_cum.columns else 0
	ratio_previous = int(evs_previous/epoints_previous) if epoints_previous != 0 else evs_previous

	# Calculating the delta between the selected year and the previous year
	delta_epoints = epoints_current - epoints_previous
	delta_evs = evs_current - evs_previous
	delta_ratio = ratio_current - ratio_previous

	return epoints_current, evs_current, ratio_current, delta_epoints, delta_evs, delta_ratio
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	# Load the data
	df_epoints, df_evs, df_epoints_cum, df_evs_cum, df_ratio_cum = load_datasets()

	st.title("DASHBOARD")
	st.header(":electric_plug: Bornes de recharge et Véhicules électriques en France :car:")

	selected_year, selected_department = ft_sidebar(df_epoints_cum, df_evs_cum)

	plot_barchart(df_epoints, 'Bornes de recharge par département, cumulatif :')
	plot_barchart(df_evs, 'Véhicules électriques par département, cumulatif :')

	if selected_department != 'France entière':
		df_epoints_cum = df_epoints_cum[df_epoints_cum['dept_code_name'] == selected_department]
		df_evs_cum = df_evs_cum[df_evs_cum['dept_code_name'] == selected_department]
		df_ratio_cum = df_ratio_cum[df_ratio_cum['dept_code_name'] == selected_department]
	
	# Calculating the delta between the selected year and the previous year
	epoints_current, evs_current, ratio_current, delta_epoints, delta_evs, delta_ratio = calculate_delta(df_epoints_cum, df_evs_cum, selected_year)

	st.header("Véhicules électriques par borne de rechargei cumulatif :")

	mettric_col = st.columns(3)
	with mettric_col[0]:
		st.markdown("### VÉ par borne")
		st.metric(label=selected_department, value='{:,}'.format(ratio_current), delta='{:}'.format(int(delta_ratio)), delta_color='inverse')
	with mettric_col[1]:
		st.markdown(f"### Véhicules électriques")
		st.metric(label=selected_department, value='{:,}'.format(evs_current), delta='{:,}'.format(int(delta_evs)))
	with mettric_col[2]:
		st.markdown("### Bornes de recharge")
		st.metric(label=selected_department, value='{:,}'.format(epoints_current), delta='{:,}'.format(int(delta_epoints)))

	render_map(df_epoints_cum, df_evs_cum, df_ratio_cum, selected_year)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    main()

# Saving some emojis
# st.header("Ce tableau de bord montre le nombre de véhicules électriques et de points de charge en France métropolitaine.")
# st.title("🇫🇷, :fr:")
# st.title("🔋, :battery:")
# st.title("🔌, :electric_plug:")
# st.title("🚗, :car:")
# st.title("🚙, \U0001F699")
# st.title("⚡, :zap:")
# st.title("Ce Dashboard montre le nombre de véhicules électriques et de points de charge en France métropolitaine.")

