#! python3
# Data Downloader.py --  A simple program used to download options data from
#						 Trade Alert


print("Hello. I won't be printing the files that already exist. \nIf you want to turn this feature on, \ngo to check_file_exists function and 'enable' it.")	

import sys
sys.path.append('C:/Users/lorig/Desktop/PythonCode/Projects, Exercises, Programs/Trade Alert Journey')

import os
os.chdir(r"\\LAPTOP-JEK6IRL1\PythonCode\Projects, Exercises, Programs\Trade Alert Journey")

import re
import requests

import pandas as pd

from pandas import DataFrame
 
from datetime import date

import time
from time import process_time


import numpy as np

import requests

# ~ from IPython.core.display import HTML
# ~ css = open('style-table.css').read() + open('style-notebook.css').read()
# ~ HTML('<style>{}</style>'.format(css))


holidays2020 = ['2020-01-01', '2020-01-20', '2020-02-17', '2020-04-10', '2020-05-25', '2020-07-03', '2020-09-07']
holidays2021 = ['2021-01-01', '2021-01-18', '2021-02-15', '2021-04-02', '2021-05-31', '2021-07-05', '2021-09-06', '2021-11-25', '2021-12-24']
holidays2022 = ['2022-01-17', '2022-02-21', '2022-04-15', '2022-05-30', '2022-06-20', '2022-07-04', '2022-09-05', '2022-11-24', '2022-12-26']
holidays2023 = ['2023-01-02', '2023-01-16', '2023-02-20', '2023-04-07', '2023-05-29', '2023-06-19', '2023-07-04', '2023-09-04', '2023-11-23', '2023-12-25']


weekdays_2022_2023 = pd.date_range(start='2023/01/01', end='2023/12/31', freq='B')# Complete NYSE & Nasdaq Ticker List

# weekdays_2022_2023 = pd.date_range(start='2020/01/01', end='2023/12/31', freq='B')# Complete NYSE & Nasdaq Ticker List

error_count = 0
# above variable used to exit() program if more than 'x' errors ~~ 4


holidays = holidays2022
holidays.extend(holidays2023)
# holidays.extend(holidays2021)
# holidays.extend(holidays2020)

def closestTradingDate():
	# closest trading day
	from pandas.tseries.offsets import DateOffset

	today_date = pd.Timestamp(date.today())
	closest_date = today_date

	# Checks if today's date is SATURDAY
	if (today_date.isoweekday() == 6):
		closest_date = today_date - DateOffset(days = 1)
	# Checks if today_date is SUNDAY

	elif (today_date.isoweekday() == 7):
		closest_date = today_date - DateOffset(days = 2)

	# Check if the Friday is a holiday and subtract another day
	while(str(closest_date)[:10] in holidays):
		closest_date = closest_date - DateOffset(days = 1)

	# Check if today is a Monday Holiday and adjust for weekend
	if (closest_date.isoweekday() == 6):
		closest_date = closest_date - DateOffset(days = 1)

	elif (closest_date.isoweekday() == 7):
		closest_date = closest_date - DateOffset(days = 2)

	# Check if Friday Holiday Preceeding Monday Holiday
	while(str(closest_date)[:10] in holidays):
		closest_date = closest_date - DateOffset(days = 1)
			
	# returns only date ('YYYY-MM-DD') without time
	closest_date = str(closest_date)[:10]
	return closest_date

def listOfDatesToCurrent():
# returns a list of active trading dates from the year 2022 (can change to be any year)
    dates = []

    for num in range(len(weekdays_2022_2023)):

        # Changing it from a 'pandas timestamp' to a string with only year-month-day
        dates.append(weekdays_2022_2023.date[num].strftime('%Y-%m-%d'))

    # Disclude holidays from active trading days
    dates = [date for date in dates if date not in holidays]
    try:
        # this slice will stop at today's date from first day
        # finds the index of today's date (date.today()) and slices list to stop at today
        dates_to_present = dates[:dates.index(closestTradingDate())+1]
    except:
        print("ERROR?! UNCOMMENT BELOW LINE TO GIVE STATIC AMOUNT OF DATES")
        dates_to_present = dates[:252]

    return dates_to_present







