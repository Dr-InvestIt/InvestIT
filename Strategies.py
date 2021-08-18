from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import backtrader as bt
import yfinance as yf

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class KDJ_MACDStrategy(bt.Strategy):

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

        self.crossover = bt.indicators.CrossOver(self.K, self.D, plot=False)
        # self.above

        self.buy_signal = (self.crossover == 1)
        self.sell_signal = (self.crossover == -1)

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
            if self.buy_signal[0]:
                self.order = self.buy()

        else:
            if self.sell_signal[0]:
                self.order = self.sell()


class MacdCross(bt.Strategy):
    params = (
        # MACD Parameters
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
        self.macd = bt.ind.MACDHisto(
            self.data,
            period_me1=self.p.macd1,
            period_me2=self.p.macd2,
            period_signal=self.p.macdsig)

        self.mcross = bt.ind.CrossOver(self.macd.macd, self.macd.signal)

        self.atr = bt.ind.ATR(
            self.data, period=self.p.atrperiod, plotname='ATR')

        self.sma = bt.ind.SMA(
            self.data, period=self.p.smaperiod, plotname='SMA')

        self.smadir = self.sma - self.sma(-self.p.dirperiod)

    def start(self):
        self.order = None  # to avoid operations on pending order

    def next(self):
        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            if self.mcross[0] > 0.0 and self.smadir < 0.0:  # logic for deciding when to buy
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


# class GoldenCross(bt.Strategy):
