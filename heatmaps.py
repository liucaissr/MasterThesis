from os import getcwd, sep, listdir
import pandas as pd
import re
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np

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
fig = tools.make_subplots(rows=numplot/2, cols=2, subplot_titles=titles)

reg_d = re.compile('\d+')
tracex = range(1,r)
tracey = range(1,c)


for fname,df in dfs.items():
    pos = fname.split('.')[-2].split('_')[-1]
    name = fname.split('.')[-2].split('_')[0]
    dt = []
    dt = np.zeros((r+1,c+1))
    dt[df['x'].tolist(),df['y'].tolist()] = df['time'].tolist()
    if re.match('nonopt\d+', pos):
        layer_or = int(reg_d.findall(pos)[0])
        titleo = str(layer_or)+' original'
        trace = go.Heatmap(z=dt, x=tracex, y=tracey, zmin=mint, zmax=maxt, colorscale='Reds')
        fig.append_trace(trace, layer_or, 1)
    else:
        layer_op = int(reg_d.findall(pos)[0])
        titlep = str(layer_op) + ' optimization'
        trace = go.Heatmap(z=dt, x=tracex, y=tracey, zmin=mint, zmax=maxt, colorscale='Reds')
        fig.append_trace(trace, layer_op, 2)


fig['layout'].update(title=name)
py.plot(fig,filename = name )