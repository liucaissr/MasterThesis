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
    yaxis=yid, opacity=0.6 )
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
    yaxis=yid, opacity=0.6)
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


layout= go.Layout(layoutlist)
fig=go.Figure(data=traces,layout=layout)
py.plot(fig,filename = name )
