# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 09:08:56 2016

@author: cdesbois
"""
import matplotlib.pyplot as plt
import numpy as np
import os
#import utils
plt.rcParams["figure.figsize"] = (8.5,3)
#%%
def plotHeader(descr, param={'save':False}):
    """
    plot the header of the file
    """
    hcell = 2
    wcell = 2
    wpad = 0.2
    nbrows = 11
    nbcol = 2
    hpad = 0.1
    txt = []
    for key in descr.keys():
        value = descr[key]
        if key == 'Weight':
            value *= 10
        txt.append([key, value])
#    ['Age', 'Sex', 'Weight', 'Version', 'Date', 'Patient Name', 'Sampling Rate',
#    'Height', 'Patient ID', 'Equipment', 'Procedure']
    fig = plt.figure(figsize=(nbcol*hcell + hpad, nbcol* wcell + wpad))
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    table = ax.table(cellText= txt, loc='center', fontsize=18, bbox=[0,0,1,1])
    #table.auto_set_font_size(False)
    table.set_fontsize(10)
    #table.set_zorder(10)
    for sp in ax.spines.values():
        sp.set_color('w')
        sp.set_zorder(0)
    if param['save']:
        figName = 'header'+ str(param['item'])
        name = os.path.join(param['path'],figName)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            figMemo(param['path'],figName)
    return fig


def histPaM(data, param={'save':False}):
    """PaM histogramme using matplotlib without dropna()to remove NaN"""

    if 'ip1m' not in data.columns:
        print('no ip1 in the data')
        return
    if 'ip1PR' not in data.columns:
        print('no ip1PR in the data')
        return

#    fig = plt.figure(figsize=(15,8))
    fig = plt.figure(figsize=(8,4))
    
    ax1 = fig.add_subplot(121)
    ax1.set_title('arterial pressure (+ quartiles)')
    ax1.set_xlabel('arterial pressure (mmHg)')
    ax1.hist(data.ip1m.dropna(), bins= 50, color='red',
             edgecolor='none')
#    q25, q50, q75 = np.percentile(data.ip1m.dropna(), [25, 50, 75])
#    ax1.axvline(q50, linestyle= 'dashed', linewidth= 2, color= 'k' )
#    ax1.axvline(q25, linestyle= 'dashed', linewidth= 1, color= 'k' )
#    ax1.axvline(q75, linestyle= 'dashed', linewidth= 1, color= 'k' )

    ax2 = fig.add_subplot(122)
    ax2.hist(data.ip1PR.dropna(), bins = 50, range=(25,65), color= 'gray',
             edgecolor= 'none')
    ax2.set_title('heart rate  (+ quartiles)')
    ax2.set_xlabel('heart rate (bpm)')
    axes = [ax1, ax2]
    for i, item in enumerate(['ip1m', 'ip1PR']):
        try:
            q25, q50, q75 = np.percentile(data[item].dropna(),[25,50,75])
            axes[i].axvline(q50, linestyle= 'dashed', linewidth= 2, color= 'k' )
            axes[i].axvline(q25, linestyle= 'dashed', linewidth= 1, color= 'k' )
            axes[i].axvline(q75, linestyle= 'dashed', linewidth= 1, color= 'k' )
        except:
            print('no arterial pressure recorded')
    for ax in axes:
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for locs in ['top', 'right', 'left']:
            ax.spines[locs].set_visible(False)
    fig.tight_layout() 
    if param['save']:
        figName = 'histPaM'+ str(param['item'])
        name = os.path.join(param['path'],figName)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            figMemo(param['path'],figName)
    return fig

#---------------------------------------------------------------------------------------------------
def plotOneOverTime(x, y, colour):
    """
    plot y over x using colour
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, color=colour)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()        
    return fig

#----------------------------------------------------------------------------------------
def histCO2iso(data, param={'save':False}):
    """CO2 and iso histogramme (NB CO2 should have been converted from % to mmHg)"""

    if 'co2exp' not in data.columns:
        print('no co2exp in the data')
        return

