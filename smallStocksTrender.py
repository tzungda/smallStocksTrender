import plotly.graph_objs #as go
from plotly.subplots import make_subplots
import bs4 as bs
import requests
import yfinance as yf
import datetime
import math
from threading import Thread
import pandas as pd
#
import stock_utils
import importlib 
importlib.reload( stock_utils )
#import importlib 
#importlib.reload( yf )
#pip install yfinance --upgrade --no-cache-dir

##################################################
input_symbols = input("Type stock symbols( eg. VOO,AAPL,GOOG,QQQ ), or SP500 for S&P500 stocks, or SPTSX for S&P/TSX(Canada), or TW50_100 for Taiwan stocks(testing) : \n")
input_symbols = input_symbols.upper()
input_symbols.replace(' ', '')
print( f"symbols: {input_symbols} \n" )
#eg. QQQ,AMZN,AMGN,AAPL,VOO,HON

##################################################
max_num = 20
start_sp500_index = 0
is_compare_200_average = 'Y'
is_compare_50_average = 'N'
compare_num_days = 40
if input_symbols == 'SP500' or input_symbols == 'SPTSX' or input_symbols == 'TW50_100':
    tmp = input(f"Start index of {input_symbols}: ")
    start_sp500_index = int( tmp )
    #
    is_compare_200_average = input("Compare 200-day average(Y or N): ")
    is_compare_50_average = input("Compare 50-day average(Y or N): ")
    #
    tmp = input("Compare days( eg. 40 ): ")
    compare_num_days = int( tmp )
    #
    print(f"-->Maximum of filtered stocks is {max_num}")
    
    if ( is_compare_200_average != 'Y' and  is_compare_50_average != 'Y' ):
        print(f"-->Both 200-day and 50-day are not Y, set to compare the 200-day")
        is_compare_200_average = 'Y'
    
    if ( is_compare_200_average == 'Y' ):
        print( f"-->Compare the 200-day average" )
    if ( is_compare_50_average == 'Y' ):
        print( f"-->Compare the 50-day average" )

##################################################
def get_taiwan_symbols( tw_link ):
    resp = requests.get( tw_link )
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find_all('table', {'class': 'TableBorder'} )[0]
    stock_symbols_tw = []
    for row in table.findAll('tr')[1:]:
        for td_row in row.findAll('td'):
            ticker = td_row.text.encode('utf-8')
            if ( len(ticker) >= 4 ):
                t = ticker[0:4]
                if ( t.isdigit() ):
                    stock_symbols_tw.append( t.decode("utf-8") + '.TW' )
    return stock_symbols_tw
                    
##################################################
temp_stock_symbols = []
sp_link = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
if (input_symbols == 'SPTSX'):
    sp_link = 'https://en.wikipedia.org/wiki/S%26P/TSX_Composite_Index'
if (input_symbols == 'TW50_100' ):
    sp_link = 'http://moneydj.emega.com.tw/js/T50_100.htm'
#
if input_symbols == 'SP500' or input_symbols == 'SPTSX':
    
    resp = requests.get( sp_link )
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = None
    if ( input_symbols == 'SP500' ):
        table = soup.find('table', {'class': 'wikitable sortable'})
    if ( input_symbols == 'SPTSX' ):
        table = soup.find_all('table', {'class': 'wikitable sortable'})[1]
        
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker.replace('\n', '' )
        ticker = ticker.replace('.', '-' )
        if ( input_symbols == 'SPTSX' ):
            if ( ticker.find('.') == -1 ):
                ticker = ticker + '.TO'
        temp_stock_symbols.append(ticker)    
elif (input_symbols == 'TW50_100'):
    print(f"Getting Taiwanese stocks")
    temp_stock_symbols = get_taiwan_symbols( sp_link )
else:
    temp_stock_symbols = input_symbols.split(',')


##################################################
market_period = input("Days of Period( eg.260 ): ")
market_period_200 = str( int( market_period ) + 200 ) + 'd'
market_period = market_period + 'd'

