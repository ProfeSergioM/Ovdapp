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
fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

volcanes_auto=['Villarrica']
volcanes_list=[]
for volcan in volcanes_auto:
    volcanes_list.append({'label': volcanes[volcanes.nombre_db==volcan].nombre.iloc[0],'value':volcanes[volcanes.nombre_db==volcan].nombre_db.iloc[0]})

freqconteo = dcc.Dropdown(id='freqconteo-autovdas',
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
                                      'width':'100%'
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
          interval=60*1000*1, # in milliseconds
          n_intervals=0
      )

def helicorder(detect,horas):
    import ovdas_WWS_lib as wws
    import ovdas_SeismicProc_lib as sp
    import datetime as dt
    ejex =10 #minutos en el eje x
    from datetime import timedelta
    import pandas as pd
    import numpy as np
    fini = dt.datetime.utcnow() - dt.timedelta(hours=horas)
    ffin = dt.datetime.utcnow()
    subsample=10
    finiround = fini - (fini -fini.min) % timedelta(minutes=ejex)
    ffinround = ffin + (ffin.min - ffin) % timedelta(minutes=ejex)-timedelta(milliseconds=100)
    
    traza = wws.extraer_signal(estacion='VN2',componente='Z',inicio=finiround,fin=ffin)
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
    aer = df_traza.reindex(t_index)
    aer.index = aer.index.rename('fecha')
    aer = aer.rename(columns={0:'amp'})
    grp = aer.groupby(pd.Grouper(freq='10Min'))
    
    filas = []
    for key, df in grp:
        filas.append(df)

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
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
        if len(detect)>0:
            evs = detect[detect.index.to_series().between(min(filas[i].index),max(filas[i].index))]
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
        if len(detect)>0:
            evs = evs.sort_values(by='DRc',ascending=False)
            e=0
            for index,row in evs.iterrows():
                DR = str(int(row.DRc))
                lev = go.Scatter(x=[index,index],y=[-scale/2,scale/2],showlegend=False,hoverinfo='x',line=dict(color='red'))
                fig.append_trace(lev,i+1,1)
                if e==0:
                    fig.add_annotation(go.layout.Annotation(x=index,y=scale,font=dict(color='white'),
                                            xanchor='center',yanchor='middle',xref='x'+str(i+1),
                                            yref='y'+str(i+1),text=DR+r' cm<sup>2</sup> ',showarrow=False)) 
                e=+1
    for minu in range(0,11):
        fig.add_annotation(go.layout.Annotation(x=minu*0.1,y=0,font=dict(color='white'),
                                        xanchor='center',yanchor='top',xref='paper',
                                        yref='paper',text=str(minu),showarrow=False))  
        
    fig.update_yaxes(row=i+1,range=[-scale,scale],showticklabels=False)  
    fig.update_xaxes(row=i+1,tickformat="%M",showticklabels=False,title='Minutos')  
        
    fig.layout.template = 'plotly_dark'
    fig.update_layout(bargap=0,margin={"r":10,"t":25,"l":60,"b":30},
                    
    title={
    'text':'Estación VN2',
    'y':0.99,
    'x':0.5,
    'xanchor':'center',
    'yanchor':'top'
    }
    )
    return fig

