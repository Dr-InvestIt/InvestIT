from datetime import datetime
import backtrader as bt
import yfinance as yf


class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma = bt.ind.SMA(period=50)
        price = self.data
        crossover = bt.ind.CrossOver(price, sma)
        self.signal_add(bt.SIGNAL_LONG, crossover)


class MACDCross(bt.SignalStrategy):
    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data, period_me1=self.p.macd1, period_me2=self.p.macd2, period_signal=self.p.macdsig)

        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        self.sma = bt.indicators.SMA(self.data, period=self.p.smaperiod)
        self.smadir = self.sma - self.sma(-self.p.dirperiod)


cerebro = bt.Cerebro()
cerebro.addstrategy(MACDCross)

data = bt.feeds.PandasData(dataname=yf.download(
    'SPY', '2015-07-06', '2021-07-01', auto_adjust=True))

cerebro.adddata(data)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
start_portfolio_value = cerebro.broker.getvalue()

cerebro.broker.setcash(10000.00)
cerebro.addsizer(bt.sizers.AllInSizer, percents=95)

cerebro.run()
cerebro.plot()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
end_portfolio_value = cerebro.broker.getvalue()
print("PnL:", end_portfolio_value - start_portfolio_value)
