import streamlit as st
import pandas as pd

APP_TITLE = "Map Dashboard"

def main():
	st.set_page_config(APP_TITLE)
	st.title(APP_TITLE)
	st.caption("A simple dashboard to display maps and data tables. made by: `Serge` and `Nammi`. `Plug-In Progress`")

	# Loading data
	df = pd.read_csv("data/born_20240408.csv")

	st.write(df.shape)
	st.write(df.head())
	st.write(df.columns)
 
	# Displaying filters and map
 
	# Displaying data tables and metrics
 

if __name__ == "__main__":
    main()
