# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 12:39:36 2020

@author: sergio
"""
import dash
import dash_leaflet as dl
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
from random import random
tileurl =  'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}'
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")
iconUrl_volcan = app.get_asset_url('img/triangle.fw.png?random='+str(random())) 

def dibujar_mapa(evs,sel):
    if sel==0:
        evsel=evs.head(1)
        evnos=evs.iloc[1:]
        zoom=3
        center=[-30,-70]
    else:
        evsel = evs[evs.idevento==int(sel)]
        evnos = evs[evs.idevento!=int(sel)]
        zoom=6
        center=[volcanes[volcanes.id==evsel.idvolc.iloc[0]].latitud.iloc[0],volcanes[volcanes.id==evsel.idvolc.iloc[0]].longitud.iloc[0]]
        
    volcanes_star=[]
    for index,row in volcanes.iterrows():
        volcanes_star.append(dl.Marker(position=[row.latitud,row.longitud],zIndexOffset=-5000,children=[dl.Popup(html.Table([html.Tr([html.Td(row.nombre)])]))],
                                    icon=dict(iconUrl=iconUrl_volcan, iconSize=[7,7],iconAnchor=[7, 7]),id='estrellita'))
    evs = []
    evsinputs = []
    for index,row in evnos.iterrows():
        evs.append(dl.CircleMarker(id='evento'+str(row.idevento),
                                   center=[row.latitud,row.longitud],
                           radius=row.ml*4,
                           color='#ffffff',
                           fillColor='#'+ffig.colores_cla_hex(row.tipoevento)[:-2],
                           weight=1,
                           fillOpacity=0.75))
        evsinputs.append(Input('evento'+str(row.idevento),'n_clicks'))
    seleccionado = dl.CircleMarker(id='evento'+str(evsel.idevento.iloc[0]),center=[evsel.latitud.iloc[0],evsel.longitud.iloc[0]],
                           radius=evsel.ml.iloc[0]*4,
                           color='#000000',
                           fillColor='white',
                           weight=1,
                           fillOpacity=1)
    
    evsinputs.append(Input('evento'+str(evsel.idevento.iloc[0]),'n_clicks'))
    
    escala = dl.ScaleControl(imperial=False)
    contenidomapa = [dl.TileLayer(id="tiles", url=tileurl),escala,*volcanes_star,*evs,seleccionado]
    if sel==0:
        mapa = dl.Map(contenidomapa,style={'width': '100%', 'height': '75vh', 'margin': "auto", "display": "block","z-index":"0"}
                        ,center=center,zoom=zoom,id='mapaloc_electriceye'
                        )   
    else:
        mapa = dl.Map(contenidomapa,style={'width': '100%', 'height': '75vh', 'margin': "auto", "display": "block","z-index":"0"}
                        ,center=center,id='mapaloc_electriceye'
                        )   
        

 
    return mapa,evsinputs

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
        texto = fechastr+ ' - '+row.tipoevento+', ML='+str(row.ml)+' en '+volcan
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

counter_imgfija = dcc.Interval(id='interval-component-ev',interval=60*1000*2,n_intervals=0)
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
mapa,evsinputs= dibujar_mapa(eventos,sel)



card_listaeventos = dbc.Card([dbc.CardHeader('Listado de eventos destacados'),
                          dbc.CardBody(dcc.Loading(id='loading-card_listaeventos',type='circle',
                                                   
                                                   children=[html.Div(id='body_card_listaeventos', children=listaev)]),
                                       style={'overflow':'auto',"height": "75vh"},id='bodyevssinloading')
                          ],outline=True,color='light',className='m-1')

card_mapaeventos = dbc.Card([dbc.CardHeader('Mapa de localizaciones'),
                          dbc.CardBody(children=mapa,id='cardbody_mapa')
                          ]
                            ,outline=True,color='light',className='m-1')

card_datoseventos = dbc.Card([dbc.CardHeader('Datos del evento'),
                          dbc.CardBody(html.Div(id='body_card_datoseventos'))],outline=True,color='light',className='m-1')



layout = (navbar,html.Div(children=[dbc.Row([dbc.Col([card_listaeventos],width=4),
                                      dbc.Col([card_mapaeventos],width=4),
                                      dbc.Col([card_datoseventos],width=4)],
                                     id='layout-electrieye')]
                   ),counter_imgfija
          )




@app.callback(
    [Output('bodyevssinloading','children'),Output('cardbody_mapa','children'),Output('body_card_datoseventos','children')],
    [Input('interval-component-ev','n_intervals')]+inputs+evsinputs,prevent_initial_call=True
    )
def get_eventos(counter,*evs):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')

    if trigger[1]=='n_clicks':
        if trigger[0][0:6]!='evento':
            listgroupitems_eventos,inputs_listaev,eventosdf,sel  = get_lista(ini=False,sel=trigger[0])
        else:
            listgroupitems_eventos,inputs_listaev,eventosdf,sel  = get_lista(ini=False,sel=int(trigger[0][6:]))
            
    else:
        print('inicial!')
        listgroupitems_eventos,inputs_listaev,eventosdf,sel  = get_lista(ini=True)
        
    listgroup_eventos = dbc.ListGroup(
    listgroupitems_eventos,id='listgroup'
    )
    
    mapa,evsinputs = dibujar_mapa(eventosdf,sel)
    
    datosev=sel
    return listgroup_eventos,mapa,datosev


