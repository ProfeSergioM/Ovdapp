import dash
import json
from random import random
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dash import no_update
from plotly.subplots import make_subplots
import numpy as np
from io import BytesIO
from dash_extensions.snippets import send_bytes
from simplekml import (Kml, OverlayXY, ScreenXY, Units, RotationXY,
                           AltitudeMode, Camera)
import plotly.graph_objects as go
from dash.dependencies import Input, Output,State
from dash.exceptions import PreventUpdate
from app import app
import dash_leaflet as dl
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import pandas as pd
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_getfromdb_lib as gdb
import ovdas_figure_lib as ffig
import datetime as dt

def get_fechahoy(): 
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return fini,ffin

def get_markers_loc(volcan,fi,ff):
    def postproc(df):
        df['fecha'] = df['fecha'].astype('datetime64[s]')
        return df
        
    volcanes =gdb.get_metadata_volcan('*',rep='y')
    volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")
    if(len(volcan))==1:
        if volcan !='*':
            volcan = volcan[0]
        df = gdb.extraer_eventos(fi, ff, volcan)
        df= pd.DataFrame(df) 
        if len(df)>0:
            df = df[df.calidad.isin(['A1','B1','C1'])]
            df['volcan_real'] = df['idvolc'].map(volcanes.set_index('id')['nombre'])
            df['nref_loc']=df['idvolc'].map(volcanes.set_index('id')['nref'])
            df['prof_msnm'] = (df['profundidad']*1000-df['nref_loc'])/1000
    else:
        df = gdb.extraer_eventos(fi, ff, volcan[0])
        df= pd.DataFrame(df)
        if len(df)>0:
            df = df[df.calidad.isin(['A1','B1','C1'])]
            df['volcan_real'] = df['idvolc'].map(volcanes.set_index('id')['nombre'])
            df['nref_loc']=df['idvolc'].map(volcanes.set_index('id')['nref'])
            df['prof_msnm'] = (df['profundidad']*1000-df['nref_loc'])/1000
        for v in range(1,len(volcan)):
            dfvolcan = gdb.extraer_eventos(fi, ff, volcan[v])
            dfvolcan= pd.DataFrame(dfvolcan)
            df = df.append(dfvolcan)
    return postproc(df)
    
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

red = gdb.get_metadata_wws('*')
red=red[red.tipo=='SISMOLOGICA']
sis = red[red.cod.str.startswith('S')]
ace = red[red.cod.str.startswith('A')]
mic =red[red.tipo=='INFRASONIDO']

modal = dbc.Modal(
    [
        dbc.ModalHeader("Información!"),
        dbc.ModalBody("No existen eventos clasificados para el filtro de datos seleccionado :("),
        dbc.ModalFooter(
            dbc.Button("Cerrar", id="close-modal", className="ml-auto")
        ),
    ],
    id="modal-info-locali6",
)
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {

    "background-color": " #141d26",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {


}

PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))       

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
                    dbc.Col(dbc.NavbarBrand("Revisión de sismicidad localizada - Locali6"),width=10),
                    dbc.Col(dbc.Button("Ovdapp", color="primary",outline=True, className="mr-1",id='volver-home',href='http://172.16.47.13:8080/'),width=1)
                    
                ],
                align="left",style={'width':'100%'},
                no_gutters=True,
            ),
          
                style={ 'width':'100%', 'margin-left':'0px' }
        ),
        dbc.NavbarToggler(id="navbar-toggler"),

    ],
    color="dark",
    dark=True,
)

lista_volcanes=[]
lista_volcanes.append({'label': 'Todos','value':'*'})
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan)  

