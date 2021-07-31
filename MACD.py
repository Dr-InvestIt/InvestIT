from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class MacdCross(bt.SignalStrategy):
    # lines = ('macd', 'signal', 'histo')
    params = (
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),   # ATR distance for stop price
        ('smaperiod', 30),  # SMA Period (pretty standard)
        ('dirperiod', 10),  # Lookback period to consider SMA trend direction
    )

    def __init__(self):
        # Main function to buy and sell
        # me1 = EMA(self.data, period=self.p.period_me1)
        # me2 = EMA(self.data, period=self.p.period_me2)
        # self.l.macd = me1 - me2
        # self.l.signal = EMA(
        #     self.l.macd, period=self.p.period_signal, plotname='signal')
        # self.l.histo = self.l.macd - self.l.signal
        self.macd = bt.ind.MACD(
            self.data,
            period_me1=self.p.macd1,
            period_me2=self.p.macd2,
            period_signal=self.p.macdsig)

        self.mcross = bt.ind.CrossOver(self.macd.macd, self.macd.signal)

        self.atr = bt.ind.ATR(self.data, period=self.p.atrperiod)

        self.sma = bt.ind.SMA(
            self.data, period=self.p.smaperiod, plotname='SMA')

        self.smadir = self.sma - self.sma(-self.p.dirperiod)

    def start(self):
        self.order = None  # to avoid operations on pending order

    def next(self):
        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            if self.mcross[0] > 0.0 and self.smadir < 0.0:
                self.order = self.buy()
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = self.data.close[0] - pdist

        else:  # in the market
            pclose = self.data.close[0]
            pstop = self.pstop

            if pclose < pstop:
                self.close()  # stop met - get out
            else:
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = max(pstop, pclose - pdist)

    def notify_order(self, order):
        if order.status == order.Completed:
            pass

        if not order.alive():
            self.order = None


# def runstrat(args=None):
#     cerebro = bt.Cerebro()
#     cerebro.broker.set_cash(10000.00)

#     stock = 'PLUG'

#     # set from date
#     fromdate = '2015-07-06'

#     # set to date
#     todate = '2020-01-01'

#     data = bt.feeds.PandasData(dataname=yf.download(
#         stock, fromdate, todate, auto_adjust=True))
#     cerebro.adddata(data)

#     cerebro.addstrategy(MacdCross)

#     # cerebro.addsizer(FixedPerc)


cerebro = bt.Cerebro()
cerebro.addstrategy(MacdCross)

stock = 'AAPL'

fromdate = '2015-07-06'

todate = '2020-01-01'

data = bt.feeds.PandasData(dataname=yf.download(
    stock, fromdate, todate, auto_adjust=True))

cerebro.adddata(data)


class FixedPerc(bt.Sizer):
    '''This sizer simply returns a fixed size for any operation

    Params:
      - ``perc`` (default: ``0.20``) Perc of cash to allocate for operation
    '''

    params = (
        ('perc', 0.20),  # perc of cash to use for operation
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        cashtouse = self.p.perc * cash
        if BTVERSION > (1, 7, 1, 93):
            size = comminfo.getsize(data.close[0], cashtouse)
        else:
            size = cashtouse // data.close[0]
        return size


cerebro.addsizer(FixedPerc, perc=0.9)

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
