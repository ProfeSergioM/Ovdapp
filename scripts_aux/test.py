import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut

df_RSAM = fut.get_fastRSAM2('2020-11-01','2020-11-30','VN2',0.5,10,5,True,'15T') 