#    fig = plt.figure(figsize=(15,8))
    fig = plt.figure(figsize=(8,4))

    ax1 = fig.add_subplot(121)
    ax1.hist(data.co2exp.dropna(), bins= 50, color= 'blue')
    ax1.set_title('etCO2 (+ quartiles)')
    ax1.set_xlabel('EtCO2 (mmHg)')

    ax2 = fig.add_subplot(122)
    ax2.hist(data.aaExp.dropna(), bins= 50, color= ['magenta'], range=(0.5, 2))
    ax2.set_title('etIsoflurane  (+ quartiles)')
    ax2.set_xlabel('EtIso (%)')

    axes = [ax1, ax2]
    for i, item in enumerate(['co2exp', 'aaExp']):
        try:
            q25, q50, q75 = np.percentile(data[item].dropna(),[25,50,75])
            axes[i].axvline(q50, linestyle= 'dashed', linewidth= 2, color= 'k' )
            axes[i].axvline(q25, linestyle= 'dashed', linewidth= 1, color= 'k' )
            axes[i].axvline(q75, linestyle= 'dashed', linewidth= 1, color= 'k' )
        except:
            print(item, 'not used')

    for ax in axes:
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for locs in ['top', 'right', 'left']:
            ax.spines[locs].set_visible(False)
    fig.tight_layout()   
    if param['save']:
        figName = 'histCO2iso'+ str(param['item'])
        name = os.path.join(param['path'],figName)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            figMemo(param['path'],figName)

    return fig

#-----------------------------------------------------------------------------------------
def bppa(data):
    """arterial box plot """
    fig = plt.figure(figsize=(8,4))

    card = ['ip1s','ip1m','ip1d']
    fdata = data.loc[:,card]    ##filter the data

    ax1 = fig.add_subplot(111)
    for n,col in enumerate(fdata.columns) :
        ax1.boxplot(fdata[col], positions=[n+1], notch=True)

    ax1.set_xticks(range(n+2))
    card.insert(0,'')
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.get_yaxis().tick_left()
    ax1.get_xaxis().tick_bottom()
    ax1.set_xticklabels(card)
    ax1.set_ylim(30,140)
    ax1.set_ylabel('mmHg')
    ax1.set_title('arterial pressure distribution (quartiles & +1.5 IQR)')
    ax1.axhline(70, linestyle='dashed', linewidth=2, color = 'gray')
    #ax1.axhline(50, linestyle='dashed', linewidth=1, color = 'gray')
    #ax1.axhline(100, linestyle='dashed', linewidth=1, color = 'gray')
    fig.tight_layout() 
    return fig

#----------------------------------------------------------------------------------------------
def bpgas(data):
    """CO2 and O2 box plot """
    fig = plt.figure(figsize=(8,4))

    resp = ['co2exp','o2insp']
    fdata = data.loc[:,resp]    ##filter the data

    ax2 = fig.add_subplot(111)
    for n,col in enumerate(fdata.columns) :
        ax2.boxplot(fdata[col], positions=[n+1], notch=True)

    ax2.set_xticks(range(n+2))
    resp.insert(0,'')
    for locs in ['top', 'right']:
        ax2.spines[locs].set_visible(False)
    ax2.get_yaxis().tick_left()
    ax2.get_xaxis().tick_bottom()
    ax2.set_xticklabels(resp)
    ax2.set_ylim(20,70)
    ax2.set_ylabel('mmHg(CO2) or %(O2)')
    ax2.set_title('gaz distribution (quartiles & +1.5 IQR)')
    ax2.axhline(38, linestyle='dashed', linewidth=2, color = 'gray')
    fig.tight_layout() 
    return fig

#---------------------------------------------------------------------------------------------------
def cardiovasc(data,param):
    """
    cardiovascular plot (ip1s,ip1m,ip1d + ip1PR,
    input = dataFrame, dic(path, xmin, xmax,unit)
    """
    #global timeUnit
    x = data.index
    if 'ip1PR' not in data.columns:
        print ('no pulseRate in the recording')
        return
    IPs = data['ip1s']
    IPm = data['ip1m']
    IPd = data['ip1d']
    HR = data['ip1PR']

    path= param['path']
    xmin= param['xmin']
    xmax= param['xmax']
    unit= param['unit']

    fig = plt.figure()
    fig.suptitle('cardiovascular')
    axL = fig.add_subplot(111)
    axL.set_xlabel('time (' + unit +')')
    axL.set_ylabel('arterial Pressure')
    axL.yaxis.label.set_color('black')
    axL.spines['left'].set_color('r')
    axL.tick_params(axis='y', colors='r')

    axL.plot(x,IPm,'-r', label= 'arterial pressure', linewidth=2)
    axL.fill_between(x,IPd,IPs,color='r',alpha=0.3)
    #ax1.fill_betweenx(x,IPm, 70, where=IPm<70, color='r',alpha=0.3)
    axL.set_ylim(30,150)
