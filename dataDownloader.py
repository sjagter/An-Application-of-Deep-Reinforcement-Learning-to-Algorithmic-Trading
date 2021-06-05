# coding=utf-8

"""
Goal: Downloading financial data (related to stock markets) from diverse sources
      (Alpha Vantage, Yahoo Finance).
Authors: Thibaut Théate and Damien Ernst
Institution: University of Liège
"""

###############################################################################
################################### Imports ###################################
###############################################################################

import pandas as pd
import pandas_datareader as pdr
import requests
import os
from datetime import datetime
import time

from io import StringIO



###############################################################################
############################## Class AlphaVantage #############################
###############################################################################

class AlphaVantage:
    """
    GOAL: Downloading stock market data from the Alpha Vantage API. See the
          AlphaVantage documentation for more information.
    
    VARIABLES:  - link: Link to the Alpha Vantage website.
                - apikey: Key required to access the Alpha Vantage API.
                - datatype: 'csv' or 'json' data format.
                - outputsize: 'full' or 'compact' (only 100 time steps).
                - data: Pandas dataframe containing the stock market data.
                                
    METHODS:    - __init__: Object constructor initializing some variables.
                - getDailyData: Retrieve daily stock market data.
                - getIntradayData: Retrieve intraday stock market data.
                - processDataframe: Process the dataframe to homogenize the format.
    """

    def __init__(self):
        """
        GOAL: Object constructor initializing the class variables. 
        
        INPUTS: /      
        
        OUTPUTS: /
        """
        
        self.link = 'https://www.alphavantage.co/query'
        self.apikey = 'APIKEY'
        self.datatype = 'csv'
        self.outputsize = 'full'
        self.data = pd.DataFrame()
        
        
    def getDailyData(self, marketSymbol, startingDate, endingDate):
        """
        GOAL: Downloading daily stock market data from the Alpha Vantage API. 
        
        INPUTS:     - marketSymbol: Stock market symbol.
                    - startingDate: Beginning of the trading horizon.
                    - endingDate: Ending of the trading horizon.
          
        OUTPUTS:    - data: Pandas dataframe containing the stock market data.
        """
        
        # Send an HTTP request to the Alpha Vantage API
        payload = {'function': 'TIME_SERIES_DAILY_ADJUSTED', 'symbol': marketSymbol, 
                   'outputsize': self.outputsize, 'datatype': self.datatype, 
                   'apikey': self.apikey}
        response = requests.get(self.link, params=payload)
        
        # Process the CSV file retrieved
        csvText = StringIO(response.text)
        data = pd.read_csv(csvText, index_col='timestamp')
        
        # Process the dataframe to homogenize the output format
        self.data = self.processDataframe(data)
        if(startingDate != 0 and endingDate != 0):
            self.data = self.data.loc[startingDate:endingDate]

        return self.data
        
        
    def getIntradayData(self, marketSymbol, startingDate, endingDate, timePeriod=60):
        """
        GOAL: Downloading intraday stock market data from the Alpha Vantage API. 
        
        INPUTS:     - marketSymbol: Stock market symbol. 
                    - startingDate: Beginning of the trading horizon.
                    - endingDate: Ending of the trading horizon.
                    - timePeriod: Time step of the stock market data (in seconds).
          
        OUTPUTS:    - data: Pandas dataframe containing the stock market data.
        """
        
        # Round the timePeriod value to the closest accepted value
        possiblePeriods = [1, 5, 15, 30, 60]
        timePeriod = min(possiblePeriods, key=lambda x:abs(x-timePeriod))
        
        # Send a HTTP request to the AlphaVantage API
        payload = {'function': 'TIME_SERIES_INTRADAY', 'symbol': marketSymbol, 
                   'outputsize': self.outputsize, 'datatype': self.datatype, 
                   'apikey': self.apikey, 'interval': str(timePeriod)+'min'}
        response = requests.get(self.link, params=payload)
        
        # Process the CSV file retrieved
        csvText = StringIO(response.text)
        data = pd.read_csv(csvText, index_col='timestamp')
        
        # Process the dataframe to homogenize the output format
        self.data = self.processDataframe(data)
        if(startingDate != 0 and endingDate != 0):
            self.data = self.data.loc[startingDate:endingDate]

        return self.data
    
    
    def processDataframe(self, dataframe):
        """
        GOAL: Process a downloaded dataframe to homogenize the output format.
        
        INPUTS:     - dataframe: Pandas dataframe to be processed.
          
        OUTPUTS:    - dataframe: Processed Pandas dataframe.
        """
        
        # Reverse the order of the dataframe (chronological order)
        dataframe = dataframe[::-1]

        # Remove useless columns
        dataframe['close'] = dataframe['adjusted_close']
        del dataframe['adjusted_close']
        del dataframe['dividend_amount']
        del dataframe['split_coefficient']
        
        # Adapt the dataframe index and column names
        dataframe.index.names = ['Timestamp']
        dataframe = dataframe.rename(index=str, columns={"open": "Open",
                                                         "high": "High", 
                                                         "low": "Low",
                                                         "close": "Close",
                                                         "volume": "Volume"})
        # Adjust the format of the index values
        dataframe.index = dataframe.index.map(pd.Timestamp)

        return dataframe