##################################################
stock_data = []
stock_data_200 = []
stocks = []
stock_symbols = []
symbol_index = 1
temp_stock_symbol_index = 0
compare_num_days_half = int(compare_num_days/2)
matched_index = 0
for stock_symbol in temp_stock_symbols:
    if (  temp_stock_symbol_index < start_sp500_index ):
        temp_stock_symbol_index = temp_stock_symbol_index + 1
        continue
    stock = yf.Ticker( stock_symbol ) #yf.download( tickers=stock_symbol, period = market_period ) 
    #
    print(f"Getting history of {stock_symbol} [{temp_stock_symbol_index + 1}/{len(temp_stock_symbols)}]")
    temp_stock_symbol_index = temp_stock_symbol_index + 1
    data = stock.history(period=market_period, interval='1d')
    data_200 = stock.history(period=market_period_200, interval='1d')
    data_200["50MA"]=data_200[["Close"]].rolling(50).mean()
    data_200["200MA"]=data_200[["Close"]].rolling(200).mean()
    
    if ( symbol_index > max_num ):
        break
    #
    if input_symbols == 'SP500' or input_symbols == 'SPTSX' or input_symbols == 'TW50_100':
        close_sum = math.fsum( list( data['Close'].values[-compare_num_days:] ) )
        if ( close_sum < 0.01 ):
            continue
            
        # for the new high
        if ( ( len( data['Close'].values ) > 10 ) and ( data['Close'].values[-60:].mean() < data['Close'].values[:60].max() ) ):
            continue
        
        close_sum_second = math.fsum( list( data['Close'].values[-compare_num_days_half:] ) )
        #
        close_sum_first = math.fsum( list(data['Close'].values[-compare_num_days:-compare_num_days_half]) )
        #print(f" ***** close_sum_first = {close_sum_first}" )
        #print(f" ***** close_sum_second = {close_sum_second}" )
        if (close_sum_second < close_sum_first ):
            continue
        #
        if ( is_compare_200_average == 'Y' ):
            m200_sum = math.fsum( list( data_200['200MA'].values[-compare_num_days:] ) )
            if( m200_sum > close_sum ):
                continue
        if ( is_compare_50_average == 'Y' ):
            m50_sum = math.fsum( list( data_200['50MA'].values[-compare_num_days:] ) )
            if( m50_sum > close_sum ):
                continue
        #
        print( f"====> Matched the filter conditions ( {matched_index} )" )
        matched_index = matched_index + 1
    #
    symbol_index = symbol_index + 1
    
    stock_data_200.append( data_200 )
    stock_data.append( data )
    stocks.append( stock )
	#
    stock_symbols.append( stock_symbol )

if not stock_symbols:
    print( "No Stock data to process" )
    exit()

##################################################	
num_traces = 3
stock_length = len( stock_data )
row_width_list = []
row_height_list = []
subplot_title_list = []
for i in range( 0, stock_length ):
    #row_width_list.append( 0.2 )
    #row_width_list.append( 0.4 )
    #row_width_list.append( 0.3 )
    #
    row_height_list.append( 0.6 )
    row_height_list.append( 0.2 )
    row_height_list.append( 0.2 )
    #
    subplot_title_list.append( f"********************{stock_symbols[i]}:  {market_period}********************")
    subplot_title_list.append( f"{stock_symbols[i]} volume" )
    subplot_title_list.append( f"{stock_symbols[i]} EPS" )


##################################################
row_index = 1
ind = 0
vertical_spacing_value = 0.0095#(float)(1/ (len(temp_stock_symbols) * num_traces - 1 )) #0.009
print(f"--Spacing = {vertical_spacing_value}")
print(f"--Started to get earnings")
#########################
no_earnings_history = False
#
earnings_history_list = [pd.DataFrame() for s in stocks]
def get_earnings_history( stock_ticker, result, index):
    if no_earnings_history: 
        return
    se = stock_utils.StockEarnings(stock_ticker, 16)
    try:
        result[index] = se.get_earnings_dates()
    except Exception as e: 
        print('Failed get earnings: '+ str(e) + ': ' + stock_ticker)
    
#
threads = []
for ii in range(len(stocks)):
    # We start one thread per url present.
    process = Thread(target=get_earnings_history, args=[stock_symbols[ii], earnings_history_list, ii])
    process.start()
    threads.append(process)
#
for process in threads:
    process.join()
#########################