#    axL.spines["top"].set_visible(False)
#    axL.get_xaxis().tick_bottom()
    axL.axhline(70, linewidth=1, linestyle= 'dashed', color='r')

    axR = axL.twinx()
    axR.set_ylabel('heart Rate')
    axR.yaxis.label.set_color('black')
    axR.spines['left'].set_color('gray')
    axR.tick_params(axis='y', colors='gray')
    axR.set_ylim(20,100)

    axR.plot(x,HR,'gray',label = 'heart rate', linewidth=2)
    #ax2.set_ylim(0,2)
#    axR.spines["top"].set_visible(False)
#    axR.get_xaxis().tick_bottom()
    axes = [axL, axR]
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin,xmax)
    fig.tight_layout()
#    axR.set_xlim(xmin,xmax)
#    axL.set_xlim(xmin,xmax)

    if param['save']:
        figName = 'cardiovasc'+ str(param['item'])
        name = os.path.join(path,figName)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            figMemo(path,figName)

    return fig

#---------------------------------------------------------------------------------------------------
def co2iso(data,param):
    """
    anesth plot (CO2/iso)
    input = dataFrame, dic(path, xmin, xmax,unit)
    """
    if 'co2exp' not in data.columns:
        print ('no co2exp in the recording')
        return
    x = data.index
    etCO2 = data.co2exp
    inspCO2 = data.co2insp

    path= param['path']
    xmin= param['xmin']
    xmax= param['xmax']
    unit= param['unit']

    #rr = data['CO2 RR‘]
    inspO2 = data.o2insp
    etO2 = data.o2exp
    inspIso = data.aaInsp
    etIso = data.aaExp

    fig = plt.figure()
    fig.suptitle('CO2 Isoflurane')
    axL = fig.add_subplot(111)
    axL.set_xlabel('time (' + unit +')')

    axL.set_ylabel('CO2')
    axL.yaxis.label.set_color('black')
    axL.spines['left'].set_color('blue')
    axL.tick_params(axis='y', colors='blue')

    axL.plot(x, etCO2, color='blue')
    axL.plot(x, inspCO2, color='blue')
    axL.fill_between(x,etCO2,inspCO2,color='blue', alpha=0.1)
#    axL.spines["top"].set_visible(False)
#    axL.get_xaxis().tick_bottom()
    axL.axhline(38,linewidth=1, linestyle='dashed', color='blue')

    axR = axL.twinx()
    axR.set_ylabel('Isoflurane')
    axR.yaxis.label.set_color('black')
    axR.spines['right'].set_color('m')
    axR.tick_params(axis='y', colors='m')
    # func(axR, x, etIso, inspIs, color='m', x0=38)
    axR.plot(x,etIso,color='m')
    axR.plot(x,inspIso,color='m')
    axR.fill_between(x,etIso,inspIso,color='m',alpha=0.2)
    axR.set_ylim(0,3)
#    axR.spines["top"].set_visible(False)
#    axR.get_xaxis().tick_bottom()

#    axR.set_xlim(xmin, xmax)
#    axL.set_xlim(xmin, xmax)
    
    for ax in [axL, axR]:
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin,xmax)
    fig.tight_layout()

    if param['save']:
        figName = 'co2iso'+ str(param['item'])
        name = os.path.join(path,figName)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            figMemo(path,figName)

    return fig

# proposition de yann pour simplifier le code (à implémenter)
def func(ax, x, y1, y2, color='blue', x0=38):
    ax.plot(x, y1, color=color)
    ax.plot(x, y2, color=color)
    ax.fill_between(x,y1, y2,color=color, alpha=0.1)
    ax.axhline(x0,linewidth=1, linestyle='dashed', color=color)

#-----------------------------------------------------------------------------------------------------------
def co2o2(data,param):
    """
    respiratory plot (CO2 and Iso)
    input = dataFrame, dic(path, xmin, xmax,unit)
    output = plot
    """
    x = data.index
    try:
        etCO2 = data.co2exp
    except:
        print('no CO2 records in this recording')
        return
    inspCO2 = data.co2insp
    path= param['path']
    xmin= param['xmin']
    xmax= param['xmax']
    unit= param['unit']

    rr = data.co2RR
    inspO2 = data.o2insp
    etO2 = data.o2exp
    inspIso = data.aaInsp
    etIso = data.aaExp

    fig = plt.figure()
    fig.suptitle('CO2 & O2 (insp & endTidal)')

    axL = fig.add_subplot(111)
    axL.set_ylabel('CO2')
    axL.set_xlabel('time (' + unit +')')
    axL.yaxis.label.set_color('blue')
    axL.spines['left'].set_color('blue')
    axL.tick_params(axis='y', colors='blue')
    axL.plot(x, etCO2, color='blue')
    axL.plot(x, inspCO2, color='blue')
    axL.fill_between(x,etCO2,inspCO2,color='blue', alpha=0.1)
    axL.axhline(38,linestyle= 'dashed', linewidth=1,color='blue')

    axR = axL.twinx()
    axR.set_ylabel('O2')
    axR.yaxis.label.set_color('k')
    axR.spines['right'].set_color('k')
    axR.tick_params(axis='y', colors='k')
    axR.plot(x,etO2,color='y')
    axR.plot(x,inspO2,color='y')
    axR.fill_between(x,etO2,inspO2,color='y',alpha=0.2)
    axR.set_ylim(21,80)
    axR.axhline(30,linestyle= 'dashed', linewidth=1,color='y')
    
    axes = [axL, axR]
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin,xmax)
    fig.tight_layout()

    if param['save']:
        figName = 'co2o2'+ str(param['item'])
        name = os.path.join(path,figName)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            figMemo(path,figName)
    return fig

