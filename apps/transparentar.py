# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash
import json
from numpy import arange
import datetime
from random import random
from app import app
from dash.dependencies import Input, Output,State
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
import dash_daq as daq
from dash import dash_table,dcc,html
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan) 


df = pd.DataFrame()




loc_switch = daq.BooleanSwitch(id='loc-switch', on=True,labelPosition="right",
                               label={'label':'Shi','style':{'padding':'8px'}}) 

volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes-transparentar',
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
    id='fechas-transparentar',
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

tipoev_picker = dcc.Checklist(id='tipoev_check-transparentar',
    options=[
        {'label': 'VT', 'value': 'VT'},
        {'label': 'LP', 'value': 'LP'},
        {'label': 'TR', 'value': 'TR'},
        {'label': 'EX', 'value': 'EX'},
        {'label': 'HB', 'value': 'HB'},
        {'label': 'VD', 'value': 'VD'},
        {'label': 'TO', 'value': 'TO'},
        {'label': 'MF', 'value': 'MF'},
        {'label': 'LV', 'value': 'LV'}
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





PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("Ovdapp - TRANSPARENTAR",style={'color':'white'}),width=10),
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
    html.Tr([html.Td("¿Sólo sismos localizados?"), html.Td(loc_switch)
                ]),
    html.Div(dbc.Button("Enviar", color="primary", id="submit-transparentar"),style={'text-align':'right'})

    ])





controlescard = dbc.Card([
    dbc.CardHeader('Opciones'),
    dbc.CardBody(controles,id='controles-sismodb')
    
    ],outline=True,color='light')


banner_inferior = dbc.Card([
    dbc.CardHeader('Resultados de la búsqueda'),
    dbc.CardBody(children=[''],id='resultados-transparentar')
    
    ],outline=True,color='light')



layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col(children=[dcc.Loading(html.Div(id='col-datatable'))],width=9)
                                   ]),
                   dbc.Row([counter_imggif,counter_reloj],no_gutters=True,justify='start'),
                   html.Div(id='cajita-transparentar', style={'display': 'none'}),
                   dcc.Download(id="download_data-transparentar")
                   
                   ])


@app.callback(
    Output('loc-switch', 'label'),
    [Input('loc-switch', 'on')], prevent_initial_call=True
)
def update_output(value):
    if value==True:
        label={'label':'Shi','style':{'padding':'8px'}}
    else:
        label={'label':'Ño','style':{'padding':'8px'}}
    return label


@app.callback(
    [Output("col-datatable", "children"),
     Output('resultados-transparentar','children'),
     Output("cajita-transparentar", "children")
     
     ],

    [Input("submit-transparentar", "n_clicks")],
    [State('dropdown_volcanes-transparentar','value'),
     State('fechas-transparentar','start_date'),
     State('fechas-transparentar','end_date'),
     State('tipoev_check-transparentar','value'),
     State('loc-switch', 'on')
     ],
    prevent_initial_call=True
    )
def update_datatable(nclicks,volcan,fechai,fechaf,tipoevs_custom,locs):
    from collections import OrderedDict
    import numpy as np
    import sys; sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
    import ovdas_getfromdb_lib as gdb
    import pandas as pd
    pd.options.mode.chained_assignment = None  # default='warn'
    df_volcan=gdb.get_metadata_volcan("*")
    voldf = df_volcan[df_volcan.nombre_db==volcan].head(1)
    
    df=gdb.extraer_eventos(fechai, fechaf, volcan)
    
    df = pd.DataFrame(df)
    df = df[df.tipoevento.isin(tipoevs_custom)]
    if locs==True:

        df['profundidad_kmbnm']=np.round((-voldf.nref.iloc[0]/1000)+df['profundidad'],1)
        
        df.loc[df.calidad=='D1',['latitud','longitud','profundidad','magduracion','nfases','gap',
                                 'distmedia','rms','erh','erz','nestaciones','ml','prof_kmbnm',
                                 'id_loc','tiempo_origen','tipoloc','dr','energia','direccion',
                                 'distancia','calidad']]=np.nan        
        df = df[['fecha','tipoevento','unixtime','s_p','duracion','frecuencia',
                 'latitud','longitud','profundidad_kmbnm','nfases','gap','distmedia',
                 'rms','erh','erz','calidad','nestaciones','ml','comp','tiempo_origen']]  
        df = df[df.ml>0]
        
    
    df.fecha =df.fecha.round('S')
    
    
    
    df = df.rename(columns={'latitud':'latitud (°)',
                'longitud':'longitud (°)',
                'profundidad_kmbnm':'prof. (kmbnm)',
                'erh':'error hor. (km)',
                'erz':'error ver. (km)',
                'ml':'ML',
                'gap':'Gap (°)',
                'tipoevento':'Tipo'
                })
    
    

    if (len(df)>0) and (len(df)<99999):
        dfshow = df.head(20).sort_index(ascending=False)
        texto=html.Div([
            html.Div(children=['Se encontraron '+str(len(df))+' sismos, mostrando máximo los 20 últimos registros.']),
            html.Div(dbc.Button("Descargar datos", color="primary", id="download-transparentar"),style={'text-align':'right'})

            
            ])
    elif len(df)>100000:
        dfshow = df.head(20).sort_index(ascending=False)
        texto='Se econtraron mas de 100.000 sismos, trate con un periodo de tiempo menor (un año?). Mostrando máximo los 20 últimos registros.'
    else:
        texto='Sin resultados =('
    return [dash_table.DataTable(
        
        columns=[{"name": i, "id": i} for i in df.columns],
        data=dfshow.to_dict(into=OrderedDict,orient='records'),
        style_table={'overflowX': 'auto'},
        
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white'
    },
    style_data={ 'selectColor':'white',
                'selectBackgroundColor':'white',
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white'
    },
        
        
        )],texto,df.to_json()
    
    
@app.callback([Output('fechas-transparentar','start_date'),Output('fechas-transparentar','end_date'),
               Output('fechas-transparentar','max_date_allowed'),
],
              [Input('url','href')]
              )
def update_date(href):
    from flask import request
    print('tic! from '+request.remote_addr)
    fini = dt.datetime.strftime((dt.datetime.utcnow() - dt.timedelta(days=365)).replace(day=1), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return fini,ffin,ffin




@app.callback(
Output("download_data-transparentar", "data"),
[Input("download-transparentar", "n_clicks")],
[State('cajita-transparentar', 'children')],
prevent_initial_call=True
)
def download_transparentar(n_clicks,df):
     
    if n_clicks is not None:
        if dash.callback_context.triggered[0]['prop_id'] =='download-transparentar.n_clicks':
            df = pd.read_json(df)
            if len(df)>200:
                return dcc.send_data_frame(df.to_csv, "mydf.csv")
            else:
                return dcc.send_data_frame(df.to_excel, "mydf.xlsx")
        else:
            dash.no_update
    

    
