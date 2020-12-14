import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd

ini='2020-01-25'
fin='2020-02-25'

vols = gdb.get_metadata_volcan('*', rep='y')
vols = pd.DataFrame(vols)
ids = list(vols.id)

ids = ids[0:3]
M=[]
for idvol in ids:
    aer = gdb.get_disp_dia_volcan(idvol,ini,fin)
    for esta in aer.cod.unique():
        df = aer[aer.cod==esta]
        df = df.rename(columns={'porcentaje':esta}).set_index('fecha',drop=True).drop(columns=['cod'])
        M.append(df)
M = pd.concat(M,axis=1)

def dispo(M):
    pointopacity=0.5
    datalinewidth=1
    import plotly.express as px
    import numpy as np
    import locale     
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    locale.setlocale(locale.LC_ALL, 'es_ES')
    colors = px.colors.qualitative.Plotly
    
    fig = make_subplots(rows=M.shape[1],cols=1)

    return fig

fig = dispo(M)

fig.update_layout(
        xaxis = dict(
            showgrid=False),
        yaxis = dict(
            showgrid=False))
fig.write_html('first_figure.html', auto_open=True)


        