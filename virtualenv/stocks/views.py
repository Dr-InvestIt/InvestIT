# from stocks.forms import StockForm
from django.shortcuts import render
from .models import Stock
from .forms import StockForm
import matplotlib.pyplot as plt
import io
import urllib, base64

def stock_create_view(request):
    form = StockForm(request.POST or None)
    uri=''
    if form.is_valid():
        ticker1 = form.cleaned_data.get('ticker1')
        ticker2 = form.cleaned_data.get('ticker2')
        print(ticker1,ticker2)
        stock_list = [ticker1, ticker2]
        plot_stock_together(stock_list)

        # plt.show()
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        # form.save()
    form = StockForm()

    context = {
        'form' : form,
        'image': uri
    }

    return render(request,'stocks/stock_create.html',context)

def plot_stock_together(list_of_stocks):
    from yahoofinancials import YahooFinancials
    from datetime import date, timedelta
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 1, figsize=(7, 5))

    for stock_symbol in list_of_stocks:

        # set date range for historical prices
        end_time = date.today()
        start_time = end_time - timedelta(days=365)

        #format date range
        end = end_time.strftime('%Y-%m-%d')
        start = start_time.strftime('%Y-%m-%d')

        json_prices = YahooFinancials(stock_symbol).get_historical_price_data(start,end,'daily')
        # print(json_prices)

        #json -> dataframe
        prices = pd.DataFrame(json_prices[stock_symbol]['prices'])[['formatted_date','close']]
        prices.sort_index(ascending = False, inplace = True)

        #Calculate daily log return
        prices['returns'] = (np.log(prices.close / prices.close.shift(-1)))

        #calculate daily std of return
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
        ax.hist(data1, alpha=0.5, bins = 50, label = stock_symbol)

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
    ax.text(x, y , 'Annualized Volatility: ' + str(np.round(std*100, 1))+'%',
        fontsize=11, fontweight='bold')
    x = x_corr[0] + (x_corr[1] - x_corr[0]) / 15
    y -= (y_corr[1] - y_corr[0]) / 20
    
    # save histogram plot of historical price volatility
    fig.tight_layout()
    # fig.savefig('historical volatility.png')