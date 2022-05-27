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
        df[col]= [i[10:].strip() for i in temp] #remove the first 10 characters to get rid of the index
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
    
    
    
    
### Historical Data: stock price ###    
    
def hist_stock_price(ticker):
    
    """
    Webscrape historical stock price data from Yahoo! Finance.

    Parameters
    ----------
    ticker : str
        Ticker of the company you want to consult.

    Returns
    -------
    pandas DataFrame
    
    Warning
    -------
    When a dividend gets payed a row with all zeros will be in the dataset, to remove this row use the following code:
        df = df.drop(df[df.Open == 0].index).
    """
    
    #webscraping
    url_hist = "https://finance.yahoo.com/quote/" + ticker + "/history?p=" + ticker
    response = requests.get(url_hist, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.111 Safari/537.36",
    })
    soup = BeautifulSoup(response.text, 'html.parser')
    
    #focus on the table
    hist_data = soup.find_all("table")
    
    #initiate empty list
    ls=[]
    
    #scrape
    for table in hist_data:
        for i in soup.find_all('span'):
            ls.append(i.string)
            if i.string != i.get('title'):
                ls.append(i.get('title'))
                
    #filter out all the 'none'-values
    new_ls = list(filter(None,ls))
    
    #remove the first elements of new_ls until we find the starting point of the table
    new_ls = new_ls[new_ls.index('Date'):]
    
    #trim the end of the list that does not contain relevant data, use try/except to let the function run in case the string is not found or changes
    target_element = "*Close price adjusted for splits."
    try:
        target_index = new_ls.index(target_element) + 1
    except ValueError:
        target_index = None
    new_ls=new_ls[:target_index]
    
    
    #Fill the list up with 6 Dividend values to allow good use of the zip function later
    try: #use try/except to not crash the function when 'Dividend' is not in the list 
        if 'Dividend' in new_ls:
            i = new_ls.index("Dividend") #only retrieves first occurence
            new_ls.insert(i+1, "Dividend")
            new_ls.insert(i+1, "Dividend")
            new_ls.insert(i+1, "Dividend")
            new_ls.insert(i+1, "Dividend")
            new_ls.insert(i+1, "Dividend")
    except ValueError:
        pass
    
    #second time should it appear twice in the dataset
    try:
        if new_ls.index("Dividend", i+6) > i+6: #if a second occurence of 'Dividend' exists do the same
            j = new_ls.index("Dividend", i+6)
            new_ls.insert(j+1, "Dividend")
            new_ls.insert(j+1, "Dividend")
            new_ls.insert(j+1, "Dividend")
            new_ls.insert(j+1, "Dividend")
            new_ls.insert(j+1, "Dividend")
    except ValueError:
        pass
    
    
    #zip per 6 for inc-st & cash flow and per 5 for balance sheet
    zipped_ls = list(zip(*[iter(new_ls)]*7))
    
    #turn list into dataframe
    df = pd.DataFrame(zipped_ls)
    
    #format dataset
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    
    #make strings numeric
    for col in df[['Open', 'High', 'Low', 'Close*', 'Adj Close**']]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    #format Date
    df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y', dayfirst=True)
    
    #format Volume, make numeric
    temp = df['Volume'].to_string().replace(',','').split('\n')
    df['Volume']= [i[3:].strip() for i in temp] #remove the first 3 characters to get rid of the index (up to 999)
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0).astype(int)

    return df