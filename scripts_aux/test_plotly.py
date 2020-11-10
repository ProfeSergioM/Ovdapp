import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_getfromdb_lib as gdb
import pandas as pd
volcan='Villarrica'
rangef=[0.5,10]
voldata = gdb.get_metadata_volcan(volcan)
voldata = voldata.drop_duplicates(subset='nombre', keep="first")
red = gdb.get_metadata_wws(volcan='*')
red = red[(red.nombre_db==volcan) & (red.tipo=='SISMOLOGICA') & (red.cod.str.startswith('S')==True)]
es='VN2'
estas=[es+'Z',es+'N',es+'E']
fini='2020-11-01'
ffin='2020-11-30'
#%%
RSAMS = []
for esta in list(red.codcorto):
    try:
        df = fut.get_fastRSAM2(fini,ffin,esta,rangef[0],rangef[1],5,True,'15T')
        df = df.rename(columns={'fastRSAM':esta+'Z'})
        RSAMS.append(df)
        
    except:
        ()
    try:
        for comp in ['N','E']:
            df2 = fut.get_fastRSAM2(fini,ffin,esta+comp,rangef[0],rangef[1],5,True,'15T')
            df2 = df2.rename(columns={'fastRSAM':esta+comp})
            RSAMS.append(df2)
    except:
        ()
RSAM = pd.concat(RSAMS,axis=1) 
del RSAMS
#%%
listaRE = [item[:-1] for item in RSAM.columns if item[-1]=='Z']
redRE = red[red.codcorto.isin(listaRE)].sort_values(by='distcrater', ascending=True)
estaRE =list(redRE.codcorto)
df_RE = []
for i in range(0,len(listaRE)):
    for j in range(i+1,len(estaRE)):
        esta1=estaRE[i]
        esta2=estaRE[j]
        df = (RSAM[esta1+'Z']/RSAM[esta2+'Z'])
        df = df.rename(esta1+'Z'+'/'+esta2+'Z')
        df_RE.append(df)
df_RE = pd.concat(df_RE,axis=1)
RSAM = pd.concat([RSAM,df_RE],axis=1)
listaHV = [item[:-1] for item in RSAM.columns if item[-1]=='N']
if len(listaHV)>0:
    hvs=[]
    for es in listaHV:
        hv = ((RSAM[es+'N']+RSAM[es+'E'])/2)/RSAM[es+'Z']
        hv = hv.rename(es+'_H/V')
        hvs.append(hv)
    hvs = pd.concat(hvs)
    
RSAM = pd.concat([RSAM,hvs],axis=1)
#%%
import plotly.express as px
import locale     
from plotly.subplots import make_subplots
import plotly.graph_objects as go
locale.setlocale(locale.LC_ALL, 'es_ES')
colors = px.colors.qualitative.Plotly

fig = make_subplots(rows=3, cols=1,vertical_spacing=0.025,shared_xaxes='all')
i=0

listaRSAM = [item for item in list(RSAM.columns) if (len(item)==4) & (item[-1]=='Z')]
for sta in listaRSAM:
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

listaRE = [item for item in list(RSAM.columns) if (len(item)==9)]
if len(listaRE)>0:
    for sta in list(listaRE):
        data = RSAM[sta]
        fig.add_trace(go.Scattergl(x=RSAM.index, y=data.values,name=sta,mode='markers',marker_size=5,opacity=0.2,
                                   hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',marker_color=colors[i]),row=2, col=1) 
        fig.add_trace(go.Scattergl(x=RSAM.index, y=data.rolling(10).mean(),name=sta+' 10 MM',mode='lines',line_width=0.5,
                                    hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',line_color=colors[i]),row=2, col=1) 
        i+=1
    fig.update_yaxes(range=[0,RSAM[listaRE].max().max()*1.1],col=1,row=2)
    fig.update_yaxes(title_font=dict(size=14),title_text='Razón RSAM',fixedrange=True,col=1,row=2)
listaHV = [item for item in list(RSAM.columns) if (len(item)==7)]
if len(listaHV)>0:
    for sta in list(listaHV):
        data = RSAM[sta]
        fig.add_trace(go.Scattergl(x=RSAM.index, y=data.values,name=sta,mode='markers',marker_size=5,opacity=0.2,
                                   hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',marker_color=colors[i]),row=3, col=1) 
        fig.add_trace(go.Scattergl(x=RSAM.index, y=data.rolling(10).mean(),name=sta+' 10 MM',mode='lines',line_width=0.5,
                                    hovertemplate='%{x|%Y/%m/%d %H:%M} - %{y:.2f} um/s',line_color=colors[i]),row=3, col=1) 
        i+=1
    fig.update_yaxes(range=[0,RSAM[listaHV].max().max()*1.1],col=1,row=3)
    fig.update_yaxes(title_font=dict(size=14),title_text='Razón H/V',fixedrange=True,col=1,row=3)

fig.layout.template = 'plotly_dark'
fig.update_yaxes(title_font=dict(size=14),title_text='RSAM - um/s',fixedrange=True,col=1,row=1)

fig.update_xaxes(title_font=dict(size=14),title_text='Fecha',col=1,row=3)
fig.update_xaxes(range=[min(data.index),max(data.index)],col=1,row=3)
fig.update_yaxes(range=[0,RSAM[listaRSAM].max().max()*1.1],col=1,row=1)


fig.update_xaxes(tickfont=dict(size=12))    
fig.update_layout(
    font=dict(
        family="Tahoma",
        size=18,
        ),
    title={
        'text': "RSAM Rápido - "+str(rangef[0])+" - "+str(rangef[1])+" Hz - "+voldata.vol_tipo.iloc[0]+' '+voldata.nombre.iloc[0],
        'y':0.97,
        'x':0.5,
        
        'xanchor': 'center',
            'yanchor': 'top'})
fig.write_html('first_figure.html', auto_open=True)


        