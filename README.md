# smallStocksTrender
Display some statistical data if the given stocks

# Use
- install Python 3.6 or the newer version
- pip install the needed Python packages: yfinance and plotly
- run the smallStocksTrender.py in terminal or command prompt
- type stock symbols( eg. VOO,AAPL,GOOG,QQQ )
- or type SP500 or SPTSX(Canada) or TW50_100(Taiwan) and its following conditions for filtering the stocks
- type period( eg. 2y )
- the result will be displayed to the browser

# Note
- Function of getting earnings isn't reliable, and will try to fix it

# Example
1) Display the input stock symbols:
![alt text](https://github.com/tzungda/smallStocksTrender/blob/main/images/example02.png)

2) Filter TSX(Canada) stocks based on comparing the closed prices and 200/50-day averages within the given days(eg. 40 days)
![alt text](https://github.com/tzungda/smallStocksTrender/blob/main/images/example_tsx.png)

3) Able to display earnings
![alt text](https://github.com/tzungda/smallStocksTrender/blob/main/images/example_earnings.png)
![alt text](https://github.com/tzungda/smallStocksTrender/blob/main/images/example_earnings_02.png)

# Future Work
- clean and modularize the code
- create a proper ui

# References
- https://github.com/bhanuprathap2000/pythonprograms/blob/master/historical%20data.ipynb
- https://medium.datadriveninvestor.com/how-to-generate-a-graph-for-a-stock-price-with-python-yahoo-finance-and-plotly-7f3a36f5ce7e
- https://wire.insiderfinance.io/how-to-get-all-stocks-from-the-s-p500-in-python-fbe5f9cb2b61
