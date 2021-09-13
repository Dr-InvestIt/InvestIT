# from stocks.forms import StockForm
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.http import HttpResponse, Http404, JsonResponse
from .models import *
from .forms import *
import matplotlib.pyplot as plt
import io
import urllib
import base64
import csv, io
from django.contrib.auth.decorators import permission_required
efficiency_frontier_stocks = {}


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

    context = {'graph_form': graph_form, 'form': form, 'image': uri}

    return render(request, 'stocks/stock_create.html', context)


# Delete a stock
def delete_stock(request, stock_id):
    efficiency_frontier_stocks.pop(stock_id, None)
    return redirect('frontier')


# Calculate efficient frontier
# def calculate_frontier(request):
#     return red

# def add_stock(response):
#     if response.method == 'POST':
#         form = EfficientForm(response.POST)

#         if form.is_valid():
#             name = form.cleaned_data['stock_id']
#             value = form.cleaned_data['stock_value']
#             t = Stock(stock_id=name, stock_value=value)
#             t.save()

#         return HttpResponseRedirect('frontier')
#     else:
#         form = EfficientForm()
#     return render(response, 'stocks/add_stock.html', {'form': form})


def plot_efficient_frontier(request):
    form = EfficientForm(request.POST or None)

    plot_div = ''
    stock_name = []
    stock_value = []
    output_string = ''

    for item in efficiency_frontier_stocks:
        stock_name.append(item)
        stock_value.append(efficiency_frontier_stocks[item])
    print(stock_name)

    if len(stock_name) >= 2:
        plot_div = interactive_efficient_frontier(stock_name, stock_value)
    else:
        output_string = 'Sorry, you need at least two stocks to perform efficient frontier calculation'
    context = {
        'plot_div': plot_div,
        'form': form,
        'stocks': efficiency_frontier_stocks,
        'output_string': output_string,
    }
    return render(request, 'stocks/frontier_create.html', context)


def stock_create_efficient_frontier_view(request):
    # graph_form = GraphForm(request.POST or None)
    form = EfficientForm(request.POST or None)

    # stocks = Stock.objects.all()

    # uri = ''
    # plot_div = ''
    if form.is_valid():

        name = form.cleaned_data['stock_id']
        value = form.cleaned_data['stock_value']
        efficiency_frontier_stocks[name] = value

        # stock_name = []

        # for item in stocks:
        #     stock_name.append(item.stock_id)
        # print(stock_name)
        # if len(stock_name) >= 2:

        #     plot_div = interactive_efficient_frontier(stock_name)
        # save image as html div and output it on html

        # fig = plt.gcf()
        # buf = io.BytesIO()
        # fig.savefig(buf, format='png')
        # buf.seek(0)
        # string = base64.b64encode(buf.read())
        # uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    # graph_form = GraphForm()
    form = EfficientForm()

    context = {
        # 'graph_form': graph_form,
        'form': form,
        # 'image': uri,
        'stocks': efficiency_frontier_stocks,
        # 'plot_div': plot_div
    }

    return render(request, 'stocks/frontier_create.html', context)


def save_stock_entry_view(request):

    form = EfficientForm(request.POST or None)

    print(efficiency_frontier_stocks)
    for item in efficiency_frontier_stocks:
        name = item
        value = efficiency_frontier_stocks[item]
        t = Stock(stock_id=name, stock_value=value)
        t.save()

    context = {
        # 'graph_form': graph_form,
        'form': form,
        # 'image': uri,
        'stocks': efficiency_frontier_stocks,
        # 'plot_div': plot_div
    }

    return render(request, 'stocks/frontier_create.html', context)


