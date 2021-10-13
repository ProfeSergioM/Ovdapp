# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 11:51:12 2021

@author: sergio.morales
"""


import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly
import locale
import numpy as np

locale.setlocale(locale.LC_TIME, 'es_ES')
ini='2021-01-01'
fin='2021-03-31'
vol='NevChillan'

def getEventos(ini,fin,vol):
    evs_blacklist=['IC','ZZ','AV','VA','MI','RY','MF','EX','RE']
    orderev = ['LP','TR','TO','HB','VLP','VT','VD']
    t_index = pd.date_range(start=ini, end=fin, freq='D')
    voldf =gdb.get_metadata_volcan(vol,rep='y')
    voldf = voldf.drop_duplicates(subset='nombre', keep="first")
    df_evs = pd.DataFrame(gdb.extraer_eventos(inicio=ini,final=fin,volcan=vol))
    df_evs['tipoevento'] = df_evs['tipoevento'].replace({'LV':'VLP'})
    cat = pd.api.types.CategoricalDtype(categories=orderev, ordered=True)
  
    if len(df_evs)>0:
        df_evs = df_evs[~df_evs.tipoevento.isin(evs_blacklist)]
        df_evs['tipoevento'] = df_evs['tipoevento'].astype(cat)
        df_evs.set_index('fecha',inplace=True)
        df_evs['volcan']=vol
        
    count_evs = []
    
    for tipoev in df_evs.tipoevento.unique():
        df2 = df_evs[df_evs.tipoevento==tipoev]
        df2 = df2.resample('D').count()[['zona']].rename(columns={'zona':tipoev+'/dia'})
        df2 = df2.reindex(t_index).fillna(0)
        count_evs.append(df2)
    dfCountEvs = pd.concat(count_evs,axis=1)
    dfEvs= df_evs
    return dfEvs,dfCountEvs

dfEvs,dfCountEvs = getEventos(ini, fin, vol)

        
import ovdas_figure_lib as ffig
nrows=np.shape(dfCountEvs)[1]   
nrows=nrows+2 #row de ML y de DR
     
fig = make_subplots(rows=nrows, cols=1,vertical_spacing=0.02,shared_xaxes='all',horizontal_spacing=0.075)
colorgraficas='rgba(225,183,29,1)'
i=1
for tipoev in dfCountEvs.columns: 
    etiquetacolor=tipoev[:2]
    if tipoev=='VLP/dia':etiquetacolor='LV'

    colorcla='#'+ffig.colores_cla_hex(etiquetacolor)[:-2]
    ejex = dfCountEvs[tipoev].index
    ejey = dfCountEvs[tipoev]
    trace_num=go.Bar(x=ejex,y=ejey,
                opacity=1,name=tipoev,legendgroup='group1',width=1000*3600*24,showlegend=False,marker= { "color" : colorgraficas})
    fig.append_trace(trace_num,i,1)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(ejey),font=dict(color=colorcla),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                            yref='y'+str(i),text=tipoev,showarrow=False))
    
    i+=1

#ML
for tipoev in dfEvs.tipoevento.unique(): 
    etiquetacolor=tipoev[:2]
    if tipoev=='VLP':etiquetacolor='LV'
    df=dfEvs[dfEvs.tipoevento==tipoev]    
    plotMl =  go.Scattergl(x=df.index,y=df['ml'],name='ML '+tipoev,
                        mode='markers',marker_size=5,showlegend=False,
                        opacity=0.75,marker= { "color" : '#'+ffig.colores_cla_hex(etiquetacolor)[:-2]})
    fig.append_trace(plotMl,i,1)
    if tipoev in ['VLP','HB','LP','TO']:
        plotDr =  go.Scattergl(x=df.index,y=df['dr'],name='DR '+tipoev,
                            mode='markers',marker_size=5,showlegend=False,
                            opacity=0.75,marker= { "color" : '#'+ffig.colores_cla_hex(etiquetacolor)[:-2]})
        fig.append_trace(plotDr,i+1,1)
fig.add_annotation(go.layout.Annotation(x=0.01,y=np.nanmax(dfEvs['ml']),font=dict(color='white'),
                                        xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                        yref='y'+str(i),text='Mag.',showarrow=False))
fig.add_annotation(go.layout.Annotation(x=0.01,y=np.nanmax(dfEvs['dr']),font=dict(color='white'),
                                        xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                        yref='y'+str(i+1),text='DR',showarrow=False))
fig.update_yaxes(title_text="<b>ML</b>", row=i)
fig.update_yaxes(title_text="<b>cm*cm</b>", row=i+1)

    
fig.layout.template = 'plotly_dark'
fig.write_html('first_figure.html', auto_open=True)