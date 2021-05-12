# -*- coding: utf-8 -*-
"""
Created on Tue May 11 14:58:56 2021

@author: sergio.morales
"""
import dash_bootstrap_components as dbc
import dash
from app import app
import dash_html_components as html
from random import random
import sys
import dash_core_components as dcc
import dash_html_components as html
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_getfromdb_lib as gdb
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

#volcanes = volcanes[volcanes.nombre_db.isin(['Villarrica','PuyehueCCaulle'])]

lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan) 


volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes-nllvsh71',
    options=lista_volcanes,
    value='NevChillan',
    multi=False,
    style={'color': '#212121','background-color': '#212121'})

fechas_picker = dcc.DatePickerRange(
    id='fechas-nllvsh71',
    start_date_placeholder_text="Inicio",end_date_placeholder_text="Final",
    calendar_orientation='vertical',display_format='Y-MM-DD',
    min_date_allowed='2010-01-01',style={ 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                      'width':'100%'
                                    })  

controles = html.Div([
    html.Div(volcan_selector),
    html.Div(html.P('Intervalo de fechas',id='titulo-fecha-fastrsam')),
    fechas_picker,
    html.Div(children=[dcc.Loading(children=[
                dbc.Button("Descargar datos", color="success", id="csv-realtime-nllvsh71", className="mr-1",style={'pointer-events': 'none','opacity':'0.2'}),
                dbc.Button("Online", color="success", id="submit-realtime-nllvsh71", className="mr-1"),
                dbc.Button("Enviar", color="primary", id="submit-filtro-nllvsh71", className="mr-1")])],style={'text-align':'right'})

    ])
controlescard = dbc.Card([
    dbc.CardHeader('Opciones'),
    dbc.CardBody(controles,id='controles-fastrsam')
    
    ],outline=True,color='light')

banner_inferior = dbc.Card([
    dbc.CardHeader('Fecha y Hora actual (UTC)'),
    dbc.CardBody('',id='live-update-text-nllvsh71')
    
    ],outline=True,color='light')

modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Finalizado!"),
                dbc.ModalBody([dbc.Alert("Datos cargados, presione el botón a continuación para descargar :)", color="success"),
                dbc.Button("Descargar datos", color="primary", className="mr-1",external_link=True,id="xlsx-download-nllvsh71")]),
                dbc.ModalFooter(
                    dbc.Button("Cerrar", id="close-modal-nllvsh71", className="ml-auto")
                ),
            ],
            id="modal-nllvsh71",
        ),
    ]
)

