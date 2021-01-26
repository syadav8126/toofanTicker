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
from finstar import finstar

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
		self.symbol  = kwargs.get('SYMBOL')
		self.mode    = kwargs.get('mode')
			
	def parse(self, response, *args, **kwargs):
		url = self.url
		request = scrapy.Request(url, callback=self.get_peers_info, headers=self.headers)
			
		yield request

	def get_peers_info(self, response):
		raw_data = response.body
		print(raw_data)

		peer=raw_data.decode('utf-8')
		ls = json.loads(peer)
		for data in ls:
			if data['SYMBOL'] == '0':
				continue
			dic={}
			dic['SYMBOL']     = data['SYMBOL']
			dic['COMPNAME']   = data['COMPNAME']
			dic['PE']         = data['PE']
			dic['ROCE']       = data['ROCE']
			dic['ROE']        = data['ROE']
			dic['EPS']        = data['EPS']
			dic['ROA']        = data['ROA']
			dic['PB']         = data['PB']
			dic['EV_EBITDA']  = data['EV_EBITDA']
			dic['MCAP']	      = data['MCAP']
			dic['perchg']     = data['perchg']
			dic['52WeekHigh'] = data['52WeekHigh']
			dic['52WeekLow']  = data['52WeekLow']
			fields=['SYMBOL','COMPNAME','PE','ROCE','ROE','EPS','ROA','PB','EV_EBITDA','MCAP','perchg','52WeekHigh','52WeekLow']
			with open(output_file, 'a') as f_object:
				dicwriter = DictWriter(f_object, fieldnames=fields)
				dicwriter.writerow(dic)
				f_object.close()

def get_peer(symbol='COALINDIA',fincode=219300, mode='S'):
	base_url = 'https://ticker.finology.in/Peers.ashx?v=3.1&fincode='
	url = base_url + str(fincode) + '&MODE=' + mode
	process.crawl(MySpider, url=url, symbol=symbol, mode=mode, action=1)

def linetodata(line):
	the_file = open(input_file, 'r')
	reader = csv.reader(the_file)
	for i,row in enumerate(reader):
		if i == line:
			try:
				return row[1]
			except:
				continue

def remove_duplicate():
	lines_seen = set() # holds lines already seen
	with open(output_file, "r+") as f:
		d = f.readlines()
		f.seek(0)
		for i in d:
			if i not in lines_seen:
				f.write(i)
				lines_seen.add(i)
		f.truncate()



if __name__ == "__main__":
	process = CrawlerProcess({
		"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
	})

	start  = int(sys.argv[1])
	end    = int(sys.argv[2])

	for i in range(start,end):
		code=linetodata(i)
		if code:
			get_peer(fincode=code)

	process.start()
	process.stop()
	remove_duplicate()