###############################################################################
########################### Class YahooFinance ################################
###############################################################################

class YahooFinance:   
    """
    GOAL: Downloading stock market data from the Yahoo Finance API. See the
          pandas.datareader documentation for more information.
    
    VARIABLES:  - data: Pandas dataframe containing the stock market data.
                                
    METHODS:    - __init__: Object constructor initializing some variables.
                - getDailyData: Retrieve daily stock market data.
                - processDataframe: Process a dataframe to homogenize the
                                    output format.
    """
    

    def __init__(self):
        """
        GOAL: Object constructor initializing the class variables. 
        
        INPUTS: /      
        
        OUTPUTS: /
        """
        
        self.data = pd.DataFrame()

    
    def getDailyData(self, marketSymbol, startingDate, endingDate):
        """
        GOAL: Downloding daily stock market data from the Yahoo Finance API. 
        
        INPUTS:     - marketSymbol: Stock market symbol.
                    - startingDate: Beginning of the trading horizon.
                    - endingDate: Ending of the trading horizon.
          
        OUTPUTS:    - data: Pandas dataframe containing the stock market data.
        """
        
        data = pdr.data.DataReader(marketSymbol, 'yahoo', startingDate, endingDate)
        self.data = self.processDataframe(data)
        return self.data


    def processDataframe(self, dataframe):
        """
        GOAL: Process a downloaded dataframe to homogenize the output format.
        
        INPUTS:     - dataframe: Pandas dataframe to be processed.
          
        OUTPUTS:    - dataframe: Processed Pandas dataframe.
        """
        
        # Remove useless columns
        dataframe['Close'] = dataframe['Adj Close']
        del dataframe['Adj Close']
        
        # Adapt the dataframe index and column names
        dataframe.index.names = ['Timestamp']
        dataframe = dataframe[['Open', 'High', 'Low', 'Close', 'Volume']]

        return dataframe


    
###############################################################################
############################# Class CSVHandler ################################
###############################################################################
    
class CSVHandler:
    """
    GOAL: Converting "Pandas dataframe" <-> "CSV file" (bidirectional).
    
    VARIABLES: /
                                
    METHODS:    - dataframeToCSV: Saving a dataframe into a CSV file.
                - CSVToDataframe: Loading a CSV file into a dataframe.
    """
    
    
    def dataframeToCSV(self, name, dataframe):
        """
        GOAL: Saving a dataframe into a CSV file.
        
        INPUTS:     - name: Name of the CSV file.   
                    - dataframe: Pandas dataframe to be saved.
          
        OUTPUTS: /
        """
        
        path = name + '.csv'
        dataframe.to_csv(path)
        
        
    def CSVToDataframe(self, name):
        """
        GOAL: Loading a CSV file into a dataframe.
        
        INPUTS:     - name: Name of the CSV file.   
          
        OUTPUTS:    - dataframe: Pandas dataframe loaded.
        """
        
        path = name + '.csv'
        return pd.read_csv(path,
                           header=0,
                           index_col='Timestamp',
                           parse_dates=True)
    

###############################################################################
############################## Class AlphaVantage #############################
###############################################################################