class Parser():
# Parse through Trade-Alert widget data from HTML.

	def __init__(self, url):
		self.url = url
		self.html = requests.get(self.url).text
		self.parsed_data = self.parse()
		self.ticker, self.desc, self.chart, self.date = self.description()
	def parse(self):
		myDictRegex = re.compile(r"(?s)var myDict=(.*var container)")
		datum = myDictRegex.findall(self.html)
		# datum is class 'list'
		
		if datum == []:
			print("System Error (500)... OR data DNE")
			return ''
	
		# return 'str'
		return datum[0]
	
	def error(self):
		if self.parsed_data == '':
			return True
		
		errorRegex = re.compile(r"'error': '(.*?)'")
		
		# this stores error message from HTML
		error = errorRegex.findall(self.parsed_data)[0]
		
		if error == 'none':
			return False
		else:
			global error_count
			error_count += 1
			if error_count > 4:
				
				return True
			print("Error detected:\n{}\ndate:{} - ticker:{}\n".format(error, self.date, self.ticker))
			return True

	def description(self):
		# this method is mainly here for the __init__ attributes
		if self.parsed_data == '':
			return None, None, None, None

			
		tickerRegex = re.compile(r"var symbol='(.*)';")
		descriptionRegex = re.compile(r"var description='(.*)';")
		chartTypeRegex = re.compile(r"var chart_name='(.*)';")
		dateRegex = re.compile(r"var date=\"(.*)\";")
		
		ticker = tickerRegex.findall(self.parsed_data)[0]
		description = descriptionRegex.findall(self.parsed_data)[0]
		chart_type = chartTypeRegex.findall(self.parsed_data)[0]
		date = dateRegex.findall(self.parsed_data)[0]
		
		return ticker, description, chart_type, date
		
	def file_name(self):
		return(r"{}_{}_{}.csv".format(self.ticker, self.chart, self.date))
		
	def specific_chart_data(self):
		if bool(self.error()):
			return None
			
		#check what kind of chart it is.
		# depending on the chart, use different regexes to find all the data.
		
		
		# check if chart == strikes + expiries Open Interest per day (sometimes data is delayed 2-3 days from realtime)
		# can code something to determine if there is lag between intraday_volume big purchases and it showing up here
# --------------------------------------------------------------------------------#
		if self.chart == 'oi_strike_series':
			
			# ***  THIS IN TO SKIP IF NO DATA FOUND ON DAY"
			if self.parsed_data == None:
				return None
			# *** PUTTING THIS IN TO SKIP IF NO DATA FOUND ON DAY"
			
			expiryListRegex = re.compile(r"'expirylist': \[([-'A-Za-z0-9 ,.]+)\]")
			expiryRegex = re.compile(r"\d{4}-\d{2}-\d{2}")

			strikeListRegex = re.compile(r"'strikelist': \[(['A-Za-z0-9 ,.]+)\],")
			decimalRegex = re.compile(r"([0-9.]+)")

			openInterestListRegex = re.compile(r"\[([\d., ]+)\]")

			# checks if error == True --> SKIP


			expiryList = expiryListRegex.findall(self.parsed_data)[0]

			# list of expiries
			expiries = expiryRegex.findall(expiryList)

			# list of total OI per strike per expiry
			oi = openInterestListRegex.findall(self.parsed_data)
			# list of all strikes (ex. 138)
			strikes = decimalRegex.findall(oi.pop(-2))

			total_oi_per_strike = decimalRegex.findall(oi.pop(-1))   

			oi_list_of_lists = []
			oi_list_of_lists.insert(0, strikes)

			#function to create lists of oi_data per expiry & adds expiry to beginning of list
			for x in range(len(expiries)):
				temp_list = decimalRegex.findall(oi[x])
				oi_list_of_lists.append(temp_list)
				
			oi_list_of_lists.append(total_oi_per_strike)

			# expiries will be my df.columns
			# "Strikes" - "Expiries (1,2,3...)" - "Total OI per strike"
			expiries.insert(0, "Strikes")
			expiries.append("Total OI per Strike")

			# transpose data so Expiries:Horizontal & Strikes:Vertical
			data_to_df = np.array(oi_list_of_lists).transpose()
			df = pd.DataFrame(data=data_to_df, columns=expiries)

			return df
