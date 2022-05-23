# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 16:05:15 2021

@author: sergio.morales
"""

import time
from timeloop import Timeloop
from datetime import timedelta

tl = Timeloop()

import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_imageProc_lib as ima
import ovdas_getfromdb_lib as gdb


@tl.job(interval=timedelta(seconds=60))
def sample_job_every_30s():
    print("Current time : {}".format(time.ctime()))   
    ejex =15 #minutos en el eje x
    horas=6 #horas totales
    escala=5 #escala peak 2 peak
    fili,filf=0.4,12 #Frecuencia inicial y final
    markersize=10 #Tamaño de la estrellita
    outdir='C:/GitHub/ovdapp/assets/liveHeli/'
    #outdir='C:/assets/'
    ima.liveHeli(ejex, horas, escala, fili, filf, markersize,outdir)

        
if __name__ == "__main__":
    tl.start(block=True)