# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash_bootstrap_components as dbc
import datetime
from random import random
from app import app
from dash.dependencies import Input, Output,State
from dash import dcc,html
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_getfromdb_lib as gdb
horas=2

volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan) 


volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes-defcon',
    options=lista_volcanes,
    value='Villarrica',
    multi=False,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
counter_imggif = dcc.Interval(
          id='interval-component-gif-defcon',
          interval=60*1000*5, # in milliseconds
          n_intervals=0
      )
counter_reloj = dcc.Interval(
          id='interval-component-reloj-defcon',
          interval=60*1000*60, # in milliseconds
          n_intervals=0
      )



def crear_defcon(fin,vol):
    print('oli')
    ini='2010-01-01'
    import sys
    sys.path.append('//172.16.40.10/sismologia/pyOvdas_lib/')
    import ovdas_getfromdb_lib as gdb
    from datetime import datetime, timedelta
    volcanes =gdb.get_metadata_volcan(vol,rep='y')
    volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")
    
    #Extraer todos los cambios de alerta
    fechas=[]
    alertas=[]
    #fechas.append(datetime.strptime(final,'%Y-%m-%d'))         
    aer = gdb.extraer_alerta_x_dia(vol,fin)
    alertas.append(aer[0])
    fechas.append(datetime.strptime(aer[1],'%d/%m/%Y'))      
    #%%
    fecha_busqueda = datetime.strptime(aer[1],'%d/%m/%Y')
    
    while fecha_busqueda>datetime.strptime(ini,'%Y-%m-%d'):
        aer = gdb.extraer_alerta_x_dia(vol,datetime.strftime(fecha_busqueda-timedelta(days=1),'%Y-%m-%d'))
        try:
            
            fecha_busqueda = datetime.strptime(aer[1],'%d/%m/%Y')
            fechas.append(fecha_busqueda)
            alertas.append(aer[0])
        except:
            break
    
    #%%
    import pandas as pd
    df = pd.DataFrame([fechas,alertas]).T
    df = df.set_index(0).rename(columns={1:'alerta'})
    df = df.sort_index()
    lastRow = pd.DataFrame([[datetime.strptime(fin,'%Y-%m-%d'),df.tail(1)['alerta'].iloc[0]]],columns=[0,'alerta']).set_index(0)
    
    dfAlerta = df.append(lastRow)
    
    
    DICT_ALEC = dict(VERDE='success',AMARILLA='warning',NARANJA='Orange',ROJA='danger')
    listacambios =[]
    import dash_bootstrap_components as dbc
    
    #listacambios.append(dbc.ListGroupItem(str(dfAlerta.index[0])[0:10]+' - '+'Inicio Monitoreo (alerta inicial :'+dfAlerta['alerta'].iloc[0].capitalize()+')',color=DICT_ALEC[dfAlerta['alerta'].iloc[0]]))
    
    dfcambios=[]
    for j in range(1,len(dfAlerta)):
        intervalodias=(dfAlerta.index[j]-dfAlerta.index[j-1]).days
        if intervalodias==1:sufijo=' día)'
        else:sufijo=' días)'
        listacambios.append(dbc.ListGroupItem(str(dfAlerta.index[j-1])[0:10]+' al '+str(dfAlerta.index[j]-timedelta(days=1))[0:10]+' - '+dfAlerta['alerta'].iloc[j-1].capitalize()+
                                              ' ('+str(intervalodias)+sufijo,
                                              color=DICT_ALEC[dfAlerta['alerta'].iloc[j-1]]))
        dfcambios.append([dfAlerta.index[j-1],dfAlerta.index[j]-timedelta(days=1),dfAlerta['alerta'].iloc[j-1].capitalize(),intervalodias])
    
    #listacambios.append(dbc.ListGroupItem(str(dfAlerta.index[-1])[0:10]+' - '+'Nivel actual :'+dfAlerta['alerta'].iloc[-1].capitalize(),color=DICT_ALEC[dfAlerta['alerta'].iloc[-1]]))
    
    #%%
    colors = {'VERDE': 'rgb(0, 255, 0)',
              'AMARILLA': 'rgb(255,255,0)',
              'NARANJA': 'rgb(255,165,0)',
              'ROJA': 'rgb(255,0,0)'}
    
    order = {'Nivel':['VERDE','AMARILLA','NARANJA','ROJA']}
    filas = []
    import pandas as pd
    from datetime import datetime,timedelta
    for i in range(0,len(dfAlerta)-1):
        start = dfAlerta.index[i]
        end = dfAlerta.index[i+1]-timedelta(seconds=1)
        rowDict = dict(Start=start,Finish=end,Alerta=dfAlerta['alerta'].iloc[i],Nivel=dfAlerta['alerta'].iloc[i])
        filas.append(rowDict)
    dfGantt = pd.DataFrame(filas)
    
    
    import plotly.express as px
    fig = px.timeline(dfGantt, x_start="Start", x_end="Finish", y="Alerta",color='Nivel',color_discrete_map=colors,category_orders=order)
    fig.layout.template = 'plotly_dark'
    
    

    return fig,listacambios,dfcambios