#---------------------------------------------------------------------------------------
def ventil(data,param):
    """
    ventilation plot (.tvInsp, .pPeak, .pPlat, .peep, .minVexp, .co2RR, .co2exp )
    input = dataFrame, dic(path, xmin, xmax,unit)
    """
    x = data.index
    path= param['path']
    xmin= param['xmin']
    xmax= param['xmax']
    unit= param['unit']
#    if 'tvInsp' not in data.columns:
#        print('no spirometry data in the recording')
#        return

    fig = plt.figure(figsize=(8.5,5))
    fig.suptitle('ventilation')

    ax1 = fig.add_subplot(211)
    ax1.set_ylabel('tidal volume')
    ax1.yaxis.label.set_color('k')
    ax1.spines['left'].set_color('k')
    ax1.tick_params(axis='y', colors='k')
    ax1.yaxis.label.set_color('k')
    try:
        ax1.plot(x,data.tvInsp,color='y', linewidth=2)
    except:
        print('no spirometry data in the recording')
    ax1R = ax1.twinx()
    ax1R.set_ylabel('pression')
    ax1R.yaxis.label.set_color('r')
    ax1R.spines['right'].set_color('r')
    ax1R.tick_params(axis='y', colors='r')
    try:
        ax1R.plot(x, data.pPeak, color='r', linewidth=1, linestyle='-')
        ax1R.plot(x, data.pPlat, color='r', linewidth=1, linestyle=':')
        ax1R.plot(x, data.peep, color='r', linewidth=1, linestyle='-')
        ax1R.fill_between(x,data.peep,data.pPeak,color='r', alpha=0.1)
    except:
        print('no spirometry data in the recording')        
    ax2 = fig.add_subplot(212, sharex= ax1)
    ax2.set_ylabel('MinVol & RR')
    try:
        ax2.plot(x,data.minVexp,color='y', linewidth=2)
        ax2.plot(x,data.co2RR,color='black', linewidth=1, linestyle = '--')
    except:
        print('no spirometry data recorded')
    ax2.set_xlabel('time (' + unit +')')

    ax2R = ax2.twinx()
    ax2R.set_ylabel('etCO2')
    ax2R.yaxis.label.set_color('b')
    ax2R.spines['right'].set_color('b')
    ax2R.tick_params(axis='y', colors='b')
    try:
        ax2R.plot(x, data.co2exp, color='b', linewidth=1, linestyle='-')
    except:
        print('no capnometry in the recording')
    ax1R.set_ylim(0,50)
    ax1.set_ylim(500,2000)
    
    axes = [ax1, ax1R, ax2, ax2R]
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin,xmax)
    fig.tight_layout()
    if param['save']:
        figName = 'ventil'+ str(param['item'])
        name = os.path.join(path,figName)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            figMemo(path,figName)
    return fig

