import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
import yfinance as yf

##################################################
input_symbols = input("Type stock symbols( eg. VOO,AAPL,GOOG,QQQ ): ")
input_symbols = input_symbols.upper()
print( f"symbols: {input_symbols} \n" )
#eg. QQQ,AMZN,AMGN,AAPL,VOO,HON
stock_symbols = input_symbols.replace(' ', '').split(',')


##################################################
market_period = input("Period( eg.2y ): ")


##################################################
stock_data = []
for stock_symbol in stock_symbols:
    stock = yf.Ticker( stock_symbol ) #yf.download( tickers=stock_symbol, period = market_period ) 
    data=stock.history(period=market_period)
    data["50MA"]=data[["Close"]].rolling(50).mean()
    data["200MA"]=data[["Close"]].rolling(200).mean()
    stock_data.append( data )


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
fig = make_subplots(rows = stock_length*2, cols=1, shared_xaxes=False, vertical_spacing=0.02, row_width=tuple( row_width_list ), subplot_titles=tuple( subplot_title_list )  )
for data in stock_data:
    sub_fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=0.02) 
    candlestick = go.Candlestick( x=data.index, open = data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name = f"{stock_symbols[ind]} market data" )
    ind = ind + 1
    bar = go.Bar(x=data.index, y=data['Volume'], showlegend=False, marker_color='rgba(0, 0, 255, 1)')
    #
    sub_fig.add_trace(candlestick, row= 1, col=1)
    sub_fig.add_trace( go.Scatter(x=data["50MA"].index, y=data["50MA"].values, mode='lines', name='50MA', marker_color='rgba(200, 200, 255, 1)'), row= 1, col=1)
    sub_fig.add_trace( go.Scatter(x=data["200MA"].index, y=data["200MA"].values, mode='lines', name='200MA', marker_color='rgba(255, 200, 200, 1)'), row= 1, col=1)
    sub_fig.add_trace(bar, row= 2, col=1)
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

