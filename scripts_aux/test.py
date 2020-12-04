import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import matplotlib.pyplot as plt
import ovdas_doc_lib as odl
import ovdas_figure_lib as ffig

ini='2020-11-25'
fin='2020-12-25'



df = gdb.extraer_eventos(ini, fin, 'LagMaule')
df = pd.DataFrame(df)
df = df[df.tipoevento!='VD']