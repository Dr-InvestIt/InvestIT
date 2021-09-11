from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class MBuyKSellStrategy(bt.Strategy):
    params = (
        # MACD Params
        ('me1period', 12),
        ('me2period', 26),
        ('macdsig', 9),
    )

    # def log(self, txt, dt=None, doprint=False):
    #     if doprint:
    #         dt = dt or self.datas[0].datetime.date(0)
    #         print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # MACD Lines
        me1 = bt.indicators.EMA(self.data, period=self.p.me1period)
        me2 = bt.indicators.EMA(self.data, period=self.p.me2period)

        self.macd = me1 - me2

        self.signal = bt.indicators.EMA(
            self.macd, period=self.p.macdsig, plotname='signal')

        bt.indicators.MACDHisto(self.data)

        # KDJ Lines
        self.high_nine = bt.indicators.Highest(
            self.data.high, period=9, plot=False)

        self.low_nine = bt.indicators.Lowest(
            self.data.low, period=9, plot=False)

        self.rsv = 100 * bt.DivByZero(
            self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None
        )

        self.K = bt.indicators.EMA(self.rsv, period=3, plot=False)

        self.D = bt.indicators.EMA(self.K, period=3, plot=False)

        self.J = 3 * self.K - 2 * self.D

        # self.buy_signal = (self.below30 == -1)
        # self.sell_signal = (self.below30 == 1)

        self.order = None  # sentinel to avoid operrations on pending order

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def next(self):
        # self.log('Close, %.2f' % self.data[0])
        # print()

        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            condition1 = self.macd[-1] - self.signal[-1]
            condition2 = self.macd[0] - self.signal[0]
            if condition1 < 0 and condition2 > 0:
                # self.log('BUY CREATE, %.2f' % self.data[0])
                # print()
                self.order = self.buy()

        else:  # in the market
            condition1 = self.J[-1] - self.D[-1]
            condition2 = self.J[0] - self.D[0]
            if condition1 > 0 or condition2 < 0:
                # self.log('SELL CREATED, %.2f' % self.data[0])
                # print()
                self.order = self.sell()


cerebro = bt.Cerebro()
cerebro.addstrategy(MBuyKSellStrategy)

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
