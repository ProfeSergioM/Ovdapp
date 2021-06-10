# -*- coding: utf-8 -*-
"""
Created on Mon May 17 16:57:15 2021

@author: sergio.morales
"""
fini='2020-05-17'
ffin='2021-05-17'
esta='VN2'
fi=0.5
ff=10
volcan='Villarrica'
countev_period='D'

import ovdas_ovdapp_lib as oap
df = oap.get_pickle_OVV(volcan,fini,ffin,countev_period)
LP_df = df[1]
import ovdas_getdatafastRSAM as gdr
RSAM_df  = gdr.fastRSAM_dataL(fini+' 00:00:00', ffin+' 00:00:00', esta+'Z', fi, ff,60)
#%%
