# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 12:47:44 2021

@author: sergio.morales
"""

#%%
def odHeli(ejex,horas,escala,fili,filf,markersize,vol):
    import sys
    sys.path.append('//172.16.40.10/sismologia/pyovdas_lib/')
    import ovdas_WWS_lib as wws
    import ovdas_getfromdb_lib as gdb
    import pandas as pd
    import ovdas_figure_lib as ffig
    import ovdas_SeismicProc_lib as sep
    import datetime as dt
    from datetime import timedelta
    import numpy as np
    volcan =gdb.get_metadata_volcan(vol,rep='y')
    volcan = volcan.drop_duplicates(subset='nombre', keep="first")
    
    estas = gdb.get_metadata_wws(volcan=volcan.nombre_db.iloc[0], est=None, estadoEst='on', estadoInst='on')
    estas = estas[estas.tipo=='SISMOLOGICA']
    estas = estas.sort_values(by='referencia',ascending=True)
    estas = estas.reset_index(drop=True)
    
    fini = dt.datetime.utcnow() - dt.timedelta(hours=horas)
    ffin = dt.datetime.utcnow()
    subsample=10
    finiround = fini - (fini -fini.min) % timedelta(minutes=ejex)
    ffinround = ffin + (ffin.min - ffin) % timedelta(minutes=ejex)-timedelta(milliseconds=100)
    try:
        esta0=estas[estas.index==0].codcorto.iloc[0]
        traza = wws.extraer_signal(estacion=esta0,componente='Z',inicio=finiround,fin=ffin)
        if len(traza)==0:
            i=1
    
            flag=False
            while flag==False:
                esta0=estas[estas.index==i].codcorto.iloc[0]
                try:
                    traza = wws.extraer_signal(estacion=esta0,componente='Z',inicio=finiround,fin=ffin)
                except:
                    i+=1
                if len(traza)>0:
                    flag=True
                else:
                    i+=1   
    except:
        print("Estación con problemas")
    traza = sep.filtrar_traza(traza,tipo="butter",orden=4,fi=fili,ff=filf)
    t_index = pd.date_range(start=finiround, end=ffinround, freq='100ms').round('100ms')
    times = []
    amps = []
    for i in range(0,len(traza)):
        times.extend(traza[i].times('timestamp'))
        amps.extend(traza[i].data*traza[i].stats.calib)
    times = np.around(times,2)
    amps = np.around(amps,2)
    df_traza = pd.DataFrame(amps,index=times)
    df_traza = df_traza[::subsample]
    df_traza['fecha_abs'] = pd.to_datetime(df_traza.index, unit='s')
    df_traza = df_traza.set_index('fecha_abs',drop=True)
    df_traza.index = df_traza.index.round('100ms')
    aer = df_traza.reindex(t_index)
    aer.index = aer.index.rename('fecha')
    aer = aer.rename(columns={0:'amp'})
    grp = aer.groupby(pd.Grouper(freq=str(ejex)+'Min'))
    filas = []
    for key, df in grp:
        filas.append(df)
        
        
    evs = pd.DataFrame(gdb.extraer_eventos(finiround.strftime('%Y-%m-%d %H:%M'), ffin.strftime('%Y-%m-%d %H:%M'),
                                           volcan.nombre_db.iloc[0]))
    if len(evs)>0:
        evs = evs.set_index('fecha')
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    plt.rcParams["axes.linewidth"]  = 1.25
    plt.rcParams['axes.edgecolor']  = 'k'
    plt.rcParams["axes.grid"] = True
    fig = plt.figure(figsize=(12, 8))
    outer_grid = gridspec.GridSpec(1, 1, wspace=0.0, hspace=0.0)
    inner_grid = gridspec.GridSpecFromSubplotSpec(len(filas), 1,
                subplot_spec=outer_grid[0], wspace=0.0, hspace=0.0)
    from itertools import cycle
    azules =['#072F5F', '#1261A0', '#3895D3']
    pool = cycle(azules)
    from matplotlib.lines import Line2D
    if len(amps)>0:
        maxy = abs(max(amps))*1.5
        scale=round(maxy/2)
        if scale==0:scale=1
        #scale=escala/2
        for i in range(0,len(filas)):
            evsfila = (evs.loc[min(filas[i].index).strftime('%Y-%m-%d %H:%M'):max(filas[i].index).strftime('%Y-%m-%d %H:%M')])
            ax = plt.Subplot(fig, inner_grid[i])
            wave = ax.plot(filas[i].index,filas[i].amp,clip_on=False,color=next(pool))
            if len(evsfila)>0:
                legend_elements=[]
                for te in evs.tipoevento.unique():
                    legend_elements.extend([Line2D([], [], marker='*', label=te,lw=0,ms=markersize,mec='k',mfc=ffig.colores_cla(te))])
                fig.legend(ncol=1,title='Eventos',handles=legend_elements, loc='lower right', fontsize=10,frameon=True)
                for index,row in evsfila.iterrows():
                    evplot = ax.plot(row.name,scale/2,'*',ms=markersize,
                                 mec='k',mfc=ffig.colores_cla(row.tipoevento),label=row.tipoevento)
                
                
            ax.set_xlim(min(filas[i].index),max(filas[i].index))
            tituloy = str(min(filas[i].index))[11:16]
            ax.get_yaxis().set_ticks([])
            ax.get_xaxis().set_ticks([])
            ax.set_ylim(-scale,scale)
            ax.text(min(filas[i].index),0,str(min(filas[i].index))[11:16]+' -',ha='right',va='center')    
            ax.patch.set_facecolor("None")
            if (tituloy in ['00:00','06:00','12:00','18:00']) or i==0:
                diatxt=str(min(filas[i].index))[8:10]+'-'+str(min(filas[i].index))[5:7]+'            '
                ax.text(min(filas[i].index),0,diatxt,ha='right',va='bottom')        
            fig.add_subplot(ax)
            med=filas[i].index[int(len(filas[i].index)/2)]
            if i==0:
                titulo = 'Estación '+esta0+' - '+volcan.vol_tipocorto.iloc[0]+' '+volcan.nombre.iloc[0]
                ax.text(min(filas[i].index),scale*3,'Hora actual \n'+str(dt.datetime.utcnow())[:19]+' UTC',
                        ha='left',va='top',size=10)
                ax.text(filas[i].index[int((len(filas[i].index)-1)*1/5)],scale*3,
                        'Trazas filtradas entre \n'+str(fili)+' y '+str(filf)+' Hz',
                        ha='left',va='top',size=10)
                ax.text(max(filas[i].index),scale*3,titulo,ha='right',va='top',size=15) 
            # Get dimensions of y-axis in pixels
                y1, y2 = plt.gca().get_window_extent().get_points()[:, 1]
                
                # Get unit scale
                yscale = (y2-y1)/(scale*2)
                
                # We want 2 of these as fontsize
                fontsize = 4*yscale
                #escala
                escala1 = ax.vlines(filas[1].index[70],-scale,scale,lw=5)
                escala2 = ax.text(filas[1].index[150],0,str(int(scale*2))+' um/s\n  (p2p)',ha='left',va='center',size=10)
                escala1.set_clip_on(False);escala1.set_clip_on(False)
            if i==len(filas)-1:
                
                ax.text(med,-scale*1.75,'+ minutos',ha='center',va='top') 
                ax.text(min(filas[i].index),-scale*1.75,'hora (UTC)',ha='right',va='top') 
                for minu in range(0,ejex):
                    ax.text(filas[i].index[int(minu*len(filas[i].index)/ejex)],-scale*1.1,str(minu),ha='center',va='top') 
    
    
    all_axes = fig.get_axes()
    #show only the outside spines
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
        if ax.is_last_row():
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
        if ax.is_last_col():
            ax.spines['right'].set_visible(True)
    
    
    
    
    plt.subplots_adjust(left=0.1, right=0.925, top=0.925, bottom=0.05)
    plt.savefig(volcan.nombre_db.iloc[0]+'.png')
    plt.close('all')

vol='Hudson'
ejex =30 #minutos en el eje x
horas=12 #horas totales
escala=5 #escala peak 2 peak
fili,filf=0.4,12
markersize=10


odHeli(ejex, horas, escala, fili, filf, markersize,vol)