# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 09:32:34 2021

@author: sergio.morales
"""

import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_figure_lib as ffig
import ovdas_getfromdb_lib as gdb
import pandas as pd
aer = gdb.extraer_eventos('2021-01-01','2021-01-10',volcan='*')
aer = pd.DataFrame(aer)
aer = aer[aer.tipoevento=='VT']
vol = volcanes =gdb.get_metadata_volcan('LagMaule',rep='y')
ffig.plot_map_REAV_ovdapp(aer.head(1),vol)