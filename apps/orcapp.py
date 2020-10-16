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
import datetime as dt
fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=2), '%Y-%m-%d')

def get_usgs(fini,ffin):
    #SISMOS USGS
    import json
    import urllib
    import pandas as pd
    import datetime
    usgs = json.load(urllib.request.urlopen('https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime='+fini+'%2000:00:00&endtime='+ffin+'%2023:59:59&maxlatitude=-61.71&minlatitude=-62.855&maxlongitude=-56.689&minlongitude=-59.985&minmagnitude=0&orderby=time'))
    df=[]
    for i in range(len(usgs['features'])):
        ev = pd.DataFrame(usgs['features'][i]['properties'],index=[i])
        ev['lon'] = usgs['features'][i]['geometry']['coordinates'][0]
        ev['lat'] = usgs['features'][i]['geometry']['coordinates'][1]
        ev['z'] = usgs['features'][i]['geometry']['coordinates'][2]
        ms = usgs['features'][i]['properties']['time']
        ev['fecha']= datetime.datetime.utcfromtimestamp(ms//1000).replace(microsecond=ms%1000*1000)
        df.append(ev)
    df = pd.concat(df)
    return df

freqconteo = dcc.Dropdown(id='freqconteo',
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


fechas_picker = dcc.DatePickerRange(
    id='fechas',
    start_date_placeholder_text="Inicio",
    end_date_placeholder_text="Final",
    calendar_orientation='vertical',
    display_format='Y-MM-DD',
    start_date=fini,
    end_date=ffin,
    min_date_allowed='2020-08-28',
    max_date_allowed=ffin,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)  

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
counter_imggif = dcc.Interval(
          id='interval-component-gif',
          interval=60*1000*5, # in milliseconds
          n_intervals=0
      )
counter_reloj = dcc.Interval(
          id='interval-component-reloj',
          interval=60*1000, # in milliseconds
          n_intervals=0
      )

def crear_figura(rangef,fini,ffin,countev_period):
    if countev_period=='H':name='ev/hora'
    elif countev_period=='D':name='ev/día'
    ffinxaxis = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    df = pd.read_pickle('//172.16.40.10/Sismologia/OVV/Orca/Orca.pkl')
    df = df.set_index('inicio')
    df_x_ev = df.copy()

    df = df.resample(countev_period).count()
    df = df.rename(columns={'ampl':name})
    df.index = df.index.rename('Fecha (día)')
    df['cumsumev']=df[name].cumsum()
    
    df_RSAM = fut.get_fastRSAM2(fini,ffin,'JUB',rangef[0],rangef[1],1,True,'15T')               
    
    fig = make_subplots(rows=4, cols=1,shared_xaxes=True, vertical_spacing=0.02)
    fig.add_trace(
    go.Bar( x=df.index, y=df[name],marker= { "color" : 'white'},name=name),
    row=1, col=1
    )

    
    fig.add_trace(
    go.Scattergl( x=df.index, y=df['cumsumev'],name='Acum. '+name,line=dict(color='crimson')),
    row=1, col=1
    )
    
    
    fig.add_trace(
    go.Scattergl( x=df_x_ev.index, y=df_x_ev['ampl'], mode='markers',name='Amplitud',
               marker= {"size":df_x_ev['ampl'], "color" : 'black'}),
    row=2, col=1
    )
    
    fig.add_trace(
    go.Scattergl( x=df_x_ev.index, y=df_x_ev['duracion'], mode='markers',name='Duración',
               marker= {"size":8, "color" : 'white'}),
    row=3, col=1
    )
    
    fig.add_trace(
    go.Scattergl( x=df_RSAM.index, y=df_RSAM.fastRSAM, mode='markers',name='RSAM',
               marker= {"size":8, "color" : 'white'}),
    row=4, col=1
    )
    


    fig['layout']['xaxis']['tickfont']['color']='rgba(0,0,0,0)'
    fig['layout']['xaxis4']['range']=[fini,ffinxaxis]
    

    import numpy as np
    ampslogs=np.power(df_x_ev['ampl'],0.2)/1

    fig.update_traces(opacity=0.75,marker=dict(color='white',size=ampslogs,line=dict(color='crimson',width=0)),
                  row=2,
                  )
    fig.update_traces(opacity=0.5,marker=dict(color='white',size=3,line=dict(color='crimson',width=0)),
                  row=3,
                  )
    fig.update_traces(opacity=0.5,marker=dict(color='white',size=5,line=dict(color='crimson',width=0)),
                  row=4,
                  )
    
    fig['data'][1].update(yaxis='y5')
    fig['layout']['yaxis5']=dict(overlaying='y1',side='right',title='Acum. '+name,title_font=dict(color='crimson'))
    
    
    
    fig.update_yaxes(title_text=name, row=1)
    fig.update_yaxes(title_text="um/s", row=2)
    fig.update_yaxes(type="log",row=2)
    fig.update_yaxes(type="log",row=4,range=[-2,5])
    fig.add_annotation(go.layout.Annotation(x=0.01,y=0.75,font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='paper',text='Amplitud/ev',showarrow=False))

    fig.update_yaxes(title_text="s", row=3)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df_x_ev['duracion']),font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y3',text='Duración/ev',showarrow=False))
    
    
    fig.update_yaxes(title_text="um/s", row=4)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=4,font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y4',text='RSAM '+str(rangef[0])+ ' - '+ str(rangef[1])+ ' Hz',showarrow=False))

    fig.update_xaxes(title_text="Fecha", row=4)
  

    #fig = px.bar(df, x=df.index, y=df['ev/hora'],color_discrete_sequence =['white']*len(df))
    fig.layout.template = 'plotly_dark'
    fig.update_layout(bargap=0,margin={"r":1,"t":25,"l":1,"b":1},
                      
    
    title={
    'text':'Detección automática de eventos - Volcán Orca',
    'y':0.98,
    'x':0.5,
    'xanchor':'center',
    'yanchor':'top'
    },
    showlegend=False
    )
    return fig


PLOTLY_LOGO = app.get_asset_url('img/orca_volcano.fw.jpg?random='+str(random()))       
navbar = dbc.Navbar(
[
html.A(
    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=2),
            dbc.Col(dbc.NavbarBrand("Monitoreo sísmico automático -Volcán Orca - OVV",style={'color':'white'}),width=9),
            dbc.Col(dbc.Button("Ovdapp", color="primary",outline=True, className="mr-1",id='volver-home',href='http://172.16.47.23:8080/'),width=1)
            
        ],
        align="left",
        no_gutters=True,
    )
,style={'width':'100%'})
],
color="#141d26"

)
      


