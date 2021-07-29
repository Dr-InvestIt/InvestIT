# from stocks.forms import StockForm
from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from .models import *
from .forms import *
import matplotlib.pyplot as plt
import io
import urllib
import base64


def index_view(request):

    return render(request, 'stocks/index.html')


def stock_create_volatility_view(request):
    graph_form = GraphForm(request.POST or None)
    form = StockForm(request.POST or None)
    uri = ''
    if form.is_valid():
        stock_name = form.cleaned_data.get('stock_id')
        print(stock_name)
        stock_volatility(stock_name)
        # plt.show()
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        # form.save()
    graph_form = GraphForm()
    form = StockForm()

    context = {
        'graph_form': graph_form,
        'form': form,
        'image': uri
    }

    return render(request, 'stocks/stock_create.html', context)


def stock_create_efficient_frontier_view(request):
    graph_form = GraphForm(request.POST or None)
    form = StockForm(request.POST or None)
    uri = ''
    if form.is_valid():
        stock_name = form.cleaned_data.get('stock_id')
        print(stock_name)
        efficient_frontier(stock_name)
        # plt.show()
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        # form.save()
    graph_form = GraphForm()
    form = StockForm()

    context = {
        'graph_form': graph_form,
        'form': form,
        'image': uri
    }

    return render(request, 'stocks/frontier_create.html', context)


def stock_detail_view(request, stock_id, *args, **kwargs):
    uri = ""
    graph_form = GraphForm(request.POST or None)
    graph_form = GraphForm()

    context = {
        'form': graph_form,
        'image': uri
    }

    return render(request, 'stocks/stock_create.html', context)


def efficient_frontier(stocks):
    import yfinance as yf
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    from pandas_datareader import data as pdr
    from scipy.optimize import minimize
    from datetime import date, timedelta

    # %matplotlib inline

    # obtain today's date
    today = date.today()
    five_years_ago = today-timedelta(days=5*365)

    today = today.strftime("%Y-%m-%d")
    five_years_ago = five_years_ago.strftime("%Y-%m-%d")

    # obtain Adj Close data for selected stocks
    data = yf.download(stocks, start=five_years_ago, end=today)

    closing_price = data['Adj Close']

    # compute daily log return
    log_ret = np.log(closing_price/closing_price.shift(1))

    # create portfolios with random weights
    np.random.seed(41)
    num_ports = 5000
    all_weights = np.zeros((num_ports, len(closing_price.columns)))
    ret_arr = np.zeros(num_ports)
    vol_arr = np.zeros(num_ports)
    sharpe_arr = np.zeros(num_ports)

    for x in range(num_ports):
        # Weights
        weights = np.array(np.random.random(closing_price.columns.shape[0]))
        weights = weights/np.sum(weights)

        # Save weights
        all_weights[x, :] = weights

        # Expected return
        ret_arr[x] = np.sum((log_ret.mean() * weights * 252))

        # Expected volatility
        vol_arr[x] = np.sqrt(
            np.dot(weights.T, np.dot(log_ret.cov()*252, weights)))

        # Sharpe Ratio
        sharpe_arr[x] = ret_arr[x]/vol_arr[x]

    max_sr_ret = ret_arr[sharpe_arr.argmax()]
    max_sr_vol = vol_arr[sharpe_arr.argmax()]

    min_vol_ret = ret_arr[vol_arr.argmin()]

    # plot scatter point with highest sharpe is highlighted
    plt.figure(figsize=(12, 8))
    plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='YlGnBu')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.scatter(max_sr_vol, max_sr_ret, c='red', marker='*', s=300)  # red dot
    plt.scatter(vol_arr.min(), min_vol_ret, c='green',
                marker='*', s=300)  # green dot

    # plt.show()

    pass


def stock_volatility(list_of_stocks):
    from yahoofinancials import YahooFinancials
    from datetime import date, timedelta
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    stock_id = list_of_stocks.replace(" ", "")
    list_of_stocks = stock_id.split(",")
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    print(type(list_of_stocks))
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
        # print(prices)

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
