import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import json


app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
url = "https://data.ontario.ca/dataset/f4f86e54-872d-43f8-8a86-3892fd3cb5e6/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11/download/covidtesting.csv"
status = pd.read_csv(url)
url = "https://data.ontario.ca/dataset/752ce2b7-c15a-4965-a3dc-397bf405e7cc/resource/8a89caa9-511c-4568-af89-7f2174b4378c/download/vaccine_doses.csv"
vaccine = pd.read_csv(url)

status = status[["Reported Date", "Confirmed Positive", "Resolved", "Deaths", "Total Cases"]]
status["Reported Date"] = pd.to_datetime(status["Reported Date"]).dt.date
status = status.rename(columns={"Confirmed Positive":"Active Cases", "Total Cases":"Confirmed Positive"})

# Calculate daily cases
daily_status = status[["Active Cases", "Confirmed Positive", "Resolved", "Deaths"]].diff()
daily_status["Reported Date"] = status["Reported Date"]


# table Info
vaccine["report_date"] = pd.to_datetime(vaccine["report_date"]).dt.date
mod_vaccine = vaccine.tail(2)[["total_doses_administered", "total_individuals_fully_vaccinated"]]
mod_vaccine["total_doses_administered"] = [int(data.replace(",", "")) for data in mod_vaccine["total_doses_administered"]]
mod_vaccine["total_individuals_fully_vaccinated"] = [int(data.replace(",", "")) for data in mod_vaccine["total_individuals_fully_vaccinated"]]

vaccine_latest = list([mod_vaccine["total_doses_administered"].values[-1],
                       mod_vaccine["total_individuals_fully_vaccinated"].values[-1]])
status_latest = list([status["Reported Date"].values[-1],
                      status["Active Cases"].values[-1],
                      status["Confirmed Positive"].values[-1]])

table = pd.DataFrame(columns=["Reported Date", "Total Active Cases", "Total Confirmed Cases",
                              "Total Administered Doses", "Total Completed Vaccination"])
table.loc[0] = status_latest + vaccine_latest

diff_vaccine = mod_vaccine.diff()

table.loc[1] = ["Change from the previous day",
                daily_status["Active Cases"].values[-1],
                daily_status["Confirmed Positive"].values[-1],
                diff_vaccine["total_doses_administered"].values[-1],
                diff_vaccine["total_individuals_fully_vaccinated"].values[-1]]


# map
url = "https://data.ontario.ca/dataset/1115d5fe-dd84-4c69-b5ed-05bf0c0a0ff9/resource/d1bfe1ad-6575-4352-8302-09ca81f7ddfc/download/cases_by_status_and_phu.csv"
phu_cases = pd.read_csv(url)

phu_cases["FILE_DATE"] = pd.to_datetime(phu_cases["FILE_DATE"])
date = phu_cases["FILE_DATE"].values[-1]
regions = phu_cases[phu_cases["FILE_DATE"] == date]

regions.columns = ["FILE_DATE", "PHU_NAME", "PHU_NUM", "Active Cases", "Resolved Cases", "Deaths"]

phu_map = json.load(open("data/ON_PHU.geojson", "r"))

case_name = ["Active Cases", "Resolved Cases", "Deaths"]


# ------------------------------------------------------------------------------

# App layout
app.layout = html.Div([

    html.H1("Covid19 Dashboard", style={'text-align': 'center'}),

    # line chart
    dcc.Dropdown(id="line_option",
                 options=[
                     {"label": "Confirmed Cases", "value": "Confirmed Positive"},
                     {"label": "Resolved Cases", "value": "Resolved"},
                     {"label": "Deaths", "value": "Deaths"}],
                 multi=False,
                 value="Confirmed Positive",
                 style={'width': "40%"}
                 ),

    dcc.Graph(id='line_chart', figure={}),

    # map
    dcc.Tabs([
                dcc.Tab(label='Active Cases', children=[
                    dcc.Graph(
                        id='Active_map',
                        figure={}
                    )
                ]),
                dcc.Tab(label='Resolved', children=[
                    dcc.Graph(
                        id='Resolved_map',
                        figure={}
                    )
                ]),
                dcc.Tab(label='Deaths', children=[
                    dcc.Graph(
                        id='Deaths_map',
                        figure={}
                    )
                ]),
            ]),

    # table
    dash_table.DataTable(id="vaccine_table",
                         columns=[{"name": i, "id": i}
                                  for i in table.columns],
                         data=table.to_dict('records'),
                         style_cell=dict(textAlign='left'),
                         style_header=dict(backgroundColor="paleturquoise"),
                         style_data=dict(backgroundColor="lavender"))


])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='line_chart', component_property='figure'),
     Output(component_id='Active_map', component_property='figure'),
     Output(component_id='Resolved_map', component_property='figure'),
     Output(component_id='Deaths_map', component_property='figure')],
    [Input(component_id='line_option', component_property='value')]
)
def update_line_graph(line_option):

    fig = px.line(daily_status, x="Reported Date", y=line_option)

    active_map = px.choropleth(regions,
                               geojson=phu_map,
                               color="Active Cases",
                               locations="PHU_NUM",
                               featureidkey="properties.PHU_ID",
                               color_continuous_scale="mint")
    active_map.update_geos(fitbounds='locations', visible=False)
    active_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    resolved_map = px.choropleth(regions,
                                 geojson=phu_map,
                                 color="Resolved Cases",
                                 locations="PHU_NUM",
                                 featureidkey="properties.PHU_ID",
                                 color_continuous_scale="mint")
    resolved_map.update_geos(fitbounds='locations', visible=False)
    resolved_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    deaths_map = px.choropleth(regions,
                               geojson=phu_map,
                               color="Deaths",
                               locations="PHU_NUM",
                               featureidkey="properties.PHU_ID",
                               color_continuous_scale="mint")
    deaths_map.update_geos(fitbounds='locations', visible=False)
    deaths_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig, active_map, resolved_map, deaths_map

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)