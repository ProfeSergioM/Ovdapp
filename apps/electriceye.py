# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 12:39:36 2020

@author: sergio
"""
import dash
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from app import app
import sys
import pandas as pd
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_getfromdb_lib as gdb
import ovdas_figure_lib as ffig
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
import datetime as dt
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

def dibujar_mapa(evs,sel):
    if sel==0:
        evsel=evs.head(1)
        evnos=evs.iloc[1:]
    else:
        evsel = evs[evs.idevento==int(sel)]
        evnos = evs[evs.idevento!=int(sel)]
        
    fig =go.Figure()
 
    trace_volcanes = go.Scattermapbox(lon=volcanes.longitud,lat=volcanes.latitud,showlegend=False,
                         name='Volcán',mode='markers',marker=go.scattermapbox.Marker(symbol='volcano',size=12),text =volcanes.nombre_db)   
    fig.add_trace(trace_volcanes)
    
    for tipoev in evnos['tipoevento'].unique():
        df = evnos[evnos['tipoevento']==tipoev]
        trace = go.Scattermapbox(lon=df['longitud'],
                                 lat=df['latitud'],
                                 showlegend=False,
                                 hoverinfo='skip',
                                 name='Evento '+tipoev,
                                 opacity=1,
                                 mode='markers',
                                 customdata=df,
                                 marker=go.scattermapbox.Marker(
                                 size=10,
                                 #color='#'+ffig.colores_cla_hex(tipoev)[:-2]
                                 color='green'
                                     ),
                                 )
        fig.add_trace(trace)    
    
    trace = go.Scattermapbox(lon=evsel.longitud,lat=evsel.latitud,
                                 showlegend=False,
                                 hoverinfo='skip',
                             marker=go.scattermapbox.Marker(
                                 size=15,
                                 color='red',
                                     ))
    fig.add_trace(trace)
    
    
    fig.update_layout(mapbox1=dict(
        accesstoken= 'pk.eyJ1IjoicHJvZmVzZXJnaW9tIiwiYSI6ImNrZXk5ZG9yaTB3Y3IycnA5bTlscWZqZjMifQ.s1qn784tAww2oGZYWeTi8w',
        style="mapbox://styles/profesergiom/ckfpoplbw1bpl1any6qj7eqtn",
        center=dict(lat=-30,lon=-70),
        zoom=2
                                    ),
        margin = dict(l = 0, r = 0, t = 0, b = 0),
                    )
 
    return fig

def get_fechahoy(): 
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return fini,ffin

def get_lista(ini=True,sel=0):
    
    inicio,final=get_fechahoy()
    eventos = gdb.extraer_eventos(inicio,final,volcan='*',ML='>1')
    eventos = pd.DataFrame(eventos)
    eventos = eventos.sort_values(by='fecha',ascending=False).head(20)
    listgroupitems_eventos=[]
    inputs_listaev =[]
    i=0
    for index,row in eventos.iterrows():
        volcan = volcanes[volcanes.id==row.idvolc].nombre
        fechastr = (str(row.fecha)[0:19])
        texto = fechastr+ ' - '+row.tipoevento+' en '+volcan
        if ini==True:
            if i==0:
                listgroupitems_eventos.append(dbc.ListGroupItem(texto,id=str(row.idevento),active=True))
            else:
                listgroupitems_eventos.append(dbc.ListGroupItem(texto,id=str(row.idevento)))
        else:
            if str(row.idevento)==str(sel):
                listgroupitems_eventos.append(dbc.ListGroupItem(texto,id=str(row.idevento),active=True))
            else:
                listgroupitems_eventos.append(dbc.ListGroupItem(texto,id=str(row.idevento)))
        inputs_listaev.append(Input(str(row.idevento),'n_clicks'))
        i+=1
    return listgroupitems_eventos, inputs_listaev,eventos,sel

counter_imgfija = dcc.Interval(id='interval-component-ev',interval=60*1000,n_intervals=0)
navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px"),width=2),
                    dbc.Col(dbc.NavbarBrand("Últimos eventos destacados - Electric Eye"))
                    
                ],
                align="left",
                no_gutters=True,
            ),
          
                style={ 'width':'60%', 'margin-left':'0px' }
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse([], id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)


listaev,inputs,eventos,sel = get_lista()
mapa = dibujar_mapa(eventos,sel)


card_listaeventos = dbc.Card([dbc.CardHeader('Listado de eventos destacados'),
                          dbc.CardBody(dcc.Loading(id='loading-card_listaeventos',type='circle',
                                                   
                                                   children=[html.Div(id='body_card_listaeventos', children=listaev)]),
                                       style={'overflow':'auto',"height": "75vh"},id='bodyevssinloading')
                          ],outline=True,color='light',className='m-1')

card_mapaeventos = dbc.Card([dbc.CardHeader('Mapa de localizaciones'),
                          dbc.CardBody(dbc.Container(dcc.Graph(figure=mapa,id='mapa-ee',style={'height':'100%'}),style={'height':'100%','padding-left':'0','padding-right':'0'}))
                          ]
                            ,outline=True,color='light',className='m-1')

card_datoseventos = dcc.Loading(id='loading-card_datos',type='circle',children=[
                dbc.Card([dbc.CardHeader('Datos del evento'),
                          dbc.CardBody([html.Div(id='body_card_datoseventos')])],outline=True,color='light',className='m-1')])



layout = (navbar,html.Div(children=[dbc.Row([dbc.Col([card_listaeventos],width=4),
                                      dbc.Col([card_mapaeventos],width=4),
                                      dbc.Col([card_datoseventos],width=4)],
                                     id='layout-electrieye')]
                   ),counter_imgfija
          )



@app.callback(
    [Output('bodyevssinloading','children'),Output('mapa-ee','figure')],
    [Input('interval-component-ev','n_intervals')]+inputs
    )
def get_eventos(counter,*evs):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')
    

    if trigger[1]=='n_clicks':
        listgroupitems_eventos,inputs_listaev,eventosdf,sel  = get_lista(ini=False,sel=trigger[0])
    else:
        print('inicial!')
        listgroupitems_eventos,inputs_listaev,eventosdf,sel  = get_lista(ini=True)
        
    listgroup_eventos = dbc.ListGroup(
    listgroupitems_eventos,id='listgroup'
    )
    
    mapa = dibujar_mapa(eventosdf,sel)
    return listgroup_eventos,mapa