#------------------------------------------------------------------------
def recrut(data, param):
    """
    to show a recrut manoeuver (.pPeak, .pPlat, .peep, .tvInsp)
    input = dataFrame, dic(path, xmin, xmax,unit)
    """
    x = data.index
    path= param['path']
    xmin= param['xmin']
    xmax= param['xmax']
    unit= param['unit']

    fig = plt.figure()
    fig.suptitle('recrutement')

    ax1 = fig.add_subplot(111)
    ax1.set_xlabel('time (' + unit +')')
    ax1.spines["top"].set_visible(False)
    ax1.set_ylabel('pression : peep & Peak, (cmH2O)')
    ax1.yaxis.label.set_color('black')
    ax1.spines['left'].set_color('red')
    ax1.tick_params(axis='y', colors='red')
    ax1.plot(x, data.pPeak, color='r', linewidth=1, linestyle='-')
    ax1.plot(x, data.pPlat, color='r', linewidth=1, linestyle=':')
    ax1.plot(x, data.peep, color='r', linewidth=2, linestyle='-')
    ax1.fill_between(x,data.peep,data.pPeak,color='red', alpha=0.1)
    ax1.set_ylim(0,50)

    ax2 = ax1.twinx()
    ax2.set_ylabel('volume')
    ax2.yaxis.label.set_color('black')
    ax2.spines['right'].set_color('yellow')
    ax2.tick_params(axis='y', color='yellow')
    ax2.plot(x,data.tvInsp,color='y', linewidth=2)

    ax1.set_xlim(xmin, xmax)
    #ax2.set_xlim(xmin, xmax)
    
    axes = [ax1, ax2]
    for ax in axes:
        ax.get_xaxis().tick_bottom()
        ax.spines["top"].set_visible(False)
        
    fig.tight_layout() 
    if param['save']:
        figName = 'recrut'+ str(param['item'])
        name = os.path.join(path,figName)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            figMemo(path,figName)
    return fig

def ventilCardio(data, param):
    x = data.index
    path= param['path']
    xmin= param['xmin']
    xmax= param['xmax']
    unit= param['unit']

    if 'tvInsp' not in data.columns:
        print('no spirometry data in the recording')

    fig = plt.figure()
    fig.suptitle('ventilation & cardiovasc')

    ax1 = fig.add_subplot(211)
    ax1.set_ylabel('tidal volume')
    ax1.yaxis.label.set_color('k')
    ax1.spines['left'].set_color('k')
    ax1.tick_params(axis='y', colors='k')
    ax1.yaxis.label.set_color('k')
    ax1.plot(x,data.tvInsp,color='y', linewidth=2)

    ax1R = ax1.twinx()
    ax1R.set_ylabel('pression')
    ax1R.yaxis.label.set_color('r')
    ax1R.spines['right'].set_color('r')
    ax1R.tick_params(axis='y', colors='r')
    ax1R.plot(x, data.pPeak, color='r', linewidth=1, linestyle='-')
    ax1R.plot(x, data.pPlat, color='r', linewidth=1, linestyle=':')
    ax1R.plot(x, data.peep, color='r', linewidth=1, linestyle='-')
    ax1R.fill_between(x,data.peep,data.pPeak,color='r', alpha=0.1)

    ax2 = fig.add_subplot(212, sharex= ax1)
    ax2.set_ylabel('arterial pressure')
    ax2.plot(x, data.ip1m, color='r', linewidth =1, linestyle='-')
    ax2.plot(x, data.ip1s, color='r', linewidth =0, linestyle='-')
    ax2.plot(x, data.ip1d, color='r', linewidth =0, linestyle='-')
    ax2.fill_between(x, data.ip1s, data.ip1d, color='r', alpha=0.2)
    ax2.set_xlabel('time (' + unit +')')

#    ax1.set_xlim(108, 114)
#    ax2.set_ylim(35, 95)
#    ax1R.set_ylim(5, 45)
#    ax2.set_ylim(40, 95)
#    ax2.set_ylim(40, 90)
    ax2.yaxis.label.set_color('r')
    ax2.spines['left'].set_color('r')
    ax2.tick_params(axis='y', colors='r')
#    ax2.set_ylim(35, 95)
    
    axes = [ax1, ax1R, ax2]
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()

    fig.tight_layout() 
    return fig

#------------------------------------------------------------------------
def saveDistri(data,path):
    """save as '0_..' the 4 distributions graphs for cardiovasc annd respi"""
    bpgas(data).savefig((path['sFig'] + '0_bpgas.png') , bbox_inches = 'tight')
    histCO2iso(data).savefig((path['sFig']+ '0_histCO2iso.png') , bbox_inches = 'tight')
    bppa(data).savefig((path['sFig'] + '0_bppa.png') , bbox_inches = 'tight')
    histPaM(data).savefig((path['sFig']+ '0_histPaM.png') , bbox_inches = 'tight')

def figMemo(path,figName):
    """
    append latex citation commands in a txt file inside the fig folder
    create the file iif it doesn't exist
    """
    includeText = "\\begin{frame}{fileName}\n\t\\includegraphics[width = \\textwidth]{bg/" + figName + "} \n\end{frame} \n %----------------- \n \\n"

    figInsert = os.path.join(path,'figIncl.txt')
    with open(figInsert,'a') as file:
        file.write( includeText +'\n')
        file.close()