stock_data_len = len( stock_data )
fig = make_subplots(rows = stock_length*num_traces, cols=1, shared_xaxes=False, vertical_spacing=vertical_spacing_value, row_heights=row_height_list, subplot_titles=tuple( subplot_title_list )   )
for i in range( 0, stock_data_len):
    data = stock_data[i]
    data_200 = stock_data_200[i]
    print( f"Processing figure of stock data {i+1}/{stock_data_len}" )
    sub_fig = make_subplots(shared_xaxes=False, vertical_spacing=vertical_spacing_value) 
    candlestick = plotly.graph_objs.Candlestick( x=data.index, open = data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name = f"{stock_symbols[i]} market data" )
    #ind = ind + 1
    bar = plotly.graph_objs.Bar(x=data.index, y=data['Volume'], showlegend=False, marker_color='rgba(0, 0, 255, 1)')
    #
    sub_fig.add_trace(candlestick)
    #data_50_index = data_200["50MA"].index[200:]
    #data_200_index = data_200["200MA"].index[200:]
    data_50_values = data_200["50MA"].values[200:]
    data_200_values = data_200["200MA"].values[200:]
    sub_fig.add_trace( plotly.graph_objs.Scatter(x=data.index, y=data_50_values, mode='lines', name='50MA', marker_color='rgba(200, 200, 255, 1)') )
    sub_fig.add_trace( plotly.graph_objs.Scatter(x=data.index, y=data_200_values, mode='lines', name='200MA', marker_color='rgba(255, 200, 200, 1)') )
    sub_fig.add_trace(bar)
    
    # EPS
    e = earnings_history_list[i]
    if not e.empty:
        e = e.iloc[::-1]
        e_estimate = e['EPS Estimate']
        e_reported = e['Reported EPS']
        sub_fig.add_trace( plotly.graph_objs.Scatter(x=e.index, y=e_estimate.values, mode='lines', name='EPS Estimate', marker_color='rgba(190, 190, 190, 1)') )
        sub_fig.add_trace( plotly.graph_objs.Scatter(x=e.index, y=e_reported.values, mode='lines', name='Reported EPS', marker_color='rgba(50, 50, 50, 1)') )
    else:
        sub_fig.add_trace( plotly.graph_objs.Scatter(x=None, y=None, mode='lines', name='EPS Estimate', marker_color='rgba(200, 200, 0, 1)') )
        sub_fig.add_trace( plotly.graph_objs.Scatter(x=None, y=None, mode='lines', name='Reported EPS', marker_color='rgba(0, 0, 200, 1)') )
    #stock = stocks[i]
    #e_date = None
    #e_estimate = None
    #e_reported = None
    #if no_earnings_history or stock.earnings.empty:
    #    sub_fig.add_trace( plotly.graph_objs.Scatter(x=None, y=None, mode='lines', name='EPS Estimate', marker_color='rgba(100, 100, 100, 1)') )
    #    sub_fig.add_trace( plotly.graph_objs.Scatter(x=None, y=None, mode='lines', name='Reported EPS', marker_color='rgba(255, 255, 0, 1)') )
    #else:
    #    e = stock.earnings_dates[:10]
    #    e = e.iloc[::-1]
        #e_date = e['Earnings Date']
    #    e_estimate = e['EPS Estimate']
    #    e_reported = e['Reported EPS']
    #    sub_fig.add_trace( plotly.graph_objs.Scatter(x=e.index, y=e_estimate.values, mode='lines', name='EPS Estimate', marker_color='rgba(200, 200, 0, 1)') )
    #    sub_fig.add_trace( plotly.graph_objs.Scatter(x=e.index, y=e_reported.values, mode='lines', name='Reported EPS', marker_color='rgba(0, 0, 200, 1)') )
        
    
    #
    sub_fig.update_layout( xaxis_rangeslider_visible=False) 
    sub_fig.update_xaxes( rangeslider_visible=False )
	#
    fig.update_yaxes(title_text='Stock Price (USD)', row=row_index, col=1)
    fig = fig.add_trace(sub_fig.data[0], row=row_index, col=1)
    fig = fig.add_trace(sub_fig.data[1], row=row_index, col=1)
    fig = fig.add_trace(sub_fig.data[2], row=row_index, col=1)
    row_index = row_index + 1
    fig = fig.add_trace(sub_fig.data[3], row=row_index, col=1)
    row_index = row_index + 1
    fig = fig.add_trace(sub_fig.data[4], row=row_index, col=1)
    fig = fig.add_trace(sub_fig.data[5], row=row_index, col=1)
    row_index = row_index + 1
    #

	

##################################################
print(f"Starting to draw")
fig.update_xaxes( rangeslider_visible=False )

fig = fig.update_layout(
    xaxis_rangeslider_visible=False, 
    #xaxis3={"anchor": "y3"},
    #xaxis2_rangeslider_visible=False,
    autosize=True,
	width=1600,
    paper_bgcolor='rgba(180,180,180,1)',
	height=540*stock_length
)

fig.show()
