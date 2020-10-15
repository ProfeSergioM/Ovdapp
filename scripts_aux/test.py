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
import pandas as pd
import numpy as np
volcanes =gdb.get_metadata_volcan('*',rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")
def get_fechahoy(): 
    fini = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=7), '%Y-%m-%d')
    ffin = dt.datetime.strftime(dt.datetime.utcnow() + dt.timedelta(days=1), '%Y-%m-%d')
    return fini,ffin

inicio,final=get_fechahoy()
eventos = gdb.extraer_eventos(inicio,final,volcan='*')
eventos = pd.DataFrame(eventos)
#ml general
eventosml = eventos[eventos.ml>2]
#dr general
eventosdr = eventos[eventos.dr>=500]
#dr villarrica
eventosdr_villarrica = eventos[(eventos.idvolc==28) & (eventos.dr>=30)]

eventos = pd.concat([eventosml,eventosdr,eventosdr_villarrica])
eventos = eventos.sort_values(by='fecha',ascending=False).head(20)
eventos.fecha = eventos.fecha.astype('datetime64[s]')
eventos = eventos.drop_duplicates(subset='fecha', keep="first")
eventos = eventos.fillna({'profundidad':-1,'ml':0})
eventos.latitud = np.where(eventos.latitud.isnull(),eventos.idvolc.map(volcanes.set_index('id')['latitud']),eventos['latitud']).astype(float)
eventos.longitud = np.where(eventos.longitud.isnull(),eventos.idvolc.map(volcanes.set_index('id')['longitud']),eventos['longitud']).astype(float)