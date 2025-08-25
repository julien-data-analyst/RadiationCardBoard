# RadiationCardBoard

This project will analyze the radiation in the natural area.
The data source can be found in the OpenRadiation website by downloading the compressed file.
The notebook above extract these data directly from the html request.
In this project, we will use two tools which are :
- Python (Folium, Pandas, Plotnine, ...)
- Power BI

First part will be about to understand these data with the notebook python named "Analyse_exploratoire.ipynb".
- Analyze the measurements taken
- Analyze the measurement period

Second part will be about the creation of many models to try to predict the radioactivity in the natural area.
- Machine Learning 
- Deep Learning

The last part will be about the creation of a dashboard with Power BI.
- Automate the data extraction (Use of Flask to do it)
- A map highlighting the radioactivity measurements taken
- Bar Graphic to observe the scale of each measurements
- KPI to detect the atypic measurements (%)

For the Power BI Extraction, I created a Flask API which permit to extract the CSV File we need.
With this app, it actualizes the Data every morning.
The only thing else to do is to deploy the little app in a server to test it out on Power BI.