def dibujar_mapa(fi,ff):
    usgs = get_usgs(fini, ffin)
    #tileurl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    tileurl =  'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}'
    escala = dl.ScaleControl()
    
    
    names = ['PMSZ','JUBZ','ESPZ']
    lons = [-64.0489,-58.662700,-56.9963]
    lats  = [-64.7744,-62.237300,-63.3981]
    alts = [40,16,31]
    dist = [25,129,384]
    df = pd.DataFrame([names,lons,lats,alts,dist]).T
    df = df.rename(columns={0:'cod',1:'lon',2:'lat',3:'alt',4:'dist'})
    estaciones = []
    iconUrl_esta = app.get_asset_url('img/triangle.fw.png?random='+str(random())) 

    for index,row in df.iterrows():
        popup = dl.Popup(html.Table(
                              [html.Tr([html.Td('Estación :'),html.Td(row.cod)])]+
                              [html.Tr([html.Td('Longitud :'),html.Td(row.lon)])]+
                              [html.Tr([html.Td('Latitud :'),html.Td(row.lat)])]+
                              [html.Tr([html.Td('Altitud (msnm) :'),html.Td(row.alt)])]+
                              [html.Tr([html.Td('Dist. a Vn. Orca (km):'),html.Td(row.dist)])]
        
                              
                                              ))
        estaciones.append(dl.Marker(position=[row.lat,row.lon],id=row.cod,children=[popup],
                                    icon=dict(iconUrl=iconUrl_esta, iconSize=[30,30],iconAnchor=[15, 15])))
    eq_usgs=[]
    for index,row in usgs.iterrows():
        popup2 = dl.Popup(html.Table(
                      [html.Tr([html.Td('Fecha (UTC)'),html.Td(str(row.fecha)[0:19])])]+
                      [html.Tr([html.Td('Profundidad'),html.Td(str(row.z)+ ' km')])]+
                      [html.Tr([html.Td('Mag'),html.Td(row.mag)])]+
                      [html.Tr([html.Td('Tipo mag'),html.Td(row.magType)])]+
                      [html.Tr([html.Td('+ info'),html.Td(dcc.Link('USGS',href=row.url,target='_blank',style={'color':'white','text-decoration':'underline'}))])]

                      
                                      ))
        eq_usgs.append(dl.CircleMarker(center=[row.lat,row.lon],
                                   radius=row.mag*1.5,
                                   color='#ffffff',
                                   fillColor='red',
                                   weight=1,
                                   fillOpacity=0.5,
                                   children=[popup2]
                                   ))
    
    iconUrl_volcan = app.get_asset_url('img/star.fw.png?random='+str(random())) 
    orca = dl.Marker(position=[-62.431719,-58.40589],children=[dl.Popup(html.Table([html.Tr([html.Td('Volcán Orca')])]))],
                                    icon=dict(iconUrl=iconUrl_volcan, iconSize=[30,30],iconAnchor=[15, 15]))
    mapa = dl.Map([dl.TileLayer(id="tiles", url=tileurl),escala,*estaciones,*eq_usgs,orca],
                  style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"},
                    center=[-62.431719,-58.40589],zoom=7,id='mapaloc')
    
    return mapa

