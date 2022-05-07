### Import Packages ###

import pandas as pd
import numpy as np
import datetime

#import web scraping package
from bs4 import BeautifulSoup
import requests


### Financials ###

def income_statement(ticker, type='balance-sheet'):
    
    """
    Webscrape financial data from Yahoo! Finance.

    Parameters
    ----------
    ticker : str
        Ticker of the company you want to consult.
    type : str
        Type of financial information you would like.
        -Options for type: financials, balance-sheet & cash-flow. Default is balance-sheet.

    Returns
    -------
    pandas DataFrame

    Caution
    --------
    Numbers are in thousands.
    """
    
    #scraping
    url_fin = "https://finance.yahoo.com/quote/" + ticker + "/" + type + "?p=" + ticker
    
    response = requests.get(url_fin, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.111 Safari/537.36",
    })
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    ls = []

    #find all HTML code that is div
    for i in soup.find_all('div'):
        ls.append(i.string)
        
        #fill up missing titles
        if i.string != i.get('title'):
            ls.append(i.get('title'))
                
    #filter out all the 'none'-values
    new_ls = list(filter(None,ls))
    
    #remove the first elements of new_ls until we find the starting point of the table
    new_ls = new_ls[new_ls.index('Expand All'):]
    
    #zip per 6 for inc-st & cash flow and per 5 for balance sheet
    if type == 'balance-sheet':
        zipped_ls = list(zip(*[iter(new_ls)]*5))
    else:
        zipped_ls = list(zip(*[iter(new_ls)]*6))
    
    #turn list into dataframe
    df = pd.DataFrame(zipped_ls)
    
    #cleaning up the dataframe
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    df.rename(columns = {'Expand All':'Breakdown'}, inplace = True)
    df.set_index('Breakdown', inplace=True, drop=True)
    df = df.T
    df.index.name = None #remove zero in index title
    df.sort_index(inplace=True)
    
    #convert values to int
    col = df.columns
    for col in df: 
        temp = df[col].to_string().replace(',','').split('\n')
        df[col]= [i[10:].strip() for i in temp]
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df
    
    
    
### Statistics ###    
    
def statistics(ticker):
    
    """
    Webscrape statistical information from Yahoo! Finance.

    Parameters
    ----------
    ticker : str
        Ticker of the company you want to consult.

    Returns
    -------
    pandas DataFrame with 2 columns
    """
    
    #scraping
    url_stat = "https://finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker
    response = requests.get(url_stat, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.111 Safari/537.36",
    })
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    li = []
    
    #focus on the tables
    stat_data = soup.find_all("table")
    
    for table in stat_data:
        #scrape all table rows into variable trs
        trs = table.find_all('tr')
        for tr in trs:
            # scrape all table data tags into variable tds
            tds = tr.find_all('td')
            li.append(tds[0].get_text()) #index 0 of tds will contain the measurement
            li.append(tds[1].get_text()) #index 1 of tds will contain the value
            
    zipped_li = list(zip(*[iter(li)]*2)) #group the variable and value togheter
    df = pd.DataFrame(zipped_li, columns=['parameter', 'value']) #turn it into a dataframe
    
    return df
    
    
    
    
    
    