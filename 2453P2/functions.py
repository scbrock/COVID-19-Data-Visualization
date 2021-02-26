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
import datetime


def clean_region(data_input):
    data = data_input.copy()
    cols = ['FILE_DATE', 'PHU_NAME', 'ACTIVE_CASES',
       'RESOLVED_CASES', 'DEATHS']
    data = data[cols]
    
    # fix FILE_DATE
    #print('type of file date', data['FILE_DATE'][0])
    data['FILE_DATE'] = [str(datetime.datetime.strptime(str(s), '%Y-%m-%d').date()) for s in data['FILE_DATE']]
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