import time
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()

import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_imageProc_lib as ima
import ovdas_getfromdb_lib as gdb


@tl.job(interval=timedelta(seconds=60*7))
def sample_job_every_60s():
    print("Current time : {}".format(time.ctime()))
    import sys
    sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
    import ovdas_imageProc_lib as ima
    import ovdas_getfromdb_lib as gdb
    
    
    volcanes =gdb.get_metadata_volcan('*',rep='y')
    for index,row in volcanes.iterrows():
        #print(row.id)
        ima.gif_normales(volcanes='("'+str(row.id)+'")',salida='',rutasal='C:/dash/ovdapp/assets/timelapses/')
    #%%
    from os import listdir
    from os.path import isfile, join
    giffiles = [f for f in listdir('C:/dash/ovdash/assets/timelapses/') if isfile(join('C:/dash/ovdash/assets/timelapses/', f))]
    
    #%%
    import subprocess
    for item in giffiles:
        subprocess.Popen(['gifsicle.exe', 
                              '-b',
                                  'C:/dash/ovdapp/assets/timelapses/'+item[:-4]+'.gif',
                                 #'--colors','256',
                                 '--resize-width','400',
                                 
                                 #'-O3',
                                 #'>','C:/Users/sergio/dash/ovdash/assets/timelapses/'+item[:-4]+'_opt.gif'
                                 ],shell=True, stdout=subprocess.PIPE)

        
if __name__ == "__main__":
    sample_job_every_60s()
    tl.start(block=True)