# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 11:04:43 2021

@author: sergio.morales
"""
import json
import sys
sys.path.append('//172.16.40.10/Sismologia/pyOvdas_lib/')
import ovdas_getdatafastRSAM as gdfr
import pandas as pd

RSAMS = []
fini,ffin='2021-03-13 00:00:00','2021-03-15 00:00:00'
for esta in ['VN2','MRN','TRA']:
    #try:
    df= gdfr.fastRSAM_data_EstaFilt(fini,ffin, esta+'Z', 0.5,5.0, 3,False) 
    df = df.rename(columns={'fastRSAM':esta+'Z'})
    #df = df.resample('5T').asfreq()
    print(len(df))
    RSAMS.append(df)
#except:
#    ()
#try:
    for comp in ['N','E']:
        #df2 = fut.get_fastRSAM2(fini,ffin,esta+comp,rangef[0],rangef[1],5,True,sampling)
        #df2 = df2.rename(columns={'fastRSAM':esta+comp})
        
        df2= gdfr.fastRSAM_data_EstaFilt(fini,ffin, esta+comp, 0.5,5.0, 3,False) 
        df2 = df2.rename(columns={'fastRSAM':esta+comp})
        #df2 = df2.resample('5T').asfreq()
        print(len(df2))
        RSAMS.append(df2)
    #except:
    #    ()
    
RSAM = pd.concat(RSAMS,axis=1)


