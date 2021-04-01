import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import matplotlib.pyplot as plt
import ovdas_doc_lib as odl
import ovdas_figure_lib as ffig

vol='NevChillan'

esta_meta = gdb.get_metadata_wws(volcan=vol)
df = gdb.extraer_eventos(inicio='2021-03-01',final='2021-03-31',volcan=vol)
df = pd.DataFrame(df)
df['amplitud_ums_old'] = df['est'].map(esta_meta.drop_duplicates('idestacion').set_index('idestacion')['sens1'])*df['amplitudctas']
df['amplitud_ums'] = df['amplitud_ums'].fillna(df['amplitud_ums_old'])