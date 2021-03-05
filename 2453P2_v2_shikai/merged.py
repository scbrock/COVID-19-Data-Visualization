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
from datetime import date
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

from functions import *


#This is the data link
# ------------------------------------------------------------------------------
# --------------Kexin's Data and Plots-------------------------------------------
# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)

# confirmed cases, resolved cases, deaths
url = "https://data.ontario.ca/dataset/f4f86e54-872d-43f8-8a86-3892fd3cb5e6/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11/download/covidtesting.csv"
status = pd.read_csv(url)
# vaccine data
url = "https://data.ontario.ca/dataset/752ce2b7-c15a-4965-a3dc-397bf405e7cc/resource/8a89caa9-511c-4568-af89-7f2174b4378c/download/vaccine_doses.csv"
vaccine = pd.read_csv(url)

# select required columns and rename them
status = status[["Reported Date", "Confirmed Positive", "Resolved", "Deaths", "Total Cases"]]
status["Reported Date"] = pd.to_datetime(status["Reported Date"]).dt.date
status = status.rename(columns={"Confirmed Positive":"Active Cases", "Total Cases":"Confirmed Positive"})

# Calculate daily cases
daily_status = status[["Active Cases", "Confirmed Positive", "Resolved", "Deaths"]].diff()
daily_status["Reported Date"] = status["Reported Date"]


# table Info
# get total_doses_administered and total_individuals_fully_vaccinated which shown in summary table
vaccine["report_date"] = pd.to_datetime(vaccine["report_date"]).dt.date
mod_vaccine = vaccine.tail(2)[["total_doses_administered", "total_individuals_fully_vaccinated"]]
mod_vaccine["total_doses_administered"] = [int(data.replace(",", "")) for data in mod_vaccine["total_doses_administered"]]
mod_vaccine["total_individuals_fully_vaccinated"] = [int(data.replace(",", "")) for data in mod_vaccine["total_individuals_fully_vaccinated"]]

vaccine_latest = list([mod_vaccine["total_doses_administered"].values[-1],
                       mod_vaccine["total_individuals_fully_vaccinated"].values[-1]])

# get date current confirmed cases and total confirmed cases for summary table
status_latest = list([status["Reported Date"].values[-1],
                      status["Active Cases"].values[-1],
                      status["Confirmed Positive"].values[-1]])

# build the table
table = pd.DataFrame(columns=["Reported Date", "Total Active Cases", "Total Confirmed Cases",
                              "Total Administered Doses", "Total Completed Vaccination"])
table.loc[0] = status_latest + vaccine_latest

# calculate the changes from the previous day
diff_vaccine = mod_vaccine.diff()

table.loc[1] = ["Change from the previous day",
                daily_status["Active Cases"].values[-1],
                daily_status["Confirmed Positive"].values[-1],
                diff_vaccine["total_doses_administered"].values[-1],
                diff_vaccine["total_individuals_fully_vaccinated"].values[-1]]



# map
# read region cases data
url = "https://data.ontario.ca/dataset/1115d5fe-dd84-4c69-b5ed-05bf0c0a0ff9/resource/d1bfe1ad-6575-4352-8302-09ca81f7ddfc/download/cases_by_status_and_phu.csv"
phu_cases = pd.read_csv(url)
# select up to date cases
phu_cases["FILE_DATE"] = pd.to_datetime(phu_cases["FILE_DATE"])
dates = phu_cases["FILE_DATE"].values[-1]
regions = phu_cases[phu_cases["FILE_DATE"] == dates]

regions.columns = ["FILE_DATE", "PHU_NAME", "PHU_NUM", "Active Cases", "Resolved Cases", "Deaths"]

# read phu geojson file
phu_map = json.load(open("data/ON_PHU.geojson", "r"))

case_name = ["Active Cases", "Resolved Cases", "Deaths"]

# modified geojson file to make PHU_NAME as the feature id
phu_dict = regions.set_index('PHU_NUM')['PHU_NAME'].to_dict()

for i in range(34):
    id = phu_map['features'][i]['properties']['PHU_ID']
    phu_map['features'][i]['properties']['PHU_ID'] = phu_dict[id]