PLOTLY_LOGO = app.get_asset_url('img/sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("DEFCON - Historial de niveles de alerta técnica",style={'color':'white'}),width=10),
            dbc.Col(dbc.Button("Ovdapp", color="primary",outline=True, className="mr-1",id='volver-home',href='http://172.16.47.13:8080/'),width=1)
            
            
        ],justify="left",
    style={'width':'100%'})

],
color="#141d26",

)
      




controles = html.Div([
    
    html.Div(html.P('Selecione Volcán',id='titulo-defcon-volcan')),
    html.Div(volcan_selector),
     dbc.Row([html.Div(dbc.Button("Descargar datos", color="primary", id="download-defcon",external_link=True,style={'pointer-events': 'none','opacity':'0.2'}),className='m-1',style={'text-align':'right'}),
              html.Div(dbc.Button("Enviar", color="primary", id="submit-defcon"),className='m-1',style={'text-align':'right'})],justify='end'),
    

    ])





controlescard = dbc.Card([
    dbc.CardHeader('Opciones'),
    dbc.CardBody(controles,id='controles-defcon')
    
    ],outline=True,color='light')

banner_inferior = dbc.Card([
    dbc.CardHeader('Fecha y Hora actual (UTC)'),
    dbc.CardBody('',id='live-update-text-defcon')
    
    ],outline=True,color='light')


layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col([dcc.Loading(html.Div(id='colgrafica-defcon'))],width=9)
                                   ]),
                   dbc.Row([counter_imggif,counter_reloj]    ,    className="mr-1 g-0",justify='start'),
                   html.Div(id='cajita-loc-defcon', style={'display': 'none'})
                   
                   ])

@app.callback(
    [Output("colgrafica-defcon", "children"),Output('cajita-loc-defcon', 'children'),Output('download-defcon','style'),Output('download-defcon','href')],
    [Input("submit-defcon", "n_clicks")],
    [State('dropdown_volcanes-defcon','value')]
,prevent_initial_call=True)
def update_cam_fija(nclicks,volcan):
    ffin=str(datetime.datetime.now())[:10]

    fig,listacambios,dfcambios = crear_defcon(ffin,volcan)
    grafico = html.Div(children=[
        dcc.Graph(
            id='timeline-orca',
            figure=fig,
            style={ 'height':'80vh' }
        )
    ])
    
    graficocard = dbc.Card([
        dbc.CardHeader('Evolución temporal de la alerta técnica para el volcán'),
        dbc.CardBody(grafico)
        
        ],outline=True,color='light')

    lista_cambios = dbc.ListGroup(
        listacambios
        )

    list_group = dbc.ListGroup(
        [
            dbc.ListGroupItem(
                [
                    lista_cambios
                    
                ]
            )
        ]
    )
    
    listcard = dbc.Card([
        dbc.CardHeader('Lista de cambios de alertas'),
        dbc.CardBody(list_group)
        
        ],outline=True,color='light')

    content = html.Div([dbc.Row([dbc.Col(graficocard,width=12)]),dbc.Row([dbc.Col(listcard,width=12)])])
    
    content = dbc.Card([dbc.CardBody([content])])
    
    if nclicks==0:
        show = {'pointer-events': 'none','opacity':'0.2'}
    else:
        show = {'pointer-events': 'auto','opacity':'1'}
    
    data=[]
    import pandas as pd
    datos = pd.DataFrame(dfcambios)
    
    import doc_lib as odl
    file_path = odl.xlsxdownload_ovdapp(datos)
    
    file_path = 'assets/dynamic/'+file_path+'.xlsx'
    link_url= '/dash/urlToDownloaddefcon?value={}'.format(file_path)
    link_url=link_url+'&filename={}'.format('alertas_'+volcan+'.xlsx')
    return [content],data,show,link_url


@app.server.route('/dash/urlToDownloaddefcon') 
def descargar_defcon():
    import io,os,flask
    value = flask.request.args.get('value')
    filename = flask.request.args.get('filename')
    return_data = io.BytesIO()
    with open(value, 'rb') as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)
    os.remove(value) 
    return flask.send_file(return_data,
                     attachment_filename=filename,
                     as_attachment=True)
    
    
@app.callback([Output('live-update-text-defcon', 'children'),
],
              [Input('url','href')]
              )
def update_date(href):
    from flask import request
    print('tic! from '+request.remote_addr)
    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})]