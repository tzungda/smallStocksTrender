import yfinance as yf
import pandas as pd
import time

class StockEarnings:

    def __init__(self, choice, num):
        self.__choice = choice# = input("Write a stock symbol: ")
        self.__num = num
        self.__data = None
        
    def get_earnings_dates( self ):
        #self.__choice = input("Write a stock symbol: ")
        self.__data = yf.Ticker( self.__choice )
        if self.__data.earnings.empty:
            return pd.DataFrame()
        e = self.__data.earnings_dates[:self.__num]
        time.sleep(8)
        return e
        #
        #print (e)