# --------------------------------------------------------------------------------#
		
		
		elif self.chart == 'intraday_volume':
			if self.parsed_data == None:
				return None
				
			timeRegex = re.compile(r"\d{2}:\d{2}:\d{2}")

			priceListRegex = re.compile(r"'pricelist': \[(['A-Za-z0-9 ,.]+)\],")
			priceRegex = re.compile(r"('null'|\d*\.\d*)")

			ivolListRegex = re.compile(r"'ivollist': \[(['A-Za-z0-9 ,.]+)\],")
			ivolRegex = re.compile(r"('null'|\d*\.\d*)")

			putVolumeRegex = re.compile(r"'putlist': \[(['A-Za-z0-9 ,.]+)\],")
			putRegex = re.compile(r"('null'|\d+)")

			callVolumeRegex = re.compile(r"'calllist': \[(['A-Za-z0-9 ,.]+)\],")
			callRegex = re.compile(r"('null'|\d+)")

			stockVolumeRegex = re.compile(r"'cumlist': \[(['A-Za-z0-9 ,.]+)\]};")
			volumeRegex = re.compile(r"('null'|\d+\.\d*)")


			timeList = timeRegex.findall(self.parsed_data)

			priceList = priceListRegex.findall(self.parsed_data)[0]
			price = priceRegex.findall(priceList)
			
			ivolList = ivolListRegex.findall(self.parsed_data)[0]
			ivol = ivolRegex.findall(ivolList)
			
			putList = putVolumeRegex.findall(self.parsed_data)[0]
			sum_puts = putRegex.findall(putList)

			callList = callVolumeRegex.findall(self.parsed_data)[0]
			sum_calls = putRegex.findall(callList)

			stockVolumeList = stockVolumeRegex.findall(self.parsed_data)[0]
			sum_volume = volumeRegex.findall(stockVolumeList)
			
			# df_1 is not the final dataframe i save to excel.
			# I still need to turn 'str' to 'float' and find volumes by subtracting
			df = pd.DataFrame({'time': timeList,
				'price': price,
				'ivol': ivol,
				'sum_puts': sum_puts,
				'sum_calls': sum_calls,
				'sum_volume': sum_volume
			})
			
			# change str --> float
			column_index_str_to_float = [1,2,3,4,5] #[price, ivol, sum_puts, sum_calls, sum_vol]
			for column_index in column_index_str_to_float: # 5 columns to change str --> float
				for x in range(len(df[df.columns[column_index]])):
					if df[df.columns[column_index]].iloc[x] == "'null'":
						df[df.columns[column_index]].iloc[x] = 0.0
					else:
						df[df.columns[column_index]].iloc[x] = float(df[df.columns[column_index]].iloc[x])
				
				
			stock_volume = [df.sum_volume.iloc[0]]
			call_volume = [df.sum_calls.iloc[0]]
			put_volume = [df.sum_puts.iloc[0]]
			for x in range(len(df.time)-1):
				vol = df.sum_volume.iloc[x+1] - df.sum_volume.iloc[x]
				stock_volume.append(vol)

				callvol = df.sum_calls.iloc[x+1] - df.sum_calls.iloc[x]
				call_volume.append(callvol)

				putvol = df.sum_puts.iloc[x+1] - df.sum_puts.iloc[x]
				put_volume.append(putvol)
			
			df = DataFrame({
					'time': timeList,
					'price': df.price,
					'put_volume': put_volume,
					'call_volume': call_volume,
					'stock_volume': stock_volume,
					'ivol': df.ivol,
					'sum_puts': df.sum_puts,
					'sum_calls': df.sum_calls,
					'sum_volume': df.sum_volume
				})
			
			return df
						
			
