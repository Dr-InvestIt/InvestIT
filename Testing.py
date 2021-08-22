from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class CombinedStrategy(bt.Strategy):

    params = (
        ('fast', 50),
        ('slow', 200),
    )

    def __init__(self):
        self.fast_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.fast, plotname='50 day moving average'
        )

        self.slow_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.slow, plotname="200 day moving average"
        )

        self.crossover = bt.indicators.CrossOver(
            self.fast_moving_average, self.slow_moving_average)

    def nest(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                self.order = self.buy()

        else:
            if self.crossover < 0:
                self.order = self.sell()


cerebro = bt.Cerebro()
cerebro.addstrategy(CombinedStrategy)

# Define your backtest
stock = 'AAPL'

fromdate = '2015-07-06'

todate = '2021-08-09'

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
