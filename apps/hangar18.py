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
app.config.suppress_callback_exceptions = True
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
        html.H2("Hangar 18", className="display-4"),
        html.Hr(),
        html.P(
            "Información crítica asociada al monitoreo 24/7", className="lead"
        ),
        dbc.ButtonGroup(
    [
        dbc.Button("Inicio",id='inicio-button-hangar18'),
        dbc.Button("Criterios REAV",id="seccion-reavs-hangar18"),
        dbc.Button("Instrucciones RAV 2020",id="seccion-RAV2020-hangar18")
    ],
    vertical=True,style={'width':'100%'}
),
    ],
    style=SIDEBAR_STYLE,
)




content = html.Div(id="contenido-hangar18", style=CONTENT_STYLE)

layout = html.Div([sidebar, content])


@app.callback(
    Output("contenido-hangar18", "children"), 
    [Input("inicio-button-hangar18", "n_clicks"),Input("seccion-reavs-hangar18", "n_clicks"),
     Input("seccion-RAV2020-hangar18", "n_clicks")]
)
def on_button_click(n_inicio,n_reavs,n_rav2020):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if (button_id == "inicio-button-hangar18") or (ctx.triggered[0]['prop_id'] =='.'):
        return "Bienvenido!"
    elif button_id == "seccion-reavs-hangar18":
        
        lista_criterios_general = dbc.ListGroup(
    [
        dbc.ListGroupItem("Registro de un evento sísmico tipo VT o HB con un valor de magnitud local (ML) igual o superior a 3.0", color="info"),
        dbc.ListGroupItem(("Registro de un evento sísmico tipo LP, EX, TR, TO,"+ 
                          "VLP o HB con un valor de desplazamiento reducido (DR) igual o superior a 500 cm*cm"), color="info"),
        dbc.ListGroupItem("Registro de un enjambre sísmico, es decir, la clasificación de 100 eventos sísmicos distribuidos en un periodo de tres horas", color="info")
    ]
    )

        lista_criterios_NevChillan = dbc.ListGroup( [html.H5("C.V. Nevados de Chillán"),
        dbc.ListGroupItem("Emisión de columna eruptiva por sobre los 2000 m sobre el punto de emisión", color="info")])
        lista_criterios_Villarrica = dbc.ListGroup( [html.H5("Vn. Villarrica"),
        dbc.ListGroupItem("Registro de material particulado en columna de desgasificación (inclusive incandescencias nocturnas con emisiones pulsátiles)", color="info"),
        dbc.ListGroupItem("Registro de un evento sísmico tipo LP, EX, TR, TO, VLP o HB con un desplazamiento reducido (DR) igual o superior a 30 cm*cm", color="info")
        
        ])                                             
        lista_criterios_particular = dbc.ListGroup(
            dbc.ListGroupItem(
                    [
                        
                              lista_criterios_NevChillan,
                              lista_criterios_Villarrica
           ,
                    ]
                )
  
    )
            
        list_group = dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    [
                        html.H5("Criterios EN GENERAL (para todos los sistemas volcánicos)"),
                        lista_criterios_general,
                    ]
                ),
                dbc.ListGroupItem(
                    [
                        html.H5("Criterios EN PARTICULAR (para un sistema volcánico en específico)"),
                        lista_criterios_particular
                    ]
                ),
            ]
        )
        
        contenido = html.Div([list_group])
        
    elif button_id == "seccion-RAV2020-hangar18":
        texto=dcc.Markdown('''
                           
#### Pasos para una correcta generación del RAV mensual 2020
##### Versión 1.0 -  2 de noviembre de 2020

* Diseñar portada
    * Comprobar que en  ```\\172.16.40.10\Sismologia\pyOvdas_lib\templates\portadasRAV ``` 
    esté el archivo RAV_yyyymm.jpg y RAV_yyyymm_cp.jpg (portada y contraportada)
        > (yyyymm corresponde a año y mes, ej. 202010 para octubre de 2020)

    * Este archivo es recomendarlo guardarlo en png y en jpg (Versión editable y versión liviana para el RAV), el png queda guardado en la subcarpeta "png"
    * Yo uso como editor Adobe Fireworks CS6 (en la carpeta sismología/software está)
* Glosarios
    * Los glosarios no debieran tener cambios de forma periodica, pero de todas formas estos se encuentran en la ruta ```\\172.16.40.10\Sismologia\pyOvdas_lib\templates\glosarios```
    * Ambos son utilizados directamente en .png por el RAV (falta pasar a jpg)
    > REVISAR ORTOGRAFÍA DE AMBAS IMAGENES
                            
* Una vez comprobada la existencia de estas figuras, se procede a ejecutar desde spyder la siguente instrucción: 
   ```py                  
      import sys
      import os
      sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
      import ovdas_reportes_scripts as reportes
      reportes.RAV2020('yyyy-mm') 
   ```
   
(nuevamente, yyyy-mm corresponde a año-mes, ejemplo: reportes.RAV2020('2020-10') para octubre de 2020

                           
NOTA ACLARATORIA: ESTE PASO DE GENERACIÓN DEL RAV AÚN SE PREFIERE REALZIAR DE FORMA LOCAL Y NO EL EL OVDAPP, DEBIDO A QUE ES UN PASO QUE TOMA MEDIA HORA, Y DE FORMA LOCAL ES MÁS FÁCIL DE REVISAR POR POSIBLES ERRORES
                            
* Una vez generado el archivo 
    * Agregar páginas de contenido de cada volcán destacado
                            	En este paso, se debe adicionar todo el contenido extra que se crea necesario (descripcion de acividad desde todas las áreas, mapas de peligro, etc, etc, etc). Ojalá manteniendo la simplicidad en el texto y con el apoyo de toda 
                            	imagen que se crea necesaria.
    * En word, agregar numero de página AL COSTADO DE LA PÁGINA, para no interferir con el pie de página del servicio
    * Agregar Tabla de contenidos: En la página que el RAV ya posee con con banner de "Tabla de contenidos" agregar la tabla (índice) que word permite construir
    * Exportar a PDF
    * Listo!
                           
                           ''')
        
        contenido = html.Div([texto])
    return contenido
   