def stock_detail_view(request, stock_id, *args, **kwargs):
    uri = ""
    graph_form = GraphForm(request.POST or None)
    graph_form = GraphForm()

    context = {'form': graph_form, 'image': uri}

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
    five_years_ago = today - timedelta(days=5 * 365)

    today = today.strftime("%Y-%m-%d")
    five_years_ago = five_years_ago.strftime("%Y-%m-%d")

    # obtain Adj Close data for selected stocks
    data = yf.download(stocks, start=five_years_ago, end=today)

    closing_price = data['Adj Close']

    # compute daily log return
    log_ret = np.log(closing_price / closing_price.shift(1))

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
        weights = weights / np.sum(weights)

        # Save weights
        all_weights[x, :] = weights

        # Expected return
        ret_arr[x] = np.sum((log_ret.mean() * weights * 252))

        # Expected volatility
        vol_arr[x] = np.sqrt(
            np.dot(weights.T, np.dot(log_ret.cov() * 252, weights)))

        # Sharpe Ratio
        sharpe_arr[x] = ret_arr[x] / vol_arr[x]

    max_sr_ret = ret_arr[sharpe_arr.argmax()]
    max_sr_vol = vol_arr[sharpe_arr.argmax()]

    min_vol_ret = ret_arr[vol_arr.argmin()]

    # plot scatter point with highest sharpe is highlighted
    plt.figure(figsize=(16, 8))
    plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='YlGnBu')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.scatter(max_sr_vol, max_sr_ret, c='red', marker='*', s=300)  # red dot
    plt.scatter(vol_arr.min(), min_vol_ret, c='green', marker='*',
                s=300)  # green dot

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
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    print(type(list_of_stocks))
    for stock_symbol in list_of_stocks:

        # set date range for historical prices
        end_time = date.today()
        start_time = end_time - timedelta(days=365)

        # format date range
        end = end_time.strftime('%Y-%m-%d')
        start = start_time.strftime('%Y-%m-%d')

        json_prices = YahooFinancials(stock_symbol).get_historical_price_data(
            start, end, 'daily')
        # print(json_prices)

        # json -> dataframe
        prices = pd.DataFrame(
            json_prices[stock_symbol]['prices'])[['formatted_date', 'close']]
        prices.sort_index(ascending=False, inplace=True)

        # Calculate daily log return
        prices['returns'] = (np.log(prices.close / prices.close.shift(-1)))

        # calculate daily std of return
        daily_std = np.std(prices.returns)
        prices['daily std'] = daily_std
        # annualized daily standard deviation
        std = daily_std * 252**0.5
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
    ax.set_title('Historical Volatility for ' + string_of_stocks)
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
    ax.text(x,
            y,
            'Annualized Volatility: ' + str(np.round(std * 100, 1)) + '%',
            fontsize=11,
            fontweight='bold')
    x = x_corr[0] + (x_corr[1] - x_corr[0]) / 15
    y -= (y_corr[1] - y_corr[0]) / 20

    # save histogram plot of historical price volatility
    fig.tight_layout()
    # fig.savefig('historical volatility.png')


