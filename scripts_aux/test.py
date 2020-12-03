import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import matplotlib.pyplot as plt

ini='2020-01-25'
fin='2020-02-25'

vols = gdb.get_metadata_volcan('*', rep='y')
vols = pd.DataFrame(vols)
ids = list(vols.id)


for idvol in ids:
    M=[]
    aer = gdb.get_disp_dia_volcan(idvol,ini,fin)
    for esta in aer.cod.unique():
        df = aer[aer.cod==esta]
        df = df.rename(columns={'porcentaje':esta}).set_index('fecha',drop=True).drop(columns=['cod'])
        M.append(df)
    M = pd.concat(M,axis=1)
    fig,axes = plt.subplots(nrows=M.shape[1],sharex=True,squeeze=False)

    i=0
    for col in M.columns:

        axes[i][0].bar(M[col].index,M[col])
        axes[i][0].set_ylim(0,100)

        i+=1
        
    plt.close('all')
    