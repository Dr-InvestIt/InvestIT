from datetime import datetime
import backtrader as bt
import yfinance as yf


class SmaCross(bt.SignalStrategy):
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

    def start(self):
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None

    def next(self):

        global last_value
        last_value = self.fast_moving_average.get(-1)[0]

        if self.order:
            return

        if not self.position:
            if self.crossover == 1:
                self.order = self.buy()

        else:
            if self.crossover == -1:
                self.order = self.sell()


cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

data = bt.feeds.PandasData(dataname=yf.download(
    'PLUG', '2015-07-06', '2020-01-01', auto_adjust=True))

cerebro.adddata(data)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
start_portfolio_value = cerebro.broker.getvalue()

cerebro.broker.setcash(10000.00)
cerebro.addsizer(bt.sizers.AllInSizer, percents=95)

cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

thestrats = cerebro.run()
print(last_value)
thestrat = thestrats[0]

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
end_portfolio_value = cerebro.broker.getvalue()
print("PnL:", end_portfolio_value - start_portfolio_value)

print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())

cerebro.plot()
