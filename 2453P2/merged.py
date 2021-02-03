import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_bootstrap_components
import pandas as pd
import dash_table
import requests
from bs4 import BeautifulSoup
import re

from functions import *

# ------------------------------------------------------------------------------
# --------------Kexin's Data and Plots-------------------------------------------
# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
status = pd.read_csv("data/covid19ON.csv")
vaccine = pd.read_csv("data/vaccine_doses.csv")

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


table1 = dash_table.DataTable(
                         id="vaccine_table",
                         columns=[{"name": i, "id": i}
                                  for i in table.columns],
                         data=table.to_dict('records'),
                         style_cell=dict(textAlign='left'),
                         style_header=dict(backgroundColor="paleturquoise"),
                         style_data=dict(backgroundColor="lavender"))



# ------------------------------------------------------------------------------
# --------------Shikai's Data and Plot-------------------------------------------
# ------------------------------------------------------------------------------
dff = pd.read_csv("data/cases_data.csv")
dff = dff.dropna()
region = ['CENTRAL', 'EAST', 'NORTH', 'TORONTO' ,'WEST']
# ------------------------Done--------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dash_bootstrap_components.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )


fig2 = px.bar(
    data_frame=dff,
    x=['ICU','ICU_vented','hospitalizations'],
    y='oh_region',
    animation_frame="date",
    template='plotly_dark',
    orientation='h'
    )
fig2.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 30
fig2.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 5


# ------------------------------------------------------------------------------
# --------------Stephen's Data and Plot-------------------------------------------
# ------------------------------------------------------------------------------
# ontario testing data
data_s = pd.read_csv('data/percent_positive_by_agegrp.csv')
data_s['DATE'] = pd.to_datetime(data_s['DATE'])

# import ontario region data
odata = pd.read_csv('data/on_cases_by_region.csv')
# clean on_cases by region
odata = pd.read_csv('data/on_cases_by_region.csv')
odata = clean_region(odata)
odata = daily_rec_deaths(odata)
news_df = get_news_table()
all_regions = odata['PHU_NAME'].unique()
my_options = [{"label":col, "value":col} for col in data_s['age_category'].unique()]
my_options.insert(0,{'label':'All', "value": 'All'})
region_options = [{"label": name, "value": name} for name in odata['PHU_NAME'].unique()]
region_options.insert(0,{"label":"All", "value":"All"})



# ------------------------------------------------------------------------------
# ---------------------------Layout---------------------------------------------
# ------------------------------------------------------------------------------

app.layout = dbc.Container([
    
    # row1 This is the title
    dbc.Row(
        dbc.Col(html.H1("COVID19 Dashboard",
                        className='text-center text-primary mb-4'))
    ),
    
    # row2
    dbc.Row(
        dbc.Col(table1)
        ),
    
    html.Br(),
    
    #row3
    dbc.Row([
        
        dbc.Col([
            
            ## drop down
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
            
            ## graph
            dcc.Graph(id='line_chart', figure={})
        ], width={'size':5}), # end of column
        
        dbc.Col([
            dash_table.DataTable(
                    id='news_table',
                    columns=[{"name": i, "id": i} for i in news_df.columns],
                    data=news_df.to_dict('records'),
                    style_table={},
                    fixed_rows={'headers': True},
                    style_cell={
                        'maxWidth':'500px', 'textAlign': 'left', 'font-family':'sans-serif'
                    },
                    style_data={
                        'whiteSpace':'normal', 'height':'auto', 'font-size':'14px'
                    },
                    style_header={
                        'fontWeight': 'bold',
                        'font-size':'16px'
                    },
                )
         ], width={'size':7}), #end of column
        
    ],justify="start"), # end of row
    
    html.Br(),
    
    
    #row4
    dbc.Row([

        dbc.Col([
            dcc.Dropdown(id="slct_impact",
                 options=[{"label": x, "value":x} for x in region],
                 value="TORONTO",multi=False,
                 style={"width": "50%"}),
            
            html.Br(),
   
            dcc.Graph(id='my_bee_map', figure={})
            ], width={'size':12, 'order':1},
        ),

    ], no_gutters=False, justify='start'),  # Horizontal:start,center,end,between,around
    
    
    html.Br(),
    
    #row5
    dbc.Row([
        dbc.Col([
            html.P("Dashboard for monitiorng covid19 in Ontario:",
                   style={"textDecoration": "underline"}),
            dcc.Markdown('''
                    * Language: Python, Dash, Plotly
                    * Data Source:
                      * Ontario data Source:
                    * Github: https://github.com/scbrock/COVID-19-Data-Visualization
                    * Reference:
                    *
                    ''') ,
                                
        ], width={'size':4},
         ),
        
        dbc.Col([
          html.P("Dynamic Animation:"),
          html.Br(),
            dcc.Graph(id='animation', 
                      figure=fig2),
            ], width={'size':8},
        )
   
    ], align="start"),
    html.Br()                     # Vertical: start, center, end







], fluid=True)

                    
                         
                    


# Callback section: connecting the components
# ************************************************************************


@app.callback(
     Output('my_bee_map','figure'),
     Input('slct_impact', 'value')
)
def update_graph(option_slctd):
 

    dfff = dff.copy()
    dfff = dfff[dfff["oh_region"] == option_slctd]
   
    fig = px.line(
        data_frame=dfff,
        x='date',
        y=['ICU','ICU_vented','hospitalizations'],

        template='plotly_dark'
    )

    return  fig


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='line_chart', component_property='figure'),
    [Input(component_id='line_selection', component_property='value')]
)
def update_graph2(line_selected):

    df1 = status.copy()
    df1 = df1[["Reported Date", line_selected]]

    fig1 = px.line(df1, x="Reported Date", y=line_selected)

    return fig1



if __name__=='__main__':
    app.run_server(debug=True, port=8000)