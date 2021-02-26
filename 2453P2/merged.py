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
        dbc.Col(html.H1("COVID-19 Dashboard",
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
            html.H1('News Feed'),

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
                    style={'color':'black'}
                )
            ], style={'font-size':'14px'}),
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
    html.Br(),                     # Vertical: start, center, end
    # dbc.Row([
    #     dbc.Col([
    #         html.P("Dashboard for monitiorng covid19 in Ontario:",
    #                style={"textDecoration": "underline"}),
    #         dcc.Markdown('''
    #                 * Language: Python, Dash, Plotly
    #                 * Data Source:
    #                   * Ontario data Source:
    #                 * Github: https://github.com/scbrock/COVID-19-Data-Visualization
    #                 * Reference:
    #                 *
    #                 ''') ,
                                
    #     ], width={'size':4},
    #      ),
        
    #     dbc.Col([
    #       html.P("Dynamic Animation:"),
    #       html.Br(),
    #         dcc.Graph(id='animation', 
    #                   figure=fig2),
    #         ], width={'size':8},
    #     )
   
    # ], align="start"),

    #row 6
    dbc.Row([
        dbc.Col([
            html.H3('Select Age Group(s)', style={'padding-left':"40px"}),
            dcc.Dropdown(id="age_group",
                options=my_options,
                multi=True,
                value=[my_options[0]['value']],
                style={"width":"100%", "display":"inline-block", "padding-left":"40px"},
                className='text-dark'
            ),
            html.Div(id='select_ref', children=[], style={"padding-left":"40px"}),
        ], className="three columns"),

        dbc.Col([
            html.H3('Select Date Range'),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=date(2020, 1, 1),
                end_date=date(2020, 12, 1),
                end_date_placeholder_text='Select a date!',
                style = {'width': "100%", "display":"inline-block"}
            )
        ], className="three columns"),
        dbc.Col([
            html.H3('Select Region(s)', style={'padding-left':"0px"}),
            dcc.Dropdown(id="region_select",
                options=region_options,
                multi=True,
                value=[region_options[0]['value']],
                style={"width":"100%", "display":"inline-block", "padding-left":"40px"},
                className='text-dark'
            )
        ], className="three columns"),
        dbc.Col([
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
    ], align='start'),

    # ROW 7
    dbc.Row([
        dbc.Col([
            html.Br(),
            #html.H3('Daily Recovered'),
            dcc.Graph(id='graph_animate', figure={})
        ], style={}, className="six columns"),
        
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
        ], style={}, className='six columns text-dark')


    ], align='start'),

    # ROW 8 - testing and active
    dbc.Row([
        dbc.Col([
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
        ], className="six columns"),
        
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


    ], align='start'),

    # Row 9 - deaths by day
    dbc.Row([
        dbc.Col([
            html.Br(),
            #html.H3('Daily Recovered'),
            dcc.Graph(id='graph6', figure={})
        ], className="six columns"),

    
        dbc.Col([
            html.Br(),
            #html.H3('Fatalities'),
            dcc.Graph(id='graph5', figure={})
        ], className="six columns"),
    ], align='start'),

    # Row 10 - animation
    # dbc.Row([
    #     dbc.Col([
    #         html.Br(),
    #         #html.H3('Daily Recovered'),
    #         dcc.Graph(id='graph_animate', figure={})
    #     ], style={}, className="six columns"),
    #     dbc.Col([
    #         html.Br(),
    #         #html.H3('Daily Recovered'),
    #         dcc.Graph(id='graph_animate2', figure={})
    #     ], style={}, className="six columns"),
    # ], align='start')

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


# Callback for the dropdown menu used for regional data and testing
@app.callback(
    [Output(component_id='select_ref', component_property='children'),
     Output(component_id='graph1', component_property='figure'),
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

    if df.shape[0] == 0:
        fig = px.line()
        return select_ref, px.line(), {}
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
            },
            template='plotly_dark'
        )


    fig.update_xaxes(tickangle=90, nticks=20)
    #fig.update_layout(width=int(700))

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

    return select_ref, fig, fig2


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