import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import matplotlib.pyplot as plt
import ovdas_doc_lib as odl
import ovdas_figure_lib as ffig
import ovdas_WWS_lib as waves
from datetime import timedelta
vol='Villarrica'
fi,ff='2021-01-01','2021-03-31'
tipoevs_custom=['MF','LP']
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_getfromdb_lib as gdb
voldf =gdb.get_metadata_volcan(vol,rep='y')
voldf = voldf.drop_duplicates(subset='nombre', keep="first")
import plotly
cols = plotly.colors.DEFAULT_PLOTLY_COLORS
#import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import locale
import numpy as np

t_index = pd.date_range(start=fi, end=ff, freq='D')
t_index_mes = pd.date_range(start=fi, end=ff, freq='M')
df = pd.DataFrame(gdb.extraer_eventos(inicio=fi,final=ff,volcan=vol))
df = df[df.tipoevento.isin(tipoevs_custom)]
df.set_index('fecha',inplace=True)
esta_meta = gdb.get_metadata_wws(volcan=vol)



df['amplitud_ums_old'] = df['est'].map(esta_meta.drop_duplicates('idestacion').set_index('idestacion')['sens1'])*df['amplitudctas']
df['amplitud_ums'] = df['amplitud_ums'].fillna(df['amplitud_ums_old'])
df['Par'] = df['est'].map(esta_meta.drop_duplicates('idestacion').set_index('idestacion')['distcrater'])*df['amplitud_ums']
df.loc[df.tipoevento != 'MF', 'Par'] = None 

