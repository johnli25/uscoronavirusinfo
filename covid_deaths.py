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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#6A5ACD'
}

'''Dataframes and Graphs (Deaths)'''
covid_deaths = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
covid_deaths["FIPS"] = covid_deaths["FIPS"].apply(lambda x: f"{x:05.0f}") #Fixes FIPS code of certain states and counties

last_column_deaths = covid_deaths.columns[-1]

'''Regressions/Prediction/Projections'''
month_before = covid_deaths.columns[-31]
covid_us_adjust = covid_deaths.loc[:,month_before:last_column_deaths].sum(axis = 0)
covid_us_adjust_df = covid_us_adjust.to_frame()
numbers = []
i = 0
for index, row in covid_us_adjust_df.iterrows():
  numbers.append(i)
  i += 1
numbers
covid_us_adjust_df["days_after_1"] = numbers #how many days after start date

y = covid_us_adjust_df.iloc[:, 0].values.reshape(-1, 1)
x = covid_us_adjust_df.iloc[:, 1].values.reshape(-1, 1)
model = LinearRegression()
model.fit(x,y) 
y_pred_line = model.predict(x)

def today_deaths():
	covid_us_scatter = covid_deaths.loc[:,"1/22/20":last_column_deaths].sum(axis = 0) 
	total_deaths_today = covid_us_scatter.iloc[-1] #Insert commas every 3 digits
	total_deaths_today_string = str('{:,}'.format(total_deaths_today))
	return total_deaths_today_string

def death_map():
	with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
	  counties = json.load(response)

	hovertext = covid_deaths["Admin2"] + ", " + covid_deaths["Province_State"]
	fig_death = go.Figure(go.Choroplethmapbox(geojson = counties, locations = covid_deaths["FIPS"], z = covid_deaths.iloc[:,-1],
	                                     colorscale = 'Viridis', zmin = 0, zmax = 2000, marker_opacity = 0.5, marker_line_width = 0,
	                                     hovertext = hovertext))
	fig_death.update_layout(mapbox_style = "carto-positron", mapbox_zoom = 4, title='Latest Map and Total Death Count by County'
	                  ,mapbox_center = {"lat": 40.785794, "lon": -89.20973})
	return fig_death

def timeline_deaths():
	covid_us_scatter = covid_deaths.loc[:,"1/22/20":last_column_deaths].sum(axis = 0) 
	fig2_death = px.scatter(x = covid_us_scatter.index, y = covid_us_scatter.values)
	fig2_death.update_layout(xaxis_title = "Date", yaxis_title = "Deaths (Cumulative)", title = "Total Number of COVID-19 deaths in the United States")
	return fig2_death

def death_prediction_intercept():
	r_sq = model.score(x,y)
	print(r_sq)
	intercept = model.intercept_
	return intercept

def death_prediction_slope():
	slope = model.coef_
	return slope