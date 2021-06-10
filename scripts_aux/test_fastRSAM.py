# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:00:49 2021

@author: sergio.morales
"""
import sys
sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
import ovdas_future_lib as fut

fini='2019-01-01'
ffin='2021-12-31'
esta='VN2'
fi=0.5
ff=10

import ovdas_getdatafastRSAM as gdr

aer2  = gdr.fastRSAM_dataL(fini+' 00:00:00', ffin+' 00:00:00', esta+'Z', fi, ff,60*6)

#%%
import datetime as dt
import matplotlib.dates as mdates
x_lims = list(map(dt.datetime.fromtimestamp, [aer2.fecha.min(), aer2.fecha.max()]))
x_lims = mdates.date2num(x_lims)

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
fig = plt.figure(figsize=(20,10))
gs = gridspec.GridSpec(1, 1)
fig1 = fig.add_subplot(gs[0])
import numpy as np
bandas = np.arange(0.5,10.1,0.1)
spec = aer2[bandas.astype('|S3').astype(str)].T
y_lims = [spec.head(1).index[0],spec.tail(1).index[0]]
spec_norm = (spec-spec.min())/(spec.max()-spec.min())
specgram = fig1.imshow(spec_norm,aspect='auto',vmin=0,vmax=1,
                       origin='lower',cmap='viridis',
                       extent = [x_lims[0], x_lims[1], 0.5,9.9])
plt.colorbar(specgram)