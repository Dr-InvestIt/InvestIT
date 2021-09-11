from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class CCIStrategy(bt.Strategy):
    params = dict(
        period=20,  # to apply to CCI
    )

    def __init__(self):
        cci = bt.ind.CCI(self.data, period=self.p.period)

        # pperiod = self.p.pperiod or self.p.period

    # def notify_order(self, order):
    #     if order.status in [order.Submitted, order.Accepted]:
    #         return

    #     if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
    #         self.order = None

    # def next(self):

    #     if self.order:
    #         return

    #     if not self.position:
    #         if self.buy_signal[0]:
    #             self.order = self.buy()

    #     else:
    #         if self.sell_signal[0]:
    #             self.order = self.sell()


cerebro = bt.Cerebro()
cerebro.addstrategy(CCIStrategy)

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
