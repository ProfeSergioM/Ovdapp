# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 19:34:17 2020

@author: sergio
"""
import sys
sys.path.append('//172.16.40.102/Monitoreo/Ovdas_pyLib/ovdapp/')
import get_data_lib as gdl
import ovdas_getfromdb_lib as gdb
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from pyproj import Proj
myProj = Proj("+proj=utm +zone=19S, +south +ellps=WGS84 +datum=WGS84 +units=km +no_defs")

volcan ='Copahue'
ini= '2018-01-01'
fin= '2021-05-11'
tipoev='VT'
mlmin=0
df = gdl.get_comparison_loc(volcan, ini, fin,tipoev,mlmin)

df['lonUTM_hypo']=myProj(df.longitud,df.latitud)[0]
df['latUTM_hypo']=myProj(df.longitud,df.latitud)[1]
df['lonUTM_NLL']=myProj(df.lonN,df.latN)[0]
df['latUTM_NLL']=myProj(df.lonN,df.latN)[1]
df =df.reset_index()
df['diflat']=df['latUTM_NLL']-df['latUTM_hypo']
df['diflon']=df['lonUTM_NLL']-df['lonUTM_hypo']
df['difpro']=df['profN']-df['profH']


esta_meta = gdb.get_metadata_wws(volcan)
esta_meta = esta_meta[esta_meta.tipo=='SISMOLOGICA']
esta_meta['tiposism'] = esta_meta.cod.str[0]
esta_meta = esta_meta[esta_meta.tiposism=='S']
esta_meta['lonUTM']=myProj(esta_meta.longitud,esta_meta.latitud)[0]
esta_meta['latUTM']=myProj(esta_meta.longitud,esta_meta.latitud)[1]

volcanes =gdb.get_metadata_volcan(volcan,rep='y')
voldf = volcanes.drop_duplicates(subset='nombre', keep="first")
voldf['lonUTM']=myProj(voldf.longitud,voldf.latitud)[0]
voldf['latUTM']=myProj(voldf.longitud,voldf.latitud)[1] 
#%%
fig = make_subplots(rows=9, cols=2,shared_xaxes=True,subplot_titles=['Localizaciones','Diferencias en Localización'],
                    specs=[
                               [{"rowspan":6},{"rowspan":3}],
                               [None,None],
                               [None,None],
                               [None,{"rowspan":3}],
                               [None,None],
                               [None,None],
                               [{"rowspan":3},{"rowspan":3}],
                               [None,None],
                               [None,None]
                           ],print_grid=True)

lonlat_hypo = go.Scattergl(x=df['lonUTM_hypo'],y=df['latUTM_hypo'],name='Hypo71',mode='markers',opacity=0.5,legendgroup='group1',marker_color='#7b85d4')
lonlat_NLL = go.Scattergl(x=df['lonUTM_NLL'],y=df['latUTM_NLL'],name='NLL',mode='markers',opacity=0.5,legendgroup='group2',marker_color='#f37738')
red = go.Scattergl(x=esta_meta['lonUTM'],y=esta_meta['latUTM'],mode='markers',marker_symbol='triangle-up',marker_color='red',name='Estación',marker_size=10)
volcan = go.Scattergl(x=voldf['lonUTM'],y=voldf['latUTM'],mode='markers',marker_symbol='star',marker_color='red',name='Estación',marker_size=10)

fig.add_trace(lonlat_hypo,row=1,col=1)
fig.add_trace(lonlat_NLL,row=1,col=1)
fig.add_trace(red,row=1,col=1)

fig.update_yaxes(scaleanchor = "x",scaleratio = 1,row=1,col=1)
fig.update_yaxes(row=1,col=1,tickformat='int',title='Northing UTM (km)')
fig.update_xaxes(row=7,col=1,tickformat='int',title='Easting UTM (km)')

lonprof_hypo = go.Scattergl(x=df['lonUTM_hypo'],y=df['profN'],name='Hypo71',mode='markers',opacity=0.5,legendgroup='group1',showlegend=False,marker_color='#7b85d4')
fig.add_trace(lonprof_hypo,row=7,col=1)

lonprof_NLL = go.Scattergl(x=df['lonUTM_NLL'],y=df['profN'],name='Hypo71',mode='markers',opacity=0.5,legendgroup='group2',showlegend=False,marker_color='#f37738')
fig.add_trace(lonprof_NLL,row=7,col=1)

diflon = go.Scattergl(x=df.index,y=df.diflat,mode='lines',name='Δ N (NLL-Hypo)')
#diflon = go.Bar(x=df.index,y=df.diflat,bargap=0)
fig.add_trace(diflon,row=1,col=2)

diflon = go.Scattergl(x=df.index,y=df.diflon,mode='lines',name='Δ E (NLL-Hypo)')
fig.add_trace(diflon,row=4,col=2)

difpro = go.Scattergl(x=df.index,y=df.difpro,mode='lines',name='Δ Z (NLL-Hypo)')
fig.add_trace(difpro,row=7,col=2)

fig.update_yaxes(range=[min(df['profH'].min(),df['profN'].min()), max(df['profH'].max(),df['profN'].max())],row=7,col=1,autorange='reversed',title='Profundidad (km)')

fig.update_yaxes(title='Δ N (km)',col=2,row=1)
fig.update_yaxes(title='Δ E (km)',col=2,row=4)
fig.update_yaxes(title='Δ Z (km)',col=2,row=7)

fig.update_xaxes(title='Evento',col=2,row=7)

fig.update_layout(template='plotly_dark',title='Visor de diferencias en algoritmos de localización NonLinLoc vs Hypo71 - '+volcan)
fig.write_html('first_figure.html', auto_open=True)