import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

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
from datetime import date, timedelta

from covid_deaths import death_map
from covid_deaths import timeline_deaths
from covid_deaths import death_prediction_slope
from covid_deaths import death_prediction_intercept
from covid_deaths import today_deaths
pio.renderers.default = 'colab'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
	'background': '#111111',
	'text': '#6A5ACD'
}

'''Dataframes and Graphs (Cases)'''
covid_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv")
covid_df["FIPS"] = covid_df["FIPS"].apply(lambda x: f"{x:05.0f}") #Fixes the FIPS code of certain states and counties

last_column = covid_df.columns[-1]

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
	counties = json.load(response)

hovertext = covid_df["Admin2"] + ", " + covid_df["Province_State"]
fig = go.Figure(go.Choroplethmapbox(geojson = counties, locations = covid_df["FIPS"], z = covid_df.iloc[:,-1],
									 colorscale = 'Viridis', zmin = 0, zmax = 100000, marker_opacity = 0.5, marker_line_width = 0,
									  hovertext = hovertext))
fig.update_layout(mapbox_style="carto-positron", title='Latest Map and Total Confirmed Case Count by County',
				  mapbox_zoom=4, mapbox_center = {"lat": 40.785794, "lon": -89.209738})

covid_us_scatter = covid_df.loc[:,"1/22/20":last_column].sum(axis = 0)
fig2 = px.scatter(x = covid_us_scatter.index, y = covid_us_scatter.values)
fig2.update_layout(xaxis_title = "Date", yaxis_title = "Cases (Cumulative)", title = "Timeline of Total COVID-19 Cases In The US")

#vaccination data
vax = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')
vax = vax.loc[vax["location"] == "United States"]
total_vax = vax["total_vaccinations"]
total_vax = total_vax.to_frame()
for i in total_vax.iterrows():
  total_vax_value = total_vax.iloc[-1]
total_vax_value = int(total_vax_value)
total_vax_value = str('{:,}'.format(total_vax_value))

vax = vax.loc[:, ["date", "total_vaccinations"]]
vax_series = pd.Series(vax["total_vaccinations"].values, index=vax['date'])
fig_vax = px.scatter(x = vax_series.index, y = vax_series.values)
fig_vax.update_layout(xaxis_title = "Date", yaxis_title = "vaccinations", title = "Total COVID-19 Vaccinations in the U.S")

#Today's stats
original = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/"
try:
	today = date.today() - timedelta(days = 1)
	current_yr = str(today.year)
	current_month = str(today.month)
	current_day = str(today.day)
	current_date = current_month + '-' + current_day + '-' + current_yr
	build_string = original + current_month + '-' + current_day + '-' + current_yr + '.csv'
	print(build_string)
	today_stats = pd.read_csv(build_string)
except:
	today = date.today() - timedelta(days = 2)
	current_yr = str(today.year)
	current_month = str(today.month)
	current_day = str(today.day)
	current_date = current_month + '-' + current_day + '-' + current_yr
	build_string = original + current_month + '-' + current_day + '-' + current_yr + '.csv'
	print(build_string)
	today_stats = pd.read_csv(build_string)

'''Miscellaneous additions'''
total_cases_today = covid_us_scatter.iloc[-1] #Insert commas every 3 digits
total_cases_today_string = str('{:,}'.format(total_cases_today))

total_deaths_today_string = today_deaths()

for col in covid_df.columns: #Get last updated date
  last_updated = col

'''Projections/Predictions/Regressions (Cases)'''
month_before = covid_df.columns[-31]
covid_us_adjust = covid_df.loc[:,month_before:last_column].sum(axis = 0)
covid_us_adjust_df = covid_us_adjust.to_frame()
numbers = []
i = 0
for index, row in covid_us_adjust_df.iterrows():
  numbers.append(i)
  i += 1
numbers
covid_us_adjust_df["days_after_1"] = numbers #how many days after start date

'''(deaths)'''
y = covid_us_adjust_df.iloc[:, 0].values.reshape(-1, 1)
x = covid_us_adjust_df.iloc[:, 1].values.reshape(-1, 1)
model = LinearRegression()
model.fit(x,y)
y_pred_line = model.predict(x)


r_sq = model.score(x, y)
intercept = model.intercept_
slope = model.coef_

'''covid_deaths.py import/call functions'''
fig_death = death_map()
fig2_death = timeline_deaths()
estimate_deaths_slope = death_prediction_slope()
estimate_deaths_intercept = death_prediction_intercept() 


