from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class RSIStrategy(bt.Strategy):
    lines = ('below30',)
    params = dict(
        period=10,  # to apply to RSI
    )

    plotlines = dict(below30=dict(ls='--'))

    def __init__(self):
        rsi = bt.ind.RSI(self.data, period=self.p.period)

        self.crossover = bt.indicators.CrossOver(rsi, bt.LineNum(30.0))

        self.below30 = bt.Cmp(rsi, bt.LineNum(30.0))

        self.buy_signal = (self.below30 == -1)
        self.sell_signal = (self.below30 == 1)

        self.order = None  # sentinel to avoid operrations on pending order

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def next(self):

        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            if self.buy_signal[0]:
                self.order = self.buy()

        else:  # in the market
            if self.sell_signal[0]:
                self.order = self.sell()


cerebro = bt.Cerebro()
cerebro.addstrategy(RSIStrategy)

# Define your backtest
stock = 'AAPL'

fromdate = '2015-07-06'

todate = '2021-09-02'

data = bt.feeds.PandasData(dataname=yf.download(
    stock, fromdate, todate, auto_adjust=True))

cerebro.adddata(data)

cerebro.addsizer(bt.sizers.AllInSizer, percents=99)

cerebro.broker.setcash(10000.00)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
start_portfolio_value = cerebro.broker.getvalue()

results = cerebro.run()
result = results[0]

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
end_portfolio_value = cerebro.broker.getvalue()
print("PnL:", end_portfolio_value - start_portfolio_value)

cerebro.plot()
