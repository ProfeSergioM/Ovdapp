# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 12:39:36 2020

@author: sergio
"""
import dash
import json
import numpy as np
import dash_leaflet as dl
from dash_extensions import Download
from dash_extensions.snippets import send_bytes
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output,ALL,State
from app import app
import sys
import pandas as pd
from obspy.clients.iris import Client
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_getfromdb_lib as gdb
import ovdas_doc_lib as odl
import ovdas_figure_lib as ffig
import ovdas_future_lib as ffut
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
import datetime as dt
from random import random
tileurl =  'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}'
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")
iconUrl_volcan = app.get_asset_url('img/triangle.fw.png?random='+str(random())) 
sizescale=7
client = Client()
def dibujar_mapa(eventos):
    volcanes_star=[]
    for index,row in volcanes.iterrows():
        volcanes_star.append(dl.Marker(position=[row.latitud,row.longitud],zIndexOffset=-10000,
                                       children=[dl.Popup(html.Table([html.Tr([html.Td(row.nombre)])]))],
                                    icon=dict(iconUrl=iconUrl_volcan, iconSize=[7,7]),id='estrellita'))
    evs=[]
    i=0
    for index,row in eventos.iterrows():
        size=row.ml*sizescale
        evs.append(dl.Marker(position=[row.latitud,row.longitud],zIndexOffset=-5000,
                                    icon=dict(iconUrl=app.get_asset_url('img/'+row.tipoevento+'.png?random='+str(random())) , 
                                              iconSize=[size,size],iconAnchor=[size/2,size/2]),id={'type':'evento-mapa','index':i}))
        i=i+1


    
    escala = dl.ScaleControl(imperial=False)
    contenidomapa = [dl.TileLayer(id="tiles", url=tileurl),escala,*volcanes_star,*evs]

    mapa = dl.Map(contenidomapa,style={'width': '100%', 'height': '75vh', 'margin': "auto", "display": "block","z-index":"0"}
                    ,center=[-30,-70],zoom=3,id='mapaloc_electriceye'
                    )   
 
        

 
    return mapa

def get_fechahoy(): 
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return fini,ffin

def get_lista(ini=True,sel=0):
    
    inicio,final=get_fechahoy()
    eventos = gdb.extraer_eventos(inicio,final,volcan='*',ML='>2')
    eventos = pd.DataFrame(eventos)
    eventos = eventos.sort_values(by='fecha',ascending=False).head(20)
    listgroupitems_eventos=[]
    inputs_listaev =[]
    i=0
    for index,row in eventos.iterrows():
        volcan = volcanes[volcanes.id==row.idvolc].nombre
        
        
        
        result = client.distaz(stalat=float(volcanes[volcanes.id==row.idvolc].latitud.iloc[0]),
                               stalon=float(volcanes[volcanes.id==row.idvolc].longitud.iloc[0]),
                               evtlat=row.latitud,
                               evtlon=row.longitud)
        direccion = ffut.direccion_geo(result['backazimuth'])[0]
        direccion_largo = ffut.direccion_geo(result['backazimuth'])[1]
        distancia = np.round(result['distancemeters']/1000,1)
                            
        texto1 = str(distancia)+' km al '+direccion+' del '+volcanes[volcanes.id==row.idvolc].vol_tipocorto+' '+volcan
        fechastr = (str(row.fecha)[0:19])
        texto = fechastr+ ' - '+row.tipoevento
        divtext = html.Div([dbc.Row([dbc.Col(texto1,width=10),dbc.Col('Prof',width=2)],no_gutters=True),
                         dbc.Row([dbc.Col(texto,width=10),dbc.Col(str(np.round(row.profundidad,1))+' km',width=2)],no_gutters=True)])
        divML = html.Div([dbc.Row(['ML'],style={'font-weight':'bold','color':'white'}),
                          dbc.Row([row.ml],style={'font-weight':'bold','color':'white'})])
        texto = dbc.Row([dbc.Col(divML,width=1),dbc.Col(divtext,width=11)],no_gutters=True)
        

        id_lgi = {'type':'evento-listgroupitem','index':i}
        if ini==True:
            if i==0:
                listgroupitems_eventos.append(dbc.ListGroupItem(texto,id=id_lgi ,active=True,style={'padding-left':'1%'}))
            else:
                listgroupitems_eventos.append(dbc.ListGroupItem(texto,id=id_lgi ,style={'padding-left':'1%'}))
        else:
            if str(row.idevento)==str(sel):
                listgroupitems_eventos.append(dbc.ListGroupItem(texto,id=id_lgi,active=True,style={'padding-left':'1%'}))
            else:
                listgroupitems_eventos.append(dbc.ListGroupItem(texto,id=id_lgi ,style={'padding-left':'1%'}))
        inputs_listaev.append(Input(str(row.idevento),'n_clicks'))
        i+=1
    eventos = eventos.reset_index(drop=True)
    return listgroupitems_eventos, inputs_listaev,eventos,sel


def get_carddatoev(eventosel,volcansel):

    result = client.distaz(stalat=volcansel.latitud.iloc[0],
                           stalon=volcansel.longitud.iloc[0],
                           evtlat=eventosel.latitud.iloc[0],
                           evtlon=eventosel.longitud.iloc[0])
    direccion = ffut.direccion_geo(result['backazimuth'])[0]
    direccion_largo = ffut.direccion_geo(result['backazimuth'])[1]
    distancia = np.round(result['distancemeters']/1000,1)
    titulo='ML '+str(eventosel.ml.iloc[0])+' - '+str(distancia)+' km al '+direccion+' del '+volcansel.vol_tipo.iloc[0]+' '+volcansel.nombre.iloc[0]

    
    fila1 =  html.Tr([html.Td("Fecha"), html.Td(str(eventosel.fecha.iloc[0])[0:19].replace('T',' '))])
    fila2 =  html.Tr([html.Td("Latitud"), html.Td(str(eventosel.latitud.iloc[0])+'°')])
    fila3 =  html.Tr([html.Td("Longitud"), html.Td(str(eventosel.longitud.iloc[0])+'°')])
    fila4 =  html.Tr([html.Td("Profundidad"), html.Td(str(eventosel.profundidad.iloc[0])+ 'km (bajo referencia)')])
    filas =     html.Tbody([fila1,fila2,fila3,fila4])
    table = dbc.Table(filas,bordered=True, dark=True,hover=True,responsive=True,striped=True)
    bg=dbc.ButtonGroup(   [
        dbc.Button("Generar borrador REAV", id='btn-reav')
        #dbc.Button("Generar correo", id='btn-correo')
                                    ],vertical=True,style={'width':'100%'}
        
        )
    card = dbc.Card(
    dbc.CardBody(
        [
            html.H4(titulo, className="card-title"),
            table,bg

        ]
    ),
    style={"width": "100%",'height':'100%'},
    )
    return card

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







card_listaeventos = dbc.Card([dbc.CardHeader('Listado de eventos destacados'),
                          dbc.CardBody(dcc.Loading(id='loading-card_listaeventos',type='circle',
                                                   
                                                   children=[html.Div(id='body_card_listaeventos')]),
                                       style={'overflow':'auto',"height": "75vh"},id='bodyevssinloading')
                          ],outline=True,color='light',className='m-1')

card_mapaeventos = dbc.Card([dbc.CardHeader('Mapa de localizaciones'),
                          dbc.CardBody(id='cardbody_mapa')
                          ]
                            ,outline=True,color='light',className='m-1')

card_datoseventos = dbc.Card([dbc.CardHeader('Datos del evento'),
                          dbc.CardBody(html.Div(id='body_card_datoseventos',style={'height':'100%'}))],outline=True,color='light',className='m-1',style={'height':'100%'})

modal = html.Div(
    [Download(id="download-electriceye"),
        dbc.Modal(
            [
                dbc.ModalHeader("Finalizado!"),
                dbc.ModalBody(dbc.Alert("Borrador de REAV finalizado, puede cerrar esta ventana =)", color="success")),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-modal", className="ml-auto")
                ),
            ],
            id="modal",
        ),
    ]
)


layout = (navbar,html.Div(children=[dbc.Row([dbc.Col([card_listaeventos],width=4),
                                      dbc.Col([card_mapaeventos],width=4),
                                      dbc.Col([card_datoseventos],width=4)],
                                     id='layout-electrieye')]
                   ),counter_imgfija,html.Div(id='cajita-electriceye', style={'display': 'none'}),
                                     html.Div(id='cajita2-electriceye', style={'display': 'none'})
          ,dcc.Loading(modal, style={'position':'fixed','left':'50%','top':'50%'}))

@app.callback(
    [Output('bodyevssinloading','children'),Output('cardbody_mapa','children'),Output('cajita-electriceye', 'children')],
    [Input('interval-component-ev','n_intervals')]
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
    
    mapa = dibujar_mapa(eventosdf)
    cajita =  json.dumps(eventosdf.to_json(date_format='iso'), indent=2)
 
    return listgroup_eventos,mapa,cajita

@app.callback([Output({'type': 'evento-listgroupitem', 'index': ALL}, 'active'),Output({'type': 'evento-mapa', 'index': ALL}, 'icon')
               ,Output({'type': 'evento-mapa', 'index': ALL}, 'zIndexOffset'),Output('mapaloc_electriceye','zoom'),Output('mapaloc_electriceye','center')
               ,Output('body_card_datoseventos','children'),Output('cajita2-electriceye', 'children')],
              [Input({'type': 'evento-listgroupitem', 'index': ALL}, 'n_clicks'),
               Input({'type': 'evento-mapa', 'index': ALL}, 'n_clicks'),
               Input('cajita-electriceye', 'children')],
              [State({'type': 'evento-listgroupitem', 'index': ALL}, 'active'),State({'type': 'evento-mapa', 'index': ALL}, 'zIndexOffset')]
              
              )
def elegir_evento(values,marker,cajita,active,panes):
    
    eventos = pd.read_json(json.loads(cajita))
    if (dash.callback_context.triggered[0]['value'] == None) or (dash.callback_context.triggered[0]['prop_id']=='cajita-electriceye.children'):
        index_sel=0
        zoom=3
        center=[-30,-70]  
        
    else:
        zoom=7
        index_sel = int(dash.callback_context.triggered[0]['prop_id'].split('.')[0].split(',')[0][9:])
        
        center = [eventos[eventos.index==index_sel].latitud.iloc[0],eventos[eventos.index==index_sel].longitud.iloc[0]]
    volcansel = volcanes[volcanes.id==eventos[eventos.index==index_sel].idvolc.iloc[0]]  
    activelist=np.full(len(values),False)
    activelist[index_sel]=True
    
    colorev=[]
    panelist=np.full(len(values),-5000)
    panelist[index_sel]=5000
    for index,row in eventos.iterrows():
        size=sizescale*row.ml
        colorev.append(dict(iconUrl=app.get_asset_url('img/'+row.tipoevento+'.png?random='+str(random())) , 
                                          iconSize=[size,size],iconAnchor=[size/2,size/2]))
    eventosel=eventos[eventos.index==index_sel]
    sizesel = eventosel.ml.iloc[0]*sizescale
    colorev[index_sel]=dict(iconUrl=app.get_asset_url('img/greydot.fw.png?random='+str(random())) , 
                                          iconSize=[sizesel,sizesel],iconAnchor=[sizesel/2,sizesel/2])

    datosev = get_carddatoev(eventosel,volcansel)
    return list(activelist),colorev,list(panelist),zoom,center,datosev,json.dumps(eventosel.to_json(date_format='iso'), indent=2)


  


@app.callback(
    [Output("download-electriceye", "data"),Output("modal", "is_open")],
    [Input("btn-reav",'n_clicks'),Input("close-modal",'n_clicks')],
    [State("cajita2-electriceye",'children'),State("modal", "is_open")],prevent_initial_call=True
    )
def crear_info(clickreav,close_modal,cajita2,is_open):
    if dash.callback_context.triggered[0]['value'] is not None:
        if dash.callback_context.triggered[0]['prop_id'] =='btn-reav.n_clicks':
            evento= pd.read_json(json.loads(cajita2))
            document,filename = odl.REAV_ovdapp(evento)
            def to_reav(ruta):
                document.save(ruta)
            return send_bytes(to_reav,filename),not is_open
        elif dash.callback_context.triggered[0]['prop_id'] =='close-modal.n_clicks':
            return dash.no_update,not is_open
    else:
        return dash.no_update,dash.no_update