class Binance:
    """
    GOAL: Downloading market data from the Binance API. See the
          Binance documentation for more information.
    
    VARIABLES:  - link: Link to the Binance website.
                - datatype: 'csv' or 'json' data format.
                - outputsize: 'full' or 'compact' (only 100 time steps).
                - data: Pandas dataframe containing the stock market data.
                                
    METHODS:    - __init__: Object constructor initializing some variables.
                - getDailyData: Retrieve daily stock market data.
                - getIntradayData: Retrieve intraday stock market data.
                - processDataframe: Process the dataframe to homogenize the format.
    """

    def __init__(self):
        """
        GOAL: Object constructor initializing the class variables. 
        
        INPUTS: /      
        
        OUTPUTS: /
        """
        
        self.link = "https://api.binance.com/api/v3/klines"
        self.datatype = 'csv'
        self.outputsize = 'full'
        self.data = pd.DataFrame()     

        self.klines_columns = [
            'Open time',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'Close time',
            'Quote asset volume',
            'Number of trades',
            'Taker buy base asset volume',
            'Taker buy quote asset volume',
            'Ignore'
        ]
        
        
    def getDailyData(self, marketSymbol, startingDate, endingDate):
        """
        GOAL: Downloading daily stock market data from the Alpha Vantage API. 
        
        INPUTS:     - marketSymbol: Stock market symbol.
                    - startingDate: Beginning of the trading horizon.
                    - endingDate: Ending of the trading horizon.
          
        OUTPUTS:    - data: Pandas dataframe containing the stock market data.
        """
        
        params = {
            "symbol": marketSymbol,
            "interval": "1d",
            "limit": 1000,
            "startTime": int(pd.to_datetime(startingDate).timestamp()*1000),
            "endTime": int(pd.to_datetime(endingDate).timestamp()*1000)
        }
        response = requests.get(
            self.link,
            params=params
        )
        df_klines = pd.DataFrame(response.json())
        df_klines.columns = self.klines_columns
        df_klines['Open time'] = pd.to_datetime(df_klines['Open time'], unit='ms')
        df_klines = df_klines.rename(columns={'Open time': 'Timestamp'})
        df_klines = df_klines.set_index('Timestamp')
        
        df_klines['Open'] = df_klines['Open'].astype(float)
        df_klines['High'] = df_klines['High'].astype(float)
        df_klines['Low'] = df_klines['Low'].astype(float)
        df_klines['Close'] = df_klines['Close'].astype(float)
        df_klines['Volume'] = df_klines['Volume'].astype(float)
        
        # Process the dataframe to homogenize the output format
        self.data = self.processDataframe(df_klines)
        if(startingDate != 0 and endingDate != 0):
            self.data = self.data.loc[startingDate:endingDate]

        return self.data
        
        
    def getIntradayData(self, marketSymbol, startingDate, endingDate, minutes=60):
        """
        GOAL: Downloading intraday stock market data from the Alpha Vantage API. 
        
        INPUTS:     - marketSymbol: Stock market symbol. 
                    - startingDate: Beginning of the trading horizon.
                    - endingDate: Ending of the trading horizon.
                    - timePeriod: Time step of the stock market data (in minutes).
          
        OUTPUTS:    - data: Pandas dataframe containing the stock market data.
        """

        print(marketSymbol)
        print(startingDate)
        print(endingDate)
        print(minutes)
        
        # Round the timePeriod value to the closest accepted value
        possiblePeriods = [5, 15, 30, 60]
        if minutes not in possiblePeriods:
            raise ValueError
        
        if minutes == 60:
            interval = '1h'
        else:
            interval = f'{minutes}m'

        dfs = []

        for date in pd.date_range(startingDate, endingDate):
            params = {
                "symbol": marketSymbol,
                "interval": interval,
                "startTime": int(date.timestamp()*1000),
                "endTime": int((date + pd.Timedelta('1d')).timestamp()*1000)-1,
                "limit": 1000
            }
            response = requests.get(
                self.link,
                params=params
            )
            df_klines = pd.DataFrame(response.json())
            df_klines.columns = self.klines_columns
            df_klines['Open time'] = pd.to_datetime(df_klines['Open time'], unit='ms')
            df_klines = df_klines.rename(columns={'Open time': 'Timestamp'})
            df_klines = df_klines.set_index('Timestamp')
            
            df_klines['Open'] = df_klines['Open'].astype(float)
            df_klines['High'] = df_klines['High'].astype(float)
            df_klines['Low'] = df_klines['Low'].astype(float)
            df_klines['Close'] = df_klines['Close'].astype(float)
            df_klines['Volume'] = df_klines['Volume'].astype(float)

            dfs.append(df_klines)
            
        # Process the dataframe to homogenize the output format
        self.data = self.processDataframe(pd.concat(dfs))
        if(startingDate != 0 and endingDate != 0):
            self.data = self.data.loc[startingDate:endingDate]

        return self.data
    
    
    def processDataframe(self, dataframe):
        """
        GOAL: Process a downloaded dataframe to homogenize the output format.
        
        INPUTS:     - dataframe: Pandas dataframe to be processed.
          
        OUTPUTS:    - dataframe: Processed Pandas dataframe.
        """
        
        # Reverse the order of the dataframe (chronological order)
        dataframe = dataframe.sort_index()

        # Remove useless columns
        dataframe = dataframe[['Open', 'High', 'Low', 'Close', 'Volume']]

        return dataframe