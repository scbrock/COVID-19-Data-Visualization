import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_table
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from datetime import date
import datetime
import numpy as np

import requests
from bs4 import BeautifulSoup
import re


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


"""
Web Scraping
"""
def get_updated_date(url='https://globalnews.ca/news/6859636/ontario-coronavirus-timeline/'):
    '''
    return updated date from website
    '''
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.find_all('span', text=re.compile("^Updated"))[0].text

def get_news_table(url = 'https://globalnews.ca/news/6859636/ontario-coronavirus-timeline/'):
    '''
    Get the news data from URL
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    ps = soup.find_all('p')
    events = [ps[i].text.replace(u'\xa0', u' ') for i in range(6,len(ps)) if ps[i].find('strong')]
    events = events[::-1]
    dates = [e.split(':',1)[0] for e in events]
    descriptions = [e.split(':',1)[1].strip()+'\n' for e in events]
    news = pd.DataFrame({'Date':dates, 'Description':descriptions})
    
    return news


news_df = get_news_table()

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


app = JupyterDash(__name__, external_stylesheets = external_stylesheets)
#app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
my_options = [{"label":col, "value":col} for col in data['age_category'].unique()]
my_options.insert(0,{'label':'All', "value": 'All'})

region_options = [{"label": name, "value": name} for name in odata['PHU_NAME'].unique()]
region_options.insert(0,{"label":"All", "value":"All"})

app.layout = html.Div([

    html.H1("Ontario COVID-19 Dashboard", style={'text-align': 'center', 'font-size':'50px'}),
    
    # Row 0 - cool data and news
    html.Div([
        
        html.Div([
            html.H3('Description'),
            html.P('This is a test paragraph')
        ], style={'padding-left':"40px"}, className="six columns bg-white text-dark"),
        
        
        html.Div([
            #html.Br(),
            html.H3('News Updates', className="bg-secondary text-white"),
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
            ),
            html.Div([
                dcc.Link(
                    id='news_link', 
                    children=['Source: Global News Canada'], 
                    href='https://globalnews.ca/news/6859636/ontario-coronavirus-timeline/',
                    target='_blank',
                    style={'color':'white'}
                )
            ], style={'font-size':'14px'})

        ], style={}, className="six columns text-dark"),
        

        

    ], className="row"),
    html.Br(),
   
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
    # ROW 2
    #html.Br(),
        html.Div([
        html.Div([
            #html.H3('Plot 1'),
            html.Br(),
            dcc.Graph(id='placeholder', figure={}
                        )
        ], style={"padding-left":"40px"}, className="six columns"),
        
        html.Div([
            dcc.Tabs([
                dcc.Tab(label='Active Cases', children=[
                    dcc.Graph(
                        id='bar1',
                        figure={}
                    )
                ]),
                dcc.Tab(label='Resolved Cases', children=[
                    dcc.Graph(
                        id='bar2',
                        figure={}
                    )
                ]),
                dcc.Tab(label='Fatal Cases', children=[
                    dcc.Graph(
                        id='bar3',
                        figure={}
                    )
                ]),
            ])
        ], style={}, className='six columns text-dark')


    ], className="row"),
    
    # ROW 3 - testing and active
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
            dcc.Tabs([
                dcc.Tab(label='Active Cases', children=[
                    dcc.Graph(
                        id='graph2',
                        figure={}
                    )
                ]),
                dcc.Tab(label='Resolved Cases', children=[
                    dcc.Graph(
                        id='graph3',
                        figure={}
                    )
                ]),
                dcc.Tab(label='Fatal Cases', children=[
                    dcc.Graph(
                        id='graph4',
                        figure={}
                    )
                ]),
            ])
        ], style={}, className='six columns text-dark')


    ], className="row"),
    
  
    
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
    html.Br(),


    
    
], className='bg-secondary text-white')




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
            title="Percent Positive",
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


@app.callback([Output(component_id='bar1', component_property='figure'),
              Output(component_id='bar2', component_property='figure'),
              Output(component_id='bar3', component_property='figure')],
             [Input('region_select', 'value')])

def build_bars(regions):
    '''
    build 3 bar charts: active, resolved, deaths for region cases
    '''

    
    if 'All' in regions:
        regions = all_regions
    elif len(regions) == 0:
        return {}, {}, {}
    
    maxdate = odata['DATE'].max()
    
    df = odata[odata['PHU_NAME'].isin(regions) & (odata['DATE'] == str(maxdate))]
    
    fig1 = px.bar(df, x="PHU_NAME", y="ACTIVE_CASES", color = "PHU_NAME", title="Active Cases as of "+maxdate)
    
    fig2 = px.bar(df, x="PHU_NAME", y="RESOLVED_CASES", color = "PHU_NAME", title="Resolved Cases as of "+maxdate)
    fig3 = px.bar(df, x="PHU_NAME", y="DEATHS", color = "PHU_NAME", title="Fatal Cases as of "+maxdate)
    
    return fig1, fig2, fig3
    

app.run_server(mode='external')


