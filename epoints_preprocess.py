import streamlit as st
import pandas as pd

st.set_page_config(
	page_title="Data Clean",
	layout="wide",
)

def load_dataset():
	df = pd.read_csv('data/charging_points.csv', dtype=str)
	return df


def main():
	df = load_dataset()
	st.write(df)
	st.write(df.columns)

	stats = df.describe(include='all')
	st.write(stats)



if __name__ == '__main__':
    main()