def crear_figura(rangef,fini,ffin,volcan,estaRSAM,countev_period):
    if countev_period=='H':name='/hora'
    elif countev_period=='D':name='/día'
    markersize=4
    ffinxaxis = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    df_count,df = oap.get_pickle_OVV(volcan,fini,ffin,countev_period)


    df_RSAM = fut.get_fastRSAM2(fini,ffin,estaRSAM,rangef[0],rangef[1],5,True,'15T')               
    import numpy as np
    #ampslogs=np.power(df['ampl'],0.2)/1
    tipoevs = len(df.tipoev.unique())
    
    fig = make_subplots(rows=tipoevs+5, cols=1,shared_xaxes=True, vertical_spacing=0.025)
    
    i=1
    for tipoev in df.tipoev.unique():

        fig.add_trace(
        go.Bar( x=df_count.index, y=df_count[tipoev],marker= { "color" : 'white'},name='ev'),
        row=i, col=1
        )
        fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df_count[tipoev]),font=dict(color='white'),
                                            xanchor='left',yanchor='bottom',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text=tipoev+name,showarrow=False))      
        
        fig.add_trace(
        go.Scattergl( x=df_count.index, y=df_count[tipoev+'cumsum'],name='Acum. ev'+name,line=dict(color='crimson')),
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
    fig.add_shape(
            type="rect",
            xref="paper",
            yref='y'+str(i),
            x0=0,
            y0=0,
            x1=1,
            y1=max(df_RSAM.fastRSAM)*1.5,
            fillcolor="#141d26",
            opacity=0.5,
            layer="below",
            line_width=0         
            )
    i+=1
    ######################          #DR
    dfdr = df[df.tipoev=='LP']
    fig.add_trace(
    go.Scattergl( x=dfdr.index, y=dfdr['DRc'], mode='markers',name='DR',
               marker= {"size":markersize, "color" : 'white'}),
    row=i, col=1
    )
    fig.update_traces(opacity=0.6,marker=dict(color='white',size=df['ampl']**0.2*3  ,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(row=i,range=[0,max(dfdr['DRc'])*1.5])        
    fig.update_yaxes(title_text="cm*cm", row=i)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(dfdr['DRc'])*1.5,font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='DR/ev',showarrow=False))  
    
    fig.add_shape(
            type="rect",
            xref="paper",
            yref='y'+str(i),
            x0=0,
            y0=0,
            x1=1,
            y1=max(dfdr['DRc'])*1.5,
            fillcolor="#141d26",
            opacity=0.5,
            layer="below",
            line_width=0         
            )
    i+=1
    ######################           # freq

    fig.add_trace(
    go.Scattergl( x=df.index, y=df['fdom'], mode='markers',name='fdom',
               marker= {"size":markersize, "color" : 'white'}),
    row=i, col=1
    )
    fig.update_traces(opacity=0.6,marker=dict(color='white',size=df['ampl']**0.2*3,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(title_text="Hz", row=i)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=1,font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='Frecuencia dom/ev',showarrow=False))  
    fig.update_yaxes(type="log",row=i)
    fig.update_yaxes(row=i,range=[np.log10(0.5),np.log10(20)],dtick=np.log10(2))
	
    fig.add_shape(
            type="rect",
            xref="paper",
            yref='y'+str(i),
            x0=0,
            y0=0,
            x1=1,
            y1=10,
            fillcolor="#141d26",
            opacity=0.5,
            layer="below",
            line_width=0         
            )
    i+=1
    
    
    
    ################################     # AMPLITUD
    fig.add_trace(
    go.Scattergl( x=df.index, y=df['ampl'], mode='markers',name='Amplitud',
               marker= {"size":df['ampl'], "color" : 'black'}),
    row=i, col=1
    )
    fig.update_traces(opacity=0.6,marker=dict(color='white',size=df['ampl']**0.2*3,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(title_text="um/s", row=i)
    fig.update_yaxes(row=i,range=[0,max(df['ampl'])*1.5])
    #fig.update_yaxes(type="log",row=i)
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df['ampl'])*1.5,font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='Amplitud/ev',showarrow=False))  
    fig.add_shape(
            type="rect",
            xref="paper",
            yref='y'+str(i),
            x0=0,
            y0=0,
            x1=1,
            y1=max(df['ampl'])*1.5,
            fillcolor="#141d26",
            opacity=0.5,
            layer="below",
            line_width=0         
            )
    i+=1
    #################################       # Duracion
    fig.add_trace(
    go.Scattergl( x=df.index, y=df['duracion'], mode='markers',name='Duración',
               marker= {"size":markersize, "color" : 'white'}),
    row=i, col=1
    )
    fig.update_traces(opacity=0.6,marker=dict(color='white',size=df['ampl']**0.2*3,line=dict(color='crimson',width=0)),
                  row=i,
                  )
    fig.update_yaxes(title_text="s", row=i)
    fig.update_yaxes(row=i,range=[0,max(df['duracion'])*1.5])
    fig.add_annotation(go.layout.Annotation(x=0.01,y=max(df['duracion'])*1.5,font=dict(color='white'),
                                            xanchor='left',yanchor='top',xref='paper',bgcolor='#141d26',
                                            yref='y'+str(i),text='Duración/ev',showarrow=False))  
   

    
    fig['layout']['xaxis']['tickfont']['color']='rgba(0,0,0,0)'
    fig['layout']['xaxis'+str(i)]['range']=[fini,ffinxaxis]
    
    fig.update_yaxes(title_text="um/s", row=i)
    fig.update_xaxes(title_text="Fecha", row=i)
    fig.add_shape(
            type="rect",
            xref="paper",
            yref='y'+str(i),
            x0=0,
            y0=0,
            x1=1,
            y1=max(df['duracion'])*1.5,
            fillcolor="#141d26",
            opacity=0.5,
            layer="below",
            line_width=0         
            )
    i+=1
    
    
    
    totalfilas = i
    j=1
    k=1    
 
    for tipoev in df.tipoev.unique():
        fig['data'][j].update(yaxis='y'+str(i))
        fig['layout']['yaxis'+str(i)]=dict(overlaying='y'+str(k),side='right',title='Acum. ev'+name,title_font=dict(color='crimson'))
        #fig.update_yaxes(title_text="ev/hora", row=j)
        
        fig.add_shape(
                type="rect",
                xref="paper",
                yref='y'+str(i),
                x0=0,
                y0=0,
                x1=1,
                y1=max(df_count[tipoev+'cumsum']),
                fillcolor="#141d26",
                opacity=0.5,
                layer="below",
                line_width=0         
                )
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


