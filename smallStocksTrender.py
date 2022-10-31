import plotly.graph_objs #as go
from plotly.subplots import make_subplots
import bs4 as bs
import requests
import yfinance as yf
import datetime
import math

##################################################
input_symbols = input("Type stock symbols( eg. VOO,AAPL,GOOG,QQQ or SP500 for S&P500 stocks, and SPTSX for S&P/TSX(Canada): ")
input_symbols = input_symbols.upper()
input_symbols.replace(' ', '')
print( f"symbols: {input_symbols} \n" )
#eg. QQQ,AMZN,AMGN,AAPL,VOO,HON

##################################################
max_num = 25
start_sp500_index = 0
is_compare_200_average = 'Y'
is_compare_50_average = 'N'
compare_num_days = 40
if input_symbols == 'SP500' or input_symbols == 'SPTSX':
    tmp = input(f"Start index of {input_symbols}: ")
    start_sp500_index = int( tmp )
    #
    is_compare_200_average = input("Compare 200-day average(Y or N): ")
    is_compare_50_average = input("Compare 50-day average(Y or N): ")
    #
    tmp = input("Compare days: ")
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
temp_stock_symbols = []
sp_link = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
if (input_symbols == 'SPTSX'):
    sp_link = 'https://en.wikipedia.org/wiki/S%26P/TSX_Composite_Index'
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
        if ( input_symbols == 'SPTSX' ):
            ticker = ticker + '.TO'
        temp_stock_symbols.append(ticker)
        
    
else:
    temp_stock_symbols = input_symbols.split(',')
    end_ind = len( temp_stock_symbols )


##################################################
market_period = input("Period( eg.2y ): ")


##################################################
stock_data = []
stock_symbols = []
symbol_index = 1
temp_stock_symbol_index = 0
for stock_symbol in temp_stock_symbols:
    if (  temp_stock_symbol_index < start_sp500_index ):
        temp_stock_symbol_index = temp_stock_symbol_index + 1
        continue
    stock = yf.Ticker( stock_symbol ) #yf.download( tickers=stock_symbol, period = market_period ) 
    #
    print(f"Getting history of {stock_symbol} [{temp_stock_symbol_index + 1}/{len(temp_stock_symbols)}]")
    temp_stock_symbol_index = temp_stock_symbol_index + 1
    data = stock.history(period=market_period, interval='1d')
    data["50MA"]=data[["Close"]].rolling(50).mean()
    data["200MA"]=data[["Close"]].rolling(200).mean()
    
    if ( symbol_index > max_num ):
        break
    #
    if input_symbols == 'SP500' or input_symbols == 'SPTSX':
        close_sum = math.fsum( data['Close'][-compare_num_days:] )
        if ( close_sum < 0.01 ):
            continue
        #
        if ( is_compare_200_average == 'Y' ):
            m200_sum = math.fsum( data['200MA'][-compare_num_days:] )
            if( m200_sum > close_sum ):
                continue
        if ( is_compare_50_average == 'Y' ):
            m50_sum = math.fsum( data['50MA'][-compare_num_days:] )
            if( m50_sum > close_sum ):
                continue
        #
        print( "====> Matched the filter conditions" )
    #
    symbol_index = symbol_index + 1
    
    stock_data.append( data )
	#
    stock_symbols.append( stock_symbol )

if not stock_symbols:
    print( "No Stock data to process" )
    exit()

##################################################	
stock_length = len( stock_data )
row_width_list = []
subplot_title_list = []
for i in range( 0, stock_length ):
    row_width_list.append( 0.2 )
    row_width_list.append( 0.7 )
    #
    subplot_title_list.append( f"{stock_symbols[i]}:  {market_period}")
    subplot_title_list.append( f"{stock_symbols[i]} volume" )


##################################################
row_index = 1
ind = 0
vertical_spacing_value = 0.01#(float)(1/ (len(temp_stock_symbols) * 2 - 1 ))
print(f"--Spacing = {vertical_spacing_value}")

#
stock_data_len = len( stock_data )
fig = make_subplots(rows = stock_length*2, cols=1, shared_xaxes=False, vertical_spacing=vertical_spacing_value, row_width=tuple( row_width_list ), subplot_titles=tuple( subplot_title_list )  )
for i in range( 0, stock_data_len):
    data = stock_data[i]
    print( f"Processing figure of stock data {ind+1}/{stock_data_len}" )
    sub_fig = make_subplots(shared_xaxes=False, vertical_spacing=0.02) 
    candlestick = plotly.graph_objs.Candlestick( x=data.index, open = data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name = f"{stock_symbols[ind]} market data" )
    ind = ind + 1
    bar = plotly.graph_objs.Bar(x=data.index, y=data['Volume'], showlegend=False, marker_color='rgba(0, 0, 255, 1)')
    #
    sub_fig.add_trace(candlestick)
    sub_fig.add_trace( plotly.graph_objs.Scatter(x=data["50MA"].index, y=data["50MA"].values, mode='lines', name='50MA', marker_color='rgba(200, 200, 255, 1)') )
    sub_fig.add_trace( plotly.graph_objs.Scatter(x=data["200MA"].index, y=data["200MA"].values, mode='lines', name='200MA', marker_color='rgba(255, 200, 200, 1)') )
    sub_fig.add_trace(bar)
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
	

##################################################
print(f"Starting to draw")
fig.update_xaxes( rangeslider_visible=False )

fig = fig.update_layout(
    xaxis_rangeslider_visible=False, 
    #xaxis3={"anchor": "y3"},
    #xaxis2_rangeslider_visible=False,
    autosize=True,
	width=1600,
	height=540*stock_length
)

fig.show()

