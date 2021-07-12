from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import NameForm

from yahoofinancials import YahooFinancials
from datetime import date, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import urllib, base64

# Create your views here.
def say_hello(request):
    return render(request, 'hello.html')

def action_page(request):
    return render(request, 'action_page.html')

def get_stock(request):
    if request.method == "POST":
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/action_page/")
        else:
            form = NameForm()
        
        return render(request, 'name.html', {'form':form})

def stock(request):
    string = ""
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    form = NameForm(request.POST or None)
    if form.is_valid():
        stockname = form.cleaned_data['stockname']
        stockname = stockname.replace(" ", "")
        stocknames = stockname.split(",")
        print(stocknames)
        plot_stock_together(stocknames)
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    form = NameForm()
    context = {
        'form' : form, 
        'image' : uri
    }
    return render(request, "form.html", context)

def plot_stock_together(list_of_stocks):
    
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

        data1 = prices.returns.values

        # plt.hist(data1, bins = 100, alpha = 0.5)

        # n, bins, patches = ax.hist(
        # data1,
        # bins=50, alpha=0.65, label = data_name, color = current_color)
        ax.hist(data1, alpha=0.5, bins = 50, label = stock_symbol)

        print("Calculated ", stock_symbol)

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
    fig.savefig('historical volatility.png')

    return fig