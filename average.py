# -*- coding: utf-8 -*-
import scrapy
import json
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Crawler
from pandas import DataFrame
import csv
from csv import DictWriter
from csv import reader
import io
import time
import sys
import matplotlib.pyplot as plt
from finstar import finstar
import numpy as np

output_file='data.csv'
input_file='fincode.csv'

class MySpider(scrapy.Spider):
	name = 'ntschools'
	start_urls = ['https://ticker.finology.in']

	headers = {
		"accept": "application/json, text/javascript, */*; q=0.01",
		"accept-encoding": "gzip, deflate, br",
		"cookie": "ASP.NET_SessionId=m11vkz5l0t3wx4apdhjh4v4b; _ga=GA1.2.1056050435.1610270634; _gid=GA1.2.733890492.1610270634; _gat_gtag_UA_136614031_6=1; _fbp=fb.1.1610270633963.365948770",
		"referer": "https://ticker.finology.in",
		"sec-fetch-dest": "empty",
		"sec-fetch-mode": "cors",
		"sec-fetch-site": "same-origin",
		"accept-language": "en-US,en;q=0.9",
		"dnt": "1",
		"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
		"x-requested-with": "XMLHttpRequest"
	}

	def __init__(self, *args, **kwargs):

		super(MySpider, self).__init__(*args, **kwargs)
		self.url     = kwargs.get('url')
			
	def parse(self, response, *args, **kwargs):
		url = self.url
		request = scrapy.Request(url, callback=self.get_prices, headers=self.headers)
			
		yield request

	def get_prices(self, response):
		raw_data = response.body
		global prices
		prices=json.loads(raw_data.decode('utf-8'))

def f_main():
	process = CrawlerProcess({
		"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
	})

	symbol     = sys.argv[1]
	fincode    = int(sys.argv[2])
	base_url = 'https://ticker.finology.in/GetPrices.ashx?v=3.1&fincode='
	url = base_url + str(fincode) + '&stk=NSE&type=Y&count=2'
	process.crawl(MySpider, url=url)
	process.start()
	process.stop()
	return pd.DataFrame(prices)

def populate(data):
	data.index = pd.to_datetime(data.index, dayfirst=True)

	data['12d_EMA'] = data.price.ewm(span=12, adjust=False).mean()
	data['26d_EMA'] = data.price.ewm(span=26, adjust=False).mean()
	data['macd'] = data['12d_EMA']- data['26d_EMA']
	data['macdsignal'] = data.macd.ewm(span=9, adjust=False).mean()
	# returns = (closePrice@T)/(closePrice@(T-1)) - 1
	#data['returns'] = data.price.pct_change()
	data['returns'] = (data['price']/data['price'].shift(1)) - 1
	data['trading_signal'] = np.where(data['macd'] > data['macdsignal'], 1, -1)
	data['strategy_returns'] = data.returns * data.trading_signal.shift(1)
	data['MA50'] = data['price'].rolling(50).mean()
	# Total return on Day T from Day 1
	data['CUM'] = (1 + data['returns']).cumprod()
	data['cum_strategy_ret'] = (data.strategy_returns + 1).cumprod()
	# Compound Annual Growth Rate
	# Total number of trading days
	days = len(data['cum_strategy_ret'])
	# 252 = total trading days in a year
	data['annual_ret'] = (data['cum_strategy_ret'].iloc[-1]**(252/days) - 1)*100
	# Calculate the annualised volatility the variation in stcok priice over a time period
	data['annual_volatility'] = data['strategy_returns'].std() * np.sqrt(252) * 100
	# Sharpe ratio : the risk taken in comparision to risk free investments(FD/RD/Bank Savings)
	# Assume the annual risk-free rate is 4%, as bank return principal at 4% interest
	# 252 = total trading days in a year
	risk_free_rate = 0.04
	data['daily_risk_free_return'] = risk_free_rate/252
	# Calculate the excess returns by subtracting the daily returns by daily risk-free return
	data['excess_daily_returns'] = data['strategy_returns'] - data['daily_risk_free_return']
	# Calculate the sharpe ratio using the given formula
	sharpe_ratio = (data['excess_daily_returns'].mean() /
        	        data['excess_daily_returns'].std()) * np.sqrt(252)
	print('The Sharpe ratio is %.2f' % sharpe_ratio)

def candle(df):
	import plotly.graph_objects as go
	import pandas as pd
	fig = go.Figure(data=[go.Candlestick(x=df['Date'],
										close=[df['price']])
	])
	fig.update_layout(xaxis_rangeslider_visible=False)
	fig.show()
if __name__== '__main__':
	df=f_main()
	candle(df)
	populate(df)

#df[['macd','macdsignal']].plot()
#plt.legend()
#plt.show()

		# get one year stock price
		#url = 'https://ticker.finology.in/GetPrices.ashx?v=3.1&fincode=219300&stk=BSE&type=Y&count=1'
		# get p/e ratio upto 30-07-2019
		#url = 'https://ticker.finology.in/GetValuation.ashx?v=3.1&fincode=219300&exc=BSE&top=365'
		# get all ratio of itself and peers
		#url = 'https://ticker.finology.in/Peers.ashx?v=3.1&fincode=219300&Mode=C'
		# share holding pattern
		#url = 'https://ticker.finology.in/GetShares.ashx?v=3.1&fincode=219300'
		# get dividend and patterns
		#url = 'https://ticker.finology.in/GetCorpAction.ashx?v=3.1&fincode=124208'
		#url = 'https://ticker.finology.in/News.ashx?v=3.1&fincode=219300'
		#url = 'https://ticker.finology.in/GetCompanybrief.ashx?v=3.1&fincode=219300'
