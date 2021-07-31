from datetime import datetime
import backtrader as bt
import yfinance as yf

class SmaCross(bt.SignalStrategy):
    def __init__(self):