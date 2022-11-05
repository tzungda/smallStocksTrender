import yfinance as yf
import pandas as pd

class StockEarnings:

    def __init__(self, choice, num):
        self.__choice = choice# = input("Write a stock symbol: ")
        self.__num = num
        
    def get_earnings_dates( self ):
        #self.__choice = input("Write a stock symbol: ")
        data = yf.Ticker( self.__choice )
        if data.earnings.empty:
            return pd.DataFrame()
        e = data.earnings_dates[:self.__num]
        return e
        #
        #print (e)

