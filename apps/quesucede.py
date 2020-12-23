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

def helicorder(horas,sta):
    import ovdas_WWS_lib as wws
    import ovdas_SeismicProc_lib as sp
    import datetime as dt
    ejex =30 #minutos en el eje x
    from datetime import timedelta
    import numpy as np
    fini = dt.datetime.utcnow() - dt.timedelta(hours=horas)
    ffin = dt.datetime.utcnow()
    finidetect = dt.datetime.utcnow() - dt.timedelta(hours=horas)
    subsample=10
    finiround = fini - (fini -fini.min) % timedelta(minutes=ejex)
    ffinround = ffin + (ffin.min - ffin) % timedelta(minutes=ejex)-timedelta(milliseconds=100)
    
    traza = wws.extraer_signal(estacion=sta,componente='Z',inicio=finiround,fin=ffin)
    flag = len(traza)
    traza = sp.filtrar_traza(traza,tipo="butter",orden=4,fi=0.4,ff=12)
    
    
    t_index = pd.date_range(start=finiround, end=ffinround, freq='100ms').round('100ms')
    times = []
    amps = []
    for i in range(0,len(traza)):
        times.extend(traza[i].times('timestamp'))
        amps.extend(traza[i].data*traza[i].stats.calib)
    times = np.around(times,2)
    amps = np.around(amps,2)
    df_traza = pd.DataFrame(amps,index=times)
    df_traza = df_traza[::subsample]
    df_traza['fecha_abs'] = pd.to_datetime(df_traza.index, unit='s')
    df_traza = df_traza.set_index('fecha_abs',drop=True)
    df_traza.index = df_traza.index.round('100ms')
    df_traza = df_traza[~df_traza.index.duplicated()]
    aer = df_traza.reindex(t_index)
    aer.index = aer.index.rename('fecha')
    aer = aer.rename(columns={0:'amp'})
    grp = aer.groupby(pd.Grouper(freq='30Min'))
    
    filas = []
    for key, df in grp:
        filas.append(df)

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=len(filas), cols=1,vertical_spacing=0)
    
    if len(amps)>0:
        fig = make_subplots(rows=len(filas), cols=1,vertical_spacing=0)
        maxy = abs(max(amps))*1.5
        scale=round(maxy/2)
        for i in range(0,len(filas)):
            if i==0:
                #escala
                
                
                lev = go.Scatter(x=[min(filas[i].index),min(filas[i].index)],y=[-scale,scale],
                                 showlegend=False,hoverinfo='x',line=dict(color='white',width=10))
                fig.add_annotation(go.layout.Annotation(x=min(filas[i].index),y=scale,font=dict(color='white'),
                                            xanchor='center',yanchor='bottom',xref='x1',
                                            yref='y'+str(i+1),text=str(scale*2)+' um/s',showarrow=False)) 
                fig.append_trace(lev,i+1,1)
            tituloy = str(min(filas[i].index))[11:16]
            if (tituloy in ['00:00','06:00','12:00','18:00']) or i==0:
                diatxt=str(min(filas[i].index))[8:10]+'-'+str(min(filas[i].index))[5:7]
                fig.add_annotation(go.layout.Annotation(x=-0.05,y=0.5,font=dict(color='white'),
                                            xanchor='right',yanchor='bottom',xref='paper',
                                            yref='y'+str(i+1),text=diatxt,showarrow=False)) 
            alertaplot = go.Scattergl(x=filas[i].index
                                      ,y=filas[i].amp,
                                      showlegend=False,
                                      hoverinfo='x+y',
                                      line=dict(color='rgba(66,155,245,1)',width=0.5)
                                      )
            fig.append_trace(alertaplot,i+1,1)
            fig.update_xaxes(showticklabels=False,range=[min(filas[i].index),max(filas[i].index)],row=i+1)
            fig.update_yaxes(row=i,range=[-scale,scale],showticklabels=False)
            fig.add_annotation(go.layout.Annotation(x=0,y=0,font=dict(color='white'),
                                            xanchor='right',yanchor='middle',xref='paper',
                                            yref='y'+str(i+1),text=tituloy,showarrow=False))  
        #for minu in range(0,35):
        #    fig.add_annotation(go.layout.Annotation(x=minu*0.1,y=0,font=dict(color='white'),
        #                                    xanchor='center',yanchor='top',xref='paper',
        #                                    yref='paper',text=str(minu),showarrow=False))  
            
        fig.update_yaxes(row=i+1,range=[-scale,scale],showticklabels=False)  
        fig.update_xaxes(row=i+1,tickformat="%M",showticklabels=False,title='Minutos')  
        
        fig.layout.template = 'plotly_dark'
        fig.update_layout(bargap=0,margin={"r":10,"t":25,"l":90,"b":30},
                        
        title={
        'text':'Estación '+sta,
        'y':0.99,
        'x':0.5,
        'xanchor':'center',
        'yanchor':'top'
        }
        )
    else:
        fig=[];flag=0
        
    grafico = html.Div(children=[
        dcc.Graph(
            id='timeline-orca',
            figure=fig,
            style={ 'height':'80vh' }
        )
    ])
    
    helicard = dbc.Card([
        dbc.CardHeader('Sismicidad'),
        dbc.CardBody(grafico)
        
        ],outline=True,color='light')

    return helicard
