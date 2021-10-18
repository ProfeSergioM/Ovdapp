ini='2010-01-01'
vol='Villarrica'
fin='2021-10-15'


import sys
sys.path.append('//172.16.40.10/sismologia/pyOvdas_lib/')
import ovdas_getfromdb_lib as gdb
from datetime import datetime, timedelta
volcanes =gdb.get_metadata_volcan(vol,rep='y')
volcanes = volcanes.drop_duplicates(subset='nombre', keep="first")

#Extraer todos los cambios de alerta
fechas=[]
alertas=[]
#fechas.append(datetime.strptime(final,'%Y-%m-%d'))         
aer = gdb.extraer_alerta_x_dia(vol,fin)
alertas.append(aer[0])
fechas.append(datetime.strptime(aer[1],'%d/%m/%Y'))      
#%%
fecha_busqueda = datetime.strptime(aer[1],'%d/%m/%Y')

while fecha_busqueda>datetime.strptime(ini,'%Y-%m-%d'):
    aer = gdb.extraer_alerta_x_dia(vol,datetime.strftime(fecha_busqueda-timedelta(days=1),'%Y-%m-%d'))
    try:
    
        fecha_busqueda = datetime.strptime(aer[1],'%d/%m/%Y')
        fechas.append(fecha_busqueda)
        alertas.append(aer[0])
    except:
        break
 
#%%
import pandas as pd
df = pd.DataFrame([fechas,alertas]).T
df = df.set_index(0).rename(columns={1:'alerta'})
df = df.sort_index()
lastRow = pd.DataFrame([[datetime.strptime(fin,'%Y-%m-%d'),df.tail(1)['alerta'].iloc[0]]],columns=[0,'alerta']).set_index(0)

dfAlerta = df.append(lastRow)

#%%
DICT_ALEC = dict(VERDE='success',AMARILLA='warning',NARANJA='orange',ROJA='danger')
listacambios =[]
import dash_bootstrap_components as dbc

listacambios.append(dbc.ListGroupItem(str(dfAlerta.index[0])[0:10]+' - '+'Inicio Monitoreo (alerta inicial :'+dfAlerta['alerta'].iloc[0].capitalize()+')',color=DICT_ALEC[dfAlerta['alerta'].iloc[0]]))


for j in range(1,len(dfAlerta)-1):
    listacambios.append(dbc.ListGroupItem(str(dfAlerta.index[j])[0:10]+' - '+dfAlerta['alerta'].iloc[j-1].capitalize()+' -> '+dfAlerta['alerta'].iloc[j].capitalize(),
                                          color=DICT_ALEC[dfAlerta['alerta'].iloc[j]]))

listacambios.append(dbc.ListGroupItem(str(dfAlerta.index[-1])[0:10]+' - '+'Nivel actual :'+dfAlerta['alerta'].iloc[-1].capitalize(),color=DICT_ALEC[dfAlerta['alerta'].iloc[-1]]))
