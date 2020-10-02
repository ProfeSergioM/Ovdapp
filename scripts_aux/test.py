import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_imageProc_lib as ima
import ovdas_getfromdb_lib as gdb
import ovdas_ovdapp_lib as oap

df_count,df = oap.get_pickle_OVV('Villarrica','2020-01-01','2020-10-01')