volcan_selector = dcc.Dropdown(
    clearable=False,
    id='locali5-dropdown_volcanes',
    options=lista_volcanes,
    placeholder='Seleccione uno, varios o "todos"',
    value='*',
    multi=True,
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)
fechas_picker = dcc.DatePickerRange(
    id='locali5-fechas',
    start_date_placeholder_text="Inicio",
    end_date_placeholder_text="Final",
    calendar_orientation='vertical',
    display_format='Y-MM-DD',
    start_date=get_fechahoy()[0],
    end_date=get_fechahoy()[1],
    min_date_allowed='2010-01-01',
    style=
                                    { 'width':'100%',
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)  

itemsformatos=[dbc.DropdownMenuItem("KMZ (Google Earth)", id="export-kmz-button"),
               dbc.DropdownMenuItem("XLS (Excel)", id="export-xls-button"),
               dbc.DropdownMenuItem("PNG (imagen)", id="export-png-button"),
               dbc.Alert("Opción PNG solo para 1 volcán seleccionado", color="info")
               
               
               ]



formatosalidadropdown = html.Div([dbc.DropdownMenu(itemsformatos,label='Exportar selección',color='primary',className='m-1',id='export-button',
                                                   style={'pointer-events': 'none','opacity':'0.2'})])

controles = html.Div([
    html.Div(html.P('Intervalo de fechas',id='locali5-titulo-fecha')),
    fechas_picker,
    html.Div(html.P('Volcán(es)',id='locali5-titulo-fecha')),
    volcan_selector,
    dbc.Row([formatosalidadropdown,html.Div(dbc.Button("Enviar", color="primary", id="locali5-submit-filtro"),className='m-1',style={'text-align':'right'})],justify='end')
    
    ])
   

 
controlescard = dbc.Card([
    dbc.CardHeader('Selección de eventos'),
    dbc.CardBody(controles,id='controles-locali5')
    
    ],outline=True,color='light',className='m-1')








mapalayout=dbc.Container(dcc.Graph(id='mapaloc-graph',style={'height':'100%'}),style={'height':'100%','padding-left':'0','padding-right':'0'})
mapacard = dbc.Card([dbc.CardHeader('Localizaciones'),dbc.CardBody(mapalayout,id='mapa-locali5',style={'height':'100%'})],outline=True,color='light',style={'height':'80vh'})
mapacard=dcc.Loading(mapacard)



counter_imgfija = dcc.Interval(id='interval-component-fija',interval=5*1000,n_intervals=0)


sidebar = html.Div([controlescard],style=SIDEBAR_STYLE)
content = html.Div(mapacard, style=CONTENT_STYLE)

modaldownload = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Finalizado!"),
                dbc.ModalBody([dbc.Alert("Datos cargados, presione el botón a continuación para descargar :)", color="success"),
                dbc.Button("Descargar datos", color="primary", className="mr-1",external_link=True,id="button-download-locali6")]),
                dbc.ModalFooter(
                    dbc.Button("Cerrar", id="close-modal-locali6", className="ml-auto")
                ),
            ],
            id="modal-locali6",
        ),
    ]
)




counter_timeline = dcc.Interval(
          id='interval-component-timeline-locali6',
          interval=60*1000*5, # utlimo numero son minutos
          n_intervals=0
      )

layout = html.Div([modal,navbar,dbc.Row([dbc.Col([sidebar],width=3),
                                         dbc.Col([content],width=7)]),
                   html.Div(id='cajita-loc', style={'display': 'none'}),counter_imgfija,
                   dcc.Loading(modaldownload, style={'position':'fixed','left':'50%','top':'50%'})])

    
@app.callback(
    [Output('mapaloc-graph','figure')],
    [Input('url','href'),Input('locali5-submit-filtro','n_clicks')],
    [State('locali5-dropdown_volcanes','value'),State('locali5-fechas','start_date'),
     State('locali5-fechas','end_date')])
def display_mapa(href,ir,volcan,fi,ff):

    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id']

    if trigger in['.','locali5-submit-filtro.n_clicks']:   
        dflocs = get_markers_loc(volcan, fi, ff)
        fig =go.Figure()
        
        trace_volcanes = go.Scattermapbox(lon=volcanes.longitud,lat=volcanes.latitud,
                             name='Volcán',mode='markers',marker=go.scattermapbox.Marker(symbol='volcano',size=12),text =volcanes.nombre_db)   
        fig.add_trace(trace_volcanes)

        trace_sis = go.Scattermapbox(lon=sis.longitud,lat=sis.latitud,
                             name='Sismómetro',mode='markers',marker=go.scattermapbox.Marker(size=6,color='#555555'),text =sis.codcorto)   
        fig.add_trace(trace_sis)        

        trace_ace = go.Scattermapbox(lon=ace.longitud,lat=ace.latitud,
                             name='Acelerómetro',mode='markers',marker=go.scattermapbox.Marker(size=6,color='#999999'),text =ace.codcorto)   
        fig.add_trace(trace_ace)  
        
        for tipoev in dflocs['tipoevento'].unique():
            df = dflocs[dflocs['tipoevento']==tipoev]
            trace = go.Scattermapbox(lon=df['longitud'],
                                     lat=df['latitud'],
                                     name='Evento '+tipoev,
                                     mode='markers',
                                     customdata=df,
                                     marker=go.scattermapbox.Marker(
                                     size=8,
                                     color='#'+ffig.colores_cla_hex(tipoev)[:-2]
                                         ),
                                     text = df['profundidad'],
                                     hovertemplate = "Fecha: %{customdata[0]}<br>Latitud: %{lat}<br>Longitud: %{lon} </br>Profundidad: %{text} km </br>Calidad: %{customdata[22]} </br>ML: %{customdata[24]}"

                                    
                                     )
            fig.add_trace(trace)


        
     
        fig.update_layout(legend=dict(
            bgcolor='rgba(0,0,0,0.2)',
            x=0.01,
            y=.95,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="white"
       )))
        fig.update_layout(mapbox1=dict(
            accesstoken= 'pk.eyJ1IjoicHJvZmVzZXJnaW9tIiwiYSI6ImNrZXk5ZG9yaTB3Y3IycnA5bTlscWZqZjMifQ.s1qn784tAww2oGZYWeTi8w',
            style="mapbox://styles/profesergiom/ckfpoplbw1bpl1any6qj7eqtn"),margin = dict(l = 0, r = 0, t = 0, b = 0))
        return [fig]
    else:
        return dash.no_update

