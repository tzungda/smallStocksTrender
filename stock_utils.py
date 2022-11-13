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
        if self.__data.quarterly_earnings.empty:
            return pd.DataFrame()
        for i in range( 0, 5 ):
            e = self.__data.earnings_dates[:self.__num]
            if not e.empty:
                break
        #time.sleep(10)
        return e
        #
        #print (e)
