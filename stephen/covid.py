import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from datetime import date
import datetime
import numpy as np


# ontario testing data
data = pd.read_csv('data/percent_positive_by_agegrp.csv')
data['DATE'] = pd.to_datetime(data['DATE'])

# import ontario region data
odata = pd.read_csv('../data/on_cases_by_region.csv')

# clean on_cases by region
def clean_region(data_input):
    data = data_input.copy()
    cols = ['FILE_DATE', 'PHU_NAME', 'ACTIVE_CASES',
       'RESOLVED_CASES', 'DEATHS']
    data = data[cols]
    
    # fix FILE_DATE
    data['FILE_DATE'] = [str(datetime.datetime.strptime(str(s), '%Y%m%d').date()) for s in data['FILE_DATE']]
    data = data.rename({'FILE_DATE': "DATE"}, axis='columns')
    data = data.sort_values(['PHU_NAME', 'DATE'])
    return data

def daily_rec_deaths(data):
    '''
    calculate daily deaths and recoveries from data
    returns:
        dataframe with daily resolved and daily deaths
    '''
    
    df = data.copy()
    
    regions = data.PHU_NAME.unique()
    daily_cnts = pd.DataFrame({})
    for r in regions:
        tmp = df[df.PHU_NAME == r]
        tmp['DAILY_DEATHS'] = tmp['DEATHS'] - tmp['DEATHS'].shift(1)
        tmp['DAILY_RECOVERED'] = tmp['RESOLVED_CASES'] - tmp['RESOLVED_CASES'].shift(1)
        daily_cnts = pd.concat([daily_cnts, tmp], axis=0)
    
    return daily_cnts

odata = clean_region(odata)
odata = daily_rec_deaths(odata)


'''
Start of Dashboard Application
'''

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

all_regions = odata['PHU_NAME'].unique()


app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
my_options = [{"label":col, "value":col} for col in data['age_category'].unique()]
my_options.insert(0,{'label':'All', "value": 'All'})

region_options = [{"label": name, "value": name} for name in odata['PHU_NAME'].unique()]
region_options.insert(0,{"label":"All", "value":"All"})

