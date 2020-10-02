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
fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=2), '%Y-%m-%d')
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

volcanes_auto=['Villarrica']
volcanes_list=[]
for volcan in volcanes_auto:
    volcanes_list.append({'label': volcanes[volcanes.nombre_db==volcan].nombre.iloc[0],'value':volcanes[volcanes.nombre_db==volcan].nombre_db.iloc[0]})

volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes',
    options=volcanes_list,
    value='Villarrica',
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)


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

fechas_picker = dcc.DatePickerRange(
    id='fechas-autovdas',
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
          id='interval-component-gif-autovdas',
          interval=60*1000*5, # in milliseconds
          n_intervals=0
      )
counter_reloj = dcc.Interval(
          id='interval-component-reloj-autovdas',
          interval=60*1000, # in milliseconds
          n_intervals=0
      )

def crear_figura(rangef,fini,ffin,volcan,estaRSAM):
    
    markersize=4
    ffinxaxis = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    df_count,df = oap.get_pickle_OVV(volcan,fini,ffin)

    df_RSAM = fut.get_fastRSAM2(fini,ffin,estaRSAM,rangef[0],rangef[1],1,True,'15T')               
    import numpy as np
    #ampslogs=np.power(df['ampl'],0.2)/1
    tipoevs = len(df.tipoev.unique())
    
    fig = make_subplots(rows=tipoevs+5, cols=1,shared_xaxes=True, vertical_spacing=0.02)
    
    i=1
    for tipoev in df.tipoev.unique():
        fig.add_trace(
        go.Bar( x=df_count.index, y=df_count[tipoev],marker= { "color" : 'white'},name='Ev/hora'),
        row=i, col=1
        )
        fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df_count[tipoev]),font=dict(color='white'),
                                            xanchor='left',yanchor='bottom',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text=tipoev+'/hora',showarrow=False))      
        
        fig.add_trace(
        go.Scattergl( x=df_count.index, y=df_count[tipoev+'cumsum'],name='Acum. ev/hora',line=dict(color='crimson')),
        row=i, col=1
        )
        i+=1
    ##########################RSAM
    fig.add_trace(
    go.Scattergl( x=df_RSAM.index, y=df_RSAM.fastRSAM, mode='markers',name='RSAM',
               marker= {"size":markersize, "color" : 'white'}),
    row=i, col=1
    )   
    fig.update_traces(opacity=0.5,marker=dict(color='white',size=markersize,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(row=i,range=[0,max(df_RSAM.fastRSAM)*1.5])
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df_RSAM.fastRSAM)*1.5,font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='RSAM ('+estaRSAM+') '+str(rangef[0])+ ' - '+ str(rangef[1])+ ' Hz',showarrow=False))
    i+=1
    #######################DR

    fig.add_trace(
    go.Scattergl( x=df.index, y=df['DRc'], mode='markers',name='DR',
               marker= {"size":markersize, "color" : 'white'}),
    row=i, col=1
    )
    fig.update_traces(opacity=0.5,marker=dict(color='white',size=markersize,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(title_text="cm*cm", row=i)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df['DRc']),font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='DR/ev',showarrow=False))  
    
    i+=1
    #######################freq

    fig.add_trace(
    go.Scattergl( x=df.index, y=df['fdom'], mode='markers',name='fdom',
               marker= {"size":markersize, "color" : 'white'}),
    row=i, col=1
    )
    fig.update_traces(opacity=0.5,marker=dict(color='white',size=markersize,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(title_text="Hz", row=i)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=1,font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='Frecuencia dom/ev',showarrow=False))  
    fig.update_yaxes(type="log",row=i)
    fig.update_yaxes(row=i,range=[-1,1],dtick=1)
    i+=1
    #################################AMP
    fig.add_trace(
    go.Scattergl( x=df.index, y=df['ampl'], mode='markers',name='Amplitud',
               marker= {"size":markersize, "color" : 'black'}),
    row=i, col=1
    )
    fig.update_traces(opacity=0.75,marker=dict(color='white',size=markersize,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(title_text="um/s", row=i)
    #fig.update_yaxes(type="log",row=i)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df['ampl']),font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='Amplitud/ev',showarrow=False))  
    i+=1
    
    fig.add_trace(
    go.Scattergl( x=df.index, y=df['duracion'], mode='markers',name='Duración',
               marker= {"size":markersize, "color" : 'white'}),
    row=i, col=1
    )
    fig.update_traces(opacity=0.5,marker=dict(color='white',size=markersize,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(title_text="s", row=i)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df['duracion']),font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='Duración/ev',showarrow=False))  
   

    
    fig['layout']['xaxis']['tickfont']['color']='rgba(0,0,0,0)'
    fig['layout']['xaxis'+str(i)]['range']=[fini,ffinxaxis]
    
    fig.update_yaxes(title_text="um/s", row=i)
    fig.update_xaxes(title_text="Fecha", row=i)
    i+=1
    
    
    
    totalfilas = i
    j=1
    k=1    
 
    for tipoev in df.tipoev.unique():
        fig['data'][j].update(yaxis='y'+str(i))
        fig['layout']['yaxis'+str(i)]=dict(overlaying='y'+str(k),side='right',title='Acum. ev/hora',title_font=dict(color='crimson'))
        #fig.update_yaxes(title_text="ev/hora", row=j)
        i+=1
        j+=2
        k+=1
    

     
    
    
    fig.update_layout(bargap=0,margin={"r":1,"t":25,"l":1,"b":1},
                      
    
    title={
    'text':'Detección automática de eventos - '+volcanes[volcanes.nombre_db==volcan].vol_tipo.iloc[0]+' '+volcanes[volcanes.nombre_db==volcan].nombre.iloc[0],
    'y':0.98,
    'x':0.5,
    'xanchor':'center',
    'yanchor':'top'
    },
    showlegend=False
    )
    fig.layout.template = 'plotly_dark'
    return fig


PLOTLY_LOGO = app.get_asset_url('img/orca_volcano.fw.jpg?random='+str(random()))       
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=2),
            dbc.Col(dbc.NavbarBrand("Proyecto de monitoreo sísmico automático OVV",style={'color':'white'}),width=8)
            
            
        ],justify="left",
    )

],
color="#141d26",

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
                    center=[-62.431719,-58.40589],zoom=7,id='mapaloc-autovdas')
    
    return mapa

