import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_getfromdb_lib as gdb
import pandas as pd
vol='Villarrica'
fi=0.5
ff=10
voldata = gdb.get_metadata_volcan(vol)
voldata = voldata.drop_duplicates(subset='nombre', keep="first")

red = gdb.get_metadata_wws(volcan='*')
red = red[(red.nombre_db==vol) & (red.tipo=='SISMOLOGICA') & (red.cod.str.startswith('S')==True)]

#%%
RSAMS = []
for esta in list(red.codcorto):
    try:
        df = fut.get_fastRSAM2('2020-05-01','2020-11-30',esta,fi,ff,5,True,'15T')
        df = df.rename(columns={'fastRSAM':esta})
        RSAMS.append(df)
    except:
        ()
RSAM = pd.concat(RSAMS,axis=1)

#%%
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import locale
import numpy as np
 
locale.setlocale(locale.LC_ALL, 'es_ES')
colors = px.colors.qualitative.Plotly

fig = make_subplots(rows=1, cols=1,vertical_spacing=0.025,shared_xaxes='all')
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
fig.update_layout(
    font=dict(
        family="Tahoma",
        size=18,
        ),
    title={
        'text': "RSAM Rápido - "+str(fi)+" - "+str(ff)+" Hz - "+voldata.vol_tipo.iloc[0]+' '+voldata.nombre.iloc[0],
        'y':0.97,
        'x':0.5,
        
        'xanchor': 'center',
            'yanchor': 'top'})


fig.write_html('first_figure.html', auto_open=True)