# create active map, resolved map, death map
active_map = px.choropleth(regions,
                           geojson=phu_map,
                           color="Active Cases",
                           locations="PHU_NAME",
                           featureidkey="properties.PHU_ID",
                           color_continuous_scale="darkmint",
                           template='plotly_dark')
active_map.update_geos(fitbounds='locations', visible=False)
active_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

resolved_map = px.choropleth(regions,
                             geojson=phu_map,
                             color="Resolved Cases",
                             locations="PHU_NAME",
                             featureidkey="properties.PHU_ID",
                             color_continuous_scale="darkmint",
                             template='plotly_dark')
resolved_map.update_geos(fitbounds='locations', visible=False)
resolved_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

deaths_map = px.choropleth(regions,
                           geojson=phu_map,
                           color="Deaths",
                           locations="PHU_NAME",
                           featureidkey="properties.PHU_ID",
                           color_continuous_scale="darkmint",
                           template='plotly_dark')
deaths_map.update_geos(fitbounds='locations', visible=False)
deaths_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

   



# ------------------------------------------------------------------------------
# --------------Shikai's Data and Plot-------------------------------------------
# ------------------------------------------------------------------------------

url2 = "https://data.ontario.ca/dataset/8f3a449b-bde5-4631-ada6-8bd94dbc7d15/resource/e760480e-1f95-4634-a923-98161cfb02fa/download/region_hospital_icu_covid_data.csv"

dff = pd.read_csv(url2)
dff = dff.dropna()
region = ['CENTRAL', 'EAST', 'NORTH', 'TORONTO' ,'WEST']
# ------------------------Done--------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dash_bootstrap_components.themes.DARKLY],
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
#data_s = pd.read_csv('data/percent_positive_by_agegrp.csv')
data_s = pd.read_csv('https://data.ontario.ca/dataset/ab5f4a2b-7219-4dc7-9e4d-aa4036c5bf36/resource/05214a0d-d8d9-4ea4-8d2a-f6e3833ba471/download/percent_positive_by_agegrp.csv')
data_s['DATE'] = pd.to_datetime(data_s['DATE'])

# import ontario region data
#odata = pd.read_csv('data/on_cases_by_region.csv')
# clean on_cases by region
#odata = pd.read_csv('data/on_cases_by_region.csv')
odata = pd.read_csv('https://data.ontario.ca/dataset/1115d5fe-dd84-4c69-b5ed-05bf0c0a0ff9/resource/d1bfe1ad-6575-4352-8302-09ca81f7ddfc/download/cases_by_status_and_phu.csv')
odata = clean_region(odata)
odata = daily_rec_deaths(odata)
news_df = get_news_table()
on_region_pop = pd.read_csv('data/ontario_region_population.csv')
all_regions = odata['PHU_NAME'].unique()
my_options = [{"label":col, "value":col} for col in data_s['age_category'].unique()]
my_options.insert(0,{'label':'All', "value": 'All'})
region_options = [{"label": name, "value": name} for name in odata['PHU_NAME'].unique()]
region_options.insert(0,{"label":"All", "value":"All"})
orpop = pd.read_csv('data/ontario_region_population.csv')
orpop['Population'] = [int(s.replace(',','')) for s in orpop['Population']]
odata = odata.merge(right=orpop, how='left', left_on='PHU_NAME', right_on='new_region')
odata['Population'] = odata['Population'].fillna(odata['Population'].mean())



# ------------------------------------------------------------------------------
# ---------------------------Layout---------------------------------------------
# ------------------------------------------------------------------------------