def interactive_efficient_frontier(stocks, stock_value):
    import yfinance as yf
    import numpy as np
    from plotly.offline import plot
    from datetime import date, timedelta
    import plotly.graph_objects as go
    # obtain today's date
    today = date.today()
    five_years_ago = today - timedelta(days=5 * 365)

    today = today.strftime("%Y-%m-%d")
    five_years_ago = five_years_ago.strftime("%Y-%m-%d")

    # obtain Adj Close data for selected stocks
    data = yf.download(stocks, start=five_years_ago, end=today)

    # convert str to int for stock values
    stock_value = list(map(float, stock_value))
    port_weight = []
    port_total = sum(stock_value)
    for i in stock_value:
        port_weight.append(i / port_total)
    # print(stock_weight)
    port_weight = np.array(port_weight)
    closing_price = data['Adj Close']

    # compute daily log return
    log_ret = np.log(closing_price / closing_price.shift(1))

    # create portfolios with random weights
    np.random.seed(41)
    num_ports = 2500
    all_weights = np.zeros((num_ports, len(closing_price.columns)))
    ret_arr = np.zeros(num_ports)
    vol_arr = np.zeros(num_ports)
    sharpe_arr = np.zeros(num_ports)

    for x in range(num_ports):
        # Weights
        weights = np.array(np.random.random(closing_price.columns.shape[0]))
        weights = weights / np.sum(weights)

        # Save weights
        all_weights[x, :] = weights

        # Expected return
        ret_arr[x] = np.sum((log_ret.mean() * weights * 252))

        # Expected volatility
        vol_arr[x] = np.sqrt(
            np.dot(weights.T, np.dot(log_ret.cov() * 252, weights)))

        # Sharpe Ratio
        sharpe_arr[x] = ret_arr[x] / vol_arr[x]

    # calculate user's portfolio
    port_ret = np.sum(log_ret.mean() * port_weight * 252)
    port_vol = np.sqrt(
        np.dot(port_weight.T, np.dot(log_ret.cov() * 252, port_weight)))
    print(port_ret, port_vol)

    max_sr_ret = ret_arr[sharpe_arr.argmax()]
    max_sr_vol = vol_arr[sharpe_arr.argmax()]

    min_vol = vol_arr[vol_arr.argmin()]
    min_vol_ret = ret_arr[vol_arr.argmin()]

    # plot scatter point with highest sharpe is highlighted
    fig = go.Figure()

    fig.update_layout(autosize=False,
                      width=1200,
                      height=750,
                      margin=dict(pad=0),
                      yaxis=dict(title_text="Return"),
                      xaxis=dict(title_text="Volatility"))

    fig.add_trace(
        go.Scatter(name='Inefficient',
                   mode='markers',
                   x=vol_arr,
                   y=ret_arr,
                   marker=dict(color=sharpe_arr,
                               colorscale='Viridis',
                               size=10,
                               showscale=False),
                   showlegend=False))

    fig.add_trace(
        go.Scatter(
            name='Min Vol',
            mode='markers',
            x=[min_vol],
            y=[min_vol_ret],
            marker=dict(color='orange', size=20, symbol='star'),
            text=[f'Weights: {np.round(all_weights[vol_arr.argmin()],2)}'],
            hoverinfo='text',
            showlegend=True))

    fig.add_trace(
        go.Scatter(name='Your Portfolio',
                   mode='markers',
                   x=[port_vol],
                   y=[port_ret],
                   marker=dict(color='blue', size=20, symbol='star'),
                   text=[f'Weights: {np.round(port_weight,2)}'],
                   hoverinfo='text',
                   showlegend=True))

    fig.add_trace(
        go.Scatter(
            name='Highest Sharpe',
            mode='markers',
            x=[max_sr_vol],
            y=[max_sr_ret],
            marker=dict(color='red', size=20, symbol='star'),
            text=[f'Weights: {np.round(all_weights[sharpe_arr.argmax()],2)}'],
            hoverinfo='text',
            showlegend=True))
    plt_div = plot(fig, output_type='div')
    return plt_div
    # fig.show()


def item_detail_view(request):
    obj = Item.objects.get()
    context = {

    }
    return render(request, "stocks/frontier_create.html", context)

# @permission_required('admin.can.add_log_entry')
def stock_upload(request):
    template = 'stocks/frontier_create.html'
    prompt = {
        'order' : 'Order of the CSV should be Stock ticker and postion'
    }

    if request.method == 'GET':
        return render(request, template, prompt)
    
    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        message.error(request,'This is not a csv file')

    data_set = csv_file.file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    
    for column in csv.reader(io_string, delimiter = ','):
        print('Hi')
        t = Stock.objects.create(
            stock_id = column[0],
            stock_value = column[1]
        )
        efficiency_frontier_stocks[t.stock_id]=t.stock_value
    context = {'stocks': efficiency_frontier_stocks}
    return render(request, "stocks/frontier_create.html", context)