@app.callback(
    [Output('cajita-loc', 'children'),Output('export-button','style')],
    [Input('mapaloc-graph', 'selectedData')])
def display_data(selectedData):
    if selectedData==None:
        show = {'pointer-events': 'none','opacity':'0.2'}
    else:
        show = {'pointer-events': 'auto','opacity':'1'}
    return json.dumps(selectedData, indent=2),show


@app.callback([Output("button-download-locali6", "href"),Output("modal-locali6", "is_open")],
              [Input("export-kmz-button", "n_clicks"),Input("export-xls-button", "n_clicks"),
               Input("export-png-button", "n_clicks"),Input("close-modal-locali6",'n_clicks')],
              [State('cajita-loc', 'children'),State('locali5-dropdown_volcanes','value'),
               State('locali5-fechas','start_date'),
               State('locali5-fechas','end_date'),State("modal-locali6", "is_open")],prevent_initial_call=True)
def func(kmz,xls,png,close_modal,cajita,volcansel,fini,ffin,is_open):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id']
    df = json.loads(cajita)
    df= pd.DataFrame(df['points'])
    df = df.dropna()
    custom = df['customdata'].tolist()
    fecha,lat,lon,prof,ml,tipoev,volcan = ([item[0] for item in custom],[item[12] for item in custom],
                            [item[13] for item in custom],[item[14] for item in custom],
                            [item[24] for item in custom],[item[4] for item in custom],
                            [item[-3] for item in custom])
    df['fecha'],df['latitud'],df['longitud'],df['profundidad'],df['ml'],df['tipoev'],df['volcan'] = fecha,lat,lon,prof,ml,tipoev,volcan
    dfnew = df[['fecha','latitud','longitud','profundidad','ml','tipoev','volcan']].copy()
    dfnew = dfnew.set_index('fecha',drop=True)
    if dash.callback_context.triggered[0]['prop_id'] =='close-modal-locali6.n_clicks':
        return dash.no_update,not is_open
    elif dash.callback_context.triggered[0]['prop_id'] =='export-kmz-button.n_clicks':
        print('kmz!')
        import doc_lib as odl
        file_path,filename = odl.kmz_locali6_ovdapp(dfnew)
        file_path = 'assets/dynamic/'+file_path+'.kmz'
        link_url= '/dash/urlToDownloadlocali6?value={}'.format(file_path)
        link_url=link_url+'&filename={}'.format(filename)
        return link_url,not is_open        
    elif dash.callback_context.triggered[0]['prop_id'] =='export-xls-button.n_clicks':
        print('xls!')    
        import doc_lib as odl
        file_path,filename = odl.xls_locali6_ovdapp(dfnew)
        file_path = 'assets/dynamic/'+file_path+'.xlsx'
        link_url= '/dash/urlToDownloadlocali6?value={}'.format(file_path)
        link_url=link_url+'&filename={}'.format(filename)
        return link_url,not is_open  
    elif dash.callback_context.triggered[0]['prop_id'] =='export-png-button.n_clicks':
        print('png!')
        import doc_lib as odl
        if (len(volcansel)==1) and (volcansel!='*'):
            file_path,filename = odl.png_locali6_ovdapp(dfnew,volcansel,fini,ffin)
            file_path = 'assets/dynamic/'+file_path+'.png'
            link_url= '/dash/urlToDownloadlocali6?value={}'.format(file_path)
            link_url=link_url+'&filename={}'.format(filename)
            return link_url,not is_open   
        else:
            return dash.no_update,dash.no_update
    else:
        return dash.no_update,not is_open


@app.server.route('/dash/urlToDownloadlocali6') 
def descargar_locali6():
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


      


@app.callback([Output('locali5-fechas', 'start-date'),Output('locali5-fechas', 'end-date'),
               Output('interval-component-timeline-locali6', 'interval')],
              [Input('interval-component-timeline-locali6', 'n_intervals')])
def update_date(n):
    fini,ffin=get_fechahoy()
    return fini,ffin,60*60*1000