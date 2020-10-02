import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_imageProc_lib as ima
import ovdas_getfromdb_lib as gdb

aer = gdb.get_metadata_wws('*')