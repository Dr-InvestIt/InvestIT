from datetime import datetime
import backtrader as bt
import yfinance as yf


class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma = bt.ind.SMA(period=50)
        price = self.data
        crossover = bt.ind.CrossOver(price, sma)
        self.signal_add(bt.SIGNAL_LONG, crossover)

# class SmaCross(bt.SignalStrategy):
#     def __init__(self):
#         sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
#         crossover = bt.ind.CrossOver(sma1, sma2)
#         self.signal_add(bt.SIGNAL_LONG, crossover)


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
thestrat = thestrats[0]

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
end_portfolio_value = cerebro.broker.getvalue()
print("PnL:", end_portfolio_value - start_portfolio_value)

print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())

cerebro.plot()
