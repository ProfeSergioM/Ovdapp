# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 19:34:17 2020

@author: sergio
"""
import sys
sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
import ovdas_getfromdb_lib as gdb
import datetime as dt
import pandas as pd
#variables
vol='Llaima'
per='M'
tipoevs_custom=['VT','LP']
###############
fi = dt.datetime.strftime((dt.datetime.utcnow() - dt.timedelta(days=366)),'%Y-%m-%d')
ff = dt.datetime.strftime(dt.datetime.utcnow(),'%Y-%m-%d')
t_index = pd.date_range(start=fi, end=ff, freq='D')
voldata = gdb.get_metadata_volcan(vol)
voldata = voldata.drop_duplicates(subset='nombre', keep="first")
esta_meta = gdb.get_metadata_wws(vol) 
df_x_ev=[]
for tipo in tipoevs_custom:
    df = gdb.extraer_eventos(inicio=fi,final=ff,volcan=vol,tipoEvento=tipo)
    df = pd.DataFrame(df)
    df_x_ev.append(df)
df_x_ev = pd.concat(df_x_ev)
tipoevs = df_x_ev.tipoevento.unique() 
if 'MF' in tipoevs:
    df_x_ev['PAr'] = (df['est'].map(esta_meta.set_index('idestacion')['sens1'])*
                 df['est'].map(esta_meta.set_index('idestacion')['distcrater'])*df['amplitudctas']/1000000)
df_x_ev.loc[df_x_ev.tipoevento != 'MF', 'PAr'] = None
del df

diario = {}
mensual = {}

for tipoev in tipoevs:
    dia =gdb.extraer_eventos_dia(inicio=fi,final=ff,volcan=vol,tipoevento=tipoev) 
    dia = pd.DataFrame.from_dict(dia)
    if len(dia)>0:
        dia = dia.reset_index().set_index('dia')
        dia.index = pd.to_datetime(dia.index)
        dia = dia.loc[~dia.index.duplicated(keep='first')]
        mes = dia.resample(per)['eventos'].sum()
        if per=='M':
            mes.index = mes.index.map(lambda t: t.replace(day=1))
        else:
            mes.index = mes.index+dt.timedelta(days=15)
        diario[tipoev]=dia
        mensual[tipoev]=mes
    else:
        print("Sin eventos "+tipoev+" para el periodo")
diario = pd.concat(diario,sort='False')
tipoevs = diario.eventos.unstack(level=0).columns.tolist()
num_tipoev = len(tipoevs)*2
mensual = pd.concat(mensual,sort='False')
#maximo ML-DR por dia
df2 = df_x_ev.reset_index().set_index('fecha')
max_e_dia={}
max_e_mes={}
for tipoev in tipoevs:
    if tipoev in ['VT','VD','HB']:
        param = 'ml'
    elif tipoev =='MF':
        param = 'PAr'
    elif tipoev in ['TO','LP','LV','EX','TR']:
        param= 'dr'
    else:
        param= 'amplitudctas'
    max_e_dia[tipoev] = df2[df2.tipoevento==tipoev].resample('D')[param].max()
    max_e_mes[tipoev] = df2[df2.tipoevento==tipoev].resample(per)[param].max()
    if per=='M':
        max_e_mes[tipoev].index = max_e_mes[tipoev].index.map(lambda t: t.replace(day=1))
    else:
        max_e_mes[tipoev].index = max_e_mes[tipoev].index+dt.timedelta(days=15)
    
max_e_dia = pd.concat(max_e_dia)
max_e_mes = pd.concat(max_e_mes)  

#%%
#import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import locale
import numpy as np
locale.setlocale(locale.LC_TIME, 'es_ES')
titulos = list(np.full(4*2-2,''))
titulos= ["Conteo eventos/Energía máxima<br>(M<sub>L</sub> o D<sub>R</sub>) mensual",
          "Conteo de eventos x día /Energía (M<sub>L</sub> o D<sub>R</sub>) de cada evento"]+titulos


#%%
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(rows=len(tipoevs)*2, cols=2,vertical_spacing=0,shared_xaxes='all',column_widths=[1,4],print_grid=True)
fig.update_layout(template='seaborn')
for r in range(0,len(tipoevs)):
    tipoev = tipoevs[r]
    df_mes = mensual.loc[[tipoev]][tipoev]
    df_mes = df_mes.reindex(t_index)
    df_dia = diario.loc[tipoev]
    fig.add_trace(go.Bar(x=df_mes.index, y=df_mes,name=tipoev+'/mes',width=1000 * 3600 * 24 * 29,marker_color='#2b7bba'), row=(2*r)+1, col=1) 
    fig.update_yaxes(title_text=tipoev+'/mes', row=(2*r)+1,col=1)
    fig.add_trace(go.Bar(x=df_dia.index, y=df_dia.eventos,name=tipoev+'/día',width=1000 * 3600 * 24 * 1), row=(2*r)+1, col=2) 
    fig.update_yaxes(title_text=tipoev+'/día', row=(2*r)+1,col=2)
    axesnum = str((4*r)+1)
    if axesnum=='1':axesnum=''

    fig.add_annotation(x=df_mes[df_mes==df_mes.max()].index.to_pydatetime()[0],y=df_mes.max()*1.2,
        xref='x'+axesnum,
        yref='y'+axesnum,

        text='<b> '+str(int(df_mes.max()))+'</b>' ,
        showarrow=False,

        font=dict(
            family="Roboto",
            size=18,
            color="#000000"
            ),
        align="center",
        opacity=0.8
        )

fig.write_html('first_figure.html', auto_open=True)