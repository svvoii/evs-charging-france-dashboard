#!/bin/bash

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip
python3 -m pip install --upgrade pip
# Install the necessary Python packages
python3 -m pip install pandas
# python -m pip install python-dotenv
python3 -m pip install tqdm
python3 -m pip install streamlit
python3 -m pip install streamlit-folium
python3 -m pip install unidecode
