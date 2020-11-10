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
horas=2
fini = dt.datetime.strftime((dt.datetime.utcnow() - dt.timedelta(days=7)).replace(day=1,minute=0,second=0,microsecond=0),'%Y-%m-%d')
ffin = dt.datetime.strftime(dt.datetime.utcnow(),'%Y-%m-%d')
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

volcanes = volcanes[volcanes.nombre_db.isin(['Villarrica','NevChillan'])]

lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan) 
freqconteo = dcc.Dropdown(id='freqconteo-fastrsam',
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

volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes-fastrsam',
    options=lista_volcanes,
    value='Villarrica',
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)




fechas_picker = dcc.DatePickerRange(
    id='fechas-fastrsam',
    start_date_placeholder_text="Inicio",
    end_date_placeholder_text="Final",
    calendar_orientation='vertical',
    display_format='Y-MM-DD',
    start_date=fini,
    end_date=ffin,
    min_date_allowed='2010-01-01',
    max_date_allowed=ffin,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                      'width':'100%'
                                    } 
)  

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
counter_imggif = dcc.Interval(
          id='interval-component-gif-fastrsam',
          interval=60*1000*5, # in milliseconds
          n_intervals=0
      )
counter_reloj = dcc.Interval(
          id='interval-component-reloj-fastrsam',
          interval=60*1000*1, # in milliseconds
          n_intervals=0
      )



def crear_fastRSAM(RSAM,volcan,fechai,fechaf,freqi,freqf):
    voldata = gdb.get_metadata_volcan(volcan)
    voldata = voldata.drop_duplicates(subset='nombre', keep="first")
    red = gdb.get_metadata_wws(volcan='*')
    red = red[(red.nombre_db==volcan) & (red.tipo=='SISMOLOGICA') & (red.cod.str.startswith('S')==True)]
    import locale     
    locale.setlocale(locale.LC_ALL, 'es_ES')
    colors = px.colors.qualitative.Plotly
    
    fig = make_subplots(rows=2, cols=1,vertical_spacing=0.025,shared_xaxes='all')
    i=0
    
    for sta in list(RSAM.columns):
        data = RSAM[sta]
        fig.add_trace(go.Scattergl(x=data.index, y=data.values,name=sta,mode='markers',marker_size=5,opacity=0.2,
                                   hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',marker_color=colors[i]),row=1, col=1) 
        fig.add_trace(go.Scattergl(x=data.index, y=RSAM[sta].rolling(10).mean(),name=sta+' 10 MM',mode='lines',line_width=0.5,
                                    hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',line_color=colors[i]),row=1, col=1) 
        i+=1
    
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    fig.update_xaxes(
        tickformatstops = [
            dict(dtickrange=[None, 1000], value="%H:%M:%S.%L<br>%y-%m-%d"),
            dict(dtickrange=[1000, 60000], value="%H:%M:%S<br>%y-%m-%d"),
            dict(dtickrange=[60000, 604800000], value="%H:%M<br>%y-%m-%d"),
            dict(dtickrange=[604800000, "M1"], value="%y-%m-%d"),
            dict(dtickrange=["M1", "M12"], value="%y-%m"),
            dict(dtickrange=["M12", None], value="%y-%m")
        ]
    )
    fig.layout.template = 'plotly_dark'
    fig.update_yaxes(title_font=dict(size=14),title_text='RSAM - um/s',fixedrange=True)
    fig.update_xaxes(title_font=dict(size=14),title_text='Fecha')
    fig.update_xaxes(range=[min(data.index),max(data.index)],col=1,row=1)
    fig.update_yaxes(range=[0,RSAM.max().max()*1.1],col=1,row=1)
    fig.update_xaxes(tickfont=dict(size=12))    
    fig.update_layout(
        font=dict(
            family="Tahoma",
            size=18,
            ),
        title={
            'text': "RSAM Rápido - "+str(freqi)+" - "+str(freqf)+" Hz - "+voldata.vol_tipo.iloc[0]+' '+voldata.nombre.iloc[0],
            'y':0.97,
            'x':0.5,
            
            'xanchor': 'center',
                'yanchor': 'top'})
    
    redRE = red[red.codcorto.isin(RSAM.columns)].sort_values(by='distcrater', ascending=True)
    estaRE =list(redRE.codcorto)
    df_RE = []
    
    for i in range(0,len(estaRE)):
        for j in range(i+1,len(estaRE)):
            esta1=estaRE[i]
            esta2=estaRE[j]
            df = (RSAM[esta1]/RSAM[esta2])
            df = df.rename(esta1+'_'+esta2)
            df_RE.append(df)
    df_RE = pd.concat(df_RE,axis=1)
    for sta in list(df_RE.columns):
        data = df_RE[sta]
        fig.add_trace(go.Scattergl(x=RSAM.index, y=data.values,name=sta,mode='markers',marker_size=5,opacity=0.2,
                                   legendgroup="Razón RSAM",hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',marker_color=colors[i]),row=2, col=1) 
        fig.add_trace(go.Scattergl(x=RSAM.index, y=data.rolling(10).mean(),name=sta+' 10 MM',mode='lines',line_width=0.5,
                                    legendgroup="Razón RSAM",hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',line_color=colors[i]),row=2, col=1) 
        i+=1
    

    return fig


PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("Proyecto de monitoreo sísmico automático OVV - RSAM Rápido",style={'color':'white'}),width=10),
            dbc.Col(dbc.Button("Ovdapp", color="primary",outline=True, className="mr-1",id='volver-home',href='http://172.16.47.23:8080/'),width=1)
            
            
        ],justify="left",
    style={'width':'100%'})

],
color="#141d26",

)
      




controles = html.Div([
    html.Div(volcan_selector),
    html.Div(html.P('Intervalo de fechas',id='titulo-fecha-fastrsam')),
    fechas_picker,
    html.Div(html.P('Frecuencia de filtrado',id='titulo-fecha-fastrsam')),
    dcc.RangeSlider(
        id='RSAM-range-slider-fastrsam',
        min=0.5,
        max=10,
        step=0.5,
        value=[0.5,5],
        marks=arange(0,11,1)),
    html.Div(dbc.Button("Enviar", color="primary", id="submit-filtro-fastrsam"),style={'text-align':'right'})

    ])





controlescard = dbc.Card([
    dbc.CardHeader('Opciones'),
    dbc.CardBody(controles,id='controles-fastrsam')
    
    ],outline=True,color='light')

banner_inferior = dbc.Card([
    dbc.CardHeader('Fecha y Hora actual (UTC)'),
    dbc.CardBody('',id='live-update-text-fastrsam')
    
    ],outline=True,color='light')


layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col([html.Div(id='colgrafica-fastrsam')],width=9)
                                   ]),
                   dbc.Row([counter_imggif,counter_reloj],no_gutters=True,justify='start'),
                   
                   ])

