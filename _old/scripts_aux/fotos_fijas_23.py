import time
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()

import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_imageProc_lib as ima
import ovdas_getfromdb_lib as gdb


@tl.job(interval=timedelta(seconds=30))
def sample_job_every_30s():
    print("Current time : {}".format(time.ctime()))
    volcanes =gdb.get_metadata_volcan('*',rep='y')
    try:
        for index,row in volcanes.iterrows():
            ima.fotos_normales(volcanes='("'+str(index)+'")',salida='',rutasal='C:/dash/ovdapp/assets/fijas')
    except:
        ()

        
if __name__ == "__main__":
    tl.start(block=True)