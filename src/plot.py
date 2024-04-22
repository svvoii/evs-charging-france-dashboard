import streamlit as st
import pandas as pd

def count_stations_per_month(df, department_code):
    df = df[df['depart_code']== department_code]
    df['month'] = pd.to_datetime(df['date_maj']).dt.month
    stations_per_month = df.groupby('month')['datagouv_resource_id'].size().reset_index(name='counts')

    st.write(stations_per_month)
    # Create a DataFrame for all months
    all_months = pd.DataFrame({'month': range(1, 13)})

    # Merge the two DataFrames
    stations_per_month = pd.merge(all_months, stations_per_month, on='month', how='left')

    # Replace NaN values with 0
    stations_per_month['counts'] = stations_per_month['counts'].fillna(0)
    st.write(stations_per_month)
    st.bar_chart(stations_per_month, x='month', y='counts')