app.layout = html.Div([

    html.H1("Ontario COVID-19 Dashboard", style={'text-align': 'center', 'font-size':'50px'}),
    
   
    # ROW 1 - Headers, dropdowns, etc
    html.Div([
        html.Div([
            html.H3('Select Age Group(s)', style={'padding-left':"40px"}),
            dcc.Dropdown(id="age_group",
                options=my_options,
                multi=True,
                value=[my_options[0]['value']],
                style={"width":"100%", "display":"inline-block", "padding-left":"40px"},
                className='text-dark'
            )
        ], className="three columns"),

        html.Div([
            html.H3('Select Date Range'),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=date(2020, 1, 1),
                end_date=date(2020, 12, 1),
                end_date_placeholder_text='Select a date!',
                style = {'width': "100%", "display":"inline-block"}
            )
        ], className="three columns"),
        html.Div([
            html.H3('Select Region(s)', style={'padding-left':"0px"}),
            dcc.Dropdown(id="region_select",
                options=region_options,
                multi=True,
                value=[region_options[0]['value']],
                style={"width":"100%", "display":"inline-block", "padding-left":"40px"},
                className='text-dark'
            )
        ], className="three columns"),
        html.Div([
            html.H3('Options', style={'padding-left':"0px"}),
            dcc.Checklist(
                id="per100k",
                options=[
                    {'label': 'Count per 100,000 people (not including daily resolved or fatal cases)', 'value': '100k'},
                ],
                value=[],
                style={'font-size':'12px'}
            )  
        ], className="three columns"),
    ], className="row"),
    

    html.Div(id='select_ref', children=[], style={"padding-left":"40px"}),
    #html.Br(),
    
    # ROW 2 - testing and active
    html.Div([
        html.Div([
            #html.H3('Plot 1'),
            html.Br(),
            dcc.Graph(id='graph1', figure=px.line(
                            data_frame = odata,
                            x = 'DATE',
                            y = 'RESOLVED_CASES',
                            color = 'PHU_NAME',
                            title="Active Cases vs Date",
                            labels = {
                                'DATE': 'Date',
                                'RESOLVED_CASES': "Number of Resolved Cases"
                            }
                        ))
        ], style={"padding-left":"40px"}, className="six columns"),

        html.Div([
            html.Br(),
            #html.H3('Plot 2'),
            dcc.Graph(id='graph2', figure= px.line(
                            data_frame = odata,
                            x = 'DATE',
                            y = 'ACTIVE_CASES',
                            color = 'PHU_NAME',
                            title="Active Cases vs Date",
                            labels = {
                                'DATE': 'Date',
                                'ACTIVE_CASES': "Number of Active Cases"
                            }
                        )
                     )
        ], className="six columns"),
    ], className="row"),
    
    
    # Row 3 - Recovered and Deaths
    html.Div([
        html.Div([
            html.Br(),
            #html.H3('Resolved Cases'),
            dcc.Graph(id='graph3', figure=px.line(
                            data_frame = odata,
                            x = 'DATE',
                            y = 'RESOLVED_CASES',
                            color = 'PHU_NAME',
                            title="Active Cases vs Date",
                            labels = {
                                'DATE': 'Date',
                                'RESOLVED_CASES': "Number of Resolved Cases"
                            }
                        ))
        ], style={"padding-left":"40px"}, className="six columns"),

        html.Div([
            html.Br(),
            #html.H3('New Fatal Cases by Day'),
            dcc.Graph(id='graph4', figure= {})
        ], className="six columns"),
    ], className="row"),
    
    
    # introduce plots of change per day
    # add trend line
    
    # deaths by day
    
    # Row 4 - Deaths by day
    html.Div([
        
        html.Div([
            html.Br(),
            #html.H3('Daily Recovered'),
            dcc.Graph(id='graph6', figure={})
        ], style={"padding-left":"40px"}, className="six columns"),

    
        html.Div([
            html.Br(),
            #html.H3('Fatalities'),
            dcc.Graph(id='graph5', figure={})
        ], className="six columns"),
    ], className="row"),

    
    
], className='bg-secondary text-white')

# @app.callback(
#     [Output(component_id='select_ref', component_property='children'),
#      Output(component_id='graph1', component_property='figure')],
#     [Input(component_id='age_group', component_property='value')]
# )
# # 1. callback selects value, 
# # 2. value is sent to function (defined after callback)
# # 3. function returned values go into the output of callback



@app.callback(
    [Output(component_id='select_ref', component_property='children'),
     Output(component_id='graph1', component_property='figure')],
    [Input(component_id='age_group', component_property='value'),
     Input(component_id='date-picker-range', component_property='start_date'),
     Input(component_id='date-picker-range', component_property='end_date')]
)

def update_graph_date(option_slctd, start, end):
    select_ref = "The age group chosen by user: {}".format(option_slctd)
    
    if 'All' in option_slctd:
        option_slctd = ['0to13', '14to17', '18to24', '25to64', '65+']

    
    sdt = pd.to_datetime(start)
    edt = pd.to_datetime(end)
    
    df = data[(data['age_category'].isin(option_slctd)) & (data['DATE'] >= sdt) & (data['DATE'] <= edt)] #.groupby('DATE').sum().reset_index()
    df = df.sort_values('DATE')
    print(df.head())

    if df.shape[0] == 0:
        fig = px.line()
    else:
        fig = px.line(
            data_frame = df,
            x = 'DATE',
            y = 'percent_positive_7d_avg',
            color = 'age_category',
            title="Percent Positive vs Date",
            labels = {
                'DATE': 'Date',
                'percent_positive_7d_avg': "Percent Positive (7 Day Average)"
            }
        )


    fig.update_xaxes(tickangle=90, nticks=20)
    #fig.update_layout(width=int(700))
    
    return select_ref, fig


