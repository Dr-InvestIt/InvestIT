from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class CombinedStrategy(bt.Strategy):

    params = (
        # KDJ
        ('kdj_period', 5),
        ('kdj_period_dfast', 3),
        ('kdj_period_dslow', 3),
        # MACD
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),   # ATR distance for stop price
        ('smaperiod', 30),  # SMA Period (pretty standard)
        ('dirperiod', 10),  # Lookback period to consider SMA trend direction
    )

    def __init__(self):
        # KDJ Plot
        self.kd = bt.indicators.StochasticFull(
            self.data0, period=self.p.kdj_period, period_dfast=self.p.kdj_period_dfast, period_dslow=self.p.kdj_period_dslow)

        self.K = self.kd.percD
        self.D = self.kd.percDSlow
        self.J = self.K*3 - self.D*2

        self.kcrossover = bt.indicators.CrossOver(
            self.K, self.D, plotname="K Cross D")

        # MACD Plot
        self.macd = bt.ind.MACDHisto(
            self.data,
            period_me1=self.p.macd1,
            period_me2=self.p.macd2,
            period_signal=self.p.macdsig)

        self.mcross = bt.ind.CrossOver(
            self.macd.macd, self.macd.signal, plotname="MACD Cross")

        self.signalcross = bt.ind.CrossOver(
            self.macd, bt.LineNum(0.0), plotname="Signal Cross 0")

        self.atr = bt.ind.ATR(
            self.data, period=self.p.atrperiod, plotname='ATR')

        self.sma = bt.ind.SMA(
            self.data, period=self.p.smaperiod, plotname='SMA', plot=False)

        self.smadir = self.sma - self.sma(-self.p.dirperiod)

    def start(self):
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.signalcross[0] == -1 and self.kd[0] <= 20:
                self.order = self.buy()

        else:
            if self.signalcross[0] == 1 and self.kd[0] >= 80:
                self.order = self.sell()


cerebro = bt.Cerebro()
cerebro.addstrategy(CombinedStrategy)

# Define your backtest
stock = 'AAPL'

fromdate = '2015-07-06'

todate = '2020-01-01'

data = bt.feeds.PandasData(dataname=yf.download(
    stock, fromdate, todate, auto_adjust=True))

cerebro.adddata(data)

cerebro.addsizer(bt.sizers.AllInSizer, percents=99)

# Add TimeReturn Analyzers for self and the benchmark data
cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='alltime_roi',
                    timeframe=bt.TimeFrame.NoTimeFrame)

cerebro.addanalyzer(bt.analyzers.TimeReturn, data=data, _name='benchmark',
                    timeframe=bt.TimeFrame.NoTimeFrame)

# Add TimeReturn Analyzers fot the annuyl returns
cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)
# Add a SharpeRatio
cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Years,
                    riskfreerate=0.01)

# Add SQN to qualify the trades
cerebro.addanalyzer(bt.analyzers.SQN)
cerebro.addobserver(bt.observers.DrawDown)  # visualize the drawdown evol

cerebro.broker.setcash(10000.00)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
start_portfolio_value = cerebro.broker.getvalue()

results = cerebro.run()
result = results[0]

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
end_portfolio_value = cerebro.broker.getvalue()
print("PnL:", end_portfolio_value - start_portfolio_value)

for alyzer in result.analyzers:
    alyzer.print()

cerebro.plot()
