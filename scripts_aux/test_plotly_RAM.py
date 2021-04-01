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
vol='Villarrica'
per='M'
tipoevs_custom=['VT','MF']
###############
fi = dt.datetime.strftime((dt.datetime.utcnow() - dt.timedelta(days=366)).replace(day=1,minute=0,second=0,microsecond=0),'%Y-%m-%d')
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

'''
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


import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ovdas_figure_lib as ffig

fig = make_subplots(rows=len(tipoevs)*2, cols=2,vertical_spacing=0.025,shared_xaxes='all',horizontal_spacing=0.05,
                    column_widths=[1,4],print_grid=True,subplot_titles=['Conteo de eventos/<br>Energía máxima mensual',
                                                                        'Conteo de eventos diario/Energía máxima diaria'])
fig.update_layout(template='seaborn')
for r in range(0,len(tipoevs)):
    
    tipoev = tipoevs[r]
    if tipoev in ['VT','VD']:
        ene='ml'
        enet='M<sub>L</sub>'
        enem='%{y}'
    else:
        ene='dr'
        enet='D<sub>R</sub>'
        enem='%{y:.1f} cm<sup>2</sup>'
    df_dia = diario.loc[tipoev]
    df_mes = mensual.loc[[tipoev]][tipoev]
    df_mes = df_mes.reindex(t_index)
    df_dia = df_dia.reindex(t_index)
    df_mes.index = pd.to_datetime(df_mes.index)
    df_mes.index = df_mes.index.strftime('%d de %B de %Y')
    df_dia.index = df_mes.index

    fig.add_trace(go.Bar(x=df_mes.index, y=df_mes,name=tipoev+'/mes',width=28,marker_color='#2b7bba',
                         text=df_mes.index.str.slice(6, 50),
                         hovertemplate='%{text} - '+enem+' evs'), row=(2*r)+1, col=1) 
    fig.update_yaxes(title_text='ev/mes',fixedrange=True, row=(2*r)+1,col=1)
    fig.update_yaxes(range=[0,df_mes.max()*1.7], row=(2*r)+1,col=1)
    fig.update_xaxes(range=[min(df_mes.index),max(df_mes.index)])
    fig.add_trace(go.Bar(x=df_dia.index, y=df_dia.eventos,name=tipoev+'/día',width=1,marker_color='#2b7bba'), row=(2*r)+1, col=2) 
    fig.update_yaxes(title_text='ev/día',fixedrange=True,title=dict(standoff=0), row=(2*r)+1,col=2)
    fig.update_yaxes(range=[0,df_dia.eventos.max()*1.7], row=(2*r)+1,col=2)
    

    df_ev = df2[df2.tipoevento==tipoev]
    df_ev = df_ev.resample('BMS')[ene].max()
    df_ev = df_ev.reindex(t_index)
    df_ev.index = df_mes.index

    df_ev2 = df2[df2.tipoevento==tipoev]
    df_ev2 = df_ev2.resample('D')[ene].max()
    df_ev2 = df_ev2.reindex(t_index)
    df_ev2.index = df_mes.index
    
    fig.add_trace(go.Scatter(x=df_ev2.index, y=df_ev2,name='Max '+enet+'/mes',mode='lines+markers',connectgaps=True,
                             text=df_ev.index.str.slice(6, 50),
                             marker=dict(color='red', size=5,opacity=0.5),
                             line=dict(color='#2b7bba', width=2,
                              ),
                         hovertemplate='%{text} - '+enem), row=(2*r)+2, col=2)     
    fig.update_yaxes(title_text='Max '+enet+'/mes',fixedrange=True, row=(2*r)+2,col=1)
    
    fig.add_trace(go.Scatter(x=df_ev.index, y=df_ev,name='Max '+enet+'/mes',mode='lines+markers',connectgaps=True,
                             text=df_ev.index.str.slice(6, 50),
                             marker=dict(color='red', size=10,opacity=0.5),
                             line=dict(color='#2b7bba', width=2,
                              ),
                         hovertemplate='%{text} - '+enem), row=(2*r)+2, col=1) 
    fig.update_yaxes(title_text='Max '+enet+'/día',fixedrange=True, row=(2*r)+2,col=2)
    axesnum = str((4*r)+1)
    fig.add_annotation(x=0,y=df_mes.max()*1.5,
                       xref='paper',yref='y'+axesnum,
                       text=tipoev ,
        showarrow=False,
        font=dict(

            size=16,
            color='black'
            ),
        align="center",
        bordercolor='#'+ffig.colores_cla_hex(tipoev)[:-2],
        borderwidth=2,
        borderpad=4,
        bgcolor='white',
        opacity=0.8)
    if axesnum=='1':axesnum=''
    fig.add_annotation(x=df_mes[df_mes==df_mes.max()].index[0],y=df_mes.max()*1.1,
        xref='x'+axesnum,yref='y'+axesnum,text='<b> '+str(int(df_mes.max()))+'</b>' ,
        showarrow=False,font=dict(family="Roboto",size=18,color="#000000"),
        align="center",opacity=0.8,        bordercolor='#'+ffig.colores_cla_hex(tipoev)[:-2],
        borderwidth=0,
        borderpad=0.5,
        bgcolor='white')
    
    fig.add_annotation(x=df_mes[df_mes==df_mes.max()].index[0],y=df_mes.max()*1.1,
        xref='x'+axesnum,yref='y'+axesnum,text='<b> '+str(int(df_mes.max()))+'</b>' ,
        showarrow=False,font=dict(family="Roboto",size=18,color="#000000"),
        align="center",opacity=0.8,        bordercolor='#'+ffig.colores_cla_hex(tipoev)[:-2],
        borderwidth=0,
        borderpad=0.5,
        bgcolor='white')
    
    
    axesnum = str((4*r)+2)
    fig.add_annotation(x=df_dia[df_dia.eventos==df_dia.eventos.max()].index[0],y=df_dia.eventos.max()*1.1,
        xref='x'+axesnum,yref='y'+axesnum,text='<b> '+str(int(df_dia.eventos.max()))+'</b>' ,
        showarrow=False,font=dict(family="Roboto",size=18,color="#000000"),
        align="center",opacity=0.8,        bordercolor='#'+ffig.colores_cla_hex(tipoev)[:-2],
        borderwidth=0,
        borderpad=0.5,
        bgcolor='white')
    
    axesnum = str((4*r)+3)
    fig.add_annotation(x=df_ev[df_ev==df_ev.max()].index[0],y=df_ev.max()*1.1,
        xref='x'+axesnum,yref='y'+axesnum,text='<b> '+str(int(df_ev.max()))+'</b>' ,
        showarrow=False,font=dict(family="Roboto",size=18,color="#000000"),
        align="center",opacity=0.8,        bordercolor='#'+ffig.colores_cla_hex(tipoev)[:-2],
        borderwidth=0,
        borderpad=0.5,
        bgcolor='white')

    axesnum = str((4*r)+4)
    fig.add_annotation(x=df_ev2[df_ev2==df_ev2.max()].index[0],y=df_ev2.max()*1.1,
        xref='x'+axesnum,yref='y'+axesnum,text='<b> '+str(int(df_ev2.max()))+'</b>' ,
        showarrow=False,font=dict(family="Roboto",size=18,color="#000000"),
        align="center",opacity=0.8,        bordercolor='#'+ffig.colores_cla_hex(tipoev)[:-2],
        borderwidth=0,
        borderpad=0.5,
        bgcolor='white')


which_idxs = lambda m, n: np.rint( np.linspace( 1, n, min(m,n) ) - 1 ).astype(int)
evenly_spaced = np.array( df_mes.index )[which_idxs(6,len(df_mes.index))]

evenly_spaced2 = np.array( df_mes.index )[which_idxs(int(len(df_mes.index)/10),len(df_mes.index))]

out = [x[6:9]+'-'+x[-2:] for x in list(evenly_spaced)]

fig.update_xaxes(tickfont=dict(size=12),tickmode='array',tickvals=evenly_spaced,ticktext=out,tickangle=60, row=(2*r)+2,col=1)

out2 = [x[0:9]+'-'+x[-2:] for x in list(evenly_spaced2)]

fig.update_xaxes(tickfont=dict(size=12),tickmode='array',tickvals=evenly_spaced2,ticktext=out2,tickangle=60, row=(2*r)+2,col=2)               
fig.update_layout(showlegend=False)
fig.update_layout(
  margin=go.layout.Margin(
        l=0, #left margin
        r=0, #right margin
        b=0, #bottom margin

    )
)

fig.update_xaxes(range=[0,len(t_index)],col=1,row=(2*r)+2)
fig.update_layout(
    font=dict(
        family="Tahoma",
        size=18,
        ),
    title={
        'text': "Resumen de actividad mensual - "+voldata.vol_tipo.iloc[0]+' '+voldata.nombre.iloc[0],
        'y':0.97,
        'x':0.5,
        
        'xanchor': 'center',
        'yanchor': 'top'})
fig.write_html('first_figure.html', auto_open=True)
'''