# --------------------------------------------------------------------------------#
		elif self.chart == 'historical_volume':
			if self.parsed_data == None:
				return None
			
			dateListRegex = re.compile(r"'datelist': \[(['A-Za-z0-9 ,.-]+)\],")
			dateRegex = re.compile(r"(\d{4}-\d{2}-\d{2})")
			
			priceListRegex = re.compile(r"'pricelist': \[(['A-Za-z0-9 ,.]+)\],")
			priceRegex = re.compile(r"('null'|\d*\.\d*)")
			
			ivolListRegex = re.compile(r"'ivollist': \[(['A-Za-z0-9 ,.]+)\],")
			ivolRegex = re.compile(r"('null'|\d*\.\d*)")
			
			skewListRegex = re.compile(r"'skewlist': \[(['A-Za-z0-9 ,.-]+)\],")
			skewRegex = re.compile(r"('null'|-*\d*\.\d*|-*\d+e-*\d+)")
			
			putVolumeRegex = re.compile(r"'putlist': \[(['A-Za-z0-9 ,.]+)\],")
			putRegex = re.compile(r"('null'|\d+)")

			callVolumeRegex = re.compile(r"'calllist': \[(['A-Za-z0-9 ,.]+)\]")
			callRegex = re.compile(r"('null'|\d+)")
			
			
			dateList = dateListRegex.findall(self.parsed_data)[00]
			date = dateRegex.findall(dateList)

			priceList = priceListRegex.findall(self.parsed_data)[0]
			price = priceRegex.findall(priceList)
			
			ivolList = ivolListRegex.findall(self.parsed_data)[0]
			ivol = ivolRegex.findall(ivolList)
			#smth wrong	
			skewList = skewListRegex.findall(self.parsed_data)[0]
			skew = skewRegex.findall(skewList)
			
			putList = putVolumeRegex.findall(self.parsed_data)[0]
			puts = putRegex.findall(putList)
 
			callList = callVolumeRegex.findall(self.parsed_data)[0]
			calls = callRegex.findall(callList)
			
			
			
			df = pd.DataFrame({	'date': date,
								'price': price,
								'calls': calls,
								'puts': puts,
								'ivol': ivol,
								'skew': skew
			})
			
			return df


# --------------------------------------------------------------------------------#
		elif self.chart == 'historical_oi':
			if self.parsed_data == None:
				return None
			
			dateListRegex = re.compile(r"'datelist': \[(['A-Za-z0-9 ,.-]+)\],")
			dateRegex = re.compile(r"(\d{4}-\d{2}-\d{2})")
			
			priceListRegex = re.compile(r"'pricelist': \[(['A-Za-z0-9 ,.]+)\],")
			priceRegex = re.compile(r"('null'|\d*\.\d*)")
			
			putVolumeRegex = re.compile(r"'putlist': \[(['A-Za-z0-9 ,.]+)\],")
			putRegex = re.compile(r"('null'|\d+)")

			callVolumeRegex = re.compile(r"'calllist': \[(['A-Za-z0-9 ,.]+)\]")
			callRegex = re.compile(r"('null'|\d+)")
			
			
			dateList = dateListRegex.findall(self.parsed_data)[00]
			date = dateRegex.findall(dateList)

			priceList = priceListRegex.findall(self.parsed_data)[0]
			price = priceRegex.findall(priceList)
			
			putList = putVolumeRegex.findall(self.parsed_data)[0]
			puts = putRegex.findall(putList)

			callList = callVolumeRegex.findall(self.parsed_data)[0]
			calls = putRegex.findall(callList)
			
			
			
			df = pd.DataFrame({	'date': date,
								'price': price,
								'calls': calls,
								'puts': puts
			})
			
			return df


