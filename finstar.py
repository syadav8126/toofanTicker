import requests
from bs4 import BeautifulSoup
import numpy as np 
import pandas as pd
import re
import csv
import sys

input_file='fincode.csv'
output_file='valuation.csv'
def finstar(SYMBOL, mode='S'):
	try:
		if (mode == 'C'):
			url_1 = 'https://ticker.finology.in/company/' + SYMBOL + '?mode=C'
		else:
			url_1 = 'https://ticker.finology.in/company/' + SYMBOL 
		page = requests.get(url_1)
		soup = BeautifulSoup(page.content, 'lxml')
		overallrating = soup.find('span',{'class','ratingstars overallstars'})
		rating=overallrating.get('style')
		rate=(rating.split(':')[1]).split(';')[0]
		if not rate:
			return -2
		return int(rate)
	except:
		return -1

def appendfl(SYMBOL, rate1, rate2):
	with open(input_file, 'r') as f:
		with open(output_file, 'a') as app:
			writer = csv.writer(app, lineterminator='\n')
			reader = csv.reader(f)
			for row in reader:
				all=[]
				if row[0] == SYMBOL:
					row.append(rate1)
					row.append(rate2)
					all.append(row)
					writer.writerows(all)
					return

if __name__ == "__main__":
	SYMBOL=sys.argv[1]
	rate1=finstar(SYMBOL,mode='S')
	rate2=finstar(SYMBOL,mode='C')
	print(SYMBOL,rate1, rate2)
	appendfl(SYMBOL,rate1, rate2)
