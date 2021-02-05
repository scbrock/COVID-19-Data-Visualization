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


app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
status = pd.read_csv("covid19ON.csv")
vaccine = pd.read_csv("vaccine_doses.csv")

status = status[["Reported Date", "Confirmed Positive", "Resolved", "Deaths", "Total Cases"]]
status["Reported Date"] = pd.to_datetime(status["Reported Date"])

# table Info
vaccine["report_date"] = pd.to_datetime(vaccine["report_date"])
vaccine_latest = list([vaccine["total_doses_administered"].values[-1],
                       vaccine["total_individuals_fully_vaccinated"].values[-1]])
status_latest = list([status["Reported Date"].values[-1],
                      status["Total Cases"].values[-1],
                      status["Confirmed Positive"].values[-1]])

table = pd.DataFrame(columns=["Reported Date", "Total Confirmed Cases", "Current Confirmed Cases",
                              "Total Administered Doses", "Total Completed Vaccination"])
table.loc[0] = status_latest + vaccine_latest

# ------------------------------------------------------------------------------

# App layout
app.layout = html.Div([

    html.H1("Covid19 Dashboard", style={'text-align': 'center'}),

    dcc.Dropdown(id="line_selection",
                 options=[
                     {"label": "Total Cases", "value": "Total Cases"},
                     {"label": "Confirmed Cases", "value": "Confirmed Positive"},
                     {"label": "Resolved Cases", "value": "Resolved"},
                     {"label": "Deaths", "value": "Deaths"}],
                 multi=False,
                 value="Total Cases",
                 style={'width': "40%"}
                 ),

    dcc.Graph(id='line_chart', figure={}),

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
    Output(component_id='line_chart', component_property='figure'),
    [Input(component_id='line_selection', component_property='value')]
)
def update_graph(line_selected):

    df1 = status.copy()
    df1 = df1[["Reported Date", line_selected]]

    fig1 = px.line(df1, x="Reported Date", y=line_selected)

    return fig1


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)