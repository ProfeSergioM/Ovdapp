# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 11:34:09 2020

@author: sergio
"""
import dash
import json
import dash_html_components as html
import dash_core_components as dcc
from app import app
from dash.exceptions import PreventUpdate
from random import random
from dash.dependencies import Input, Output,State
import dash_bootstrap_components as dbc
import sys
import dash_gif_component as gif
import pandas as pd
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_getfromdb_lib as gdb
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")
volcan_default='NevChillan'
import datetime as dt
def get_fechahoy(): 
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=182), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return fini,ffin

def dibujar_mapa(volcanes,volcan,fi,ff):
    from datetime import timedelta,datetime
    import dash_leaflet as dl
    import ovdas_figure_lib as ffig
    def get_markers_loc(volcan,fi,ff):
        df = gdb.extraer_eventos(fi, ff, volcan)
        df= pd.DataFrame(df)
        if len(df)>0:
            df = df[df.calidad.isin(['A1','B1'])]
        return df
    lat_vol = (volcanes[volcanes.nombre_db==volcan].latitud.iloc[0])
    lon_vol = (volcanes[volcanes.nombre_db==volcan].longitud.iloc[0])
    ###MAPA
    tileurl =  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    escala = dl.ScaleControl(imperial=False)
    iconUrl_volcan = app.get_asset_url('img/star.fw.png?random='+str(random())) 
    volcan_star = dl.Marker(position=[lat_vol,lon_vol],children=[dl.Popup(html.Table([html.Tr([html.Td(volcan)])]))],
                                    icon=dict(iconUrl=iconUrl_volcan, iconSize=[20,20],iconAnchor=[10, 10]),id='estrellita')
    dflocs = get_markers_loc(volcan, fi, ff)
    dflocs = dflocs.sort_values(by='ml',ascending=False)
    evs = []
    evs_mes = []
    mes = ((datetime.strptime(ff,'%Y-%m-%d')-timedelta(days=30)).strftime('%Y-%m-%d'))
    for item,row in dflocs.iterrows():
        #if row.fecha > datetime.strptime(mes,'%Y-%m-%d'):
        sym=app.get_asset_url('img/'+row.tipoevento+'.png?random='+str(random())) 
        popup = dl.Popup(html.Table(
                      [html.Tr([html.Td('Fecha'),html.Td(row.fecha)])]+
                      [html.Tr([html.Td('Profundidad'),html.Td(str(row.profundidad)+ ' km')])]+
                      [html.Tr([html.Td('ML'),html.Td(row.ml)])]

                      
                                      ))
        evs.append(dl.CircleMarker(center=[row.latitud,row.longitud],
                                   radius=5,
                                   color='#ffffff',
                                   fillColor='#'+ffig.colores_cla_hex(row.tipoevento)[:-2],
                                   weight=1,
                                   fillOpacity=0.5,
                                   children=[popup]))
        #evs.append(dl.Marker(position=[row.latitud,row.longitud],children=[popup],opacity=0.75,
        #                            icon=dict(iconUrl=sym, iconSize=[10,10],iconAnchor=[5, 5]),id=str(row.idevento)))        
        
    contenidomapa = [dl.TileLayer(id="tiles", url=tileurl),escala,*evs,volcan_star]
    mapa = dl.Map(contenidomapa,style={'width': '100%', 'height': '100%', 'margin': "auto", "display": "block","z-index":"0"}
                    ,center=[lat_vol,lon_vol,
                                                                                   ],zoom=10,id='mapaloc'
                    )
    legend_entry=['Tipo de evento']

    if len(dflocs)>0:
        for entrada in dflocs.tipoevento.unique():
            sym=app.get_asset_url('img/'+entrada+'.png?random='+str(random())) 
            if entrada=='LV':entrada='VLP'
            icono = html.Img(src=sym,height=10,width=10)
            legend_entry.append(html.Td(html.Div([icono,'  '+entrada])))
    else:
        legend_entry=[]

    leyenda_tabla = html.Table(html.Tr(legend_entry),id='tablita')    
    
    
    leyenda = html.Div(leyenda_tabla, style={"bottom": "0px",'background-color':'rgba(225, 225, 225, .5)',
                                     "left": "5px", "z-index": "1000", "width": "100%"})
    
    mapa = dbc.Card([
        dbc.CardBody(mapa),
        leyenda        
        ],outline=True,color='light',className='m-1',style={'height':'100%'} )
    return mapa,evs

def contar_evs(fini,ffin,volcan):
    conteo = {}
    n_subplots=0
    tipoev_list = []
    for tipoev in ['VT','LP','TR','HB','LV','EX']:
        algo = gdb.extraer_eventos_dia(inicio=fini,final=ffin,volcan=volcan,tipoevento=tipoev)
        if len(algo)>0:
            eventos_contados = pd.DataFrame(algo)
            conteo[tipoev]=eventos_contados
            n_subplots=n_subplots+1
            tipoev_list.append(tipoev)
    return conteo,n_subplots,tipoev_list

def altura_columna(ini,fin,volcan):
    vistas = []
    vistas.append(gdb.get_metadata_camIP(volcan))
    vistas = pd.concat(vistas)
    vistas.reset_index(drop=True,inplace=True)
    alturas = []
    for index,row in vistas.iterrows():
        try:
            dato = gdb.get_datos_x_vista_camIP(row.idvista, ini, fin)
            dato['idvolcan']=row.idvolcan
            dato['vista']=row.vista
            dato['vista_standard']=row.directorioac
            alturas.append(dato)
        except:()
   
    if len(alturas)>0:
        alturas = pd.concat(alturas)
        if len(alturas)>0:
            alturas.reset_index(drop=True,inplace=True) 
            alturas.set_index('fecha',inplace=True)
            alturas = alturas[alturas.altura<9999]
            excede= alturas[alturas.altura ==100000]
            noseve=alturas[alturas.altura==-1]
            alturas = alturas[alturas.altura>-1]
        else:
            alturas,excede=[],[]
    else:
        alturas,excede=[],[]
    #maximo diario
    #alturas = alturas.resample('D').max()
    return alturas, excede

def alertas(ini,fin,volcan):
    from datetime import datetime, timedelta
    df1,df2=[],[]
    fecha_busqueda= datetime.strftime(datetime.strptime(fin,'%Y-%m-%d')-timedelta(days=1),'%Y-%m-%d')
    while datetime.strptime(fecha_busqueda,'%Y-%m-%d') > datetime(int(ini[0:4]),int(ini[5:7]),int(ini[8:10]),0,0): 
        aer = gdb.extraer_alerta_x_dia(volcan,fecha_busqueda)
        if aer[1]=='Alerta inicial':
            break
        else:
            fecha_busqueda = datetime.strftime(datetime.strptime(aer[1],'%d/%m/%Y')-timedelta(days=1),'%Y-%m-%d')
            df1.append(fecha_busqueda)
            df2.append(aer[0])
        
    df1 = [fin]+df1
    df2 = [df2[0]]+df2
    df = pd.DataFrame([df1,df2]).T.set_index(0).rename(columns={1:'alerta'})
    df.index = pd.to_datetime(df.index.rename('fecha'))
    df = df.resample('D').fillna('pad')
    df=df[df.index>=ini]
    df=df[df.index<fin]
    return df

def get_DOAS(fi,ff,volcan):
    vistas = gdb.get_metadata_camIP(volcan)
    if len(vistas)==0:
        return []
    dfDOAS = gdb.get_FlujoDoas(volcan,fi,ff)
    return dfDOAS

def get_lineaGNSS(fi,ff,volcan):
    lineas_GNSS=gdb.get_lineasGNSS_x_volcan(volcan)
    linea_ref = lineas_GNSS.head(1)
    if len(linea_ref)>0:
        df = gdb.get_datos_x_lineaGps(linea_ref.id,fi,ff)
        df['linea']=linea_ref.linea
        
        try:
            df.set_index('fecha',drop=True,inplace=True)
            df = df[df.index<ff]
        except:
            df=[]
    else:
        df=[]
    return df

def get_rsamdr(fi,ff,volcan):
    rsam_blacklist=['CRU','PIC','LAV','AGU','CR3','CVI']
    red = gdb.get_metadata_wws(volcan)
    red=red[red.tipo=='SISMOLOGICA']
    red['sensor'] = red.canal.str[1]
    red = red[red.sensor!='N']
    red=red[~red.codcorto.isin(rsam_blacklist)]
    red1 = red[red.referencia==1].sort_values(by='distcrater').head(1)# 1.referencia
    #red = red[red.index!=red1.index[0]] #red menos la referencia
    #red2 = red[red.index!=red1.index[0]].sort_values(by='distcrater').head(1) #2.cercana
    #if len(red)>0:
    #    red = red[red.index!=red2.index[0]] #red menos la referencia
    #if len(red)>0:
    #    red3 = red[red.distcrater.between(5,10)].sort_values(by='distcrater').head(1)
    #    redt = pd.concat([red1,red2,red3])  
    #else:
    #    redt = pd.concat([red1,red2])  
    redt=red1
    t_index = pd.date_range(start=fi, end=ff, freq='30T')
    df_rsam = df_dr = df_freq = df_pot = pd.DataFrame({'fecha': t_index})
    df_rsam = df_rsam.set_index('fecha')
    df_dr = df_dr.set_index('fecha')
    df_freq = df_freq.set_index('fecha')
    df_pot = df_pot.set_index('fecha')
    for esta in redt.codcorto:
        try:
            df2 = gdb.extraer_rsamdr(fi,ff,esta, '15')
            df2 = pd.DataFrame(df2)
            df2.set_index('fecha',drop=True,inplace=True)
            df2.index = pd.to_datetime(df2.index)
            df2 = df2.resample('12H').mean()
            df2 = df2.reindex(t_index)
            df3 = df2.copy()
            #df2 = df2[(df2.rsam-df2.rsam.mean()) <= (1*df3.rsam.std())]
            #df3 = df3[(df3.dr-df3.dr.mean()) <= (1*df3.dr.std())]
            df_rsam[esta]=df2.rsam
            df_dr[esta]=df3.dr
            df_freq[esta]=df2.frec
            df_pot[esta]=df2.pot
        except:
            ()
    df_rsam = df_rsam[(df_rsam-df_rsam.mean()) <= (1*df_rsam.std())]   
    df_dr = df_dr[(df_dr-df_dr.mean()) <= (1*df_dr.std())]  
    df_pot = df_pot[(df_pot-df_pot.mean()) <= (1*df_pot.std())]

    df_rsam = df_rsam.dropna(how='all')
    df_dr = df_dr.dropna(how='all')
    return df_rsam,df_dr

def fig_timeline(fi,ff,df,n_subplots,tipoev_list,volcanes,volcan,alturas,excede,alertadf,rsam,dr,dfDOAS,dfVRP,GNSS):
    fini,ffin=fi,ff
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import ovdas_figure_lib as ffig
    #from datetime import timedelta
    #import plotly.express as px
    extra_subplots = 1
    t_index = pd.date_range(start=fi, end=ff, freq='D')
    if len(GNSS)>0:extra_subplots +=1
    if len(dfDOAS)>0:extra_subplots +=1
    if len(alturas)>0:extra_subplots +=1
    if len(dr)>0:extra_subplots +=1
    if len(dfVRP)>0:extra_subplots +=1    
    
    total_subplots=extra_subplots+len(df)
    
    fig = make_subplots(rows=n_subplots+extra_subplots, cols=1,shared_xaxes=True,vertical_spacing=0.02,
                        row_heights=[0.2]+(total_subplots-1)*[1])
    fig.update_layout(xaxis={'range':[fini,ffin]})
    colorgraficas='rgba(225,183,29,1)'
    for item in alertadf.alerta.unique():
        if item=='VERDE':color='rgba(0, 255, 0, 0.75)'
        elif item=='NARANJA':color='rgba(255, 128, 0, 0.75)'
        elif item=='AMARILLA':color='rgba(255, 255, 0,0.75)'
        elif item=='ROJA':color='rgba(255, 0, 0, 0.75)'
        df_alerta = alertadf.copy()
        df_alerta.loc[df_alerta.alerta==item,'alerta'] = 0.5
        df_alerta.loc[df_alerta.alerta!=0.5,'alerta'] = 0
        X=df_alerta.index
        Y=df_alerta.alerta
        alertaplot = go.Scattergl(x=X,y=Y,fill='tozeroy',mode='none',fillcolor=color,showlegend=False)
        fig.append_trace(alertaplot,1,1)
        fig.update_layout(xaxis={'range':[fini,ffin]})
    
    k=0
    i=1
    for item in df:
        i=i+1
        
        leyendaname=tipoev_list[k]
        if leyendaname=='LV':leyendaname='VLP'
        trace_num=go.Bar(x=df[item]['dia'],y=df[item]['eventos'],
                opacity=1,name=leyendaname,legendgroup='group1',width=1000*3600*24,showlegend=False,marker= { "color" : colorgraficas})
        fig.append_trace(trace_num,i,1)
        fig.update_yaxes(title_text="<b>evs</b>", row=i)
        colorcla='#'+ffig.colores_cla_hex(item)[:-2]
        #if item in ['LP','TR']:textcolor='black'
        #else:textcolor='white'
        fig.update_layout(xaxis={'range':[fini,ffin]})
        fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df[item]['eventos']),font=dict(color=colorcla),
                                                xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                                yref='y'+str(i),text='<b>'+item+'/día</b>',showarrow=False))
        
        k+=1
    
    if len(dr)>0:
        i=i+1
        for column in dr:
            drplot = go.Scattergl(x=dr.index,y=dr[column],
                        mode='markers',marker_size=5,showlegend=False,
                        opacity=0.75,name='DR '+column,marker= { "color" : colorgraficas})
            fig.append_trace(drplot,i,1)
            maxdr = dr[column].max()
            fig.add_annotation(go.layout.Annotation(x=0.01,y=maxdr,font=dict(color='white'),
                                                xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                                yref='y'+str(i),text='<b>DR '+column+'</b>',showarrow=False))  
            fig.update_yaxes(title_text="<b>cm*cm</b>", row=i)
            fig.update_xaxes(matches='x')
    
    if len(alturas)>0:
        i+=1
        maxdiario = alturas.altura.resample('D').max()
        altura_columna = go.Scattergl(x=maxdiario.index,y=maxdiario,
                    opacity=1,name='Altura columna',showlegend=False,marker= { "color" : colorgraficas})
        fig.append_trace(altura_columna,i,1)
        fig.add_annotation(go.layout.Annotation(x=0.01,y=max(maxdiario),font=dict(color='white'),
                                                xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                                yref='y'+str(i),text='<b>Max. Altura columna diaria</b>',showarrow=False))
        fig.update_yaxes(title_text="<b>m</b>", row=i)
        fig.update_xaxes(matches='x')
   
    if len(dfDOAS)>0:
        i+=1
        import plotly.express as px
        dfDOAS.set_index('fecha',inplace=True)
        
        j=0
        maxdoas=[]
        for doas in dfDOAS.estacion.unique():
            
            dfDOASplot = dfDOAS[dfDOAS.estacion==doas]
            dfDOASplot = dfDOASplot.resample('D').mean().reindex(t_index)
            maxdoas.append(dfDOASplot.flujo.max())
            doasplot = go.Scattergl(x=dfDOASplot.index,y=dfDOASplot.flujo,
                    opacity=1,name=doas,showlegend=False,marker= { "color" :colorgraficas})
            fig.append_trace(doasplot,i,1)
            j+=1
        fig.add_annotation(go.layout.Annotation(x=0.01,y=max(maxdoas),font=dict(color='white'),
                                                xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                                yref='y'+str(i),text='<b>Promedio diario flujo SO2</b>',showarrow=False))
        fig.update_yaxes(title_text="<b>t/día</b>", row=i)
        fig.update_xaxes(matches='x')
   
    
    if len(dfVRP)>0:
        i+=1
        vrpplot=go.Bar(x=dfVRP.timestamp,y=dfVRP.potencia,
                opacity=1,name='vrp',legendgroup='group1',width=1000*3600*24,showlegend=False,marker= { "color" : colorgraficas})
        fig.append_trace(vrpplot,i,1)
        fig.add_annotation(go.layout.Annotation(x=0.01,y=dfVRP.potencia.max(),font=dict(color='white'),
                                                xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                                yref='y'+str(i),text='<b>Anomalías térmicas MIROVA</b>',showarrow=False))
        fig.update_yaxes(title_text="<b>VRP (MW)</b>", row=i)
        fig.update_xaxes(matches='x')
    
    if len(GNSS)>0:
        import math
        i+=1
        GNSS = GNSS[~GNSS.index.duplicated(keep='first')]
        df2 = GNSS.reindex(t_index)
        offset=df2.desplazamiento[0]
        maxy=(df2.desplazamiento-df2.desplazamiento[0]).max()
        if math.isnan(offset):
            offset=0
            maxy=df2.desplazamiento.max()
        gnssplot = go.Scattergl(x=df2.index,y=df2.desplazamiento-offset,
            opacity=1,name=df2.linea.iloc[0],showlegend=False,marker= { "color" :colorgraficas})
        fig.append_trace(gnssplot,i,1)
        try:titulogps='<b>Largo línea GNSS '+df2.linea.iloc[0]+'</b>'
        except:titulogps= '<b>Largo línea GNSS</b>'
        
        fig.add_annotation(go.layout.Annotation(x=0.01,y=maxy,font=dict(color='white'),
                                                xanchor='left',yanchor='top',xref='paper',bgcolor='black',
                                                yref='y'+str(i),text=titulogps,showarrow=False))
        fig.update_yaxes(title_text="<b>cm</b>", row=i)
        fig.update_xaxes(matches='x')

        fig.update_yaxes(range=[0, 10], row=-1, col=1)
        
    fig.update_layout(xaxis={'range':[fini,ffin]})    
    fig.update_yaxes(showticklabels=False,row=1)
    volcan_nombre = volcanes[volcanes.nombre_db==volcan].vol_tipo.iloc[0]+' '+volcanes[volcanes.nombre_db==volcan].nombre.iloc[0]
    fig.update_layout(bargap=0,margin={"r":1,"t":25,"l":1,"b":1},
    title={
    'text':'Timeline resumen - '+volcan_nombre,
    'y':0.99,
    'x':0.5,
    'xanchor':'center',
    'yanchor':'top'
    }
    )

    fig.layout.template = 'plotly_dark'
    
    return fig 

def list_camaras(volcan):
    camaras=gdb.get_metadata_camIP(volcan)
    lista_camaras=[]
    for index, row in camaras.iterrows():
        try:label = row.vista.split('_')[1]
        except:label=row.vista
        camara = {
            'label': label,
            'value':row.vista
            }
        lista_camaras.append(camara)  
    if len(lista_camaras)==0:lista_camaras=[{'label':'Sin Cámaras','value':'Sin Cámaras'}]
    return lista_camaras



lista_volcanes=[]
for index, row in volcanes.iterrows():
    volcan = {'label': row.nombre,'value':row.nombre_db}
    lista_volcanes.append(volcan)   
volcan_selector = dcc.Dropdown(
    clearable=False,
    id='dropdown_volcanes',
    options=lista_volcanes,
    value=volcan_default,
    multi=False,
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
    start_date=get_fechahoy()[0],
    end_date=get_fechahoy()[1],
    min_date_allowed='2010-01-01',
    max_date_allowed='2099-01-01',
    style=
                                    { 
                                      'color': '#212121',
                                      'background-color': '#212121',
                                    } 
)  
search_bar = dbc.Row([dbc.Col(volcan_selector,width=4,id='dropdown_wrapper'),
           dbc.Col(fechas_picker,width=5),
           dbc.Col(dbc.Button("Enviar", color="primary",id='enviar', n_clicks=0),width=1),
           dbc.Col(dbc.Button("Ovdapp", color="primary",outline=True, className="mr-1",id='volver-home',href='/',style={'width':'100%','padding-left':'2px','padding-right':'2px'}),width=1)
   ],justify="between",no_gutters=True) 

navbar = dbc.Navbar([html.A(dbc.Row([
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=2),
                    dbc.Col(dbc.NavbarBrand("Ovdash"),width=9)
                ],
                align="left",
                no_gutters=True,
            ),
          
                style={ 'width':'60%', 'margin-left':'0px' }
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)

counter_cam = dcc.Interval(
          id='interval-component-cams',
          interval=30*1000, # in milliseconds
          n_intervals=0
      )

counter_timeline = dcc.Interval(
          id='interval-component-timeline',
          interval=60*1000*5, # utlimo numero son minutos
          n_intervals=0
      )


timeline =  dcc.Loading(dcc.Graph(id='timeline_graph',style={'height': '100%'}),parent_style={'height':'100%'})

content_cardtimeline = dbc.Card([dbc.CardHeader('Timeline'),dbc.CardBody([timeline],style={'height':'75vh'}),dbc.CardFooter('*Información preliminar obtenida del análisis primario y procesamientos automáticos del Ovdas')],
         outline=True,color='light',className='m-1',style={'height':'100%'})

cajita = html.Div(id='cajita', style={'display': 'none'})

layout = (navbar,html.Div(children=[dbc.Row([dbc.Col(width=3,id='content_camaras',style={'padding-left':'0px','padding-right':'0px'}),
                                      dbc.Col([content_cardtimeline],width=6,id='content_timeline',style={'padding-left':'0px','padding-right':'0px'}),
                                      dbc.Col(width=3,id='content_mapa',style={'padding-left':'0px','padding-right':'0px'})],
                                     id='layout-ovdash')]
                   ),counter_cam,counter_timeline,cajita)


@app.callback(
    [Output('content_camaras','children')],
    [Input('enviar','n_clicks'),Input('interval-component-cams', 'n_intervals')],
    [State('dropdown_volcanes','value')]    
)
def content_camaras(ir,timer,volcan):
    lista_camaras = list_camaras(volcan)
    div_camaras = []
    for cam in lista_camaras:
        card_gif = dbc.Card([dbc.CardBody([gif.GifPlayer(autoplay=True,gif=app.get_asset_url('timelapses/'+cam['value']+'.gif?a='+str(random())),
            still='assets/'+cam['value']+'.gif')],id='cardgif'),],style={"width": "100%"})
        
        card_fija = dbc.Card([dbc.CardImg(alt='Sin Cámara',id='cardfija',src=app.get_asset_url('fijas/'+cam['value']+'.jpg?random='+str(random())))     
                              ],style={"width": "100%"})         
        div_camaras.append(dbc.Row([dbc.Col([card_gif],width=6),dbc.Col([card_fija],width=6)],no_gutters=True)) 
        
    content = dbc.Card([dbc.CardHeader('Cámaras web'),
                              dbc.CardBody(dcc.Loading(className="loading-container",id='loading-card_listaeventos',type='circle',
                                                       
                                                       children=html.Div(div_camaras,style={'height':'100%'})),
                                           style={'overflow':'auto',"height": "75vh"},id='bodyevssinloading')
                              ],outline=True,color='light',className='m-1',style={'height':'100%'})
    
    return [content]

@app.callback(
    [Output('timeline_graph','figure')],
    [Input('enviar','n_clicks'),Input('interval-component-timeline', 'n_intervals')],
    [State('dropdown_volcanes','value'),State('fechas','start_date'),State('fechas','end_date')]    
)
def content_timeline(ir,timer,volcan,fi,ff):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id']
    if trigger=='.':
        fini,ffin = get_fechahoy()
    else:
        fini,ffin=fi,ff
    
    conteo,n_subplots,tipoev_list = contar_evs(fini,ffin,volcan)
    alturas,excede = altura_columna(fini, ffin, volcan)
    alertas_df = alertas(fini,ffin,volcan)
    rsam,dr = get_rsamdr(fini, ffin, volcan)
    DOAS = get_DOAS(fini, ffin, volcan)
    dfVRP = pd.read_json('http://172.16.47.22:8000/api/extraer_vrp?fechaini='+fini+'&fechafin='+ffin+'&volcan='+volcan+'&output=json')
    
    GNSS = get_lineaGNSS(fini, ffin, volcan)
    figure=fig_timeline(fini,ffin,conteo,n_subplots,tipoev_list,volcanes,volcan,alturas,excede,alertas_df,rsam,dr,DOAS,dfVRP,GNSS)
    return [figure]

@app.callback(
    [Output('content_mapa','children')],
    [Input(component_id='enviar', component_property='n_clicks'),Input('cajita', 'children'),Input('timeline_graph', 'relayoutData')],
     [State('dropdown_volcanes','value'),State('fechas','start_date'),
     State('fechas','end_date')]
    )
def mapa(ir,cajita,relayoutData,volcan,fi,ff):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id']
    if trigger=='enviar.n_clicks':
        mapadata,evs= dibujar_mapa(volcanes, volcan,fi,ff)
        return [mapadata]
    elif (trigger=='timeline_graph.relayoutData'):
        listakeys = list(ctx.triggered[0]['value'].keys())
        if ('autosize' in listakeys) ==True:
            mapadata,evs= dibujar_mapa(volcanes, volcan,fi,ff)   
            return [mapadata]
        elif ('xaxis.range[0]' in listakeys) ==True:
            xi = ctx.triggered[0]['value']['xaxis.range[0]'][0:10]
            xf = ctx.triggered[0]['value']['xaxis.range[1]'][0:10]
            mapadata,evs= dibujar_mapa(volcanes, volcan,xi,xf)  
            return [mapadata]
        elif ('xaxis.autorange' in listakeys) ==True:
            mapadata,evs= dibujar_mapa(volcanes, volcan,fi,ff)   
            return [mapadata]            
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate


@app.callback(
    Output('fechas','min_date_allowed'),
    [Input('dropdown_volcanes','value')]
    )
def update_fechaini(volcan):
    alertas_df =alertas('2010-01-01','2015-01-01',volcan)
    inimo = str(alertas_df.head(1).index[0])[0:10]
    return inimo

@app.callback([Output('fechas', 'start-date'),Output('fechas', 'end-date')],
              [Input('interval-component-timeline', 'n_intervals')])
def update_date(n):
    fini,ffin=get_fechahoy()
    return fini,ffin