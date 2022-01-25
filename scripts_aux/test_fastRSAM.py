# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:00:49 2021

@author: sergio.morales
"""
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut

fini='2022-01-18'
ffin='2022-01-26'
esta='VT2'
fi=0.5
ff=10

import numpy as np
bandas = [x.decode('utf-8') for x in list(np.arange(fi,ff+0.1,0.1).astype('|S3'))]

import ovdas_getdatafastRSAM as gdr

aer2  = gdr.fastRSAM_dataL(fini+' 00:00:00', ffin+' 00:00:00', esta+'E', fi, ff,60*6)




#aer = fut.get_fastRSAM2(fini, ffin, esta+'Z', fi, ff, 1, True, '15T')