app.layout = dbc.Container([
    
    # row1 This is the title
    dbc.Row(
        dbc.Col(html.H1("Ontario COVID-19 Spotlight",
                        style={'color': 'white',
                               'textAlign': 'center'}))
    ),

    # row2
    # Summary table
   dbc.Row([
       # table
       dbc.Col([
           html.H2('Summary', style={'color': 'white'}),
           dash_table.DataTable(id="vaccine_table",
                                columns=[{"name": i, "id": i}
                                         for i in table.columns],
                                data=table.to_dict('records'),
                                style_cell={'textAlign': 'left', 'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
                                style_header={'backgroundColor': 'rgb(30, 30, 30)', 'fontWeight': 'bold'}
                                )
       ]),
   ]),
    
    html.Br(),
    
    #row3
    dbc.Row([
        # daily status line chart
        dbc.Col([

            html.H2('Ontario Daily Status', style={'color': 'white'}),
            ## drop down
            dcc.Dropdown(id="line_option",
                         options=[
                             {"label": "Confirmed Cases", "value": "Confirmed Positive"},
                             {"label": "Resolved Cases", "value": "Resolved"},
                             {"label": "Deaths", "value": "Deaths"}],
                         multi=False,
                         value="Confirmed Positive",
                         style={'width': "60%"}
                         ),

            html.Br(),
            
            ## graph
            dcc.Graph(id='line_chart', figure={})
        ], width={'size':5},className='text-dark'), # end of column

        # The new feed
        dbc.Col([
            html.H2('News Feed', style={'color': 'white'}),

            dash_table.DataTable(
                    id='news_table',
                    columns=[{"name": i, "id": i} for i in news_df.columns],
                    data=news_df.to_dict('records'),
                    style_table={},
                    fixed_rows={'headers': True},
                    style_cell={
                        'maxWidth':'500px',
                        'textAlign': 'left',
                        'font-family':'sans-serif',
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    style_data={
                        'whiteSpace':'normal', 'height':'auto', 'font-size':'14px'
                    },
                    style_header={
                        'fontWeight': 'bold',
                        'font-size':'16px',
                        'backgroundColor': 'rgb(30, 30, 30)'
                    },
                ),

         ], width={'size':7},className='text-dark'), #end of column


    ],align='end'), # end of row

    html.Br(),

    # row4
    dbc.Row(
        html.Div([
        dcc.Link(
            id='news_link', 
            children=['Source: Global News Canada'], 
            href='https://globalnews.ca/news/6859636/ontario-coronavirus-timeline/',
            target='_blank',
            style={'color':'white'}
        )
    ], style={'font-size':'14px'}),
        justify="end"),

    # row5
    dbc.Row([
        # spread map
        dbc.Col([
            html.H2('Public Health Region Spread', style={'color': 'white'}),

            dcc.Tabs([
                dcc.Tab(label='Active Cases', children=[
                    dcc.Graph(
                        id='Active_map',
                        figure=active_map
                    )
                ]),
                dcc.Tab(label='Resolved', children=[
                    dcc.Graph(
                        id='Resolved_map',
                        figure=resolved_map
                    )
                ]),
                dcc.Tab(label='Deaths', children=[
                    dcc.Graph(
                        id='Deaths_map',
                        figure=deaths_map
                    )
                ]),
            ]),

        ], style={}, className='six columns text-dark')
    ]),

    html.Br(),

    # row6
    dbc.Row([
        dbc.Col([html.H2('Daily Cases Break down', style={'color': 'white'})])
    ]),
    
    # row7
    dbc.Row([

        dbc.Col([
            html.H3('Select Date Range', style={'padding-left':"40px"}),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=date(2020, 1, 1),
                end_date=date(2020, 12, 1),
                end_date_placeholder_text='Select a date!',
                style = {'width': "100%", "display":"inline-block", 'padding-left':"40px"}
            )
        ], className="three columns"),

        dbc.Col([
            html.H3('Select Region(s)', style={'padding-left':"40px"}),
            dcc.Dropdown(id="region_select",
                options=region_options,
                multi=True,
                value=[region_options[0]['value']],
                style={"width":"100%", "display":"inline-block", "padding-left":"40px"},
                className='text-dark'
            ),

        ], className="three columns"),

        dbc.Col([
            html.H3('Options', style={'padding-left':"40px"}),
            dcc.Checklist(
                id="per100k",
                options=[
                    {'label': 'Count per 100,000 people (not including daily resolved or fatal cases)', 'value': '100k'}
                ],
                value=[],
                style={'font-size':'12px', 'padding-left':"40px"}
            )
        ], className="three columns"),

    ], align="start"),
                         
    html.Br(),                     # Vertical: start, center, end

    # row8
    dbc.Row([
        dbc.Col([
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
        ], style={}, className='six columns text-dark'),

        dbc.Col([
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
    ]),

    html.Br(),

    # Row 9 - deaths by day
    dbc.Row([
        dbc.Col([
            html.Br(),
            # html.H3('Daily Recovered'),
            dcc.Graph(id='graph6', figure={})
        ], className="six columns"),

        dbc.Col([
            html.Br(),
            # html.H3('Fatalities'),
            dcc.Graph(id='graph5', figure={})
        ], className="six columns")
    ], align='end'),

    html.Br(),

    #row10
    dbc.Row([
        # Col1
        dbc.Col([
            html.H2('Positive Rate in Age Groups', style={'color': 'white'}),
            html.H3('Select Age Group(s)', style={'padding-left':"40px"}),
            dcc.Dropdown(id="age_group",
                options=my_options,
                multi=True,
                value=[my_options[0]['value']],
                style={"width":"60%", "display":"inline-block", "padding-left":"40px"},
                className='text-dark'
            ),
            html.Div(id='select_ref', children=[], style={"padding-left":"40px"}),
        ], className="three columns"),

    ], align='start'),

    html.Br(),

    # ROW11
    dbc.Row([

        dbc.Col([
            #html.H3('Daily Recovered'),
            dcc.Graph(id='graph_animate', figure={}),
        ], style={}, className="six columns")

    ], align='start'),

    html.Br(),

    # row12
    dbc.Row([
        dbc.Col([
            html.H2('Hospitalization', style={'color': 'white'}),
            html.H3('Select A Region', style={'padding-left':"40px"}),
            dcc.Dropdown(id="slct_impact",
                         options=[{"label": x, "value": x} for x in region],
                         value="TORONTO", multi=False,
                         style={"width": "50%", "padding-left":"40px"},
                         className='text-dark'
                         )
        ])
    ]),

    html.Br(),

    # row13
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='my_bee_map', figure={})
        ], width={'size': 12, 'order': 1},
        )
    ]),

    html.Br(),

    # row14
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Markdown('''
                             Language: Python, Dash, Plotly ||
                             Data Source: [Government of Ontario Data Catalogue](https://data.ontario.ca/dataset?keywords_en=COVID-19), 
                             [Ontario GeoHub](https://geohub.lio.gov.on.ca/datasets/ministry-of-health-public-health-unit-boundary) ||
                             All Codes are in [GitHub](https://github.com/scbrock/COVID-19-Data-Visualization) 
                             '''
                            )
            ], style={'textAlign': 'center'})
        ])
    ])


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

    return fig


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='line_chart', component_property='figure'),
    [Input(component_id='line_option', component_property='value')]
)
def update_graph2(line_option):

    fig = px.line(daily_status, x="Reported Date", y=line_option, template='plotly_dark')

    return fig


