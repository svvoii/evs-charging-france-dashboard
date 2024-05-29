# Map Dashboard Visualization of Electric Vehicle Charging Stations Project

## About the Project  

This project was completed as part of the Open Data University and Latitudes France challenge.  

Published project and its description are posted on `data.gouv.fr` and can be found [here](https://www.data.gouv.fr/fr/reuses/visualisation-de-ladoption-des-vehicules-electriques-et-de-linfrastructure-de-recharge-en-france/).  

The description of the challenge can be found here: [Véhicules électriques](https://defis.data.gouv.fr/defis/65a923a083cf5f728c9934b3/).    

For other challenges, visit: [data.gouv.fr](https://defis.data.gouv.fr/).


## Project Overview

This project visualizes the electric vehicle charging stations in France by departments, excluding the overseas territories.  

The Dashboard is built using Streamlit and Plotly for interactive visualizations.  
Here is the link to app on Streamlit community cloud :  
[Plug-in progres France](https://ev-plug-in-france.streamlit.app/)  

### Data Sources

The initial datasets used in this project is sourced from the `data.gouv.fr` website. These datasets are updated regularly.  
Therefor, to keep the data up to date, the datasets must be downloaded from the source and replaced in the `data` folder.  

In particular, the project uses the `charging_points.csv` dataset which contains the information about the electric vehicle charging stations in France. And the `voitures.csv` dataset which contains the information about the electric vehicles in France.  

To download the datasets, go to :  
[charging points](https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/) `charging_points.csv`    
[electric vehicles](https://www.data.gouv.fr/fr/datasets/voitures-particulieres-immatriculees-par-commune-et-par-type-de-recharge-jeu-de-donnees-aaadata/) `voitures.csv`  

Both files must be named as such and placed in the `data` folder.  
If you choos to name this file differently, you must change the name accordinly in `load_dataset()` function in the `epoints_preprocess.py` file for charging points and in `load_dataset()` function in the `vehicles_preprocess.py` file for electric vehicles.    

Additional data sources:  
### Additional data sources:  
[code-postal-corse.csv](https://www.data.corsica/explore/dataset/code-postal-code-insee-2015/table/) - the dataset containing the postal codes for the Corsica island.  
[france_departments.geojson](https://github.com/gregoiredavid/france-geojson) - geojson file with geographical information about the departments in France.  
[Streamlit documentation](https://docs.streamlit.io/)  

##### Department Structure in France:

There are 101 departments which belong to France.  
96 departments compose the mainland France (from 01 to 95 where 20 is the Corsica island devided into 2A and 2B as 2 departments).  
5 departments are overseas territories (971, 972, 973, 974, 976).  

In this project we are visualizing the electric vehicle charging stations in France by departments excluding the overseas territories.  

More information about the departments in France can be found [here](https://www.regions-et-departements.fr/departements-francais?utm_content=cmp-true)  


## Setup

### Preparing the Virtual Environment

Run these commands in the root directory of this project before running the streamlit app:  
1. `python -m venv .venv` - to create a virtual environment  
2. `source .venv/bin/activate` - to activate the virtual environment  
3. Installing necessary packages:
- `python -m pip install pandas` - to install pandas  
- `python -m pip install streamlit` - to install streamlit  
- `python -m pip install streamlit-folium` - to install streamlit-folium which is a streamlit wrapper for folium to create interactive maps.  
- `python -m pip install plotly` - to install plotly (used to create interactive plots, barcharts).  
- `python -m pip install unidecode` - to install unicode (used to deal with french specific characters in the data).  
- `python -m pip install python-dotenv` - to install python-dotenv (for loading Google API key as an environment variable, NOT needed otherwise). This is NOT necessary since I have changed the logic to avoid the extraction of the data via Google API.    
- `python -m pip install tqdm` - to install tqdm which is a progress bar library which is used in `exract_geocode.py`. This is NOT necessary since I have changed the logic to avoid the extraction of the data via Google API.      

##### To install all the packages at once, run the following script:  
`chmod +x setup.sh` - to make the script executable  
`./setup.sh` - to run the script  

## Processing the Data

### Extracting Address Data from Google API
**NOTE**: This is not necessary since the data eventually was processed differently without the need of Google API.   

Initial data from `data.gouv.fr` is incomplete and some of the atributes of the addresses are missing. We use Google API to extract the missing data.  
The code for extracting the data is in the `extract_geocode.py` file.  
After running the script, the extracted data will be saved in the `data` folder as `location_data.csv`.  

**Attention**: Extraction via Google API is expensive and it is also time consuming. Moreover, it dint prove to be very reliable, meaning there are still some missing values in the data, though minor.  

`python extract_geocode.py` - command to extract the address data from Google API given the gps coordinates. There will be a progress bar to show the progress of the extraction (it took around 45 min to receive the data via Google API for arund 25000 gps locations).      
(there ware 25154 unique values, which cost around 75EUR of free trial credit).  
**NOTE**: You will need your own Google API key to make the request !!  

Requested data was only for the missing values in `code_postal` wich are unique based on the `consolidated_longitude` and `consolidated_latitude` columns from the initial dataset for charging points (see mentioned dataset above)  

### Preprocessing the Data (Charging Points and Electric Vehicles)

The majority of time was spent cleaning the initial datasets. The charging points dataset has more than 50 columns and 100,000 rows representing charging points across France. The electric vehicles dataset has close to 500,000 rows representing registered electric vehicles.

#### Electric Vehicles Dataset:

The electric vehicles dataset is well-structured, making it relatively easy to transform and shape. It took around 80 lines of Python code to preprocess this initial dataset.  
The code for that is in the [vehicles_preprocess.py](vehicles_preprocess.py) file.  

Specifically, I added columns for the year and department code, which were extracted from the same dataset.  
The department name was cross-referenced from an additional dataset containing information like postal code and department on the communal level. This dataset: [fr-ref-geo.csv](data/fr-ref-geo.csv) was used to map the department code to its name.  
The final step was transforming the dataframe into a pivot table where each row represents one department and each year is a separate column.  

#### Charging Points Dataset:

The charging points dataset took some time to process.  
I wanted to represent the data by region and group it yearly. The main challenge with this dataset was grouping it by department since there are incomplete columns and values of postal codes in the [original dataset](data/charging_points.csv).    

To tackle this, I worked with four columns representing the `address`, `GPS coordinates`, incomplete column with `postal codes`, and dates `created_at`.  

Partially missing postal codes were extracted from the address string, where available.  
Then, I also cross-referenced the coordinates, meaning the postal code value was copied from the lines with the same coordinates where the value was available.  
Finally, the missing code for about 150 unique locations was added manually based on looked up coordinates on Google Maps.

After the column with postal codes was complete, the following step was to add a department based on the postal code.  

Another issue was discovered due to the representation of the postal codes for the Corsica region.   Conversion from numerical format 20 to 2A, 2B was necessary to maintain data consistency with other datasets as well as GEOJSON data.  

To solve this, I used another dataset with postal codes and other related info for the Corsica region. I mapped the postal code to the proper department code from the additional dataset. This dataset: [code-postal-corse.csv](data/code-postal-corse.csv) was used to map the postal code to the proper department code.  

In a similar way, I mapped the department code to its name and filled it in a new column. 

Also, since the project covers data with regards to mainland France, I dropped the rows where the department code was outside the range of 1 to 95 and 2A, 2B for Corsica.  
After these manipulations, the dataframe was transformed into a pivot table which looks the same as the electric vehicles dataset.

It took around 350 lines to preprocess the dataset with charging points. The code is available here: [epoints_preprocess.py](epoints_preprocess.py).  

Results of the preprocessing are saved in the `data` folder:  
[epoints_pivot.csv](data/epoints_pivot.csv) - the pivot table for the charging points dataset  
[epoints_pivot_cumsum.csv](data/epoints_pivot_cumsum.csv) - the pivot table for the charging points dataset with cumulative sum  
[evs_pivot.csv](data/evs_pivot.csv) - the pivot table for the electric vehicles dataset  
[evs_pivot_cumsum.csv](data/evs_pivot_cumsum.csv) - the pivot table for the electric vehicles dataset with cumulative sum  

## Running the App

Once the data is preprocessed, and needed datasets are available, the following command can be run to launch the streamlit app locally :

```bash
streamlit run map_dashboard.py
```


***
This project was completed on 25.05.2024 by [svvoii](https://github.com/svvoii)
