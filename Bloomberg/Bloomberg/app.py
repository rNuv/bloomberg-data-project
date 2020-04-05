from flask import Flask, request, redirect, url_for
from flask import render_template
from pandas_datareader import data
from bokeh.plotting import figure
from bokeh.embed import components
from newsapi import NewsApiClient
from bokeh.io import output_file, show
from bokeh.palettes import RdBu as colors
from bokeh.transform import transform
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, ColumnDataSource, PrintfTickFormatter
from math import pi
import pandas as pd
import requests
import bs4 as bs
import json
import quandl

app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker']
        return redirect(url_for('dashboard', ticker = ticker)) 
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    plots = []
    ticker = request.args.get("ticker")
    plots.append(make_plot(ticker))
    plots.append(makeCandlestick(ticker))
    companyName = getCompany(ticker)
    resp = requests.get('https://finance.yahoo.com/quote/' + ticker)
    soup = bs.BeautifulSoup(resp.text)
    table = soup.find('table', {'class': 'W(100%)'})
    table_headers = []
    table_data = []
    for row in table.findAll('tr'):
        header = row.findAll('td')[0].text
        table_headers.append(header)
        data = row.findAll('td')[1].text
        table_data.append(data)
    newsapi = NewsApiClient(api_key='dbcd03fd30e643138a73d04b39384eaa')
    headline_data = newsapi.get_everything(q = companyName)
    headlines = []
    image_urls = []
    descriptions = []
    linkToArticle = []
    articles = headline_data['articles']
    for obj in articles:
        title = obj['title']
        image_url = obj['urlToImage']
        description = obj['description']
        link = obj['url']
        if(image_url != None):
            headlines.append(title)
            image_urls.append(image_url)
            descriptions.append(description)
            linkToArticle.append(link)
        
    return render_template('dashboard.html', plots=plots, 
        companyName = companyName, table_headers = table_headers, 
        table_data = table_data, headlines = headlines, 
        image_urls = image_urls, descriptions = descriptions, linkToArticle = linkToArticle)

@app.route('/notebook')
def notebook():
    getIndexData()
    return render_template('Time Series Analysis.html')

@app.route('/sp')
def sp():
    plots = []
    tickers = save_sp500_tickers()
    main_df = get_sp500_data(tickers)
    hm = correlate(main_df)
    plots.append(hm)
    return render_template('sp.html', plots = plots)

@app.route('/cvi')
def cvi():
    plots = []
    df = getIndexData()
    plots.append(make_plot_cvi(df))
    return render_template('cvi.html', plots = plots)

def make_plot_cvi(df):
    p = figure(plot_width=800, plot_height=600, 
        x_axis_label = 'Year', y_axis_label = 'Closing Prices', 
        title = 'SSE', x_axis_type="datetime")
    df['100ma'] = df['Adj Close'].rolling(window=100, min_periods=0).mean()
    p.line(x='Date', y='Adj Close', line_width=2, source = df, line_color="#ffffff")
    p.line(x='Date', y='100ma', line_width=2, source = df, line_color="#f5a623")
    p.title.text_font = "Raleway"
    p.title.text_color = "#6e84a3"
    p.title.align = "center"
    p.title.text_font_size = "15pt"
    p.xaxis.major_label_text_color = "#6e84a3"
    p.yaxis.major_label_text_color = "#6e84a3"
    p.xaxis.axis_label_text_color = "#6e84a3"
    p.yaxis.axis_label_text_color = "#6e84a3"
    p.background_fill_color = "#142e4d"
    p.border_fill_color = "#142e4d"
    p.toolbar.autohide = True
    script, div = components(p)
    return script, div

def make_plot(symbol):
    companyName = getCompany(symbol)
    p = figure(plot_width=1200, plot_height=400, 
        x_axis_label = 'Year', y_axis_label = 'Closing Prices', 
        title = companyName, x_axis_type="datetime")
    #company = quandl.get("WIKI/" + symbol, start_date="2003-01-01", end_date="2020-01-01")
    company = data.DataReader(symbol, 'yahoo', '2003-01-01', '2020-01-19')
    company.reset_index(inplace=True)
    company['100ma'] = company['Adj Close'].rolling(window=100, min_periods=0).mean()
    p.line(x='Date', y='Adj Close', line_width=2, source = company, line_color="#ffffff")
    p.line(x='Date', y='100ma', line_width=2, source = company, line_color="#f5a623")
    p.title.text_font = "Raleway"
    p.title.text_color = "#6e84a3"
    p.title.align = "center"
    p.title.text_font_size = "15pt"
    p.xaxis.major_label_text_color = "#6e84a3"
    p.yaxis.major_label_text_color = "#6e84a3"
    p.xaxis.axis_label_text_color = "#6e84a3"
    p.yaxis.axis_label_text_color = "#6e84a3"
    p.background_fill_color = "#142e4d"
    p.border_fill_color = "#142e4d"
    p.toolbar.autohide = True
    script, div = components(p)
    return script, div