# Callback for the dropdown menu used for regional data and testing
@app.callback(
    [Output(component_id='select_ref', component_property='children'),
     Output(component_id='graph_animate', component_property='figure')],
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
    
    df = data_s[(data_s['age_category'].isin(option_slctd)) & (data_s['DATE'] >= sdt) & (data_s['DATE'] <= edt)] #.groupby('DATE').sum().reset_index()
    df = df.sort_values('DATE')
    #print(df.head())

    df['DATE'] = df['DATE'].astype(str)
    fig2 = px.bar(
            df,
            x='percent_positive_7d_avg',
            y='age_category',
            color='age_category',
            title='Percent Positive',
            animation_frame='DATE',
            animation_group='age_category',
            range_x=[0.0,0.10],
            labels = {
                'DATE': 'Date',
                'age_category': 'Age Category',
                'Percent_positive': 'Percent Positive',
                'percent_positive_7d_avg': "Percent Positive (7 Day Average)"
            },
            template='plotly_dark'
        )

    # fig2 = px.line(
    #     df, 
    #     x="DATE", 
    #     y="percent_positive_7d_avg", 
    #     animation_frame="DATE", 
    #     color = 'age_category',
    #     title="Percent Positive",
    #     labels = {
    #         'DATE': 'Date',
    #         'percent_positive_7d_avg': "Percent Positive (7 Day Average)"
    #     }
    #     # animation_group="country",
    #     # size="pop", 
    #     # color="continent", 
    #     # hover_name="country",
    #     # log_x=True,
    #     # size_max=55,
    #     # range_x=[100,100000],
    #     # range_y=[25,90]
    # )   

    # df2 = px.data.gapminder()
    # fig2 = px.scatter(df2, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
    #            size="pop", color="continent", hover_name="country",
    #            log_x=True, size_max=55, range_x=[100,100000], range_y=[25,90])
    
    #fig2 = {}

    return select_ref, fig2











# callback for regional counts
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
        df['ACTIVE_CASES'] = df["ACTIVE_CASES"]/df['Population']*100000
        df['RESOLVED_CASES'] = df["RESOLVED_CASES"]/df['Population']*100000
        df['DEATHS'] = df["DEATHS"]/df['Population']*100000
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
        },
        template='plotly_dark'
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
        },
        template='plotly_dark'
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
        },
        template='plotly_dark'
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
        },
        template='plotly_dark'
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
        },
        template='plotly_dark'
    )
    
    
    
    return fig1, fig2, fig3, fig4, fig5




