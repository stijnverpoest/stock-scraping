### Import Packages ###

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from io import StringIO
from dateutil.relativedelta import relativedelta

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
    
def hist_stock_price(ticker, startyear, startmonth, startday):
    
    """
    Webscrape historical stock price data from Yahoo! Finance.

    Parameters
    ----------
    ticker : str
        Ticker of the company you want to consult.
        
    startyear: int
    startmonth: int
    startday: int
        Starting date of the data you want to consult.

    Returns
    -------
    pandas DataFrame
    """

    #current timestamp
    curr_dt = datetime.now()
    curr_timestamp = int(round(curr_dt.timestamp()))
    
    #timestamp requested date
    dtime = datetime(startyear, startmonth, startday) #until which date [YYYY, M, D]
    dtimestamp = int(round(dtime.timestamp()))
    
    #url
    url = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&includeAdjustedClose=true'.format(ticker, dtimestamp, curr_timestamp)
    
    #get data
    response = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.111 Safari/537.36",
    })
    
    df = pd.read_csv(StringIO(response.text), parse_dates=['Date']) #StringIO module is an in-memory file-like object
    df.columns = df.columns.str.replace(' ', '_') #replace spaces in column names with underscore
    
    return df


def plot_sp(ticker, startyear, startmonth, startday):
    
    """
    Plot the historical stock price of a company from a specified time period.
    The maximum and minimum stock price of the selected time frame are indicated in red and green.

    Parameters
    ----------
    ticker : str
        Ticker of the company you want to consult.
        
    startyear: int
    startmonth: int
    startday: int
        Starting date of the data you want to consult.

    Returns
    -------
    Plot
    """
    
    dataset = hist_stock_price(ticker, startyear, startmonth, startday)
    
    maxi = dataset['Close'].max()
    maxi_dt = dataset.loc[dataset['Close'] == dataset['Close'].max(), 'Date']
    
    mini = dataset['Close'].min()
    mini_dt = dataset.loc[dataset['Close'] == dataset['Close'].min(), 'Date']
    
    #create plot
    plt.plot('Date', 'Close', color = 'navy', data = dataset)
    plt.plot('Date', 'Close', ',', color = 'black', data = dataset)
    plt.plot(maxi_dt, maxi, 'x', color='mediumseagreen')
    plt.plot(mini_dt, mini, 'h', color='firebrick')
    plt.title(str(ticker) + " Stock price")
    plt.xticks(rotation='90')
    plt.show()
    

    
    
### Various functions ###
    
def to_weekday(timestamp, type='forth'):
    
    """
    Transform the current date to a weekdate, if it is a weekend date.

    Parameters
    ----------
    timestamp : timestamp
        Date you want to transform.
        
    type: str
        Forth: Goes to the first monday. This is the default.
        Back: Goes to the last friday.

    Returns
    -------
    Timestamp
    """
    
    if type == 'back':
        if timestamp.weekday() == 5: #saturday
            timestamp = timestamp - relativedelta(days=+1)
        elif timestamp.weekday() == 6: #sunday
            timestamp = timestamp - relativedelta(days=+2)
        else:
            pass
    elif type == 'forth':
        if timestamp.weekday() == 5: #saturday
            timestamp = timestamp + relativedelta(days=+2)
        elif timestamp.weekday() == 6: #sunday
            timestamp = timestamp + relativedelta(days=+1)
        else:
            pass
    return timestamp




def relative_diff(dataset, months_back):
    
    """
    Calculate the relative percentile difference compared to prevous months.

    Parameters
    ----------
    dataset : pandas.DataFrame
        Dataset from where you would like to calculate the relative difference.
        
    months_back: int
        How many months you would like to go back to calculate the relative difference.

    Returns
    -------
    String
    """
    
    try:
        today = pd.to_datetime('today').floor('D')
        
        recent_day = to_weekday(today - relativedelta(days=+1), 'back')
        
        m3 = today - relativedelta(months=+months_back)
        m3 = to_weekday(m3)
        
        m2 = m3 + relativedelta(days=+1)
        m2 = to_weekday(m2, 'forth')
        
        m1 = m3 - relativedelta(days=+1)
        m1 = to_weekday(m1, 'back')
        
        old = dataset.loc[(dataset['Date'] > m1) & (dataset['Date'] < m2), 'Close'].iloc[0] #add iloc to make it a value instead of a Series
        new = dataset.loc[dataset['Date'] > recent_day - relativedelta(days=+1), 'Close'].iloc[0] #add iloc to make it a value instead of a Series
        
        diff = ((new - old) / old)*100
        diff2 = round(diff, 2)
        
        return print('Relative difference 3 months: ' + str(diff2)+'%' + ' [compared to ' + str(m3.date()) + ']')
    
    except IndexError:
        print("Error: No data available for that period, try a lower number.")