# Data-Analysis

In this folder the file "tradealertdownloaderclass.py" is the main file that allows you to download options data from the Chicago Board of Options Exchange (CBOE).

This is a simple program used to download options data from
the Chicago Board of Options Exchange (CBOE).

Able to download options data for any ticker in 
Nasdaq and NYSE.

# Data available:   
Intraday Option Volume,
Historical Implied Volatility,
		    Historical Volume,
			  Historical Open Interest


# Functions Provided:
 
 Parser() 		- Class used to return parsed DataFrame
 
Data() 			- Class used to download data and categorize 
 
closestTradingDate() 	- returns closest trading date
  
listOfDatesToCurrent() 	- returns a list of trading dates until present from (USER INPUT)

# Usage:

ex. Class usage:

	Data("SPY").update(chart="intraday_volume", date = closestTradingDate(), amount = 1, skip_check = False)
	
 This will download only the latest trading date's intraday options volume, and will check if another file already exists.
