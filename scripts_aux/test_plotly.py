import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_getfromdb_lib as gdb
import pandas as pd

def crear_fastRSAM():
    pointopacity=0.5
    datalinewidth=1
    import plotly.express as px
    import numpy as np
    import locale     
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    locale.setlocale(locale.LC_ALL, 'es_ES')
    colors = px.colors.qualitative.Plotly
    
    fig = make_subplots()
  
    return fig

fig = crear_fastRSAM()
fig.update_layout(
        xaxis = dict(
            showgrid=False),
        yaxis = dict(
            showgrid=False))
fig.write_html('first_figure.html', auto_open=True)


        