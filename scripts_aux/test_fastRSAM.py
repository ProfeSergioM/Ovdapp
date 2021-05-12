# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:00:49 2021

@author: sergio.morales
"""
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut

fini='2021-01-01'
ffin='2021-12-31'
esta='VN2'
fi=0.5
ff=10

aer = fut.get_fastRSAM2(fini,ffin,esta+'Z',fi,ff,5,True,'5T')

import ovdas_getdatafastRSAM as gdr

aer2  = gdr.fastRSAM_dataL(fini+' 00:00:00', ffin+' 00:00:00', esta+'Z', fi, ff)