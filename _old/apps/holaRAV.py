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
import ovdas_RAV2020_lib as rav2020
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
import datetime as dt
from random import random
from datetime import date
tileurl =  'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}'
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")
lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan)  

destacados_alertas = volcanes[volcanes.vol_alerta.isin([2,3,4])].nombre_db.unique()


modal_go = html.Div([Download(id="download-holaRAV"),dbc.Modal(
            [
                dbc.ModalHeader("Importante!"),
                dbc.ModalBody("This is the content of the modal",id='modalbody-holaRAV'),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-holaRAV", className="ml-auto")
                ),
            ],
            id="modal-holaRAV",
        )])

modal_go = dcc.Loading(modal_go, style={'position':'fixed','left':'50%','top':'50%'})

volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes-holaRAV',
    options=lista_volcanes,
    value=destacados_alertas,
    multi=True,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)

years = [{'label': year,'value':year} for year in range(2020,2022)]

year_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_year-holaRAV',
    options=years,
    value=2020,
    multi=False,
    searchable=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121'
                                    } 
)

month_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_month-holaRAV',
    options= [{'label': year,'value':year} for year in range(1,13)],
    value=10,
    multi=False,
    searchable=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121'
                                    } 
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

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Hola RAV", className="display-4"),
        html.Hr(),
        html.P(
            "Generador de RAV 2020", className="lead"
        ),
        html.H6('Volcanes destacados'),
        volcan_selector,
        html.H6('Fecha (año y mes)',style={'padding-top':'10px'}),
        dbc.Row([dbc.Col([year_selector]),dbc.Col([month_selector])],no_gutters=True),
        html.Div(dbc.Button("Generar RAV", color="primary", className="mr-1",id='ir-holaRAV',style={'width':'100%'}),style={'padding-top':'10px','width':'100%'})
        ,
    ],
    style=SIDEBAR_STYLE,
)




content = html.Div(id="contenido-holaRAV", style=CONTENT_STYLE)

layout = html.Div([sidebar, content,modal_go])

@app.callback([Output('modalbody-holaRAV','children'),Output("modal-holaRAV", "is_open"),Output("download-holaRAV", "data")],
              [Input('ir-holaRAV','n_clicks'), Input("close-holaRAV", "n_clicks")],
              [State('dropdown_month-holaRAV','value'),State('dropdown_year-holaRAV','value'),State("modal-holaRAV", "is_open")]
              ,prevent_initial_call=True
)
def lanzar_RAV(ir,close,month,year,is_open):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id']
    if trigger == 'ir-holaRAV.n_clicks':
        ultimo_mes = dt.date.today().replace(day=1)-dt.timedelta(days=1)
        fecha_select = dt.date(year,month,1)
        print(ultimo_mes,fecha_select)
        print(ultimo_mes > fecha_select)
        if (ultimo_mes > fecha_select)==True:
            print('Generando RAV')
            
            document,filename = rav2020.main('2020-09')
            def createrav(ruta):
                document.save(ruta)
  
            return 'Listo!', not is_open,send_bytes(createrav,filename)
        else:
            if fecha_select == ultimo_mes+dt.timedelta(days=1):
                print('Mes en curso')
                return "Mes en curso, faltan datos para RAV!", not is_open
            else:
                print('BASTA')
                return "¡De regreso al futuro! (fecha superior a hoy)", not is_open,dash.no_update
    elif trigger=='close-holaRAV.n_clicks':
        print('cerrado')
        return [],not is_open,dash.no_update
