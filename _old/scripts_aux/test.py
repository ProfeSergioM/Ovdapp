import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import matplotlib.pyplot as plt
import ovdas_doc_lib as odl
import ovdas_figure_lib as ffig
import ovdas_getdatafastRSAM as gdfr
fini='2021-01-01 00:00:00'
ffin='2021-01-31 00:00:00'
rangef=[0.5,10]
volcan='Villarrica'

voldata = gdb.get_metadata_volcan(volcan)
voldata = voldata.drop_duplicates(subset='nombre', keep="first")
red = gdb.get_metadata_wws(volcan='*')
red = red[(red.nombre_db==volcan) & (red.tipo=='SISMOLOGICA') & (red.cod.str.startswith('S')==True)]
red = red[~red.codcorto.isin(['CHP','KIK'])]
red = red.sort_values(by='distcrater').head(5)
RSAMS = []
for esta in list(red.codcorto):
    try:
        #df = fut.get_fastRSAM2(fini,ffin,esta+'Z',rangef[0],rangef[1],5,True,sampling)
        df= gdfr.fastRSAM_data_EstaFilt(fini,ffin, esta+'Z', rangef[0],rangef[1], 3,False) 
        df = df.rename(columns={'fastRSAM':esta+'Z'})
        RSAMS.append(df)
    except:
        ()
    try:
        for comp in ['N','E']:
            #df2 = fut.get_fastRSAM2(fini,ffin,esta+comp,rangef[0],rangef[1],5,True,sampling)
            #df2 = df2.rename(columns={'fastRSAM':esta+comp})
            
            df2= gdfr.fastRSAM_data_EstaFilt(fini,ffin, esta+comp, rangef[0],rangef[1], 3,False) 
            df2 = df2.rename(columns={'fastRSAM':esta+comp})
            RSAMS.append(df2)
    except:
        ()
RSAM = pd.concat(RSAMS,axis=1) 
del RSAMS




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
if len(df_RE)>0:
    df_RE = pd.concat(df_RE,axis=1)
    RSAM = pd.concat([RSAM,df_RE],axis=1)
listaHV = [item[:-1] for item in RSAM.columns if item[-1]=='N']
if len(listaHV)>0:
    hvs=[]
    for es in listaHV:
        hv = ((RSAM[es+'N']+RSAM[es+'E'])/2)/RSAM[es+'Z']
        hv = hv.rename(es+'_H/V')
        hvs.append(hv)
    hvs = pd.concat(hvs,axis=1)
else:
    hvs=[]
if len(hvs)>0:
    RSAM = pd.concat([RSAM,hvs],axis=1)
