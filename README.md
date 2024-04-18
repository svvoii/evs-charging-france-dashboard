#### Map Dashboard Visualization of Electric Vehicle Charging Stations Project

The datasets used in this project must be placed in the `data` folder. Sources of the datasets are:  
`https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/` - the link to the data source from `data.gouv.fr` website for electric vehicle charging stations in France. The current name of this dataset used in `streamlit_app.py` is `charging_points.csv`. Data based on (v2.3.1) update as of 2024-04-18.  
If you choos to name this file differently, you must change the name in the `streamlit_app.py` file: `df = pd.read_csv('data/charging_points.csv')`.  



OTHER RESOURCES:  

`https://data.opendatasoft.com/pages/home/` - the link to the data source from `opendatasoft` website.  
`https://geoservices.ign.fr/telechargement-api` - the link to the data source from `IGN` website.  
`https://docs.streamlit.io/` - the link to the `streamlit` documentation.  

#### Before running the streamlit app, the following steps must be taken

##### Preparing the virtual environment
Run these commands in the root directory of this project before running the streamlit app:  
`python -m venv venv` - to create a virtual environment  
`source venv/bin/activate` - to activate the virtual environment  
`python -m pip install pandas` - to install pandas  
`python -m pip install python-dotenv` - to install python-dotenv (for loading Google API key as an environment variable)  
`python -m pip install tqdm` - to install tqdm which is a progress bar library which is used in `exract_geocode.py`. Using google API to extract missing address data in the dataset which takes time (around 25156 unique gps coordinates in the dataset, took around 45 min).   
`python -m pip install streamlit` - to install streamlit  

`pip install --upgrade pip` - to upgrade pip  

##### Preprocessing the data
In this project we filter the data by regions in France. The open-data is incomplete and some of the atributes of the addresses are missing. We use Google API to extract the missing data.  
So, before running the streamlit app, we run the following:  
`python extract_geocode.py` - to extract the address data from Google API given the gps coordinates. There will be a progress bar to show the progress of the extraction (initially it took around 45 min to receive the data via Google API).    
We request the data only fo the missing values in `code_postal` wich are unique based on the `consolidated_longitude` and `consolidated_latitude` columns from the initial `charging_points.csv` dataset (about 25100 unique values).  

##### Running the streamlit app
`streamlit run streamlit_app.py` - to run the streamlit app  
...  



Credit for the tutorial goes to [Code With Zak](https://www.youtube.com/watch?v=uXj76K9Lnqc)  
(continue from min 8:00)  
