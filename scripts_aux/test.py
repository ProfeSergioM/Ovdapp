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

df = gdb.extraer_eventos('2020-01-01', '2020-02-01', 'NevChillan')
df= pd.DataFrame(df)