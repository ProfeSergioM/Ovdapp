import sys
import os
sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
#import ovdas_reportes_scripts as reportes
import ovdas_getfromdb_lib as gdb
import ovdas_figure_lib as ffig
import ovdas_WWS_lib as wws
import ovdas_SeismicProc_lib as sp
import datetime as dt
import ovdas_ovdapp_lib as oap



ejex =10 #minutos en el eje x
from datetime import timedelta
import pandas as pd
import numpy as np
fini = dt.datetime.utcnow() - dt.timedelta(hours=1)
ffin = dt.datetime.utcnow()
subsample=10
finiround = fini - (fini -fini.min) % timedelta(minutes=ejex)
ffinround = ffin + (ffin.min - ffin) % timedelta(minutes=ejex)-timedelta(milliseconds=100)
detect_count,detect = oap.get_pickle_OVV('Villarrica',finiround,ffinround)
traza = wws.extraer_signal(estacion='VN2',componente='Z',inicio=fini,fin=ffin)
traza = sp.filtrar_traza(traza,tipo="butter",orden=4,fi=0.4,ff=12)


t_index = pd.date_range(start=finiround, end=ffinround, freq='100ms').round('100ms')
times = []
amps = []
for i in range(0,len(traza)):
    times.extend(traza[i].times('timestamp'))
    amps.extend(traza[i].data*traza[i].stats.calib)
times = np.around(times,2)
amps = np.around(amps,2)
df_traza = pd.DataFrame(amps,index=times)
df_traza = df_traza[::subsample]
df_traza['fecha_abs'] = pd.to_datetime(df_traza.index, unit='s')
df_traza = df_traza.set_index('fecha_abs',drop=True)
df_traza.index = df_traza.index.round('100ms')
aer = df_traza.reindex(t_index)
aer.index = aer.index.rename('fecha')
aer = aer.rename(columns={0:'amp'})
grp = aer.groupby(pd.Grouper(freq='10Min'))

filas = []
for key, df in grp:
    filas.append(df)
#%%
import plotly.graph_objects as go
from plotly.subplots import make_subplots


fig = make_subplots(rows=len(filas), cols=1,vertical_spacing=0)


maxy = abs(max(amps))*1.5
for i in range(0,len(filas)):
    evs = detect[detect.index.to_series().between(min(filas[i].index),max(filas[i].index))]
    alertaplot = go.Scattergl(x=filas[i].index
                              ,y=filas[i].amp,
                              showlegend=False,
                              hoverinfo='x+y',
                              line=dict(color='rgba(66,155,245,1)'))
    fig.append_trace(alertaplot,i+1,1)
    fig.update_xaxes(showticklabels=False,range=[min(filas[i].index),max(filas[i].index)],row=i+1)
    fig.update_yaxes(row=i,range=[-maxy,maxy])
    
    for index,row in evs.iterrows():
        lev = go.Scatter(x=[index,index],y=[-maxy,maxy],showlegend=False,hoverinfo='x',line=dict(color='rgba(66,155,245,1)'))
        fig.append_trace(lev,i+1,1)
    
fig.update_yaxes(row=i+1,range=[-maxy,maxy])  
fig.update_xaxes(row=i+1,tickformat="%H:%M",showticklabels=True)  
fig.layout.template = 'plotly_dark'
fig.update_layout(bargap=0,margin={"r":1,"t":25,"l":1,"b":1},
title={
'text':'Sismograma - Última Hora - VN2',
'y':0.99,
'x':0.5,
'xanchor':'center',
'yanchor':'top'
}
)
fig.write_html('first_figure.html', auto_open=True)
    