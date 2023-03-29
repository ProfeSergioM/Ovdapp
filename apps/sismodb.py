# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash
from numpy import arange
import datetime
from random import random
from app import app
from dash.dependencies import Input, Output,State
from dash import dcc,html
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import datetime as dt
horas=2

volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan) 
freqconteo = dcc.Dropdown(id='freqconteo-sismodb',
    options=[
        {'label': 'Eventos/hora', 'value': 'H'},
        {'label': 'Eventos/día', 'value': 'D'},
    ],
    value='H',
        multi=False,
        searchable=False,
        clearable=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)  

volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes-sismodb',
    options=lista_volcanes,
    value='Villarrica',
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)


from datetime import date

fechas_picker = dcc.DatePickerRange(
    id='fechas-sismodb',
    start_date_placeholder_text="Inicio",
    end_date_placeholder_text="Final",
    calendar_orientation='vertical',
    display_format='Y-MM-DD',
    min_date_allowed=date(2010,1,1),
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                      'width':'100%'
                                    } 
)  

tipoev_picker = dcc.Checklist(id='tipoev_check',
    options=[
        {'label': 'VT', 'value': 'VT'},
        {'label': 'LP', 'value': 'LP'},
        {'label': 'TR', 'value': 'TR'},
        {'label': 'EX', 'value': 'EX'},
        {'label': 'HB', 'value': 'HB'},
        {'label': 'VD', 'value': 'VD'},
        {'label': 'TO', 'value': 'TO'},
        {'label': 'MF', 'value': 'MF'},
        {'label': 'LV', 'value': 'LV'},
        {'label': 'AV', 'value': 'AV'},
        {'label': 'IC', 'value': 'IC'}
    ],
    value=['VT','LP'],
    inputStyle={"margin-right": "5px","margin-left": "5px"}
) 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
counter_imggif = dcc.Interval(
          id='interval-component-gif-sismodb',
          interval=60*1000*5, # in milliseconds
          n_intervals=0
      )
counter_reloj = dcc.Interval(
          id='interval-component-reloj-sismodb',
          interval=60*1000*60, # in milliseconds
          n_intervals=0
      )



