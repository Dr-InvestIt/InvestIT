from datetime import datetime
import backtrader as bt
import yfinance as yf

fromdate = '2015-01-01'
todate = '2021-08-21'
stock = 'ALXN'

def function():
    try:
        data = bt.feeds.PandasData(dataname=yf.download(
            stock, fromdate, todate, auto_adjust=True))
    except:
        print("The data is not available")
        return
    


function()