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
    """
    clean region data

    inputs:
        data_input  - dataframe to be cleaned 
    
    returns:
        data        - cleaned input dataframe
    """
    data = data_input.copy()
    cols = ['FILE_DATE', 'PHU_NAME', 'ACTIVE_CASES',
       'RESOLVED_CASES', 'DEATHS']
    data = data[cols]
    
    # fix FILE_DATE
    data['FILE_DATE'] = [str(datetime.datetime.strptime(str(s), '%Y-%m-%d').date()) for s in data['FILE_DATE']]
    data = data.rename({'FILE_DATE': "DATE"}, axis='columns')

    # sort data
    data = data.sort_values(['PHU_NAME', 'DATE'])
    return data


def daily_rec_deaths(data):
    '''
    calculate daily deaths and recoveries from data

    inputs:
        data - dataframe of region deaths and recoveries

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
    return updated date from website url

    inputs:
        url - url of Global News website

    returns:
        res - the most recent date (Str)
    '''
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    res = soup.find_all('span', text=re.compile("^Updated"))[0].text

    return res


def get_news_table(url = 'https://globalnews.ca/news/6859636/ontario-coronavirus-timeline/'):
    '''
    Get the news data from URL

    inputs:
        url - url of Global News Canada

    returns:
        news - dataframe of news events in reverse chronological order
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


def get_population():
    '''
    return Ontario region population data retrieved from Wikipedia

    inputs:

    returns:
        res - dataframe containing Ontario region population
    '''
    url = 'https://en.m.wikipedia.org/wiki/List_of_census_divisions_of_Ontario'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    tables = soup.find_all('table')
    
    df_all = pd.DataFrame()
    
    fix_cols = {
        'Population(2016)[2]': 'Population',
        'Census division': 'Region'
    }
    
    for i in range(2,10,2):
        t = tables[i]  # 2, 4, 6, 8
        # for tr in t.find_all('tr'):
        #     print(tr.text)

        cells = np.array([[s for s in tr.text.split('\n') if s != ''] for tr in t.find_all('tr')]) #.reshape(-1,13)

        df = pd.DataFrame(cells)
        df.columns = df.iloc[0]
        df = df[1:]
        df_all = pd.concat([df_all, df], axis=0)
    #print(df_all.columns)
    
    res = df_all.sort_values('Census division').rename(fix_cols, axis=1)

    return res



def build_save_pop():
    """
    builds and saves an Ontario region population dataframe
    
    inputs:
        oname - output filename
    
    returns:
        None
    """
    
    # Mapping of region names
    region_mapping = {
        'Algoma District': 'ALGOMA DISTRICT',
        'Bruce County': 'GREY BRUCE',
        'City of Greater Sudbury[c]':'SUDBURY AND DISTRICT',
        'City of Hamilton[e]':'CITY OF HAMILTON',
        'City of Kawartha Lakes[f]': 'HALIBURTON, KAWARTHA, PINE RIDGE',
        'City of Ottawa[g]': 'CITY OF OTTAWA',
        'City of Toronto[h]':'TORONTO',
        'Cochrane District': 'PORCUPINE',
        'County of Brant[a]': 'BRANT COUNTY',
        'District Municipality of Muskoka':'',
        'Dufferin County':'WELLINGTON-DUFFERIN-GUELPH',
        'Elgin County':'',
        'Essex County': 'WINDSOR-ESSEX COUNTY',
        'Frontenac County': 'KINGSTON, FRONTENAC, LENNOX & ADDINGTON',
        'Grey County':'GREY BRUCE',
        'Haldimand-Norfolk[d][a]':'HALDIMAND-NORFOLK',
        'Haliburton County':'HALIBURTON, KAWARTHA, PINE RIDGE',
        'Hastings County':'HASTINGS & PRINCE EDWARD COUNTIES',
        'Huron County': 'HURON PERTH',
        'Kenora District':'',
        'Lambton County':'LAMBTON COUNTY',
        'Lanark County': 'LEEDS, GRENVILLE AND LANARK DISTRICT',
        'Lennox and Addington County': 'KINGSTON, FRONTENAC, LENNOX & ADDINGTON',
        'Manitoulin District':'',
        'Middlesex County': 'MIDDLESEX-LONDON',
        'Municipality of Chatham-Kent[b]': 'CHATHAM-KENT',
        'Nipissing District':'',
        'Northumberland County':'NORTH BAY PARRY SOUND DISTRICT',
        'Oxford County':'OXFORD ELGIN-ST.THOMAS',
        'Parry Sound District':'',
        'Perth County': 'HURON PERTH',
        'Peterborough County':'PETERBOROUGH COUNTY-CITY',
        'Prince Edward County':'HASTINGS & PRINCE EDWARD COUNTIES',
        'Rainy River District': 'NORTHWESTERN',
        'Regional Municipality of Durham':'DURHAM REGION',
        'Regional Municipality of Halton': 'HALTON REGION',
        'Regional Municipality of Niagara':'NIAGARA REGION',
        'Regional Municipality of Peel':'PEEL REGION',
        'Regional Municipality of Waterloo':'WATERLOO REGION',
        'Regional Municipality of York': 'YORK REGION',
        'Renfrew County':'RENFREW COUNTY AND DISTRICT',
        'Simcoe County':'SIMCOE MUSKOKA DISTRICT',
        'Sudbury District':'SUDBURY AND DISTRICT',
        'Thunder Bay District':'THUNDER BAY DISTRICT',
        'Timiskaming District':'TIMISKAMING',
        'United Counties of Leeds and Grenville': 'LEEDS, GRENVILLE AND LANARK DISTRICT',
        'United Counties of Prescott and Russell':'',
        'United Counties of Stormont, Dundas and Glengarry':'',
        'Wellington County':'WELLINGTON-DUFFERIN-GUELPH',
    }
    
    df = get_population()
    
    # apply mapping to population data, aggregate values based on new region name
    df['new_region'] = [region_mapping[r] for r in df.Region]
    
    popdata = df[['new_region','Population']].groupby('new_region').sum().reset_index().iloc[1:,:]
    
    # determine missing regions
    # set(onames).difference(set(popdata['new_region'].unique())) -> "EASTERN ONTARIO"
    
    popdata.to_csv('data/ontario_region_population.csv')
    
    return None

