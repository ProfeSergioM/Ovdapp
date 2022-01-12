# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
import dash
from numpy import arange
import datetime
from random import random
from app import app
from dash.dependencies import Input, Output,State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_getfromdb_lib as gdb
import datetime as dt
from dash_extensions import Download

volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

#volcanes = volcanes[volcanes.nombre_db.isin(['Villarrica','PuyehueCCaulle'])]

lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan) 


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


sampling_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_sampling-fastrsam',
    options=[
        {'label': '5 minutos (todos)', 'value': 5},
        {'label': '10 minutos', 'value': 10},
        {'label': '15 minutos', 'value': 15}, 
        {'label': '30 minutos', 'value': 30},
        {'label': '1 hora', 'value': 60},     
        {'label': '2 horas', 'value': 120}, 
        {'label': '6 horas', 'value': 360}, 
    ],
    value=15,
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
    min_date_allowed='2010-01-01',

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
          interval=60*1000*4, # in milliseconds
          n_intervals=0
      )
counter_reloj = dcc.Interval(
          id='interval-component-reloj-fastrsam',
          interval=60*1000*1, # in milliseconds
          n_intervals=0
      )



def crear_fastRSAM(RSAM,voldata,fechai,fechaf,rangef):
    pointopacity=0.5
    datalinewidth=1
    import plotly.express as px
    import numpy as np
    import locale     
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    #locale.setlocale(locale.LC_ALL, 'es_ES')
    colors = px.colors.qualitative.Plotly
    colors=colors+colors+colors
    RSAM.index = RSAM.index*1000
    fig = make_subplots(rows=3, cols=1,vertical_spacing=0.05,shared_xaxes='all')
    i=0
    listaRSAM = [item for item in list(RSAM.columns) if (len(item)==4) & (item[-1]=='Z')]
    for sta in listaRSAM:
        data = RSAM[sta]
        #fig.add_trace(go.Scattergl(x=data.index, y=data.values,name=sta,mode='markers',marker_size=5,opacity=pointopacity,
        #                          hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',marker_color=colors[i]),row=1, col=1) 
        
        
        
        
        
        #fig.add_trace(go.Scattergl(x=data.index,
        #                               y=RSAM[sta].rolling(int(sampling[:-1])*4,center=True).mean(),
        #                               name=sta+' '+str(int(sampling[:-1])*4)+' MM',
        #                               mode='lines',line_width=datalinewidth,
        #                            hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',line_color=colors[i]),row=1, col=1) 
        i+=1
    
    fig.add_trace(go.Scattergl(x=[np.NaN],y=[np.NaN],name='',mode='none'))
    fig.add_trace(go.Scattergl(x=[np.NaN],y=[np.NaN],name='Razón RSAM',mode='none'))
    fig.update_xaxes(showspikes=True,type='date')
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
    
    listaRE = [item for item in list(RSAM.columns) if (len(item)==9)]
    i=0
    if len(listaRE)>0:
            
        for sta in list(listaRE):
            data = RSAM[sta]
            #fig.add_trace(go.Scattergl(x=RSAM.index, y=data.values,name=sta,mode='markers',marker_size=5,opacity=pointopacity,
            #                           hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f}',marker_color=colors[i]),row=2, col=1) 
            
            
            
            #fig.add_trace(go.Scattergl(x=data.index,
            #                           y=RSAM[sta].rolling(int(sampling[:-1])*4,center=True).mean(),
            #                           name=sta+' '+str(int(sampling[:-1])*4)+' MM',
            #                           mode='lines',line_width=datalinewidth,
            #                        hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f}',line_color=colors[i]),row=2, col=1) 
            i+=1
        #fig.update_yaxes(range=[0,RSAM[listaRE].max().max()*1.1],col=1,row=2)
        fig.update_yaxes(title_font=dict(size=14),title_text='Razón RSAM',fixedrange=False,col=1,row=2)
    fig.add_trace(go.Scattergl(x=[np.NaN],y=[np.NaN],name='',mode='none'))
    fig.add_trace(go.Scattergl(x=[np.NaN],y=[np.NaN],name='Razón H/V',mode='none'))
    listaHV = [item for item in list(RSAM.columns) if (len(item)==7)]
    i=0
    if len(listaHV)>0:
        for sta in list(listaHV):
            data = RSAM[sta]
            
            #fig.add_trace(go.Scattergl(x=RSAM.index, y=data.values,name=sta,mode='markers',marker_size=5,opacity=pointopacity,
            #                           hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',marker_color=colors[i]),row=3, col=1) 
            
            
            
            
            
            #fig.add_trace(go.Scattergl(x=data.index,
            #                           y=RSAM[sta].rolling(int(sampling[:-1])*4,center=True).mean(),
            #                           name=sta+' '+str(int(sampling[:-1])*4)+' MM',
            #                           mode='lines',line_width=datalinewidth,
            #                        hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',line_color=colors[i]),row=3, col=1) 
            i+=1
        #fig.update_yaxes(range=[0,RSAM[listaHV].max().max()*1.1],col=1,row=3)
        fig.update_yaxes(title_font=dict(size=14),title_text='Razón H/V',fixedrange=False,col=1,row=3)
    
    fig.layout.template = 'plotly_dark'
    fig.update_yaxes(title_font=dict(size=14),title_text='RSAM - um/s',fixedrange=False,col=1,row=1)
    
    fig.update_xaxes(title_font=dict(size=14),title_text='Fecha',col=1,row=3)
    fig.update_xaxes(range=[min(data.index),max(data.index)],col=1,row=3)
    fig.update_yaxes(range=[0,RSAM[listaRSAM].max().max()*1.1],col=1,row=1)
    fig.update_layout(legend=dict(font=dict({'size':10})))
    fig.update_layout(legend_title_text='RSAM')
    fig.update_xaxes(tickfont=dict(size=12))    
    fig.update_layout(bargap=0,margin={"r":1,"t":25,"l":1,"b":1},
        font=dict(
            family="Tahoma",
            size=15,
            ),
        title={
            'text': "RSAM Rápido - "+str(rangef[0])+" - "+str(rangef[1])+" Hz - "+voldata.vol_tipo.iloc[0]+' '+voldata.nombre.iloc[0],
            'y':0.97,
            'x':0.5,
            
            'xanchor': 'center',
                'yanchor': 'top'})
    return fig


PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("Proyecto de monitoreo sísmico automático OVV - RSAM Rápido",style={'color':'white'}),width=10),
            dbc.Col(dbc.Button("Ovdapp", color="Descargar!",outline=True, className="mr-1",id='volver-home',href='/'),width=1)
            
            
        ],justify="left",
    style={'width':'100%'})

],
color="#141d26",

)
      




controles = html.Div([
    html.Div(volcan_selector),
    html.Div(html.P('Intervalo de fechas',id='titulo-fecha-fastrsam')),
    fechas_picker,
    html.Div(html.P('Frecuencia de filtrado (Hz)',id='titulo-fecha-fastrsam')),
    dcc.RangeSlider(
        id='RSAM-range-slider-fastrsam',
        min=0.5,
        max=10,
        step=0.5,
        value=[0.5,5],
        marks=arange(0,11,1)),
    html.Div(html.P('Muestreo de datos',id='titulo-muestreo-fastrsam')),
    html.Div(sampling_selector),
    html.Div(children=[dcc.Loading(children=[
                dbc.Button("Descargar datos", color="success", id="csv-realtime-fastrsam", className="mr-1",style={'pointer-events': 'none','opacity':'0.2'}),
                dbc.Button("Online", color="success", id="submit-realtime-fastrsam", className="mr-1"),
                dbc.Button("Enviar", color="primary", id="submit-filtro-fastrsam", className="mr-1")])],style={'text-align':'right'})

    ])





controlescard = dbc.Card([
    dbc.CardHeader('Opciones'),
    dbc.CardBody(controles,id='controles-fastrsam')
    
    ],outline=True,color='light')

banner_inferior = dbc.Card([
    dbc.CardHeader('Fecha y Hora actual (UTC)'),
    dbc.CardBody('',id='live-update-text-fastrsam')
    
    ],outline=True,color='light')

modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("Finalizado!"),
                dbc.ModalBody([dbc.Alert("Datos cargados, presione el botón a continuación para descargar :)", color="success"),
                dbc.Button("Descargar datos", color="primary", className="mr-1",external_link=True,id="xlsx-download-fastrsam")]),
                dbc.ModalFooter(
                    dbc.Button("Cerrar", id="close-modal-fastrsam", className="ml-auto")
                ),
            ],
            id="modal-fastrsam",
        ),
    ]
)



layout = html.Div([navbar,dbc.Row([dbc.Col([controlescard,banner_inferior],width=3),
                                   dbc.Col([html.Div(id='colgrafica-fastrsam')],width=9)
                                   ]),
                   html.Div(id='cajita-fastRSAM', style={'display': 'none'}),
                   dbc.Row([counter_imggif,counter_reloj],no_gutters=True,justify='start', className="mr-1"),
                   dcc.Loading(modal, style={'position':'fixed','left':'50%','top':'50%'})
                   ])



@app.callback(
    #[Output("colgrafica-fastrsam", "children"),Output("colmapa-fastrsam", "children")],
    [Output("colgrafica-fastrsam", "children"),Output('interval-component-reloj-fastrsam', 'disabled'),
     Output("submit-realtime-fastrsam",'color'),Output("submit-realtime-fastrsam",'children'),
     Output('cajita-fastRSAM', 'children'),
     Output("csv-realtime-fastrsam",'style')
     
     ],
    
    [Input("submit-realtime-fastrsam",'n_clicks'),Input('interval-component-reloj-fastrsam', 'n_intervals'),Input("submit-filtro-fastrsam", "n_clicks")],
    [State('RSAM-range-slider-fastrsam','value'),
     State('dropdown_volcanes-fastrsam','value'), State('fechas-fastrsam','start_date'),State('fechas-fastrsam','end_date'),
     State('dropdown_sampling-fastrsam','value')],prevent_initial_call=True
)

def update_cam_fija(*args):
    import numpy as np
    from scipy import stats
    import ovdas_getdatafastRSAM as gdfr
    
    def plotear(volcan,fini,ffin,rangef,sampling):
        freqi=rangef[0]
        freqf=rangef[1]
        print('iniciado')
        import numpy as np
        from scipy import stats
        #fini=fini+' 00:00:00'
        #ffin=ffin+' 23:59:59'
        voldata = gdb.get_metadata_volcan(volcan)
        voldata = voldata.drop_duplicates(subset='nombre', keep="first")
        red = gdb.get_metadata_wws(volcan='*')
        red = red[(red.nombre_db==volcan) & (red.tipo=='SISMOLOGICA') & (red.cod.str.startswith('S')==True)]
        red = red[~red.codcorto.isin(['CHP','KIK'])]
        red = red.sort_values(by='distcrater').head(5)
        
        from scipy import stats
        import timeit
        import numpy as np
        RSAMS=[]
        import ovdas_getdatafastRSAM as gdfr
        bandas = [x.decode('utf-8') for x in list(np.arange(freqi,freqf,0.1).astype('|S3'))]
        for index,row in red.iterrows():
            for comp in ['Z','N','E']:
                esta=row.codcorto
                df = gdfr.fastRSAM_dataL(fini+' 00:00:00',ffin+' 00:00:00', esta+comp, freqi,freqf,sampling ) 
                if len(df)>0:
                    #df['rsam'] =np.sqrt(np.power(df[bandas],2).values.sum(axis=1))
                    df['rsam'] = df[bandas].pow(2).sum(axis=1).pow(0.5)
                    df = df.rename(columns={'rsam':esta+comp})
                    df = df.set_index('fecha')
                    df = df[~df.index.duplicated(keep='first')]  
                    resultz = df[esta+comp]
                    resultz = resultz[(np.abs(stats.zscore(resultz)) < 3)]
                    RSAMS.append(resultz)
        import pandas as pd            
        RSAM = pd.concat(RSAMS,axis=1) 
        
        
        
        listaRE = [item[:-1] for item in RSAM.columns if item[-1]=='Z']
        redRE = red[red.codcorto.isin(listaRE)].sort_values(by='distcrater', ascending=True)
        estaRE =list(redRE.codcorto)
        df_RE = []
        for i in range(0,len(listaRE)):
            for j in range(i+1,len(estaRE)):
                esta1=estaRE[i]
                esta2=estaRE[j]
                df = RSAM[esta1+'Z'].div(RSAM[esta2+'Z'].values)
                
                df = df.rename(esta1+'Z'+'/'+esta2+'Z')
                df_RE.append(df)
        if len(df_RE)>0:
            df_RE = pd.concat(df_RE,axis=1)
            RSAM = pd.concat([RSAM,df_RE],axis=1)
        listaHV = [item[:-1] for item in RSAM.columns if item[-1]=='N']
        if len(listaHV)>0:
            hvs=[]
            for es in listaHV:
                hv = ((RSAM[es+'N']+RSAM[es+'E'])/2)/RSAM[es+'Z']
                hv = hv.rename(es+'_H/V')
                hvs.append(hv)
            hvs = pd.concat(hvs,axis=1)
        else:
            hvs=[]
        if len(hvs)>0:
            RSAM = pd.concat([RSAM,hvs],axis=1)
            
        print('datos listos, graficando...')
        fig = crear_fastRSAM(RSAM,voldata,fini,ffin,rangef)
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
        
        print(RSAM.columns)
        RSAM_raw = RSAM.copy()
        RSAM_raw = RSAM_raw.to_json()
            
            
        return graficocard,RSAM_raw





    #do
    livebutton=args[0]
    ffin=args[6]
    fini=args[5]
    volcan=args[4]
    rangef=args[3]
    sampling=args[7]
    ctx = dash.callback_context
    ctx_index = ctx.triggered[0]['prop_id'].split('.')[0]

    if ctx_index=='submit-realtime-fastrsam':
        if (livebutton==None) or (livebutton % 2 != 0):
            return dash.no_update,True,'warning','Offline',dash.no_update,dash.no_update
        else:
            graficocard,RSAM_raw = plotear(volcan,fini,ffin,rangef,sampling)
            return [graficocard],False,'success','Online',RSAM_raw,dash.no_update
    else:
        graficocard,RSAM_raw = plotear(volcan,fini,ffin,rangef,sampling)
        return [graficocard],dash.no_update,dash.no_update,dash.no_update,RSAM_raw,{'pointer-events': 'auto','opacity':'1'}


