import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import matplotlib.pyplot as plt

ini='2020-01-25'
fin='2020-02-25'

redvol = gdb.get_metadata_wws('Tatara')

redvolsis=redvol[redvol.tipo=='SISMOLOGICA']
    
estaref = redvolsis[redvolsis.referencia==1] 