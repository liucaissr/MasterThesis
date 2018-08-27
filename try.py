'''
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np

import base64


with open("/Users/my/Desktop/MT/code/MasterThesis/heatmap/171130-MicroHeaterLayout-final/171130-MicroHeaterLayout-final.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
#add the prefix that plotly will want when using the string as source
encoded_image = "data:image/png;base64," + encoded_string

with open("/Users/my/Desktop/MT/code/MasterThesis/heatmap/171130-MicroHeaterLayout-final/1.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
#add the prefix that plotly will want when using the string as source
encoded_image1 = "data:image/png;base64," + encoded_string

trace1= go.Scatter(x=[0,0.5,1,2,2.2],y=[1.23,2.5,0.42,3,1])
trace2 = go.Scatter(
    x=[20, 30, 40],
    y=[50, 60, 70],
    xaxis='x2',
    yaxis='y2'
)
xy = 'xaxis1'
xxx = 'xaxis2'
xx = 'xaxis1=dict( domain=[0, 0.45]),xaxis2=dict(domain=[0.55, 1])'
laylist = {}
laylist[xy]  = dict( domain=[0, 0.45])
laylist[xxx] = dict(domain=[0.55, 1])
laylist['images'] = [dict(
                  source= encoded_image,
                  xref= "x",
                  yref= "y",
                  x= 0,
                  y= 3,
                  sizex= 2,
                  sizey= 2,
                  sizing= "stretch",
                  opacity= 0.5,
                  layer= "below"), dict(
                  source= encoded_image1,
                  xref= "x2",
                  yref= "y2",
                  x= 20,
                  y= 50,
                  sizex= 2,
                  sizey= 2,
                  sizing= "stretch",
                  opacity= 0.5,
                  layer= "below")]

layout= go.Layout(images= [dict(
                  source= encoded_image,
                  xref= "x",
                  yref= "y",
                  x= 0,
                  y= 3,
                  sizex= 2,
                  sizey= 2,
                  sizing= "stretch",
                  opacity= 0.5,
                  layer= "below"), dict(
                  source= encoded_image1,
                  xref= "x2",
                  yref= "y2",
                  x= 20,
                  y= 50,
                  sizex= 2,
                  sizey= 2,
                  sizing= "stretch",
                  opacity= 0.5,
                  layer= "below")],xy = dict( domain=[0, 0.45]),xaxis2=dict(domain=[0.55, 1])
    )

layout = go.Layout(laylist)
fig=go.Figure(data=[trace1, trace2],layout=layout)
py.plot(fig,filename='background')

images= [dict(
                  source= encoded_image,
                  xref= "x",
                  yref= "y",
                  x= 0,
                  y= 3,
                  sizex= 2,
                  sizey= 2,
                  sizing= "stretch",
                  opacity= 0.5,
                  layer= "below")],

import plotly.plotly as py
import plotly.graph_objs as go

trace1 = go.Scatter(
    x=[1, 2, 3],
    y=[4, 5, 6]
)
trace22 = go.Scatter(
    x=[20, 30, 40],
    y=[50, 60, 70],
    xaxis='x2',
    yaxis='y2'
)
trace3 = go.Scatter(
    x=[300, 400, 500],
    y=[600, 700, 800],
    xaxis='x3',
    yaxis='y3'
)
trace5 = go.Scatter(
    x=[4000, 5000, 6000],
    y=[7000, 8000, 9000],
    xaxis='x4',
    yaxis='y4'
)
data = [trace1, trace22, trace3, trace5]
layout = go.Layout(
    xaxis3=dict(
        domain=[0, 0.45],
        anchor='y3'
    ),
    xaxis4=dict(
        domain=[0.55, 1],
        anchor='y4'
    ),
    yaxis2=dict(
        domain=[0, 0.45],
        anchor='x2'
    ),
    yaxis3=dict(
        domain=[0.55, 1]
    ),
    yaxis4=dict(
        domain=[0.55, 1],
        anchor='x4'
    ),
    xaxis=dict(
        domain=[0, 0.45]
    ),
    yaxis=dict(
        domain=[0, 0.45],
        anchor = 'x'
    ),
    xaxis2=dict(
        domain=[0.55, 1]
    )
)
fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='multiple-subplots')
'''
from os import getcwd, sep, listdir
import pandas as pd
import re
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import base64


