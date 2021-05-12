import sys
sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
import ovdas_getdatafastRSAM as gdfr
import pandas as pd

fini = '2021-05-01'
ffin = '2021-05-15'
rangef=[0.5,3]
sampling = 60
RSAMS = []
minutes=60
import numpy as np
from scipy import stats

for esta in ['MRN','VN2']:
    try:
        df = gdfr.fastRSAM_dataL(fini+' 00:00:00',ffin+' 00:00:00', esta+'Z', rangef[0],rangef[1], sampling ) 
        df = df.rename(columns={'rsam':esta+'Z'})
        df = df.set_index('fecha')
        df = df[~df.index.duplicated(keep='first')]  
        resultz = df[esta+'Z']
        resultz = resultz[(np.abs(stats.zscore(resultz)) < 3)]
        RSAMS.append(resultz)
        
    except:
        ()
    try:
        for comp in ['N','E']:
            df2 = gdfr.fastRSAM_dataL(fini+' 00:00:00',ffin+' 00:00:00', esta+comp, rangef[0],rangef[1], sampling ) 
            df2 = df2.rename(columns={'rsam':esta+comp})
            df2 = df2.set_index('fecha')
            df2 = df2[~df2.index.duplicated(keep='first')]
            result = df2[esta+comp]
            result = result[(np.abs(stats.zscore(result)) < 3)]
            RSAMS.append(result)
    except:
        ()
RSAM = pd.concat(RSAMS,axis=1) 
