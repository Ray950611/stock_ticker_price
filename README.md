# My Stock Price App

This project creates a web application hosted at https://ruiding-tdi-stockpriceproject.herokuapp.com
The web application takes in a valid stock ticker(such as AAPL) and a user selected price type(choice include Open, Close, High, Low) and 
returns a price plot of that stock in the last month(defined as 22 trading days). 

The repository is cloned from the sample flask-demo repository with given requirement specification texts. 
In the source code app.py I wrote some code to enable user to submit a form including a price type variable and a stock ticker variable.
Then I used read_json to read the data for that stock from the Quandl WIKI price dataset. After formatting the requested data into a list table, I gathered the last 22 entries of the specified price type and plotted the prices against the dates using bokeh plot.
The two template files index.html and graph.html are written for the home page and the result displaying page with required css and js specifications.
At this point I have not yet implemented robust input checking so an invalid stock ticker will result in an internal error.

The repository also contains a test.ipynb which is used for various testings during the application building process.