# add callback for another graph
@app.callback([Output(component_id='graph2', component_property='figure'),
              Output(component_id='graph3', component_property='figure'),
              Output(component_id='graph4', component_property='figure'),
              Output(component_id='graph5', component_property='figure'),
              Output(component_id='graph6', component_property='figure')],
             [Input('region_select', 'value'),
             Input('date-picker-range', 'start_date'),
             Input('date-picker-range', 'end_date'),
             Input('per100k', 'value')])

def graph2(regions, start, end, is_100k):
    '''
    function for working with the graph on the right at the top
    '''
    
    if 'All' in regions:
        regions = all_regions
    elif len(regions) == 0:
        return {}, {}, {}, {}, {}
    
    start = str(pd.to_datetime(start).date())
    end = str(pd.to_datetime(end).date())
    
    df = odata
    df = odata[odata['PHU_NAME'].isin(regions) & (odata['DATE'] >= start) & (odata['DATE'] <= end)]
    
    
    fig1_title = "Active Cases"
    fig1_yaxis = "Number of Active Cases"
    
    fig2_title = "Resolved Cases"
    fig2_yaxis = "Cumulative Number of Resolved Cases"
        
    fig3_title = "Fatal Cases"
    fig3_yaxis = "Cumulative Number of Fatal Cases"
    
    if len(is_100k) > 0:
        # list is not empty, so divide all counts by 100k
        df['ACTIVE_CASES'] = df["ACTIVE_CASES"]/100000
        df['RESOLVED_CASES'] = df["RESOLVED_CASES"]/100000
        df['DEATHS'] = df["DEATHS"]/100000
        fig1_title += ' Per 100,000'
        fig1_yaxis += ' Per 100,000'
        fig2_title += ' Per 100,000'
        fig2_yaxis += ' Per 100,000'
        fig3_title += ' Per 100,000'
        fig3_yaxis += ' Per 100,000'
        
        
    fig1 = px.line(
        data_frame = df,
        x = 'DATE',
        y = 'ACTIVE_CASES',
        color = 'PHU_NAME',
        title=fig1_title,
        labels = {
            'DATE': 'Date',
            'ACTIVE_CASES': fig1_yaxis,
            "PHU_NAME": "Region"
        }
    )
    fig2 = px.line(
        data_frame = df,
        x = 'DATE',
        y = 'RESOLVED_CASES',
        color = 'PHU_NAME',
        title=fig2_title,
        labels = {
            'DATE': 'Date',
            'RESOLVED_CASES': fig2_yaxis,
            "PHU_NAME": "Region"
        }
    )
    fig3 = px.line(
        data_frame = df,
        x = 'DATE',
        y = 'DEATHS',
        color = 'PHU_NAME',
        title=fig3_title,
        labels = {
            'DATE': 'Date',
            'DEATHS': fig3_yaxis,
            "PHU_NAME": "Region"
        }
    )
    
    fig4 = px.line(
        data_frame = df,
        x = 'DATE',
        y = 'DAILY_DEATHS',
        color = 'PHU_NAME',
        title="Daily Fatal Cases",
        labels = {
            'DATE': 'Date',
            'DAILY_DEATHS': "Daily Number of Fatal Cases",
            "PHU_NAME": "Region"
        }
    )
    
    fig5 = px.line(
        data_frame = df,
        x = 'DATE',
        y = 'DAILY_RECOVERED',
        color = 'PHU_NAME',
        title="Daily Resolved Cases",
        labels = {
            'DATE': 'Date',
            'DAILY_RECOVERED': "Daily Number of Recovered Cases",
            "PHU_NAME": "Region"
        }
    )
    
    
    
    return fig1, fig2, fig3, fig4, fig5

    

app.run_server()