def crear_nllvsh71(volcan,ini,fin,tipoev,mlmin):
    import sys
    sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
    sys.path.append('//172.16.40.102/Monitoreo/Ovdas_pyLib/ovdapp/')
    import get_data_lib as gdl
    
    from pyproj import Proj
    myProj = Proj("+proj=utm +zone=19S, +south +ellps=WGS84 +datum=WGS84 +units=km +no_defs")
    df = gdl.get_comparison_loc(volcan, ini, fin,tipoev,mlmin)
    
    df['lonUTM_hypo']=myProj(df.longitud,df.latitud)[0]
    df['latUTM_hypo']=myProj(df.longitud,df.latitud)[1]
    df['lonUTM_NLL']=myProj(df.lonN,df.latN)[0]
    df['latUTM_NLL']=myProj(df.lonN,df.latN)[1]
    df =df.reset_index()
    df['diflat']=df['latUTM_NLL']-df['latUTM_hypo']
    df['diflon']=df['lonUTM_NLL']-df['lonUTM_hypo']
    df['difpro']=df['profN']-df['profH']
    
    last_df=df.tail(1)
    
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
    import numpy as np
    import locale     
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go    
    fig = make_subplots(rows=9, cols=2,shared_xaxes=True,subplot_titles=['Localizaciones','Diferencia NLL - Hypo71'],
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
                               ])
    
    lonlat_hypo = go.Scattergl(x=df['lonUTM_hypo'],y=df['latUTM_hypo'],name='Hypo71',mode='markers',opacity=0.5,legendgroup='group1',marker_color='#7b85d4')
    lonlat_NLL = go.Scattergl(x=df['lonUTM_NLL'],y=df['latUTM_NLL'],name='NLL',mode='markers',opacity=0.5,legendgroup='group2',marker_color='#f37738')
    red = go.Scattergl(x=esta_meta['lonUTM'],y=esta_meta['latUTM'],mode='markers',marker_symbol='triangle-up',marker_color='red',name='Estación',marker_size=10)
    volcan = go.Scattergl(x=voldf['lonUTM'],y=voldf['latUTM'],mode='markers',marker_symbol='star',marker_color='yellow',name=voldf.vol_tipocorto.iloc[0],marker_size=10)
    last_lonlat_hypo = go.Scattergl(x=last_df['lonUTM_hypo'],y=last_df['latUTM_hypo'],name='Last Hypo71',mode='markers',
                                    opacity=1,legendgroup='group3',marker_color='#7b85d4',marker_symbol='circle-dot',marker_size=10,marker_line_width=2)
    last_lonlat_NLL = go.Scattergl(x=last_df['lonUTM_NLL'],y=last_df['latUTM_NLL'],name='Last NLL',mode='markers',
                                    opacity=1,legendgroup='group4',marker_color='#f37738',marker_symbol='circle-dot',marker_size=10,marker_line_width=2)
    
    fig.add_trace(lonlat_hypo,row=1,col=1)
    fig.add_trace(lonlat_NLL,row=1,col=1)
    fig.add_trace(last_lonlat_hypo,row=1,col=1)
    fig.add_trace(last_lonlat_NLL,row=1,col=1)
    fig.add_trace(red,row=1,col=1)
    fig.add_trace(volcan,row=1,col=1)
    
    fig.update_yaxes(scaleanchor = "x",scaleratio = 1,row=1,col=1)
    fig.update_yaxes(row=1,col=1,tickformat='int',title='Northing UTM (km)')
    fig.update_xaxes(row=7,col=1,tickformat='int',title='Easting UTM (km)')
    
    lonprof_hypo = go.Scattergl(x=df['lonUTM_hypo'],y=df['profH'],name='Hypo71',mode='markers',opacity=0.5,legendgroup='group1',showlegend=False,marker_color='#7b85d4')
    fig.add_trace(lonprof_hypo,row=7,col=1)
    lonprof_NLL = go.Scattergl(x=df['lonUTM_NLL'],y=df['profN'],name='NLL',mode='markers',opacity=0.5,legendgroup='group2',showlegend=False,marker_color='#f37738')
    fig.add_trace(lonprof_NLL,row=7,col=1)
    last_lonprof_hypo = go.Scattergl(x=last_df['lonUTM_hypo'],y=last_df['profH'],name='Last Hypo71',mode='markers',
                                    opacity=1,legendgroup='group3',marker_color='#7b85d4',marker_symbol='circle-dot',marker_size=10,marker_line_width=2,showlegend=False)
    last_lonprof_NLL = go.Scattergl(x=last_df['lonUTM_NLL'],y=last_df['profN'],name='Last NLL',mode='markers',
                                    opacity=1,legendgroup='group4',marker_color='#f37738',marker_symbol='circle-dot',marker_size=10,marker_line_width=2,showlegend=False)
    fig.add_trace(last_lonprof_hypo,row=7,col=1)
    fig.add_trace(last_lonprof_NLL,row=7,col=1)
    
    
    diflat = go.Scattergl(x=df.index,y=df.diflat,mode='lines',name='Δ N (NLL-Hypo)',showlegend=False)
    #diflatm = go.Scattergl(x=df.index,y=df.diflat.abs().rolling(int(len(df)/100)).mean(),mode='lines',name='Media Δ N (NLL-Hypo)',line_color='white')
    fig.add_trace(diflat,row=1,col=2)
    #fig.add_trace(diflatm,row=1,col=2)
    
    diflon = go.Scattergl(x=df.index,y=df.diflon,mode='lines',name='Δ E (NLL-Hypo)',showlegend=False)
    #diflonm = go.Scattergl(x=df.index,y=df.diflon.abs().rolling(int(len(df)/100)).mean(),mode='lines',name='Media Δ E (NLL-Hypo)',line_color='white')
    fig.add_trace(diflon,row=4,col=2)
    #fig.add_trace(diflonm,row=4,col=2)
    
    difpro = go.Scattergl(x=df.index,y=df.difpro,mode='lines',name='Δ Z (NLL-Hypo)',showlegend=False)
    #difprom = go.Scattergl(x=df.index,y=df.difpro.abs().rolling(int(len(df)/100)).mean(),mode='lines',name='Media Δ Z (NLL-Hypo)',line_color='white')
    fig.add_trace(difpro,row=7,col=2)
    #fig.add_trace(difprom,row=7,col=2)
    
    fig.add_annotation(xref="x domain",yref="y domain",x=0.95,y=0.95,text="Promedio = ±"+str(np.round(df.diflat.abs().mean(),2))+' km',
                       showarrow=False,row=1,col=2,align='right')
    fig.add_annotation(xref="x domain",yref="y domain",x=0.95,y=0.95,text="Promedio = ±"+str(np.round(df.diflon.abs().mean(),2))+' km',
                       showarrow=False,row=4,col=2,align='right')
    fig.add_annotation(xref="x domain",yref="y domain",x=0.95,y=0.95,text="Promedio = ±"+str(np.round(df.difpro.abs().mean(),2))+' km',
                       showarrow=False,row=7,col=2,align='right')
    
    fig.update_yaxes(range=[min(df['profH'].min(),df['profN'].min()), max(df['profH'].max(),df['profN'].max())],row=7,col=1,autorange='reversed',title='Profundidad (km)')
    fig.update_yaxes(title='Δ N (km)',col=2,row=1)
    fig.update_yaxes(title='Δ E (km)',col=2,row=4)
    fig.update_yaxes(title='Δ Z (km)',col=2,row=7)
    fig.update_xaxes(title='Evento',col=2,row=7)
    fig.update_layout(template='plotly_dark',
                      title=('NonLinLoc vs Hypo71 - '+
                             voldf.vol_tipo.iloc[0]+' '+voldf.nombre.iloc[0]+' - '+df.head(1).dia.iloc[0]+' - '+df.tail(1).dia.iloc[0]
                             )
                      )
    

    return fig,df

PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("Comparador localizaciones NonLinLoc - Hypo71",style={'color':'white'}),width=10),
            dbc.Col(dbc.Button("Ovdapp", outline=True, className="mr-1",id='volver-home',href='/'),width=1)
            
            
        ],justify="left",
    style={'width':'100%'})

],
color="#141d26",

)
counter_imggif = dcc.Interval(
          id='interval-component-gif-nllvsh71',
          interval=60*1000*4, # in milliseconds
          n_intervals=0
      )
counter_reloj = dcc.Interval(
          id='interval-component-reloj-nllvsh71',
          interval=60*1000*1, # in milliseconds
          n_intervals=0
      )
layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col([html.Div(id='colgrafica-nllvsh71')],width=9)
                                   ]),
                   html.Div(id='cajita-nllvsh71', style={'display': 'none'}),
                   dbc.Row([counter_imggif,counter_reloj],no_gutters=True,justify='start', className="mr-1"),
                   dcc.Loading(modal, style={'position':'fixed','left':'50%','top':'50%'})
                   ])

import datetime as dt
from dash.dependencies import Input, Output,State
import datetime

@app.callback([Output('live-update-text-nllvsh71', 'children'),Output('fechas-nllvsh71','start_date'),Output('fechas-nllvsh71','end_date'),
],
              [Input('interval-component-reloj-nllvsh71', 'n_intervals')],
              [State('dropdown_volcanes-nllvsh71','value'),State('fechas-nllvsh71','start_date'),State('fechas-nllvsh71','end_date')]
              )
def update_date(n,volcan,fini,ffin):
    from flask import request
    print('tic! from '+request.remote_addr)
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=365), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})],fini,ffin

