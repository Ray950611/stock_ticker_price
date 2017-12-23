from flask import Flask, render_template, request, redirect
import pandas as pd
from bokeh.embed import components
from bokeh.resources import CDN,INLINE
from bokeh.plotting import figure, output_file, show
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')
@app.route('/result/',methods=['POST'])
def stock_price():
  ticker = request.form['stock']
  price_type = request.form['type'] 
  dic = {'close':5,'open':2,'high':3,'low':4}
  k = dic[str(price_type)]
  X = []
  Y = []
  msg = ""
  try:
    data = pd.read_json("https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker="+str(ticker)+"&api_key=82ocY42PXsgZMnTGWcCD",orient="table")
    table=data["datatable"]["data"]
    time_period = 22
    for i in range(time_period):
        cur = table[-1-i]
        cur_date = pd.to_datetime(str(cur[1])).date()
        cur_price = float(cur[k])
        X.insert(0,cur_date)
        Y.insert(0,cur_price)
    msg = str(ticker)+":"+str(price_type)
  except:
    msg = "Invalid Stock Ticker"
  p = figure(title="Quandl WIKI Stock Prices 2017",x_axis_label='date',x_axis_type="datetime")
  p.line(pd.to_datetime(X), Y, legend=msg, line_width=2)
  script, div = components(p)
        
  return render_template('graph.html',script=script, div=div)
if __name__ == '__main__':
  app.run(port=33507)