voldef='Villarrica'

volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

volcanes_list=[]
for index,row in volcanes.iterrows():
    volcanes_list.append({'label': row.nombre,'value':row.nombre_db})
    
volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes-quesucede',
    options=volcanes_list,
    value=voldef,
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)




sta_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_sta-quesucede',
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
counter = dcc.Interval(
          id='interval-component-quesucede',
          interval=60*1000*1, # in milliseconds
          n_intervals=0
      )

fechas_picker = dcc.DatePickerRange(
    id='fechas-quesucede',
    start_date_placeholder_text="Inicio",
    end_date_placeholder_text="Final",
    calendar_orientation='vertical',
    display_format='Y-MM-DD',
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                      'width':'100%'
                                    } 
) 
PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("Ovdapp - Qué Sucede? - Helicorder en línea con eventos clasificados",style={'color':'white'}),width=10),
            dbc.Col(dbc.Button("Ovdapp", color="primary",outline=True, className="mr-1",id='volver-home',href='/'),width=1)
            
            
        ],justify="left",
    style={'width':'100%'})

],
color="#141d26",

)

controles = html.Div([
    html.Div(volcan_selector),
    html.Div(sta_selector),
    html.Div(children=[dcc.Loading(children=[dbc.Button("Online", color="success", id="submit-realtime-quesucede", className="mr-1"),
             dbc.Button("Enviar", color="primary", id="submit-filtro-quesucede", className="mr-1")])],style={'text-align':'right'})
    
    
    ])

controlescard = dbc.Card([
    dbc.CardHeader('Opciones'),
    dbc.CardBody(controles,id='controles-quesucede')
    
    ],outline=True,color='light')

banner_inferior = dbc.Card([
    dbc.CardHeader('Fecha y Hora actual (UTC)'),
    dbc.CardBody('',id='live-update-text-quesucede')
    
    ],outline=True,color='light')

layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col([html.Div(id='helicorder-quesucede')],width=9)
                                   ]),
                   dbc.Row(counter,no_gutters=True,justify='start'),
                   
                   ])

@app.callback(
    #[Output("colgrafica-autovdas", "children"),Output("colmapa-autovdas", "children")],
    [Output("helicorder-quesucede", "children"),Output('interval-component-quesucede', 'disabled'),
     Output("submit-realtime-quesucede",'color'),Output("submit-realtime-quesucede",'children')],
    [Input('interval-component-quesucede', 'n_intervals'),Input("submit-filtro-quesucede", "n_clicks"),Input("submit-realtime-quesucede",'n_clicks')],
    [State('dropdown_volcanes-quesucede','value'),State('dropdown_sta-quesucede','value')],prevent_initial_call=True
)
def update_cam_fija(nint,filtro,livebutton,volcan,sta):
    ctx = dash.callback_context
    ctx_index = ctx.triggered[0]['prop_id'].split('.')[0]

    if ctx_index=='submit-realtime-autovdas':
        if (livebutton==None) or (livebutton % 2 != 0):
            return dash.no_update,dash.no_update,True,'warning','Offline'
        else:
            helicard = helicorder(12,sta)
            return helicard,False,'success','Online'
    else:
        helicard = helicorder(12,sta)
    return helicard,dash.no_update,dash.no_update,dash.no_update

@app.callback(
[Output('dropdown_sta-quesucede','options'),Output('dropdown_sta-quesucede','value')],
[Input('dropdown_volcanes-quesucede','value')]
)
def updatesta(vol):
    red = gdb.get_metadata_wws(volcan=vol)
    red=red[red.tipo=='SISMOLOGICA']
    
    sta_list=[]
    for index,row in red.iterrows():
        sta_list.append({'label': row.sitio+' ('+row.codcorto+')','value':row.codcorto})
    op = red.sort_values(by='referencia',ascending=True).head(1).codcorto.iloc[0]
    return sta_list,op