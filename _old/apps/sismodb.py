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
import dash_core_components as dcc
import dash_html_components as html
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




fechas_picker = dcc.DatePickerRange(
    id='fechas-sismodb',
    start_date_placeholder_text="Inicio",
    end_date_placeholder_text="Final",
    calendar_orientation='vertical',
    display_format='Y-MM-DD',
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                      'width':'100%'
                                    } 
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
    import plotly
    cols = plotly.colors.DEFAULT_PLOTLY_COLORS
    
    t_index = pd.date_range(start=fi, end=ff, freq='D')
    t_index_mes = pd.date_range(start=fi, end=ff, freq='M')
    df = pd.DataFrame(gdb.extraer_eventos(inicio=fi,final=ff,volcan=vol))
    df = df[df.tipoevento.isin(tipoevs_custom)]
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
    
    fig.update_xaxes(range=[fi, ff])

    fig.layout.template = 'plotly_dark'
    
    

    return fig


PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("Proyecto de monitoreo sísmico automático OVV",style={'color':'white'}),width=10),
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
                                   dbc.Col([dcc.Loading(html.Div(id='colgrafica-sismodb'))],width=9)
                                   ]),
                   dbc.Row([counter_imggif,counter_reloj],no_gutters=True,justify='start'),
                   
                   ])

@app.callback(
    #[Output("colgrafica-sismodb", "children"),Output("colmapa-sismodb", "children")],
    [Output("colgrafica-sismodb", "children")],
    [Input("submit-filtro-sismodb", "n_clicks")],
    [State('fechas-sismodb','start_date'),State('fechas-sismodb','end_date'),State('dropdown_volcanes-sismodb','value')]
,prevent_initial_call=True)
def update_cam_fija(*args):
    fini=args[1]
    ffin=args[2]
    volcan=args[3]
    rsam_blacklist=['CRU','PIC','LAV','AGU','CR3','CVI']
    red = gdb.get_metadata_wws(volcan)
    red=red[red.tipo=='SISMOLOGICA']
    red['sensor'] = red.canal.str[1]
    red = red[red.sensor!='N']
    red=red[~red.codcorto.isin(rsam_blacklist)]
    red1 = red[red.referencia==1].sort_values(by='distcrater').head(1)# 1.referencia
    estaRSAM = red1.codcorto.iloc[0]
    tipoevs_custom=['VT','VD','HB','LP','EX','TR','LV','TO','MF']
    fig = crear_RAM(fini,ffin,volcan,tipoevs_custom)
    grafico = html.Div(children=[
        dcc.Graph(
            id='timeline-orca',
            figure=fig,
            style={ 'height':'80vh' }
        )
    ])
    
    graficocard = dbc.Card([
        dbc.CardHeader('Sismicidad'),
        dbc.CardBody(grafico)
        
        ],outline=True,color='light')



    #return [graficocard],[mapacard]
    return [graficocard]


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

    finidetect = dt.datetime.utcnow() - dt.timedelta(hours=horas)


    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})],fini,ffin,ffin