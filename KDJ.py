from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class KDJStrategy(bt.Strategy):
    params = (
        ('period', 9),
        ('period_dfast', 3),
        ('period_dslow', 3),
    )

    def __init__(self):

        self.kd = bt.indicators.StochasticFull(
            self.data0, period=self.p.period, period_dfast=self.p.period_dfast, period_dslow=self.p.period_dslow)

        self.K = self.kd.percD
        self.D = self.kd.percDSlow
        self.J = self.K*3 - self.D*2

        self.crossover = bt.indicators.CrossOver(self.K, self.D, plot=True)
        # self.above

        self.highest = bt.indicators.Highest(period=self.p.period, plot=False)
        self.lowest = bt.indicators.Lowest(period=self.p.period, plot=False)

        self.buy_signal = (self.crossover == 1)
        self.sell_signal = (self.crossover == -1)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def next(self):

        global last_k_value
        last_k_value = float(self.K.get(-1)[0])

        global second_k_value
        second_k_value = float(self.K.get(-2)[0])

        global last_d_value
        last_d_value = float(self.D.get(-1)[0])

        global second_d_value
        second_d_value = float(self.D.get(-2)[0])

        global highest
        highest = float(self.highest.get(-1)[0])

        global lowest
        lowest = float(self.lowest.get(-1)[0])

        if self.order:
            return

        if not self.position:
            if self.buy_signal[0]:
                self.order = self.buy()

        else:
            if self.sell_signal[0]:
                self.order = self.sell()


cerebro = bt.Cerebro()
cerebro.addstrategy(KDJStrategy)

# Define your backtest
stock = 'AAPL'

fromdate = '2015-07-06'

todate = '2021-09-03'

data = bt.feeds.PandasData(dataname=yf.download(
    stock, fromdate, todate, auto_adjust=True))

cerebro.adddata(data)

cerebro.addsizer(bt.sizers.AllInSizer, percents=99)

# # Add TimeReturn Analyzers for self and the benchmark data
# cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='alltime_roi',
#                     timeframe=bt.TimeFrame.NoTimeFrame)

# cerebro.addanalyzer(bt.analyzers.TimeReturn, data=data, _name='benchmark',
#                     timeframe=bt.TimeFrame.NoTimeFrame)

# # Add TimeReturn Analyzers fot the annuyl returns
# cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)
# # Add a SharpeRatio
# cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Years,
#                     riskfreerate=0.01)

# # Add SQN to qualify the trades
# cerebro.addanalyzer(bt.analyzers.SQN)
# cerebro.addobserver(bt.observers.DrawDown)  # visualize the drawdown evol

cerebro.broker.setcash(10000.00)

# cerebro.addwriter(bt.WriterFile, csv=True, out='Test_KDJ.csv', rounding=1)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
start_portfolio_value = cerebro.broker.getvalue()

results = cerebro.run()
result = results[0]

print("Previou K Values", last_k_value, second_k_value)
print("Previou D Values", last_d_value, second_d_value)

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
end_portfolio_value = cerebro.broker.getvalue()
print("PnL:", end_portfolio_value - start_portfolio_value)

print()

print("Enter the newest price for", stock, ": ")
newest_price = float(input())

# RSV = (newest_price - highest) * (highest - lowest) * 100
# K_value = ((2/3) * last_k_value) + ((1/3) * RSV)
# D_value = ((2/3) * last_d_value) + ((1/3) * K_value)

K_value = (newest_price - lowest) / (highest - lowest) * 100
D_value = K_value + last_k_value + second_k_value
D_value = float(D_value) / 3
print(K_value, D_value)
# for alyzer in result.analyzers:
#     alyzer.print()

cerebro.plot()
