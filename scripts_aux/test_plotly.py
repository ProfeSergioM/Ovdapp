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

locale.setlocale(locale.LC_TIME, 'es_ES')
cols = plotly.colors.DEFAULT_PLOTLY_COLORS

ini='2021-01-01'
fin='2021-03-31'
vol='Villarrica'
tipoev='LP'


voldf =gdb.get_metadata_volcan(vol,rep='y')
voldf = voldf.drop_duplicates(subset='nombre', keep="first")
df = pd.DataFrame(gdb.extraer_eventos(inicio=ini,final=fin,volcan=vol,tipoevento=tipoev))
df.set_index('fecha',inplace=True)
t_index = pd.date_range(start=ini, end=fin, freq='D')
t_index_mes = pd.date_range(start=ini, end=fin, freq='M')
nrows=4
if tipoev=='HB':nrows=5
fig = make_subplots(rows=nrows, cols=1,vertical_spacing=0.02,shared_xaxes='all',horizontal_spacing=0.075)

df_count = df['zona'].resample('D').count().rename('numevs').reindex(t_index).fillna(0)
df_count = df_count.drop(df_count.index[-1])
plot_numevs_dia = go.Scatter(x=df_count.index,y=df_count,name='Eventos/día',legendgroup='MF',marker_color=cols[0],marker_line_width = 1,opacity=0.75)
fig.add_trace(plot_numevs_dia,row=1,col=1)



df_maxamp_dia = df['amplitud_ums'].resample('D').max().rename('maxamp').reindex(t_index).fillna(0)
plot_amp_evs = go.Scattergl(x=df.index,y=df.amplitud_ums,name='Amp/ev',legendgroup='Amp',marker_color=cols[1],mode='markers',marker_size=4)
plot_amp_evs_max_dia = go.Bar(x=df_maxamp_dia.index,y=df_maxamp_dia,name='Max Amp/día',legendgroup='Amp MF',offset=0.5,
                                  marker_color=cols[1],opacity=0.25,marker_line_width = 0)
fig.add_trace(plot_amp_evs,row=2,col=1)
fig.add_trace(plot_amp_evs_max_dia,row=2,col=1)
fig.update_yaxes(title_text='Ev/día',row=1,col=1,rangemode='tozero')
fig.update_yaxes(title_text='um/s',row=2,col=1,rangemode='tozero')

fig.update_yaxes(type="log",row=3,col=1)
import numpy as np
fig.update_yaxes(row=3,range=[np.log10(0.5),np.log10(20)],dtick=np.log10(2))
plot_freq_evs = go.Scattergl(x=df.index,y=df.frecuencia,name='Frec/ev',legendgroup='D<sub>R</sub>',marker_color=cols[2],mode='markers',marker_size=4,opacity=0.75)
fig.add_trace(plot_freq_evs,row=3,col=1)
fig.update_yaxes(title_text='Hz',row=3,col=1,rangemode='tozero')


if tipoev in ['VT','VD','HB']:
    mag='ml'
    maglabel='Magnitud'
    magaxis='M<sub>L</sub>'
else:
    mag='dr'
    maglabel='D<sub>R</sub>'
    magaxis='cm<sup>2</sup>'
    

df_maxene_dia = df[mag].resample('D').max().rename('max'+mag).reindex(t_index).fillna(0)
                   
plot_ene_evs_max_dia = go.Bar(x=df_maxene_dia.index,y=df_maxene_dia,name='Max '+maglabel+'/día',legendgroup=maglabel+' '+tipoev,offset=0.5,
                                  marker_color=cols[3],opacity=0.25,marker_line_width = 0)

fig.add_trace(plot_ene_evs_max_dia,row=4,col=1)
plot_dr_evs = go.Scattergl(x=df.index,y=df[mag],name=maglabel+'/ev',legendgroup=maglabel,marker_color=cols[3],mode='markers',marker_size=4,opacity=0.75)
fig.add_trace(plot_dr_evs,row=4,col=1)
fig.update_yaxes(title_text=magaxis,row=4,col=1,rangemode='tozero')

        
fig.update_layout(bargap=0)
fig.update_xaxes(range=[ini, fin])
fig.update_layout(
    title={
        'text': "Características de sismos "+tipoev+" clasificados, "+voldf.vol_tipocorto.iloc[0]+" "+voldf.nombre.iloc[0],
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
fig.write_html('first_figure.html', auto_open=True)