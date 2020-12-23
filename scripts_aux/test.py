import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut
import ovdas_ovdapp_lib as oap
import ovdas_getfromdb_lib as gdb
import pandas as pd
import matplotlib.pyplot as plt
import ovdas_doc_lib as odl
import ovdas_figure_lib as ffig

volcan='PuyehueCCaulle'

red = gdb.get_metadata_wws(volcan=volcan)
red=red[red.tipo=='SISMOLOGICA']

sta_list=[]
for index,row in red.iterrows():
    sta_list.append({'label': row.sitio+' ('+row.codcorto+')','value':row.codcorto})