@app.callback(
    [Output("colgrafica-nllvsh71", "children"),Output('interval-component-reloj-nllvsh71', 'disabled'),
     Output("submit-realtime-nllvsh71",'color'),Output("submit-realtime-nllvsh71",'children'),
     Output('cajita-nllvsh71', 'children'),
     Output("csv-realtime-nllvsh71",'style')
     
     ],
    
    [Input("submit-realtime-nllvsh71",'n_clicks'),Input('interval-component-reloj-nllvsh71', 'n_intervals'),
     Input("submit-filtro-nllvsh71", "n_clicks")],
    [State('dropdown_volcanes-nllvsh71','value'), State('fechas-nllvsh71','start_date'),State('fechas-nllvsh71','end_date')
     ],prevent_initial_call=True
)
def update_cam_fija(*args):

    def plotear(volcan, fini, ffin, tipoev='VT', mlmin=0):
        print('iniciado')
        fig,df = crear_nllvsh71(volcan, fini, ffin, tipoev, mlmin)
        df = df.to_json()
        grafico = html.Div(children=[
            dcc.Graph(
                id='timeline-nllvsh71',
                figure=fig,
                style={ 'height':'80vh' }
            )
        ])
        
        graficocard = dbc.Card([
            dbc.CardHeader('Sismicidad'),
            dbc.CardBody(grafico)
            
            ],outline=True,color='light')
        return graficocard,df

    livebutton=args[0]
    ffin=args[5]
    fini=args[4]
    volcan=args[3]

    ctx = dash.callback_context
    ctx_index = ctx.triggered[0]['prop_id'].split('.')[0]

    if ctx_index=='submit-realtime-nllvsh71':
        if (livebutton==None) or (livebutton % 2 != 0):
            return dash.no_update,True,'warning','Offline',dash.no_update,dash.no_update
        else:
            graficocard,df_nllvsh71 = plotear(volcan,fini,ffin)
            return [graficocard],False,'success','Online',df_nllvsh71,dash.no_update
    else:
        graficocard,df_nllvsh71 = plotear(volcan,fini,ffin)
        return [graficocard],dash.no_update,dash.no_update,dash.no_update,df_nllvsh71,{'pointer-events': 'auto','opacity':'1'}
    
    

@app.callback([Output("xlsx-download-nllvsh71", "href"),Output("modal-nllvsh71", "is_open")],
              [Input("csv-realtime-nllvsh71", "n_clicks"),Input("close-modal-nllvsh71",'n_clicks')],
              [State('cajita-nllvsh71', 'children'),State("modal-nllvsh71", "is_open")],
              prevent_initial_call=True
              )
def download_csv(click,close,data,is_open):
    if dash.callback_context.triggered[0]['value'] is not None:
        if dash.callback_context.triggered[0]['prop_id'] =='csv-realtime-nllvsh71.n_clicks':
            print('Generando Xlsx')
            import json
            import pandas as pd
            df= json.loads(data)
            df = pd.DataFrame(df)
            import doc_lib as odl
            file_path= odl.xlsxdownload_ovdapp(df)
            filename ='datosNLLVSH71.xlsx'
            file_path = 'assets/dynamic/'+file_path+'.xlsx'
            link_url= '/dash/urlToDownloadnllvsh71?value={}'.format(file_path)
            link_url=link_url+'&filename={}'.format(filename)
            return link_url,not is_open
                
        elif dash.callback_context.triggered[0]['prop_id'] =='close-modal-nllvsh71.n_clicks':
            return dash.no_update,not is_open
    else:
        return dash.no_update,dash.no_update


@app.server.route('/dash/urlToDownloadnllvsh71') 
def descargar_nllvsh71():
    import io,os,flask
    value = flask.request.args.get('value')
    filename = flask.request.args.get('filename')
    return_data = io.BytesIO()
    with open(value, 'rb') as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)
    os.remove(value) 
    return flask.send_file(return_data,
                     #mimetype='document/xls',
                     attachment_filename=filename,
                     as_attachment=True)
