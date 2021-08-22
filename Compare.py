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


def runstrategy(strategy, stock):
    cerebro = bt.Cerebro()

    data = bt.feeds.PandasData(dataname=yf.download(
        stock, fromdate, todate, auto_adjust=True))

    cerebro.adddata(data)

    cerebro.addstrategy(strategy)

    cerebro.broker.setcash(10000.00)

    cerebro.addsizer(bt.sizers.AllInSizer, percents=95)

    # cerebro.broker.setcommission(commission=5.0, margin=2000.0, mult=1.0)

    strat_name = str(strategy.__name__)
    excel = strat_name + ".csv"
    cerebro.addwriter(bt.WriterFile, csv=True, out=excel, rounding=2)

    print(strat_name)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    start_portfolio_value = cerebro.broker.getvalue()

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    end_portfolio_value = cerebro.broker.getvalue()
    pnl = end_portfolio_value - start_portfolio_value
    print("PnL:", pnl)

    # cerebro.plot()

    strat_result = [strat_name, pnl]

    return strat_result


def testallstratonstock(stock):
    strategies_list = [KDJ_MACDStrategy, KDJStrategy, MacdCross, GoldenCross]

    best_result = ["Strats were all worse", 0]

    for strategy in strategies_list:
        result = runstrategy(strategy, stock)
        if result[1] > best_result[1]:
            best_result[0] = result[0]
            best_result[1] = result[1]

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

    print()
    print("Best strategy for", stock, "is",
          best_result[0], "with a PnL of", best_result[1])
    print()
    input("Press Enter to continue...")


fromdate = '2015-01-01'
todate = '2021-01-01'


def testmultiplestock():
    stocks = ['SPY', 'AAPL', "GOOD"]

    for stock in stocks:
        testallstratonstock(stock)


testmultiplestock()