with open("/Users/my/Desktop/MT/code/MasterThesis/heatmap/171130-MicroHeaterLayout-final/171130-MicroHeaterLayout-final.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
#add the prefix that plotly will want when using the string as source
encoded_image = "data:image/png;base64," + encoded_string

folder = 'heatmap'
model = '171130-MicroHeaterLayout-final'
opt = 'opt'

curpath = getcwd()+ sep + folder
dirs = [opt]

dfs = {}
r,c = 0,0
mint = 0
maxt = 0
for dir in dirs:
    p = curpath + sep + dir
    files = listdir(p)
    files.remove('.DS_Store')
    for name in files:
        filep = p + sep + name
        df = pd.read_csv(filep,delim_whitespace = True, header=None, names=['x','y','time'], dtype={'time': np.float64, 'y': np.int32, 'x': np.int32})
        rows, columns = df.x.max(), df.y.max()
        min,max = df.time.min(), df.time.max()
        if r==0 or r<rows:
            r = rows
        if c == 0 or c < columns:
            c = columns
        if maxt == 0 or maxt < max:
            maxt = max
        if mint == 0 or mint > min:
            mint = min
        dfs[name] = df
        print name
numplot = len(dfs)
titles = []
for i in range(1,numplot/2+1):
    t1 = 'original layer '+str(i)
    t2 = 'optimized layer '+str(i)
    titles.append(t1)
    titles.append(t2)
#fig = tools.make_subplots(rows=numplot/2, cols=2, subplot_titles=titles)

figrows = int(numplot/2)
print(np.maximum(1,2))
reg_d = re.compile('\d+')
tracex = range(1,r)
tracey = range(1,c)
imagelist = []
#traces = {}
traces = [0]*numplot
layoutlist = {}

for fname,df in dfs.items():
    pos = fname.split('.')[-2].split('_')[-1]
    name = fname.split('.')[-2].split('_')[0]
    dt = []
    dt = np.zeros((r+1,c+1))
    dt[df['x'].tolist(),df['y'].tolist()] = df['time'].tolist()
    if re.match('nonopt\d+', pos):
        layer_or = int(reg_d.findall(pos)[0])
        titleo = str(layer_or)+' original'
        no = str((layer_or-1)*2+1)
        if no != 1:
            axno = 'xaxis'+ str(no)
            ayno = 'yaxis'+ str(no)
            xid = 'x' + str(no)
            yid = 'y' + str(no)
        else:
            axno = 'xaxis'
            ayno = 'yaxis'
            xid = 'x'
            yid = 'y'
        trace = go.Heatmap(z=dt, x=tracex, y=tracey, zmin=mint, zmax=maxt, colorscale='Reds',xaxis=xid,
    yaxis=yid, opacity=0.8 )
        img = dict(
            source=encoded_image,
            xref=xid,
            yref=yid,
            x=0,
            y=c,
            sizex=r,
            sizey=c,
            sizing="stretch",
            opacity=1,
            layer="below")
        imagelist.append(img)
        posyend = 1 - np.maximum(0,round((layer_or-1)*(1.0-0.1*(figrows-1))/figrows+(layer_or-1)*0.1,2))
        posystart = 1-np.minimum(round(layer_or*(1.0-0.1*(figrows-1))/figrows+(layer_or-1)*0.1,2),1.0)
        layoutlist[ayno] = dict(domain=[posystart, posyend], anchor=xid)
        layoutlist[axno] = dict(domain=[0, 0.45], anchor=yid)
        traces[int(no)-1] = trace
        #fig.append_trace(trace, layer_or, 1)
    else:
        layer_op = int(reg_d.findall(pos)[0])
        titlep = str(layer_op) + ' optimization'
        no = str(layer_op * 2)
        if no != 1:
            axno = 'xaxis'+ str(no)
            ayno = 'yaxis'+ str(no)
            xid = 'x' + str(no)
            yid = 'y' + str(no)
        else:
            axno = 'xaxis'
            ayno = 'yaxis'
            xid = 'x'
            yid = 'y'

        trace = go.Heatmap(z=dt, x=tracex, y=tracey, zmin=mint, zmax=maxt, colorscale='Reds',xaxis=xid,
    yaxis=yid, opacity=0.8)
        img = dict(
            source=encoded_image,
            xref=xid,
            yref=yid,
            x=0,
            y=c,
            sizex=r,
            sizey=c,
            sizing="stretch",
            opacity=1,
            layer="below")
        imagelist.append(img)
        layoutlist[axno] = dict(domain=[0.55, 1],anchor = yid)
        posyend = 1-np.maximum(0, round((layer_op - 1) * (1.0 - 0.1 * (figrows - 1)) / figrows + (layer_op - 1) * 0.1,2))
        posystart = 1-np.minimum(round(layer_op * (1.0 - 0.1 * (figrows - 1)) / figrows + (layer_op - 1) * 0.1,2), 1.0)
        layoutlist[ayno] = dict(domain=[posystart, posyend], anchor = xid)
        traces[int(no)-1] = trace
        #fig.append_trace(trace, layer_op, 2)
layoutlist['images'] = imagelist
'''
fig['layout']['images'].update(source= encoded_image,
                  xref= "x",
                  yref= "y",
                  x= 0,
                  y= 90,
                  sizex= 90,
                  sizey= 90,
                  sizing= "stretch",
                  opacity= 0.5,
                  layer= "below")
'''
'''
for k,v in traces.items():
    d[int(k)]=v
'''

layout= go.Layout(layoutlist)
fig=go.Figure(data=traces,layout=layout)
py.plot(fig,filename = name )

''''xaxis': {'anchor': 'y', 'domain': [0.0, 0.45]},
               'xaxis2': {'anchor': 'y2', 'domain': [0.55, 1.0]},
               'xaxis3': {'anchor': 'y3', 'domain': [0.0, 0.45]},
               'xaxis4': {'anchor': 'y4', 'domain': [0.55, 1.0]},
               'xaxis5': {'anchor': 'y5', 'domain': [0.0, 0.45]},
               'xaxis6': {'anchor': 'y6', 'domain': [0.55, 1.0]},
               'xaxis7': {'anchor': 'y7', 'domain': [0.0, 0.45]},
               'xaxis8': {'anchor': 'y8', 'domain': [0.55, 1.0]},
               'yaxis': {'anchor': 'x', 'domain': [0.84375, 1.0]},
               'yaxis2': {'anchor': 'x2', 'domain': [0.84375, 1.0]},
               'yaxis3': {'anchor': 'x3', 'domain': [0.5625, 0.71875]},
               'yaxis4': {'anchor': 'x4', 'domain': [0.5625, 0.71875]},
               'yaxis5': {'anchor': 'x5', 'domain': [0.28125, 0.4375]},
               'yaxis6': {'anchor': 'x6', 'domain': [0.28125, 0.4375]},
               'yaxis7': {'anchor': 'x7', 'domain': [0.0, 0.15625]},
               'yaxis8': {'anchor': 'x8', 'domain': [0.0, 0.15625]}}'''