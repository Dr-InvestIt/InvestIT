from django.db import models

# Create your models here.


class Stock(models.Model):
    stock_id = models.CharField(max_length=1000)

    def get_stock_id():
        return stock_id

    def enter_stock(stock_name):
        stock_id = stock_name

    def stock_volatility(stock_name):
        from yahoofinancials import YahooFinancials
        from datetime import date, timedelta
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1, figsize=(7, 5))

        # stock_id = str(Stock.stock_id)
        # stock_id.replace(" ", "")
        stock_id = stock_name.replace(" ", "")
        list_of_stocks = stock_id.split(",")
        print(list_of_stocks)
        for stock_symbol in list_of_stocks:

            # set date range for historical prices
            end_time = date.today()
            start_time = end_time - timedelta(days=365)

            # format date range
            end = end_time.strftime('%Y-%m-%d')
            start = start_time.strftime('%Y-%m-%d')

            json_prices = YahooFinancials(
                stock_symbol).get_historical_price_data(start, end, 'daily')
            # print(json_prices)

            # json -> dataframe
            prices = pd.DataFrame(json_prices[stock_symbol]['prices'])[
                ['formatted_date', 'close']]
            prices.sort_index(ascending=False, inplace=True)

            # Calculate daily log return
            prices['returns'] = (np.log(prices.close / prices.close.shift(-1)))

            # calculate daily std of return
            daily_std = np.std(prices.returns)
            prices['daily std'] = daily_std
            # annualized daily standard deviation
            std = daily_std * 252 ** 0.5
            print(prices)

            data1 = prices.returns.values

            # plt.hist(data1, bins = 100, alpha = 0.5)

            # n, bins, patches = ax.hist(
            # data1,
            # bins=50, alpha=0.65, label = data_name, color = current_color)
            ax.hist(data1, alpha=0.5, bins=50, label=stock_symbol)

        ax.set_xlabel('log return of stock price')
        ax.set_ylabel('frequency of log return')
        string_of_stocks = str1 = ', '.join(list_of_stocks)
        ax.set_title('Historical Volatility for ' +
                     string_of_stocks)
        ax.legend(loc="upper right")

        # get x and y coordinate limits
        x_corr = ax.get_xlim()
        y_corr = ax.get_ylim()

        # make room for text
        header = y_corr[1] / 5
        y_corr = (y_corr[0], y_corr[1] + header)
        ax.set_ylim(y_corr[0], y_corr[1])

        # print historical volatility on plot
        x = x_corr[0] + (x_corr[1] - x_corr[0]) / 30
        y = y_corr[1] - (y_corr[1] - y_corr[0]) / 15
        ax.text(x, y, 'Annualized Volatility: ' + str(np.round(std*100, 1))+'%',
                fontsize=11, fontweight='bold')
        x = x_corr[0] + (x_corr[1] - x_corr[0]) / 15
        y -= (y_corr[1] - y_corr[0]) / 20

        # save histogram plot of historical price volatility
        fig.tight_layout()
        # fig.savefig('historical volatility.png')