@app.callback([Output('live-update-text-fastrsam', 'children'),Output('fechas-fastrsam','start_date'),Output('fechas-fastrsam','end_date'),
],
              [Input('interval-component-reloj-fastrsam', 'n_intervals')],
              [State('dropdown_volcanes-fastrsam','value'),State('fechas-fastrsam','start_date'),State('fechas-fastrsam','end_date')]
              )
def update_date(n,volcan,fini,ffin):
    from flask import request
    print('tic! from '+request.remote_addr)
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})],fini,ffin


@app.callback([Output("xlsx-download-fastrsam", "href"),Output("modal-fastrsam", "is_open")],
              [Input("csv-realtime-fastrsam", "n_clicks"),Input("close-modal-fastrsam",'n_clicks')],
              [State('cajita-fastRSAM', 'children'),State("modal-fastrsam", "is_open")],
              prevent_initial_call=True
              )
def download_csv(click,close,data,is_open):
    if dash.callback_context.triggered[0]['value'] is not None:
        if dash.callback_context.triggered[0]['prop_id'] =='csv-realtime-fastrsam.n_clicks':
            print('Generando Xlsx')
            import json
            import pandas as pd
            df= json.loads(data)
            df = pd.DataFrame(df)
            import doc_lib as odl
            file_path = odl.xlsxdownload_ovdapp(df)
            filename ='datosRSAM.xlsx'
            file_path = 'assets/dynamic/'+file_path+'.xlsx'
            link_url= '/dash/urlToDownloadrsam?value={}'.format(file_path)
            link_url=link_url+'&filename={}'.format(filename)
            return link_url,not is_open
                
        elif dash.callback_context.triggered[0]['prop_id'] =='close-modal-fastrsam.n_clicks':
            return dash.no_update,not is_open
    else:
        return dash.no_update,dash.no_update


@app.server.route('/dash/urlToDownloadrsam') 
def descargar():
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
                     #mimetype='document/xls',
                     attachment_filename=filename,
                     as_attachment=True)