'''
def RAM_bar(df,fi,ff):
    
    def colores_cla(tipoev):
        DICT_COL={
        'VT':	'#ff0000',
        'VD': 	'#ff00ff',
        'LP':	'#ffff00',
        'LV':	'#aaaa00',
        'TR':	'#00ffff',
        'TO':	'#636300',
        'HB': 	'#ff8c00',
        'AV':	'#96ff96',
        'IC':	'#00ff00',
        'RY':	'#00af00',
        'EX':	'#006300',
        'MI':	'#b500cc',
        'BG':	'#0000ff',
        'VA':	'#636363',
        'RE':	'#afafaf',
        'ZZ':	'#ff6363',
        'MF': 	'#ffbf00'
            }
        color= DICT_COL[tipoev]
        return color
    df_count = df.groupby('tipoevento')['tipoevento'].resample('D').count().rename('numevs')
    
    df_count = df_count.reset_index().set_index('fecha')
    
    
    df_count_mes = df.groupby('tipoevento')['tipoevento'].resample('M').count().rename('numevs')
    df_count_mes = df_count_mes.reset_index().set_index('fecha')
    
    df_max = df.groupby('tipoevento')[['dr','ml','Par']].resample('D').max()
    df_max = df_max.reset_index().set_index('fecha')
    df_max_mes = df.groupby('tipoevento')[['dr','ml','Par']].resample('M').max()
    df_max_mes = df_max_mes.reset_index().set_index('fecha')   
    
    orderev = ['VT','VD','LP','EX','TR','TO','HB','LV','MF']
    cat = pd.api.types.CategoricalDtype(categories=orderev, ordered=True)
    df.loc[:,'tipoevento'] = df['tipoevento'].astype(cat)
    df.sort_values(by='tipoevento',inplace=True)
    
    tipoevs_custom=df.tipoevento.unique()
    rows=len(tipoevs_custom)*2
        
        
    if ('VT' or 'VD') in tipoevs_custom:
        row_ml=2
        if ('LP' or 'TR' or 'EX' or 'HB' or 'TO' or 'LV') in tipoevs_custom:
            row_dr=3
            if 'MF' in tipoevs_custom:
                row_mf=4
        elif 'MF' in tipoevs_custom:
            row_mf=3
    elif ('LP' or 'TR' or 'EX' or 'HB' or 'TO' or 'LV') in tipoevs_custom:
        row_dr=2
        if 'MF' in tipoevs_custom:
            row_mf=3
    elif 'MF' in tipoevs_custom:
        row_mf=2
        
            
    fig = make_subplots(rows=rows, cols=2,vertical_spacing=0.02,shared_xaxes='all',horizontal_spacing=0.075,
                        subplot_titles=['Mensual','Diario']+list(np.full((2*3)-2,'')),
                            column_widths=[1,4])
    
    
    fig.update_layout(template='seaborn')
    i=1
    j=0
    for tipoev in tipoevs_custom:

        dfev = df[df.tipoevento==tipoev]
        if tipoev in ['VT','VD','HB']:
            mag='ml'
            maglabel='M<sub>L</sub>'
            magaxis='M<sub>L</sub>'
        elif tipoev=='MF':
            mag='Par'
            maglabel='Pa<sub>R</sub>'
            magaxis='Pa<sub>R</sub>'            
        else:
            mag='dr'
            maglabel='D<sub>R</sub>'
            magaxis='cm<sup>2</sup>'
        M = df_count[df_count.tipoevento==tipoev]
        M = M.reindex(t_index).fillna(0)
        N = df_count_mes[df_count_mes.tipoevento==tipoev]
        N = N.reindex(t_index_mes).fillna(0)
        eM = df_max[df_max.tipoevento==tipoev]
        eN = df_max_mes[df_max_mes.tipoevento==tipoev]
        plot_numevs_dia = go.Bar(x=M.index,y=M.numevs,name=tipoev,legendgroup=tipoev,marker_color=cols[0],marker_line_width = 0,offset=0.5,showlegend=False)
        plot_numevs_mes = go.Bar(x=N.index,y=N.numevs,name=tipoev,legendgroup=tipoev,xperiod='M1',xperiodalignment='middle',offset=0.5,
                                     showlegend=False,marker_color=cols[0])
        fig.add_trace(plot_numevs_dia,row=i,col=2)
        fig.add_trace(plot_numevs_mes,row=i,col=1)
        
    

        plot_ene_dia = go.Scattergl(x=dfev.index,y=dfev[mag],mode='markers',name=maglabel+' '+tipoev,marker_size=3,
                                       legendgroup='M<sub>L</sub> '+tipoev,marker_color=cols[i],showlegend=False)
        
        plot_maxene_dia = go.Bar(x=eM.index,y=eM[mag],name='Max '+maglabel+' '+tipoev,offset=0.5,opacity=0.5,width=1000 * 3600 * 24,
                                       legendgroup='M<sub>L</sub> '+tipoev,marker_color=cols[0],showlegend=False)
        
        plot_maxene_mes = go.Scattergl(x=eN.index,y=eN[mag],mode='markers+lines',name=maglabel+' '+tipoev,
                                       legendgroup='M<sub>L</sub> '+tipoev,marker_color=cols[i],line_color=cols[0],
                                    xperiod='M1',xperiodalignment='middle',showlegend=False)
        
        fig.add_trace(plot_ene_dia,row=i+1,col=2)
        fig.add_trace(plot_maxene_dia,row=i+1,col=2)
        fig.add_trace(plot_maxene_mes,row=i+1,col=1)

        
    
        fig.update_yaxes(title_text='Ev/mes',row=i,col=1,rangemode='tozero')
        fig.update_yaxes(title_text='Ev/día',row=i,col=2,rangemode='tozero')
        
        fig.update_yaxes(title_text=magaxis,row=i+1,col=1,rangemode='tozero')
        fig.update_yaxes(title_text=magaxis,row=i+1,col=2,rangemode='tozero')
        
        
        fig.add_annotation(text=tipoev,
                    xref="x"+str(1+i+2*j), yref="y"+str(1+i+2*j),
                    x=max(M.index), y=max(M.numevs),
                    bordercolor=cols[i],
                    borderwidth=2,
                    borderpad=2,
                    bgcolor='wheat',
                    opacity=0.8,
                  showarrow=False)
    
        i+=2
        j+=1
    fig.update_xaxes(range=[fi, ff])
  
  
    
    fig.update_layout(
        title={
            'text': "Estadística de eventos clasificados - "+voldf.nombre.iloc[0],
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig.write_html('first_figure.html', auto_open=True)
    return fig

RAM_bar(df, fi, ff)
'''