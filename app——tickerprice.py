from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
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
    d = request.form['days']
    n = 0
    if d=='':
        n=250
    else:
        n = int(d)
    if n>1000:
        n=250
    price_type = request.form['type'] 
    if price_type=='Candle&MACD':
        try:
            data = pd.read_json("https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker="+str(ticker)+"&api_key=82ocY42PXsgZMnTGWcCD",orient="table")
            table=data["datatable"]["data"]
            if n>len(table):
                n=len(table)
            df = pd.DataFrame(table[-n:],columns=['ticker','date', 'open', 'high', 'low', 'close','vol','ex-div','split','a_open','a_high','a_low','a_close','a_vol'])
            c = 5
            o = 2
            h=3
            l=4
            #MACD cals
            ema_12 = 0
            ema_26 = 0
            EMA_12 = []
            EMA_26 = []
            DEA = []
            dea = 0
            for i in range(len(table)):
                close = table[i][c]  
                ema_12 = ema_12*11.0/13.0+close*2.0/13.0
                ema_26 = ema_26*25.0/27.0+close*2.0/27.0
                EMA_12.append(ema_12)
                EMA_26.append(ema_26)
            DIFF = np.array(EMA_12)-np.array(EMA_26)
            for i in range(len(DIFF)):

                dea = dea*4.0/5.0+DIFF[i]*1.0/5.0
                DEA.append(dea)
            DEA = np.array(DEA)
            MACD = 2*(DIFF-DEA)
            DIFF = DIFF[-n:]
            DEA = DEA[-n:]
            MACD = MACD[-n:]
            df['DIFF'] = pd.Series(DIFF, index=df.index)
            df['DEA'] = pd.Series(DEA, index=df.index)
            df['MACD'] = pd.Series(MACD, index=df.index)
            inc = df.DIFF>=df.DEA
            dec = df.DEA > df.DIFF
            TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
            p = figure(tools=TOOLS, plot_width=1000, title = str(ticker)+" MACD Chart: Past "+str(n)+" Days")
            p.xaxis.major_label_orientation = np.pi/4
            p.grid.grid_line_alpha=0.3

            p.vbar(df.index[inc], 0.5, 0*df.MACD[inc], df.MACD[inc], fill_color="green", line_color="black")
            p.vbar(df.index[dec], 0.5,0*df.MACD[dec] ,df.MACD[dec], fill_color="red", line_color="black")
            p.line(df.index,df.DIFF,line_color="red")
            p.line(df.index,df.DEA,line_color="blue")
                       
            script_1, div_1 = components(p)
            inc = df.close>df.open
            dec = df.open>df.close
            w = 0.5# half day in ms
#MACD price segments
            cur = 0
            sign = 1*(MACD>=0)+1*(DEA>=0)-1*(MACD<0)-1*(DEA<0)
            trend = 0
            pts = []
            while cur<len(MACD):
                if sign[cur]==0 or sign[cur]==trend:
                    cur+=1
                elif sign[cur]==2:
                    end = cur+1
                    peak = cur
                    peak_value = df.high[cur]
                    while end<len(MACD) and sign[end]!=-2:
                        if df.high[end]>peak_value and sign[end]==2:
                            peak = end
                            peak_value = df.high[end]
                        end+=1
                    pts.append([peak,peak_value,'green'])
                    trend = 2
                    cur=end
                else:
                    end = cur+1
                    bottom = cur
                    bottom_value = df.low[cur]
                    while end<len(MACD) and sign[end]!=2:
                        if df.low[end]<bottom_value and sign[end]==-2:
                            bottom = end
                            bottom_value = df.low[end]
                        end+=1
                    pts.append([bottom,bottom_value,'red'])
                    trend = -2
                    cur=end  
            TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

            q = figure(tools=TOOLS, plot_width=1000, title = str(ticker)+" Candlestick Chart: Past "+str(n)+" Days")
            q.xaxis.major_label_orientation = np.pi/4
            q.grid.grid_line_alpha=0.3

            q.segment(df.index, df.high, df.index, df.low, color="black")
            q.vbar(df.index[inc], w, df.open[inc], df.close[inc], fill_color="green", line_color="black")
            q.vbar(df.index[dec], w, df.open[dec], df.close[dec], fill_color="red", line_color="black")
            
            for pt in pts:
                ind = pt[0]
                value = pt[1]
                color = pt[2]
                q.scatter([ind],[value],size=10,fill_color=color,line_color='black')
            if pts[0][2]=='red' and pts[0][0]!=0:
                q.line([0,pts[0][0]],[df.high[0],pts[0][1]],line_color='blue')
            elif pts[0][2]=='green' and pts[0][0]!=0:
                q.line([0,pts[0][0]],[df.low[0],pts[0][1]],line_color='blue')
            else:
                pass
            if pts[-1][2]=='red' and pts[-1][0]!=n-1:
                q.line([pts[-1][0],n-1],[pts[-1][1],df.high[n-1]],line_color='blue')
            elif pts[-1][2]=='green' and pts[-1][0]!=n-1:
                q.line([pts[-1][0],n-1],[pts[-1][1],df.low[n-1]],line_color='blue')
            else:
                pass
            for i in range(1,len(pts)):
                pt_0 = pts[i-1]
                pt_1 = pts[i]
                q.line([pt_0[0],pt_1[0]],[pt_0[1],pt_1[1]],line_color='black')
            
            script_2, div_2 = components(q)
            return render_template('graph_2.html',script_1=script_1, div_1=div_1,script_2 = script_2,div_2=div_2)
        except:
            msg = "Invalid Stock Ticker"
            p = figure(title="Quandl WIKI Stock Prices "+msg,x_axis_label='date',x_axis_type="datetime")
            q = figure(title="Quandl WIKI Stock MACD "+msg,x_axis_label='date',x_axis_type="datetime")
            script_1, div_1 = components(p)
            script_2, div_2 = components(q)
            return render_template('graph_2.html',script_1=script_1, div_1=div_1,script_2 = script_2,div_2=div_2)
    else:
        dic = {'close':5,'open':2,'high':3,'low':4}
        k = dic[str(price_type)]
        X = []
        Y = []
        msg = " "
        try:
            data = pd.read_json("https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker="+str(ticker)+"&api_key=82ocY42PXsgZMnTGWcCD",orient="table")
            table=data["datatable"]["data"]
            if n>len(table):
                n=len(table)
            time_period = n
            for i in range(time_period):
                cur = table[-1-i]
                cur_date = pd.to_datetime(str(cur[1])).date()
                cur_price = float(cur[k])
                X.insert(0,cur_date)
                Y.insert(0,cur_price)
            msg = str(ticker)+":"+str(price_type)
        except:
            msg = "Invalid Stock Ticker"
        p = figure(title="Quandl WIKI Stock Prices",x_axis_label='date',x_axis_type="datetime")
        p.line(pd.to_datetime(X), Y, legend=msg, line_width=2)
        script, div = components(p)

        return render_template('graph.html',script=script, div=div)
if __name__ == '__main__':
  app.run(port=33507)
