# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 12:11:30 2021

@author: sergio.morales
"""
from numpy import arange

import numpy as np
import dash_bootstrap_components as dbc
from app import app
app.config.suppress_callback_exceptions = True
from dash.dependencies import Input, Output,State
import dash
from random import random
from dash import dcc,html
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_getfromdb_lib as gdb
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")
volcan_default='NevChillan'
lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan)   
    
volcan_selector = html.Div([dbc.Label("Volcán:", html_for="volcan-label"),
    dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes_heli',
    options=lista_volcanes,
    value=volcan_default,
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)
                          ]
    
    
    
)



SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": " #141d26",
}
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Ovdapp", className="display-4"),
        html.P(
            "Helicorderizador", className="lead"
        ),
        dbc.ButtonGroup(
    [
        dbc.Button("liveHeli",id='live-button-heli'),
        dbc.Button("on Demand",id="ondemand-button-heli"),
    ],
    vertical=True,style={'width':'100%'}
),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="contenido-heli", style=CONTENT_STYLE)
layout = html.Div([sidebar, content])

@app.callback(
    Output("contenido-heli", "children"), 
    [Input("live-button-heli", "n_clicks"),Input("ondemand-button-heli", "n_clicks")]
)
def on_button_click(b_live,b_ondemand):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if (button_id == "live-button-heli") or (ctx.triggered[0]['prop_id'] =='.'):
        
        box_liveheli_png = dbc.ListGroup(
    [
        html.Div(id='content-heli'),

    ]
    )
        
        box_liveheli = dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [
                                html.H5([volcan_selector]),
                                box_liveheli_png,
                            ]
                        ),
                    ]
                )        
        
        
        contenido = html.Div([box_liveheli])

    elif button_id == "ondemand-button-heli":
        
        volcanes_selector = html.Div(
            [
                dbc.Label("Volcán:", html_for="volcan_od", width=2),
                dbc.Col(
                        dcc.Dropdown(
    clearable=False,
    id='od_volcan',
    options=lista_volcanes,
    value=volcan_default,
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
),
                    width=10,
                ),
            ],
 
        )        
        
        fechaini_selector = html.Div(
            [
                dbc.Label("Fecha y hora inicial (UTC):", html_for="fechaini_od", width=2),
                dbc.Col(
                        dcc.Input(id="od_fi", type="datetime-local"),
                    width=10,
                ),
            ],
         
        )           
        
        horas_selector = html.Div(
            [
                dbc.Label("Horas a graficar:", html_for="volcan_od", width=2),
                dbc.Col(
                        dcc.Dropdown(
    clearable=False,
    id='od_hora',
    value=1,
    options=[
                        {"label": "1 hora", "value": 1},
                        {"label": "2 horas", "value": 2},
                        {"label": "3 horas", "value": 3},
                        {"label": "4 horas", "value": 4},
                        {"label": "6 horas", "value": 6},
                        {"label": "8 hora", "value": 8},
                        {"label": "12 horas", "value": 12},
                        {"label": "24 horas", "value": 24},
                        {"label": "48 horas", "value": 48},
                    ],
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
),
                    width=10,
                ),
            ],
     
        )   
        
        minutos_selector = html.Div(
    [
        dbc.Label("Minutos en eje x", html_for="example-radios-row", width=2),
        dbc.Col(
            dbc.RadioItems(
                id="od_minuto",
                value=15,
                options=[
                    {"label": "10 min", "value": 10},
                    {"label": "15 min", "value": 15},
                    {"label": "30 min", "value": 30},
                    {"label": "60 min", "value": 60},
                ],
            ),
            width=10,
        ),
    ],
 
)
        
        freq_selector = html.Div(
    [
        dbc.Label("Frecuencia de filtrado", html_for="od_freq", width=2),
        dbc.Col( dcc.RangeSlider(
        id="od_freq",
        min=0.5,
        max=15,
        step=0.5,
        value=[0.5,12],
        marks=arange(0,16,1))),
    ],
  
)
        submit = dbc.Button('Enviar!',id='od_ir',color='primary')
        form_ondemand_heli = dbc.Form([volcanes_selector,fechaini_selector,horas_selector,minutos_selector,freq_selector,submit])
        list_group = dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    [
                        html.H5("Crear helicorder personalizado"),
                        form_ondemand_heli,
                    ]
                ),
                dbc.ListGroupItem([
                    dcc.Loading([html.Img(id='example',style={"width": "100%"})])
                    
                    ])
            ]
        )
        
        contenido = html.Div([list_group])
    return contenido

@app.callback(
    [Output('content-heli','children')],
    [Input('dropdown_volcanes_heli','value')]    
)
def content_camaras(volcan):
    print(volcan)
    div_camaras = dbc.Card([dbc.CardImg(alt='Sin Cámara',id='cardfija',src=app.get_asset_url('liveHeli/'+volcan+'.png?random='+str(random())))     
                              ],style={"width": "100%"})

        
    content = dbc.Card([dbc.CardHeader('Últimos datos cargados'),
                              dbc.CardBody(dcc.Loading(className="loading-container",id='loading-card_listaeventos',type='circle',
                                                       
                                                       children=html.Div(div_camaras,style={'height':'100%'})),id='bodyevssinloading')
                              ],outline=True,color='light',className='m-1',style={'height':'100%'})
    
    return [content]

@app.callback(
    Output('example', 'src'), # src attribute
    [Input('od_ir', "n_clicks")],
    [State('od_minuto','value'),State('od_hora','value'),State('od_freq','value'),State('od_volcan','value'),State('od_fi','value')],
    
    prevent_initial_callback=True
)
def update_figure(ir,minutos,horas,freqs,vol,fi):
    from datetime import timedelta,datetime
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id']
    if trigger=='od_ir.n_clicks':
        if fi is not None:
            ahora = datetime.utcnow()
            fechafin = datetime.strptime(fi,'%Y-%m-%dT%H:%M')+timedelta(hours=horas)
            fechaini = datetime.strptime(fi,'%Y-%m-%dT%H:%M')
            if fechafin < ahora:
                import sys
                import base64
                print(type(fechaini))
                sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
                import ovdas_imageProc_lib as ima
                buf = ima.odHeli(minutos,horas,5,freqs[0],freqs[1],10,vol,fechaini)
                data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
                return "data:image/png;base64,{}".format(data)