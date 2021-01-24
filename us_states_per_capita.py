import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
from urllib.request import urlopen
import plotly.io as pio
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import scale
from collections import Counter
from datetime import date, timedelta
pio.renderers.default = 'colab'

nytcases = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-states.csv")

data = [['AL',4887871],
['AK',737438],
['AZ',7171646],
['AR',3013825],
['CA',39557045],
['CO',5695564],
['CT',3572665],
['DE',967171],
['DC',702455],
['FL',21299325],
['GA',10519475],
['Guam', 167294 ],
['HI',1420491],
['ID',1754208],
['IL',12741080],
['IN',6691878],
['IA',3156145],
['KS',2911505],
['KY',4468402],
['LA',4659978],
['ME',1338404],
['MD',6042718],
['MA',6902149],
['MI',9995915],
['MN',5611179],
['MS',2986530],
['MO',6126452],
['MT',1062305],
['NE',1929268],
['NV',3034392],
['NH',1356458],
['NJ',8908520],
['NM',2095428],
['NY',19542209],
['NC',10488084],
['ND',760077],
['Northern Mariana Islands', 57216],
['OH',11689442],
['OK',3943079],
['OR',4190713],
['PA',12807060],
['PR',3195153],
['RI',1057315],
['SC',5084127],
['SD',882235],
['TN',6770010],
['TX',28701845],
['UT',3161105],
['VT',626299],
['VA',8517685],
['Virgin Islands', 167294],
['WA',7535591],
['WV',1805832],
['WI',5813568],
['WY',577737]]
pop = pd.DataFrame(data, columns = ['statey', 'Population'])

df = pd.concat([nytcases, pop], axis=1)
cases_capita_list = []
death_capita_list = []
cases_per_cap = (df['cases'] / df['Population']) * 100000
death_per_cap = (df['deaths'] / df['Population']) * 100000
cases_capita_list.extend(cases_per_cap)
death_capita_list.extend(death_per_cap)
df['Cases per 100,000'] = cases_capita_list
df['Deaths per 100,000'] = death_capita_list
#df['fips'] = df['fips'] * 1000
df['fips'] = df["fips"].apply(lambda x: f"{x:02d}") #Fixes FIPS code of certain states and counties

def cases_per_100k():
	with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
	    states = json.load(response)

	hovertext = df['state']
	fig = go.Figure(go.Choroplethmapbox(geojson = states, locations = df["fips"], z = df.iloc[:,-2],
	                                     colorscale = 'tempo', zmin = 0, marker_opacity = 0.5, marker_line_width = 0,
	                                      hovertext = hovertext))
	fig.update_layout(mapbox_style="carto-positron", title = "Total Cases per 100,000 People",
	                  mapbox_zoom=4, mapbox_center = {"lat": 40.785794, "lon": -89.209738})
	return fig

def deaths_per_100k():
	with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
		states = json.load(response)

	hovertext = df['state']
	fig2 = go.Figure(go.Choroplethmapbox(geojson = states, locations = df["fips"], z = df.iloc[:,-1],
	                                     colorscale = 'tempo', zmin = 0, marker_opacity = 0.5, marker_line_width = 0,
	                                      hovertext = hovertext))
	fig2.update_layout(mapbox_style="carto-positron", title = "Total Deaths per 100,000 People",
	                  mapbox_zoom=4, mapbox_center = {"lat": 40.785794, "lon": -89.209738})
	return fig2