# --------------------------------------------------------------------------------#
		elif self.chart == 'historical_volatilities':
			if self.parsed_data == None:
				return None
			dateListRegex = re.compile(r"'datelist': \[(['A-Za-z0-9 ,.-]+)\],")
			dateRegex = re.compile(r"(\d{4}-\d{2}-\d{2})")
			
			priceListRegex = re.compile(r"'pricelist': \[(['A-Za-z0-9 ,.]+)\],")
			priceRegex = re.compile(r"('null'|\d*\.\d*)")
			
			ivol30ListRegex = re.compile(r"'ivol30list': \[(['A-Za-z0-9 ,.]+)\],")
			ivol30Regex = re.compile(r"('null'|\d*\.\d*)")
			
			ivol60ListRegex = re.compile(r"'ivol60list': \[(['A-Za-z0-9 ,.]+)\],")
			ivol60Regex = re.compile(r"('null'|\d*\.\d*)")
			
			ivol90ListRegex = re.compile(r"'ivol90list': \[(['A-Za-z0-9 ,.]+)\],")
			ivol90Regex = re.compile(r"('null'|\d*\.\d*)")
			
			ivol120ListRegex = re.compile(r"'ivol120list': \[(['A-Za-z0-9 ,.]+)\],")
			ivol120Regex = re.compile(r"('null'|\d*\.\d*)")
			
			hvol30ListRegex = re.compile(r"'hvol30list': \[(['A-Za-z0-9 ,.]+)\],")
			hvol30Regex = re.compile(r"('null'|\d*\.\d*)")
			
			hvol60ListRegex = re.compile(r"'hvol60list': \[(['A-Za-z0-9 ,.]+)\],")
			hvol60Regex = re.compile(r"('null'|\d*\.\d*)")
			
			hvol120ListRegex = re.compile(r"'hvol120list': \[(['A-Za-z0-9 ,.]+)\]")
			hvol120Regex = re.compile(r"('null'|\d*\.\d*)")
			
			
			
			dateList = dateListRegex.findall(self.parsed_data)[0]
			date = dateRegex.findall(dateList)

			priceList = priceListRegex.findall(self.parsed_data)[0]
			price = priceRegex.findall(priceList)
			
			ivol30List = ivol30ListRegex.findall(self.parsed_data)[0]
			ivol30 = ivol30Regex.findall(ivol30List)
			
			ivol60List = ivol60ListRegex.findall(self.parsed_data)[0]
			ivol60 = ivol60Regex.findall(ivol60List)
			
			ivol90List = ivol90ListRegex.findall(self.parsed_data)[0]
			ivol90 = ivol90Regex.findall(ivol90List)
			
			ivol120List = ivol120ListRegex.findall(self.parsed_data)[0]
			ivol120 = ivol120Regex.findall(ivol120List)
			
			hvol30List = hvol30ListRegex.findall(self.parsed_data)[0]
			hvol30 = hvol30Regex.findall(hvol30List)
			
			hvol60List = hvol60ListRegex.findall(self.parsed_data)[0]
			hvol60 = hvol60Regex.findall(hvol60List)

			hvol120List = hvol120ListRegex.findall(self.parsed_data)[0]
			hvol120 = hvol120Regex.findall(hvol120List)
			
			
			
			df = pd.DataFrame({	'date': date,
								'price': price,
								'ivol30': ivol30,
								'ivol60': ivol60,
								'ivol90': ivol90,
								'ivol120': ivol120,
								'hvol30': hvol30,
								'hvol60': hvol60,
								'hvol120': hvol120						
			})
			
			return df	
			
			
# --------------------------------------------------------------------------------#
		elif self.chart == 'exchange_volume':
			# *** PUTTING THIS IN TO SKIP IF NO DATA FOUND ON DAY"
			if self.parsed_data == None:
				return None
			
			exchangesVolumeRegex = r"\{[^}]*'exchlist': \[.*?\}\]"

			callsPutsExchangesRegex = r"'drilldownlist': \[.*?\};"
			# *** PUTTING THIS IN TO SKIP IF NO DATA FOUND ON DAY"
			
			# Search for the pattern in the string
			exchangeVolumeList = re.search(exchangesVolumeRegex, self.parsed_data).group(0)

			callsPutsList = re.search(callsPutsExchangesRegex, self.parsed_data).group(0)
			# Extract the matched portion.group(0)
			if exchangeVolumeList and callsPutsList:
				pass
			#     print(exchangeVolumeList)
			#     print(callsPutsList)
			else:
				print("Pattern not found.")

			exchangeRegex = re.compile(r"'name': '(.*?)'")
			exchangeNames = exchangeRegex.findall(exchangeVolumeList)

			exchangeVolumesRegex = re.compile(r"'y': (\d*),")
			exchangeVolumes = exchangeVolumesRegex.findall(exchangeVolumeList)

			exchangePutsCallsRegex = re.compile(r"'data': (.*?)}")
			exchangePutsCalls = exchangePutsCallsRegex.findall(callsPutsList)


			exchangePutsRegex = re.compile(r"PUTS', (\d*)\]")
			exchangePuts = exchangePutsRegex.findall(callsPutsList)
			exchangePuts = [int(num) for num in exchangePuts]

			exchangeCallsRegex = re.compile(r"CALLS', (\d*)\]")
			exchangeCalls = exchangeCallsRegex.findall(callsPutsList)
			exchangeCalls = [int(num) for num in exchangeCalls]

			totalVolumeDay = sum(exchangePuts) + sum(exchangeCalls)

			ratioList = []
			for i in range(len(exchangeNames)):
				exchangeVolume = exchangePuts[i] + exchangeCalls[i]
				ratio = exchangeVolume/totalVolumeDay
				ratioList.append(ratio)

			df = pd.DataFrame({
				'exchange': exchangeNames,
				'puts': exchangePuts,
				'calls': exchangeCalls,
				'percentage': ratioList
			})
			# df = df.set_index('exchange', inplace=True)
			return df
