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

ini='2020-06-01'
fin='2021-03-31'
vol='NevChillan'
tipoevs=['VT','LP','LV','TO','EX','TR']


t_index = pd.date_range(start=ini, end=fin, freq='D')
t_index_mes = pd.date_range(start=ini, end=fin, freq='M')
df = pd.DataFrame(gdb.extraer_eventos(inicio=ini,final=fin,volcan=vol))
df = df[df.tipoevento.isin(tipoevs)]
df.set_index('fecha',inplace=True)
df_count = df.groupby('tipoevento')['tipoevento'].resample('D').count().rename('numevs')

df_count = df_count.reset_index().set_index('fecha')


df_count_mes = df.groupby('tipoevento')['tipoevento'].resample('M').count().rename('numevs')
df_count_mes = df_count_mes.reset_index().set_index('fecha')

df_max = df.groupby('tipoevento')[['dr','ml']].resample('D').max()
df_max = df_max.reset_index().set_index('fecha')
df_max_mes = df.groupby('tipoevento')[['dr','ml']].resample('M').max()
df_max_mes = df_max_mes.reset_index().set_index('fecha')

fig = make_subplots(rows=3, cols=2,vertical_spacing=0.02,shared_xaxes='all',horizontal_spacing=0.075,
                        column_widths=[1,4])

fig.update_layout(template='seaborn')
i=0
for tipoev in tipoevs:
    M = df_count[df_count.tipoevento==tipoev]
    M = M.reindex(t_index).fillna(0)
    N = df_count_mes[df_count_mes.tipoevento==tipoev]
    N = N.reindex(t_index_mes).fillna(0)
    eM = df_max[df_max.tipoevento==tipoev]
    eN = df_max_mes[df_max_mes.tipoevento==tipoev]
    plot_numevs_dia = go.Scatter(x=M.index,y=M.numevs,name=tipoev,legendgroup=tipoev,marker_color=cols[i],marker_line_width = 0)
    plot_numevs_mes = go.Scatter(x=N.index,y=N.numevs,name=tipoev,legendgroup=tipoev,xperiod='M1',xperiodalignment='middle',
                                 showlegend=False,marker_color=cols[i])
    fig.add_trace(plot_numevs_dia,row=1,col=2)
    fig.add_trace(plot_numevs_mes,row=1,col=1)
    if tipoev in ['VT','HB']:
        plot_maxml_dia = go.Scatter(x=eM.index,y=eM.ml,mode='markers',name='M<sub>L</sub> '+tipoev,legendgroup='M<sub>L</sub> '+tipoev,marker_color=cols[i])
        plot_maxml_mes = go.Scatter(x=eN.index,y=eN.ml,mode='markers',name='M<sub>L</sub> '+tipoev,legendgroup='M<sub>L</sub> '+tipoev,marker_color=cols[i],
                                    xperiod='M1',xperiodalignment='middle',showlegend=False)
        fig.add_trace(plot_maxml_dia,row=2,col=2)
        fig.add_trace(plot_maxml_mes,row=2,col=1)
    else:
        plot_maxdr_dia = go.Scatter(x=eM.index,y=eM.dr,mode='markers',name='D<sub>R</sub> '+tipoev,legendgroup='D<sub>R</sub> '+tipoev,marker_color=cols[i])
        plot_maxdr_mes = go.Scatter(x=eN.index,y=eN.dr,mode='markers',name='D<sub>R</sub> '+tipoev,legendgroup='D<sub>R</sub> '+tipoev,marker_color=cols[i],
                                    xperiod='M1',xperiodalignment='middle',showlegend=False)
        fig.add_trace(plot_maxdr_dia,row=3,col=2)
        fig.add_trace(plot_maxdr_mes,row=3,col=1)
    i+=1

fig.update_yaxes(title_text='Ev/mes',row=1,col=1,rangemode='tozero')
fig.update_yaxes(title_text='Ev/día',row=1,col=2,rangemode='tozero')
fig.update_yaxes(title_text='Max M<sub>L</sub>/mes',row=2,col=1,rangemode='tozero')
fig.update_yaxes(title_text='Max M<sub>L</sub>/día',row=2,col=2,rangemode='tozero')
fig.update_yaxes(title_text='Max D<sub>R</sub>/mes',row=3,col=1,rangemode='tozero')
fig.update_yaxes(title_text='Max D<sub>R</sub>/día',row=3,col=2,rangemode='tozero')

fig.update_xaxes(range=[ini, fin])
fig.write_html('first_figure.html', auto_open=True)