controles = html.Div([
    html.Div(volcan_selector),
    html.Div(html.P(' Rango de frecuencias RSAM',id='RSAM-range-display-autovdas')),
    dcc.RangeSlider(
        id='RSAM-range-slider-autovdas',
        min=0.5,
        max=10,
        step=0.5,
        value=[0.5,5],
        marks=arange(0,11,1)),
    html.Div(html.P('Intervalo de fechas',id='titulo-fecha-autovdas')),
    fechas_picker,
    html.Div(dbc.Button("Enviar", color="primary", id="submit-filtro-autovdas"),style={'text-align':'right'})
    
    
    ])





controlescard = dbc.Card([
    dbc.CardHeader('Opciones'),
    dbc.CardBody(controles,id='controles-autovdas')
    
    ],outline=True,color='light')

banner_inferior = dbc.Card([
    dbc.CardHeader('Fecha y Hora actual (UTC)'),
    dbc.CardBody('',id='live-update-text-autovdas')
    
    ],outline=True,color='light')


layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col([dcc.Loading(html.Div(id='colgrafica-autovdas'))],width=9)
                                   #dbc.Col([dcc.Loading(html.Div(id='colmapa-autovdas'))],width=3)
                                   ]),
                   dbc.Row([counter_imggif,counter_reloj],no_gutters=True,justify='start'),
                   
                   ])

@app.callback(
    #[Output("colgrafica-autovdas", "children"),Output("colmapa-autovdas", "children")],
    [Output("colgrafica-autovdas", "children")],
    [Input('interval-component-gif-autovdas', 'n_intervals'),Input("submit-filtro-autovdas", "n_clicks")],
    [State('dropdown_volcanes','value'), State('RSAM-range-slider-autovdas', 'value'),State('fechas-autovdas','start_date'),State('fechas-autovdas','end_date')]
)
def update_cam_fija(*args):
    ffin=args[-1]
    fini=args[-2]
    rangef=args[-3]
    volcan=args[-4]
    
    
    
    rsam_blacklist=['CRU','PIC','LAV','AGU','CR3','CVI']
    red = gdb.get_metadata_wws(volcan)
    red=red[red.tipo=='SISMOLOGICA']
    red['sensor'] = red.canal.str[1]
    red = red[red.sensor!='N']
    red=red[~red.codcorto.isin(rsam_blacklist)]
    red1 = red[red.referencia==1].sort_values(by='distcrater').head(1)# 1.referencia
    estaRSAM = red1.codcorto.iloc[0]
    
    
    fig = crear_figura(rangef,fini,ffin,volcan,estaRSAM)
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

    #return [graficocard],[mapacard]
    return [graficocard]


@app.callback(Output('live-update-text-autovdas', 'children'),
              [Input('interval-component-reloj-autovdas', 'n_intervals')])
def update_date(n):
    from flask import request
    print('tic! from '+request.remote_addr)
    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})]