controles = html.Div([
    html.Div(html.P(' Rango de frecuencias RSAM',id='RSAM-range-display')),
    dcc.RangeSlider(
        id='RSAM-range-slider',
        min=0.5,
        max=10,
        step=0.5,
        value=[0.5,5],
        marks=arange(0,11,1)),
    html.Div(html.P('Intervalo de fechas',id='titulo-fecha')),
    fechas_picker,
    html.Div(html.P('Periodo de conteo de eventos',id='titulo-fecha')),
    freqconteo,
    html.Div(dbc.Button("Enviar", color="primary", id="submit-filtro"),style={'text-align':'right'},className='m-1')
    
    
    ])





controlescard = dbc.Card([
    dbc.CardHeader('Opciones de gráficos'),
    dbc.CardBody(controles,id='controles')
    
    ],outline=True,color='light')

banner_inferior = dbc.Card([
    dbc.CardHeader('Fecha y Hora actual (UTC)'),
    dbc.CardBody('',id='live-update-text')
    
    ],outline=True,color='light')


layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col([dcc.Loading(html.Div(id='colgrafica'))],width=6),
                                   dbc.Col([dcc.Loading(html.Div(id='colmapa'))],width=3)]),
                   dbc.Row([counter_imggif,counter_reloj],no_gutters=True,justify='start'),
                   
                   ])

@app.callback(
    [Output("colgrafica", "children"),Output("colmapa", "children")],
    [Input('interval-component-gif', 'n_intervals'),Input("submit-filtro", "n_clicks")],
    [State('RSAM-range-slider', 'value'),State('fechas','start_date'),State('fechas','end_date'),State('freqconteo','value')]
)
def update_cam_fija(n,click,rangef,fini,ffin,freqconteo):
    fig = crear_figura(rangef,fini,ffin,freqconteo)
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

    mapa  = dibujar_mapa(fini, ffin)
    mapacard = dbc.Card([
        dbc.CardHeader('Localizaciones USGS'),
        dbc.CardBody(mapa)
        
        ],outline=True,color='light')

    return [graficocard],[mapacard]

'''
@app.callback([Output(marker.id, "children") for marker in estaciones],
              [Input(marker.id, "n_clicks") for marker in estaciones])
def marker_click(*args):
    contenido = [
                  dl.Popup(html.Table(
                      [html.Tr([html.Td('Estación :'),html.Td(df[df.cod==marker.id].cod)])]+
                      [html.Tr([html.Td('Longitud :'),html.Td(df[df.cod==marker.id].lon)])]+
                      [html.Tr([html.Td('Latitud :'),html.Td(df[df.cod==marker.id].lat)])]+
                      [html.Tr([html.Td('Altitud (msnm) :'),html.Td(df[df.cod==marker.id].alt)])]+
                      [html.Tr([html.Td('Dist. a Vn. Orca (km):'),html.Td(df[df.cod==marker.id].dist)])]

                      
                                      ))
        

                 for marker in estaciones]
    return contenido
'''

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component-reloj', 'n_intervals')])
def update_date(n):
    from flask import request
    print('tic! from '+request.remote_addr)
    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})]