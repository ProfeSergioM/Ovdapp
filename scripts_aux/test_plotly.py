import sys
import os
sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
#import ovdas_reportes_scripts as reportes
import ovdas_getfromdb_lib as gdb
import ovdas_figure_lib as ffig
import ovdas_WWS_lib as wws
import ovdas_SeismicProc_lib as sp
import datetime as dt
import ovdas_ovdapp_lib as oap



ejex =10 #minutos en el eje x
horas=2
from datetime import timedelta
import pandas as pd
import numpy as np
fini = dt.datetime.utcnow() - dt.timedelta(hours=horas)
ffin = dt.datetime.utcnow()
subsample=10
finiround = fini - (fini -fini.min) % timedelta(minutes=ejex)
ffinround = ffin + (ffin.min - ffin) % timedelta(minutes=ejex)-timedelta(milliseconds=100)
finidetect = dt.datetime.utcnow() - dt.timedelta(hours=horas)
detect_count,detect = oap.get_pickle_OVV('Villarrica',finidetect,ffin)


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
            fig.add_annotation(go.layout.Annotation(x=0,y=0.5,font=dict(color='white'),
                                        xanchor='right',yanchor='bottom',xref='paper',
                                        yref='y'+str(i+1),text=diatxt,showarrow=False))
            
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
    fig.update_layout(bargap=0,margin={"r":10,"t":25,"l":50,"b":30},
                    
    title={
    'text':'Estación VN2',
    'y':0.99,
    'x':0.5,
    'xanchor':'center',
    'yanchor':'top'
    }
    )
    return fig


fig = helicorder(detect,2)
fig.write_html('first_figure.html', auto_open=True)
    