'''Web Dashboard Design'''
app.layout = html.Div(dcc.Tabs([dcc.Tab(label="Cases", 
	style={'font-family':"Verdana",
			'color': 'green',
			'fontweight':'bold'}, 
	children=[
		html.H1(children=html.Strong('COVID-19 Cases in the United States'), style={
			"font-family" :"Georgia",
			'color':colors['text'],
			}
		),
		html.P([html.H2(children=html.Strong('Total Coronavirus Cases:'),
					style={
					'textAlign': 'center'})]
		),

		html.P(html.P(children=(html.Strong(str(total_cases_today_string) + " cases " +
			"(Last updated: " + last_updated + ')')),
				style={'textAlign': 'center'}, 
		)),

		dcc.Graph(
			id='example-graph',
			figure = fig
		),

		dcc.Graph(
				id='example-graph2',
				figure = fig2),
		html.Br(),
		html.Br(),
		html.Br(),
		html.P(children=html.Strong("Current COVID-19 statistics state by state (last updated " +
				current_date + '):'),
				style={'textAlign': 'center'}),

		dash_table.DataTable(
			id='table1',
			columns=[{"name": i, "id": i} for i in today_stats.columns],
			data=today_stats.to_dict('records')),

		html.Br(),
		html.Br(),
		html.Br(),

		html.H5(children=html.Strong('Projection/Prediction Tool!'),
				style={'color': '#8B0000'}),
		html.P(children="Enter a date: Predict the number of cases on a given selected date"),

		dcc.DatePickerSingle(
		id = 'dt-pick-single1',
		date = date.today()),
		html.Div(children="NOTE: This tool is recommended for a selected date within two months in the future from today! Beyond that, its accuracy starts to diminish."),
		html.Div(id='output-date'),

	]),
	#start of tab 2
	dcc.Tab(label='Deaths',
		children=[
		html.H1(children=html.Strong('COVID-19 Deaths in the United States'), style={
			"font-family" :"Georgia",
			'color':colors['text'],
			'fontweight':'bold'
			}
		),
		html.P([html.H2(children=html.Strong('Total Coronavirus Deaths:'),
					style={
					'textAlign': 'center'})]
		),

		html.P(html.P(children=(html.Strong(str(total_deaths_today_string) + " deaths " +
			"(Last updated: " + last_updated + ')')),
				style={'textAlign': 'center'}, 
		)),

		dcc.Graph(id='example-graph3', figure=fig_death),

		dcc.Graph(id='example-graph4',
		figure = fig2_death),

		html.Br(),
		html.Br(),
		html.Br(),

		html.H5(children=html.Strong('Projection/Prediction Tool!'),
				style={'color': '#8B0000'}),
		html.P(children=html.Strong("Enter a date: Predict the number of deaths on a given selected date")),

		dcc.DatePickerSingle(
			id = 'dt-pick-single2',
			date = date.today()), #start_date

		html.Div(children="NOTE: This tool is recommended for a selected date within roughly ~two months in the future from today! Beyond that, its accuracy starts to diminish."),
		html.Div(id='output-date2'),
		],

		style={'font-family':"Verdana",
			   'color': 'green',
				'fontweight':'bold'}),
	#Tab 3
	dcc.Tab(label='Vaccinations',
		children=[
			html.P([html.H2(children=html.Strong('Total Coronavirus Vaccinations:'),
						style={
						'textAlign': 'center'})]
			),

			html.P(html.P(children=(html.Strong(str(total_vax_value) + " vaccinations " +
				"(Last updated: " + last_updated + ')')),
					style={'textAlign': 'center'}, 
			)),

			dcc.Graph(id='example_graph5_vax', figure=fig_vax)
		], 		
		style={'font-family':"Verdana",
			   'color': 'green',
				'fontweight':'bold'}),

	#Tab 4
	dcc.Tab(label='About',
		children=[
			html.H1(children=html.Strong("Welcome to our Coronavirus Dashboard!"), 
				style={'textAlign': 'center',
					   'font-family': 'Pacifico',
					   'color': '#8B4513'}),
			html.Br(),
			html.Br(),
			html.H3(children=html.Strong("Information, statistics, and data visualizations regarding COVID-19 in the U.S."),
				style={'textAlign': 'center',
						'color': '#008080'}),
			html.H5(children="Automatically Updated Every Day!",
				style={'textAlign': 'center',
						'font-family': 'Monaco',
						'color': '#008080'}),
			html.Br(),
			dcc.Markdown('''
			### _**Useful Links and Datasets**_
			* [NYTimes Coronavirus Tracker](https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html)
			* [John Hopkins University's CSSEGISandData COVID-19 Datasets](https://github.com/CSSEGISandData/COVID-19/)
			'''),
			html.Br(),
			dcc.Markdown('''
			_If you have any burning questions to ask, great ideas you'd like to add, or pesky bugs/typos to report, feel free to email me at <johnwl2@illinois.edu> or <parink2@illinois.edu>._
				'''),
			html.Br(),
			dcc.Markdown('''_Connect me with via [LinkedIn](https://www.linkedin.com/in/johnli2023/)!_''')
			],
			
		style={'font-family':"Verdana",
			'color': 'green',
			'fontweight':'bold'}),
	])
)


@app.callback(
	Output('output-date', 'children'),
	Input('dt-pick-single1', 'date'))

def update_output1(date_value):
	if date_value is not None:
		date_object = date.fromisoformat(date_value)
		final = date_object
		start = date.today() - timedelta(days = 30)
		print(start)
		delta = final - start
		delta_days = delta.days
		y_pred = slope * delta_days + intercept
		value = y_pred[0][0]
		print(str(value) + "cases") 
		estimate_case = (int(value/10000) * 10000) #rounding the estimate
		estimate_case_string = str('{:,}'.format(estimate_case))
		estimate_case_string = "There will be approximately " + estimate_case_string + " estimated cases (rounded) on your selected date."
		return estimate_case_string


@app.callback(
	Output('output-date2', 'children'),
	Input('dt-pick-single2', 'date'))

def update_output2(date_value):
	if date_value is not None:
		date_object = date.fromisoformat(date_value)
		final = date_object
		start = date.today() - timedelta(days = 30)
		print(start)
		delta = final - start
		delta_days = delta.days
		y_pred = estimate_deaths_slope * delta_days + estimate_deaths_intercept
		value = y_pred[0][0]
		estimate_deaths = (int(value/1000) * 1000) #rounding the estimate
		estimate_death_string = str('{:,}'.format(estimate_deaths))
		estimate_death_string = "There will be approximately " + estimate_death_string + " estimated cases (rounded) on your selected date."
		return estimate_death_string


if __name__ == '__main__':
	app.run_server(debug=True)