def crear_RAM(fi,ff,vol,tipoevs_custom):
    sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
    import ovdas_getfromdb_lib as gdb
    voldf =gdb.get_metadata_volcan(vol,rep='y')
    voldf = voldf.drop_duplicates(subset='nombre', keep="first")
    import plotly
    cols = plotly.colors.DEFAULT_PLOTLY_COLORS
    
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
    
    def RAM_bar(df,fi,ff):
        df_count = df.groupby('tipoevento')['tipoevento'].resample('D').count().rename('numevs')
        df_count = df_count.reset_index().set_index('fecha')
        df_count_mes = df.groupby('tipoevento')['tipoevento'].resample('M').count().rename('numevs')
        df_count_mes = df_count_mes.reset_index().set_index('fecha')
        
        df_max = df.groupby('tipoevento')[['dr','ml','Par']].resample('D').max()
        df_max = df_max.reset_index().set_index('fecha')
        df_max_mes = df.groupby('tipoevento')[['dr','ml','Par']].resample('M').max()
        df_max_mes = df_max_mes.reset_index().set_index('fecha')   
        
        orderev = ['VT','VD','LP','EX','TR','TO','HB','LV','MF','AV','IC']
        cat = pd.api.types.CategoricalDtype(categories=orderev, ordered=True)
        df.loc[:,'tipoevento'] = df['tipoevento'].astype(cat)
        df.sort_values(by='tipoevento',inplace=True)
        
        tipoevs_custom=df.tipoevento.unique()
        rows=len(tipoevs_custom)*2
        import numpy as np
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
    
        return fig
    
    def RAM(df,fi,ff):
        df_count = df.groupby('tipoevento')['tipoevento'].resample('D').count().rename('numevs')
        
        df_count = df_count.reset_index().set_index('fecha')
        
        
        df_count_mes = df.groupby('tipoevento')['tipoevento'].resample('M').count().rename('numevs')
        df_count_mes = df_count_mes.reset_index().set_index('fecha')
        
        df_max = df.groupby('tipoevento')[['dr','ml','Par']].resample('D').max()
        df_max = df_max.reset_index().set_index('fecha')
        df_max_mes = df.groupby('tipoevento')[['dr','ml','Par']].resample('M').max()
        df_max_mes = df_max_mes.reset_index().set_index('fecha')   
        
        rows=1
        
        tipoevs_custom=df.tipoevento.unique()
        if ('VT' or 'VD') in tipoevs_custom:
            rows=rows+1
        if ('LP' or 'TR' or 'EX' or 'HB' or 'TO' or 'LV') in tipoevs_custom:
            rows=rows+1
        if 'MF' in tipoevs_custom:
            rows=rows+1
            
            
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
                                column_widths=[1,4])
        
        fig.update_layout(template='seaborn')
        i=0
        for tipoev in tipoevs_custom:
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
                plot_maxml_mes = go.Scatter(x=eN.index,y=eN.ml,mode='markers+lines',name='M<sub>L</sub> '+tipoev,legendgroup='M<sub>L</sub> '+tipoev,marker_color=cols[i],
                                            xperiod='M1',xperiodalignment='middle',showlegend=False)
                fig.add_trace(plot_maxml_dia,row=row_ml,col=2)
                fig.add_trace(plot_maxml_mes,row=row_ml,col=1)
            elif tipoev in ['LP','TR','EX','HB','TO','LV']:
                plot_maxdr_dia = go.Scatter(x=eM.index,y=eM.dr,mode='markers',name='D<sub>R</sub> '+tipoev,legendgroup='D<sub>R</sub> '+tipoev,marker_color=cols[i])
                plot_maxdr_mes = go.Scatter(x=eN.index,y=eN.dr,mode='markers+lines',name='D<sub>R</sub> '+tipoev,legendgroup='D<sub>R</sub> '+tipoev,marker_color=cols[i],
                                            xperiod='M1',xperiodalignment='middle',showlegend=False)
                fig.add_trace(plot_maxdr_dia,row=row_dr,col=2)
                fig.add_trace(plot_maxdr_mes,row=row_dr,col=1)
            elif tipoev =='MF':
                plot_maxPar_dia = go.Scatter(x=eM.index,y=eM.Par,mode='markers',name='Pa<sub>R</sub> '+tipoev,legendgroup='Pa<sub>R</sub> '+tipoev,marker_color=cols[i])
                plot_maxPar_mes = go.Scatter(x=eN.index,y=eN.Par,mode='markers+lines',name='Pa<sub>R</sub> '+tipoev,legendgroup='Pa<sub>R</sub> '+tipoev,marker_color=cols[i],
                                            xperiod='M1',xperiodalignment='middle',showlegend=False)
                fig.add_trace(plot_maxPar_dia,row=row_mf,col=2)
                fig.add_trace(plot_maxPar_mes,row=row_mf,col=1)
            i+=1
        
        fig.update_yaxes(title_text='Ev/mes',row=1,col=1,rangemode='tozero')
        fig.update_yaxes(title_text='Ev/día',row=1,col=2,rangemode='tozero')
        fig.update_yaxes(title_text='Max M<sub>L</sub>/mes',row=2,col=1,rangemode='tozero')
        fig.update_yaxes(title_text='Max M<sub>L</sub>/día',row=2,col=2,rangemode='tozero')
        fig.update_yaxes(title_text='Max D<sub>R</sub>/mes',row=3,col=1,rangemode='tozero')
        fig.update_yaxes(title_text='Max D<sub>R</sub>/día',row=3,col=2,rangemode='tozero')
        
        fig.update_xaxes(range=[fi, ff])
        fig.update_layout(
            title={
                'text': "Estadística de eventos clasificados - "+voldf.nombre.iloc[0],
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        #fig.layout.template = 'plotly_dark'
        return fig
    def DET(df,tipoevs_custom,fi,ff):
        df = df[df.tipoevento==tipoev]
        nrows=4

        
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
        u_amp='um/s'
        if tipoev=='MF':
            u_amp='Pa'

        fig.update_yaxes(title_text=u_amp,row=2,col=1,rangemode='tozero')
        
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
        elif tipoev=='MF':
            mag='Par'
            maglabel='Pa<sub>R</sub>'
            magaxis='Pa<sub>R</sub>'            
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
        fig.update_xaxes(range=[fi, ff])
        fig.update_layout(
            title={
                'text': "Características de sismos "+tipoev+" clasificados, "+voldf.vol_tipocorto.iloc[0]+" "+voldf.nombre.iloc[0],
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        return fig
    
    
    
    figRAM = RAM(df,fi,ff)
    figRAM_bar = RAM_bar(df,fi,ff)
    figDET = []
    for tipoev in tipoevs_custom:
        figDET.append(DET(df,tipoevs_custom,fi,ff))
    return figRAM,figDET,figRAM_bar


PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("Ovdapp - SismoDB",style={'color':'white'}),width=10),
            dbc.Col(dbc.Button("Ovdapp", color="primary",outline=True, className="mr-1",id='volver-home',href='/'),width=1)
            
            
        ],justify="left",
    style={'width':'100%'})

],
color="#141d26",

)
      




controles = html.Div([
    html.Div(volcan_selector),
    html.Div(html.P('Intervalo de fechas',id='titulo-fecha-sismodb')),
    fechas_picker,
    html.Div(html.P('Tipos de eventos')),
    tipoev_picker,
    html.Div(dbc.Button("Enviar", color="primary", id="submit-filtro-sismodb"),style={'text-align':'right'})

    ])





controlescard = dbc.Card([
    dbc.CardHeader('Opciones'),
    dbc.CardBody(controles,id='controles-sismodb')
    
    ],outline=True,color='light')