@app.callback([Output(component_id='bar1', component_property='figure'),
              Output(component_id='bar2', component_property='figure'),
              Output(component_id='bar3', component_property='figure')],
             [Input('region_select', 'value'),
             Input('per100k', 'value')])

def build_bars(regions, is_100k):
    '''
    build 3 bar charts: active, resolved, deaths for region cases
    '''

    
    if 'All' in regions:
        regions = all_regions
    elif len(regions) == 0:
        return {}, {}, {}
    
    maxdate = odata['DATE'].max()
    
    df = odata[odata['PHU_NAME'].isin(regions) & (odata['DATE'] == str(maxdate))]
    
    fig1_title = "Active Cases as of "+maxdate
    fig1_yaxis = "Number of Active Cases"
    
    fig2_title = "Resolved Cases as of "+maxdate
    fig2_yaxis = "Cumulative Number of Resolved Cases"
        
    fig3_title = "Fatal Cases as of "+maxdate
    fig3_yaxis = "Cumulative Number of Fatal Cases"
    
    if len(is_100k) > 0:
        # list is not empty, so divide all counts by 100k
        df['ACTIVE_CASES'] = df["ACTIVE_CASES"]/df['Population']*100000
        df['RESOLVED_CASES'] = df["RESOLVED_CASES"]/df['Population']*100000
        df['DEATHS'] = df["DEATHS"]/df['Population']*100000
        fig1_title += ' Per 100,000'
        fig1_yaxis += ' Per 100,000'
        fig2_title += ' Per 100,000'
        fig2_yaxis += ' Per 100,000'
        fig3_title += ' Per 100,000'
        fig3_yaxis += ' Per 100,000'



    fig1 = px.bar(
        df, 
        x="PHU_NAME", 
        y="ACTIVE_CASES", 
        color = "PHU_NAME", 
        title=fig1_title,
        labels= {
            'ACTIVE_CASES': fig1_yaxis,
            "PHU_NAME": "Region"
        },
        template='plotly_dark'
    )
    
    fig2 = px.bar(
        df, 
        x="PHU_NAME", 
        y="RESOLVED_CASES", 
        color = "PHU_NAME", 
        title=fig2_title,
        labels= {
            'RESOLVED_CASES': fig2_yaxis,
            "PHU_NAME": "Region"
        },
        template='plotly_dark'
    )
    fig3 = px.bar(
        df, 
        x="PHU_NAME", 
        y="DEATHS", 
        color = "PHU_NAME", 
        title=fig3_title,
        labels= {
            'DEATHS': fig3_yaxis,
            "PHU_NAME": "Region"
        },
        template='plotly_dark'
    )
    
    return fig1, fig2, fig3
    



if __name__=='__main__':
    app.run_server(debug=True, port=8000)