@app.callback(
    #[Output("colgrafica-fastrsam", "children"),Output("colmapa-fastrsam", "children")],
    [Output("colgrafica-fastrsam", "children")],
    [Input('interval-component-gif-fastrsam', 'n_intervals'),Input("submit-filtro-fastrsam", "n_clicks")],
    [State('RSAM-range-slider-fastrsam','value'),
     State('dropdown_volcanes-fastrsam','value'), State('fechas-fastrsam','start_date'),State('fechas-fastrsam','end_date')]
)
def update_cam_fija(*args):
    ffin=args[-1]
    fini=args[-2]
    volcan=args[-3]
    rangef=args[-4]

    red = gdb.get_metadata_wws(volcan='*')
    red = red[(red.nombre_db==volcan) & (red.tipo=='SISMOLOGICA') & (red.cod.str.startswith('S')==True)]
    
    #%%
    RSAMS = []
    for esta in list(red.codcorto):
        try:
            df = fut.get_fastRSAM2(fini,ffin,esta,rangef[0],rangef[1],5,True,'15T')
            df = df.rename(columns={'fastRSAM':esta})
            RSAMS.append(df)
        except:
            ()
    RSAM = pd.concat(RSAMS,axis=1)    
    fig = crear_fastRSAM(RSAM,volcan,fini,ffin,rangef[0],rangef[1])
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



    #return [graficocard],[mapacard]
    return [graficocard]


@app.callback([Output('live-update-text-fastrsam', 'children'),Output('fechas-fastrsam','start_date'),Output('fechas-fastrsam','end_date'),
               Output('fechas-fastrsam','max_date_allowed'),
],
              [Input('interval-component-reloj-fastrsam', 'n_intervals')],
              [State('dropdown_volcanes-fastrsam','value')]
              )
def update_date(n,volcan):
    from flask import request
    print('tic! from '+request.remote_addr)
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')

    finidetect = dt.datetime.utcnow() - dt.timedelta(hours=horas)


    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})],fini,ffin,ffin