def makeCandlestick(symbol):
    df = data.DataReader(symbol, 'yahoo', '2020-01-01', '2020-01-25')
    df.reset_index(inplace=True)
    df.Date = pd.to_datetime(df.Date)

    inc = df.Close > df.Open
    dec = df.Open > df.Close
    w = 12*60*60*1000

    p = figure(x_axis_type="datetime", plot_width=600, plot_height=500,
        title = "Candlestick")
    p.xaxis.major_label_orientation = pi/4
    p.grid.grid_line_alpha=0.3

    p.segment(df.Date, df.High, df.Date, df.Low, color="black")
    p.vbar(df.Date[inc], w, df.Open[inc], df.Close[inc], fill_color="#60c546", line_color="black")
    p.vbar(df.Date[dec], w, df.Open[dec], df.Close[dec], fill_color="#e40e15", line_color="black")

    p.title.text_font = "Raleway"
    p.title.text_color = "#6e84a3"
    p.title.align = "center"
    p.title.text_font_size = "15pt"
    p.xaxis.major_label_text_color = "#6e84a3"
    p.yaxis.major_label_text_color = "#6e84a3"
    p.xaxis.axis_label_text_color = "#6e84a3"
    p.yaxis.axis_label_text_color = "#6e84a3"
    p.background_fill_color = "#142e4d"
    p.border_fill_color = "#142e4d"

    script, div = components(p)
    return script, div

def getCompany(ticker):
    response = requests.get('http://d.yimg.com/autoc.finance.yahoo.com/autoc?query=' + ticker + '&region=1&lang=en')
    data = response.json()
    return (data['ResultSet']['Result'][0]['name'])

def getIndexData():
    response = requests.get('https://finance.yahoo.com/quote/000001.SS/history?p=000001.SS')
    soup = bs.BeautifulSoup(response.text)
    table = soup.find('table', {'class': 'W(100%) M(0)'})
    table_headers = []
    table_data = []
    for tr in table.findAll('tr'):
        td = tr.findAll('td')
        row = [tr.text for tr in td]
        table_data.append(row)

    df = pd.DataFrame(table_data, columns=["A", "B", "C", 'D', "E", "F", "G"])
    df.drop(df.index[0], inplace=True)
    return df

def save_sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text)
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []

    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.replace('.','-')
        ticker = ticker[:-1]
        tickers.append(ticker)
    return tickers

def get_sp500_data(tickers):
    main_df = pd.DataFrame()
    for ticker in tickers[:20]:
        try:
            df = data.DataReader(ticker, "yahoo", '2016-01-01', '2020-01-19')

            df.rename(columns={'Adj Close' : ticker}, inplace=True)
            df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')
        except Exception as e:
            print('Aw')
            print(e)
    
    return main_df

def correlate(df):

    paletteMap = list(reversed(colors[9]))

    df = df.corr()

    df.index.name = 'AllColumns1'
    df.columns.name = 'AllColumns2'
    df = df.stack().rename("value").reset_index()
    

    mapper = LinearColorMapper(
        palette=paletteMap, low=df.value.min(), high=df.value.max())

    TOOLS = "box_select,lasso_select,pan,wheel_zoom,box_zoom,reset,help"
    p = figure(
        tools=TOOLS,
        plot_width=800,    
        plot_height=600,
        title="Correlation plot",
        x_range=list(df.AllColumns1.drop_duplicates()),
        y_range=list(df.AllColumns2.drop_duplicates()),
        toolbar_location="right",
        x_axis_location="below")

    p.rect(
        x="AllColumns1",
        y="AllColumns2",
        width=1,
        height=1,
        source=ColumnDataSource(df),
        line_color=None,
        fill_color=transform('value', mapper))

    color_bar = ColorBar(
        color_mapper=mapper,
        location=(0, 0),
        ticker=BasicTicker(desired_num_ticks=10))

    color_bar.background_fill_color = "#142e4d"
    color_bar.major_label_text_color = "#6e84a3"

    p.add_layout(color_bar, 'right')
    p.title.text_font = "Raleway"
    p.title.text_color = "#6e84a3"
    p.title.align = "center"
    p.title.text_font_size = "15pt"
    p.xaxis.major_label_text_color = "#6e84a3"
    p.yaxis.major_label_text_color = "#6e84a3"
    p.xaxis.axis_label_text_color = "#6e84a3"
    p.yaxis.axis_label_text_color = "#6e84a3"
    p.background_fill_color = "#142e4d"
    p.border_fill_color = "#142e4d"
    
    script, div = components(p)
    return script, div

if __name__ == '__main__':
    app.run(debug = True)