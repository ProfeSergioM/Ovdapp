import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import matplotlib.pyplot as plt
import ovdas_doc_lib as odl
import ovdas_figure_lib as ffig

volcan='PuyehueCCaulle'
fini='2020-12-01'
ffin='2020-12-10'
rangef=[0.5,2]
sampling='5T'


voldata = gdb.get_metadata_volcan(volcan)
voldata = voldata.drop_duplicates(subset='nombre', keep="first")
red = gdb.get_metadata_wws(volcan='*')
red = red[(red.nombre_db==volcan) & (red.tipo=='SISMOLOGICA') & (red.cod.str.startswith('S')==True)]
red = red[~red.codcorto.isin(['CHP','KIK'])]
RSAMS = []
for esta in list(red.codcorto):
    try:
        df = fut.get_fastRSAM2(fini,ffin,esta+'Z',rangef[0],rangef[1],5,True,sampling)
        df = df.rename(columns={'fastRSAM':esta+'Z'})
        RSAMS.append(df)
        
    except:
        ()
    try:
        for comp in ['N','E']:
            df2 = fut.get_fastRSAM2(fini,ffin,esta+comp,rangef[0],rangef[1],5,True,sampling)
            df2 = df2.rename(columns={'fastRSAM':esta+comp})
            RSAMS.append(df2)
    except:
        ()
RSAM = pd.concat(RSAMS,axis=1) 