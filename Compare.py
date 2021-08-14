from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf
from Strategies import *
import os
import glob
import pandas as pd

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))

stock = 'AAPL'
fromdate = '2015-07-06'
todate = '2021-08-09'


def runstrategy(strategy):
    cerebro = bt.Cerebro()

    data = bt.feeds.PandasData(dataname=yf.download(
        stock, fromdate, todate, auto_adjust=True))

    cerebro.adddata(data)

    cerebro.addstrategy(strategy)

    cerebro.broker.setcash(10000.00)

    cerebro.broker.setcommission(commission=5.0, margin=2000.0, mult=1.0)

    strat_name = str(strategy.__name__)
    excel = strat_name + ".csv"
    cerebro.addwriter(bt.WriterFile, csv=True, out=excel, rounding=2)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    start_portfolio_value = cerebro.broker.getvalue()

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    end_portfolio_value = cerebro.broker.getvalue()
    print("PnL:", end_portfolio_value - start_portfolio_value)


def testall():
    strategies_list = [KDJ_MACDStrategy, KDJStrategy, MacdCross]

    for strategy in strategies_list:
        runstrategy(strategy)

    path = './'
    all_files = glob.glob(os.path.join(path, "*.csv"))
    path = './Final/'
    excel_name = path + stock + " Results.xlsx"
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for file in all_files:
        df = pd.read_csv(file)
        df.to_excel(writer, sheet_name=os.path.splitext(
            os.path.basename(file))[0])

    writer.save()


testall()