banner_inferior = dbc.Card([
    dbc.CardHeader('Fecha y Hora actual (UTC)'),
    dbc.CardBody('',id='live-update-text-sismodb')
    
    ],outline=True,color='light')


layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col([dcc.Loading(children=[ 
                                       dcc.Tabs(id='tabs-sismoDB', value='tab-RAM', children=[
        dcc.Tab(label='Resumen mensual (RAM)', value='tab-RAM'),
        dcc.Tab(label='Resumen mensual (RAM) (barras)', value='tab-RAM_bar'),
        dcc.Tab(label='Detalle/tipo de evento', value='tab-DET')

    ]),html.Div(id='colgrafica-sismodb')])],width=9)
                                   ]),
                   dbc.Row([counter_imggif,counter_reloj],        className="mr-1 g-0",justify='start'),
                   
                   ])

@app.callback(
    [Output("colgrafica-sismodb", "children")],
    [Input("submit-filtro-sismodb", "n_clicks")],
    [State('fechas-sismodb','start_date'),State('fechas-sismodb','end_date'),
     State('dropdown_volcanes-sismodb','value'),State('tipoev_check','value'),State('tabs-sismoDB','value')]
,prevent_initial_call=True)
def update_cam_fija(*args):
    fini=args[1]
    ffin=args[2]
    volcan=args[3]
    tipoevs_custom = args[4]
    tab_value = args[5]
    rsam_blacklist=['CRU','PIC','LAV','AGU','CR3','CVI']
    red = gdb.get_metadata_wws(volcan)
    red=red[red.tipo=='SISMOLOGICA']
    red['sensor'] = red.canal.str[1]
    red = red[red.sensor!='N']
    red=red[~red.codcorto.isin(rsam_blacklist)]
    red1 = red[red.referencia==1].sort_values(by='distcrater').head(1)# 1.referencia
    figRAM,figDET,figRAM_bar = crear_RAM(fini,ffin,volcan,tipoevs_custom)

    graficoRAM = html.Div(children=[
        dcc.Graph(
            id='grafico',
            figure=figRAM,
            style={ 'height':'80vh' }
        )
    ])
    graficoRAM_bar = html.Div(children=[
        dcc.Graph(
            id='grafico',
            figure=figRAM_bar,
            style={ 'height':'80vh' }
        )
    ])
    graficoDET=[]
    for fig in figDET:
        
        graficoDET.append(html.Div(children=[
            dcc.Graph(
                id='grafico',
                figure=fig,
                style={ 'height':'80vh' }
            )
        ])   )
    
    lista_ev=[]
    for item in tipoevs_custom:
        ev = {'label': item,'value':item}
        lista_ev.append(ev) 
        
    tipoev_dropdown = dcc.Dropdown(
        id='tipoev-dropdown',
    clearable=False,

    options=lista_ev,
    value=tipoevs_custom[0],
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
                                    )
        
    graficoRAM = dbc.Card(id='div-RAM',children=[
        dbc.CardHeader(id='cardheader',children=['Resumen de sismicidad clasificada']),
        dbc.CardBody(graficoRAM)
        
        ],outline=True,color='light')

    graficoRAM_bar = dbc.Card(id='div-RAM_bar',children=[
        dbc.CardHeader(id='cardheader',children=['Resumen de sismicidad clasificada (barras)']),
        dbc.CardBody(graficoRAM_bar)
        
        ],outline=True,color='light')
    
    graficoDET = dbc.Card(id='div-DET',children=[
        dbc.CardHeader(id='cardheader',children=['Detalle de eventos x tipo'] ),
        dbc.CardBody(graficoDET)
        
        ],outline=True,color='light')

    return[[graficoRAM,graficoDET,graficoRAM_bar]]


@app.callback([Output('live-update-text-sismodb', 'children'),Output('fechas-sismodb','start_date'),Output('fechas-sismodb','end_date'),
               Output('fechas-sismodb','max_date_allowed'),
],
              [Input('url','href')]
              )
def update_date(href):
    from flask import request
    print('tic! from '+request.remote_addr)
    fini = dt.datetime.strftime((dt.datetime.utcnow() - dt.timedelta(days=360)).replace(day=1), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})],fini,ffin,ffin

@app.callback([Output('div-RAM','style'),Output('div-DET','style'),Output('div-RAM_bar','style')],
              Input('tabs-sismoDB','value')
              )
def show_tabs(tabvalue):
    if tabvalue=='tab-RAM':
        styleRAM={'display':'block'}
        styleDET={'display':'none'}
        styleRAM_bar={'display':'none'}
    elif tabvalue=='tab-DET':
        styleRAM={'display':'none'}
        styleDET={'display':'block'}
        styleRAM_bar={'display':'none'}
    elif tabvalue=='tab-RAM_bar':
        styleRAM={'display':'none'}
        styleDET={'display':'none'}
        styleRAM_bar={'display':'block'}
    return styleRAM,styleDET,styleRAM_bar