PLOTLY_LOGO = app.get_asset_url('img/Sismologia_2020.png?random='+str(random()))  
navbar = dbc.Navbar(
[

    # Use row and col to control vertical alignment of logo / brand
    dbc.Row(
        [
            dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px"),width=1),
            dbc.Col(dbc.NavbarBrand("Proyecto de monitoreo sísmico automático OVV",style={'color':'white'}),width=10),
            dbc.Col(dbc.Button("Ovdapp", color="primary",outline=True, className="mr-1",id='volver-home',href='http://172.16.47.23:8080/'),width=1)
            
            
        ],justify="left",
    style={'width':'100%'})

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
    html.Div(html.P('Periodo de conteo de eventos',id='titulo-fecha-autovdas')),
    freqconteo,
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
                                   dbc.Col([dcc.Loading(html.Div(id='colgrafica-autovdas'))],width=6),
                                   dbc.Col([html.Div(id='heli-autovdas')],width=3)
                                   ]),
                   dbc.Row([counter_imggif,counter_reloj],no_gutters=True,justify='start'),
                   
                   ])

@app.callback(
    #[Output("colgrafica-autovdas", "children"),Output("colmapa-autovdas", "children")],
    [Output("colgrafica-autovdas", "children")],
    [Input('interval-component-gif-autovdas', 'n_intervals'),Input("submit-filtro-autovdas", "n_clicks")],
    [State('freqconteo-autovdas','value'),State('dropdown_volcanes','value'), State('RSAM-range-slider-autovdas', 'value'),State('fechas-autovdas','start_date'),State('fechas-autovdas','end_date')]
)
def update_cam_fija(*args):
    ffin=args[-1]
    fini=args[-2]
    rangef=args[-3]
    volcan=args[-4]
    freqconteo=args[-5]
    
    
    rsam_blacklist=['CRU','PIC','LAV','AGU','CR3','CVI']
    red = gdb.get_metadata_wws(volcan)
    red=red[red.tipo=='SISMOLOGICA']
    red['sensor'] = red.canal.str[1]
    red = red[red.sensor!='N']
    red=red[~red.codcorto.isin(rsam_blacklist)]
    red1 = red[red.referencia==1].sort_values(by='distcrater').head(1)# 1.referencia
    estaRSAM = red1.codcorto.iloc[0]
    
    

    fig = crear_figura(rangef,fini,ffin,volcan,estaRSAM,freqconteo)
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


@app.callback([Output('live-update-text-autovdas', 'children'),Output('fechas-autovdas','start_date'),Output('fechas-autovdas','end_date'),
               Output('fechas-autovdas','max_date_allowed'),
               Output("heli-autovdas", "children")],
              [Input('interval-component-reloj-autovdas', 'n_intervals')],
              [State('dropdown_volcanes','value'),State('freqconteo-autovdas','value')]
              )
def update_date(n,volcan,freq):
    from flask import request
    print('tic! from '+request.remote_addr)
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')

    finidetect = dt.datetime.utcnow() - dt.timedelta(hours=horas)
    df_count,detect = oap.get_pickle_OVV(volcan,finidetect,ffin,freq)
    heli  = helicorder(detect,horas)
    heli = html.Div(children=[
        dcc.Graph(
            id='timeline-orca',
            figure=heli,
            style={ 'height':'80vh' }
        )
    ])
    helicard = dbc.Card([
        dbc.CardHeader('Sismograma - Últimas 2 horas'),
        dbc.CardBody(heli)
        
        ],outline=True,color='light')
    return [html.P(children=[str(datetime.datetime.now())[:16]],style={'text-align':'center'})],fini,ffin,ffin,[helicard]