# Parse through Trade-Alert widget data from HTML.

# --------------------------------------------------------------------------------#

class Data():
	
	def __init__(self, ticker):
		self.ticker = ticker
		self.url_dict = {
						"hist_volume" : "https://trade-alert.com/widget/charts/historical_volume/{}/interactive/", #
						"hist_oi" : "https://trade-alert.com/widget/charts/historical_oi/{}/interactive/", #
						"hist_volatility" : "https://trade-alert.com/widget/charts/historical_volatilities/{}/interactive/", #
						"oi" : "https://trade-alert.com/widget/charts/oi_strike_series/{}/{}/interactive/", #
						"intra_volume" : "https://trade-alert.com/widget/charts/intraday_volume/{}/{}/interactive/", #
						"pc_ratio" : "https://trade-alert.com/widget/charts/historical_ratios/{}/interactive/",
						"exchange_vol" : "https://trade-alert.com/widget/charts/exchange_volume/{}/{}/interactive/",
						"borrow_rate" : "https://trade-alert.com/widget/charts/historical_borrow/{}/interactive/",
						"iv_term_structure" : "https://trade-alert.com/widget/charts/termstructure/{}/{}/interactive/",
						"iv_skew" : "https://trade-alert.com/widget/charts/historical_skew/{}/interactive/"
						}
	# can give input year to download data for


	def install_folders(self, list_of_urls):
	# Check if folder exists. Create folder if DNE.
	
	# takes a list of TradeAlert URLs and will parse them to find 
	# the chart types needed to create folders to put data in them
	
		data_folder_dir = os.getcwd() + "\Data"
		# C:\Users\lorig\Desktop\PythonCode\Projects, Exercises, Programs\Trade Alert Journey\Data

		ticker_folder_dir = data_folder_dir + "\{}".format(self.ticker)
		# C:\Users\lorig\Desktop\PythonCode\Projects, Exercises, Programs\Trade Alert Journey\Data\XLE

		if self.ticker not in os.listdir(data_folder_dir):
			print("Initializing folder for {}".format(self.ticker))
			os.mkdir(ticker_folder_dir)
		
		for url in list_of_urls:
			
			url_split = url.split("/")
			chart_url = url_split[5]
			
			folder_name = "{}_{}".format(self.ticker, chart_url)
			
			chart_folder_dir = ticker_folder_dir + "\{}".format(folder_name)
			# C:\Users\lorig\Desktop\PythonCode\Projects, Exercises, Programs\Trade Alert Journey\Data\XLE\XLE_2022_oi_strike_series

			# create '{ticker}_{chart_type}' folder
			if folder_name not in os.listdir(ticker_folder_dir):
				print("Installing {} folder! :) ".format(chart_url))
				os.mkdir(chart_folder_dir)
				
			# DONE. ALL FOLDERS SHOULD BE MADE NOW

	def update_all(self):
		url_list = self.URL_generator()
		self.install_folders(url_list)
		# check for folder & file existence before beginning downloading.
		
		
		
		for url in url_list:

			
			
			
			
			
			# WORK IN PROGRESS	
			# The idea behind introducing a new class 'Parser'
			# is that with each URL I can call a new class that will
			# store self.parsed_data as an attribute so I won't need
			# to ping HTTP multiple times with request.get slowing down SIGNIFICANTLY
			
			x = Parser(url)
			
			
			x = x.parse()
			
			# this should return like a dataframe so I can write_csv here

		return x
	
	def file_name(self, url):
		# checks if date in URL 
		url_split = url.split("/")
		chart_url = url_split[5]
		
		dateRegex = re.compile(r"\d{4}-\d{2}-\d{2}")
		
		if re.search(dateRegex, url_split[7]) == None:
			# if no date in URL = closestTradingDate
			url_date = closestTradingDate()
		else:
			url_date = url_split[7]
		
		return "{}_{}_{}.csv".format(self.ticker, chart_url, url_date)
	# return "XLE_oi_strike_series_2022-08-08.csv"

	def chart_folder_path(self, url):
		url_split = url.split("/")
		chart_url = url_split[5]
			
		folder_name = "{}_{}".format(self.ticker, chart_url)
		
		chart_folder_dir = os.getcwd() + "\Data\{}".format(self.ticker) + "\{}".format(folder_name)
		
		return chart_folder_dir
	# returns "C:\Users\lorig\Desktop\PythonCode\Projects, Exercises, Programs\Trade Alert Journey\Data\XLE\XLE_oi_strike_series"
	def check_ticker_error_file(self, url):
		ticker = self.ticker()
		pass
	
	def check_file_exists(self, url):
		# return False
		folderpath = self.chart_folder_path(url)
		filename = self.file_name(url)
		if filename not in os.listdir(folderpath):
			# file DNE
			return False

		else:
			# file exists.
			# check for file exists but small size
			

			averagefilesize = 0
			
			# clever slice to only get 3 most recent dates spread 6 apart
			for file_ in os.listdir(folderpath)[::6][-3:]:
				# this function returns average filesize to see if any files are much smaller to redownload
				averagefilesize += os.path.getsize(folderpath + "/" + file_)
				
			# using 77% lower than average
			averagefilesize = 0.77*(averagefilesize/3)
			filepath = folderpath + "/" +filename
			if os.path.getsize(filepath) < averagefilesize:
				return False
				
			print("{} already exists...".format(filename))
			return True
	# return False (if file DNE) -	return True (if file already exists)
	
	def df_to_csv(self, url, df):
		
		filename = self.file_name(url)
		
		filepath = self.chart_folder_path(url) + "\{}".format(filename)
		
		try:
			
			print("Creating {}".format(filename))
			df.to_csv(filepath, index = False)
			
		except:
			print("{} not working".format(filename))
			print("Data might not exist.\n")
	# will create CSV file in designated folder
		
	def download(self, chart, date = closestTradingDate()):
		url = self.URL_generator(charts = chart, start_date = date, quantity = 1)
		print(url)
		self.install_folders(url)
		try:
			x = Parser(url)
			dataframe = x.specific_chart_data()

			return dataframe
			self.df_to_csv(url, dataframe)
		except:
			print("Was not able to download.")
			
	def update(self, chart, date = closestTradingDate(), amount = 1, skip_check = False):
		
		# This is here because TradeAlert website can only store 84 data entries for stocks.
		
		if chart == "oi":
			if isinstance(chart, str) == True:
				chart = [chart]
			url_list = self.URL_generator(charts = chart, start_date = date, quantity = 84) #quantity should be 84
		# turns a 'str' date into a list to make sure URL_generator has iterable


		#                               THIS NEEDS LIST INPUT
		else:
			if isinstance(chart, str) == True:
				chart = [chart]
			url_list = self.URL_generator(charts = chart, start_date = date, quantity = amount)
		self.install_folders(url_list)
		
		try:
			# ~ print('what', os.listdir(self.chart_folder_path)
			
			# ~ if len(os.listdir(self.chart_folder_path())) == len(listOfDatesToCurrent()):
				# ~ print("All dates exist. SKIP.")
				
			for url in url_list:
				# Does file exist? If yes, SKIP.
				
				if skip_check == False:
					if self.check_file_exists(url) == True:
						continue
								
								
				# With URL ready, I pass into class Parser()
				# This way the website is only pinged once
				# while all the parsing is done & will return a dataframe.
				x = Parser(url)
				
				# this is my own class method that takes a dataframe and
				# saves a CSV file with custom filenames
				dataframe = x.specific_chart_data()
				self.df_to_csv(url, dataframe)
		except (IndexError):
			print("error")
			time.sleep(5)
			#uncomment for infinite...testing
		except (TypeError):
			print("error")
			time.sleep(5)

	def URL_generator(self, charts = "all", start_date = closestTradingDate(), quantity = 0):
		
		# returns a list of URLs. Can customize to be any charts (can pass a list)


		charts_only_ticker = ["hist_volume", "hist_oi", "hist_volatility", "pc_ratio", "borrow_rate", "iv_skew"]
		charts_date_ticker = ["oi", "intra_volume", "exchange_vol", "iv_term_structure"]
		date_list = listOfDatesToCurrent()
		if start_date not in date_list:
			print("Please choose a real trading date that is not a weekend OR holiday.\n\n\n---\n")
			return

		#create a date list of files already in folder.
		
		# NEEDS MORE CODE FOR THIS TO WORK
		# This is the beginning of skipping files that already exist but I need to rewrite code lower in order to make it work perfectly.
		# ~ if charts == ["intra_volume"]:
			# ~ filedate_list = os.listdir(r"C:\Users\lorig\Desktop\PythonCode\Projects, Exercises, Programs\Trade Alert Journey\Data\{}\{}_intraday_volume".format(self.ticker, self.ticker))
			# ~ newlist = [filename[-14:-4] for filename in filedate_list]
			# ~ print(newlist)
			
			# ~ date_list = [date for date in date_list if date not in newlist]
		
		# make start_date do SOMETHING
			
		inverse_dates = list(reversed(date_list))
		
		
		
		if quantity == 0:
			quantity = len(date_list)
		start_date_index = inverse_dates.index(start_date)
		# should return all dates depending on quantity wanted
		date_list = inverse_dates[start_date_index:start_date_index + quantity]
		url_list = []
		
		if charts == "all":
			for chart in charts_only_ticker:
				temp_url = self.url_dict.get(chart)
				temp_url = temp_url.format(self.ticker)
				url_list.append(temp_url)
			# url_list should now have 6 urls of 'charts_only_tickers' i.e. hist_volume, pc_ratio, etc.
			
			for chart in charts_date_ticker:
				if chart == "oi":
					for date in date_list[0:81]:
						temp_url = self.url_dict.get(chart)
						temp_url = temp_url.format(self.ticker, date)
						url_list.append(temp_url)
				else:
					for date in date_list:
						temp_url = self.url_dict.get(chart)
						temp_url = temp_url.format(self.ticker, date)
						url_list.append(temp_url)
		
		# checks if passed object is a list, will cycle through list
		# and return necessary URLs
		elif isinstance(charts, list) == True:
			for chart in charts:
				

				temp_url = self.url_dict.get(chart)
				if temp_url == None:
					print("{} not in list of 'charts' keywords. \n***Use the ones from this list:*** \n\n{}\n\n\n".format(chart, list(self.url_dict.keys())))
					return None

					
				if chart in charts_only_ticker:
					temp_url = self.url_dict.get(chart)
					temp_url = temp_url.format(self.ticker)
					url_list.append(temp_url)
			
				elif chart in charts_date_ticker:
					if chart == "oi":
						for date in date_list[0:81]:
							temp_url = self.url_dict.get(chart)
							temp_url = temp_url.format(self.ticker, date)
							url_list.append(temp_url)
					else:	
						for date in date_list:
							temp_url = self.url_dict.get(chart)
							temp_url = temp_url.format(self.ticker, date)
							url_list.append(temp_url)
		return url_list

import pprint


# 		END OF PROGRAM 		# 		CAN USE FROM HERE 	#

# x = Data("LI").update("intra_volume", amount = 0)

# print(x)