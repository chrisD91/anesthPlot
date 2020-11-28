#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Apr 19 09:08:56 2016

functions to plot the trend data

@author: cdesbois

"""
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

#import utils
font_size = 'medium' # large, medium
params = {'font.sans-serif': ['Arial'],
          'font.size': 12,
          'legend.fontsize': font_size,
          'figure.figsize': (8.5, 3),
          'axes.labelsize': font_size,
          'axes.titlesize': font_size,
          'xtick.labelsize': font_size,
          'ytick.labelsize': font_size,
          'axes.xmargin': 0}
plt.rcParams.update(params)
plt.rcParams['axes.xmargin'] = 0            # no gap between axes and traces


#////////////////////////////////////////////////////////////////
def color_axis(ax, spine='bottom', color='r'):
    """
    change the color of the label + tick + spine
    input:
        ax = matplotlib axis
        spine = in ['left', 'right', 'bottom']
        color = matplotlib color
    """
    ax.spines[spine].set_color(color)
    if spine == 'bottom':
        ax.xaxis.label.set_color(color)
        ax.tick_params(axis='x', colors=color)
    elif spine in ['left', 'right']:
        ax.yaxis.label.set_color(color)
        ax.tick_params(axis='y', colors=color)

def append_loc_to_fig(ax, dt_list, label='g'):
    """
    append vertical lines to indicate a location 'eg: arterial blood gas'
    Parameters
    ----------
    ax : matplotlib figure.axis
    dt_list = datetime list
    label = a key to add to the label (default is 'g')
    Returns
    -------
    dictionary containing the locations

    """
    num_times = mdates.date2num(dt_list)
    res = {}
    for i, num_time in enumerate(num_times):
        st = label + str(i + 1)
        ax.axvline(num_time, color='tab:blue')
        ax.text(num_time, ax.get_ylim()[1], st, color='tab:blue')
        res[i] = num_time
    return res            


#%%
def plot_header(descr, param={'save':False}):
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
    # ['Age', 'Sex', 'Weight', 'Version', 'Date', 'Patient Name', 'Sampling Rate',
    # 'Height', 'Patient ID', 'Equipment', 'Procedure']
    fig = plt.figure(figsize=(nbcol*hcell + hpad, nbcol* wcell + wpad))
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    table = ax.table(cellText=txt, loc='center', fontsize=18, bbox=[0, 0, 1, 1])
    #table.auto_set_font_size(False)
    table.set_fontsize(10)
    #table.set_zorder(10)
    for sp in ax.spines.values():
        sp.set_color('w')
        sp.set_zorder(0)
    #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    #save process
    if param['save']:
        fig_name = 'header'+ str(param['item'])
        name = os.path.join(param['path'], fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
        # saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(param['path'], fig_name)
    return fig


def hist_cardio(data, param={}):
    """
    PaM histogramme using matplotlib 
    input : 
        data pandasDataFrame (keys used : 'ip1m' and 'hr), 
        param: dictionary (save=bolean, 'path': path to directory)
    output:
        pyplot figure
    """

    if 'ip1m' not in data.columns:
        print('no ip1 in the data')
        return
    if 'hr' not in data.columns:
        print('no hr in the data')
        return
    save = param.get('save', False)
#    fig = plt.figure(figsize=(15,8))
    fig = plt.figure(figsize=(8, 4))

    ax1 = fig.add_subplot(121)
    ax1.set_title('arterial pressure', color='tab:red') 
    ax1.set_xlabel('mmHg', alpha=0.5)
    ax1.axvspan(70, 80, -0.1, 1, color='tab:grey', alpha=0.5)
    ax1.hist(data.ip1m.dropna(), bins=50, color='tab:red',
             edgecolor='tab:red')
    ax1.axvline(70, color='tab:grey', alpha=1)
    ax1.axvline(80, color='tab:grey', alpha=1)
    ax2 = fig.add_subplot(122)
    ax2.hist(data.hr.dropna(), bins=50, range=(25, 65), color='tab:grey',
             edgecolor='tab:grey')
    ax2.set_title('heart rate', color='k')
    ax2.set_xlabel('bpm', alpha=0.5)
    axes = [ax1, ax2]
    quart = True
    if quart:
        for i, item in enumerate(['ip1m', 'hr']):
            try:
                q25, q50, q75 = np.percentile(data[item].dropna(), [25, 50, 75])
                axes[i].axvline(q50, linestyle='dashed', linewidth=2, color='k', alpha=0.8)
             #   axes[i].axvline(q25, linestyle='dashed', linewidth=1, color='k', alpha=0.5)
              #  axes[i].axvline(q75, linestyle='dashed', linewidth=1, color='k', alpha=0.5)
            except:
                print('no arterial pressure recorded')
    for ax in axes:
        #call
        color_axis(ax, 'bottom', 'tab:grey')
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for locs in ['top', 'right', 'left']:
            ax.spines[locs].set_visible(False)
        #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    if save:
        fig_name = 'hist_cardio'+ str(param['item'])
        name = os.path.join(param['path'], fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
        # saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(param['path'], fig_name)
    return fig

#---------------------------------------------------------------------------------------------------
def plot_one_over_time(x, y, colour):
    """
    plot y over x using colour
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, color=colour)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    #fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    return fig

#----------------------------------------------------------------------------------------
def hist_co2_iso(data, param={}):
    """CO2 and iso histogramme (NB CO2 should have been converted from % to mmHg)"""

    if 'co2exp' not in data.columns:
        print('no co2exp in the data')
        return
    save = param.get('save', False)
    # fig = plt.figure(figsize=(15,8))
    fig = plt.figure(figsize=(8, 4))

    ax1 = fig.add_subplot(121)
    ax1.set_title('$End_{tidal}$ $CO_2$', color='tab:blue')
    ax1.axvspan(35, 45, color='tab:grey', alpha=0.5)
    ax1.hist(data.co2exp.dropna(), bins=50, 
             color='tab:blue', edgecolor='tab:blue', alpha=.8)
    ax1.axvline(35, color='tab:grey', alpha=1)
    ax1.axvline(45, color='tab:grey', alpha=1)
    ax1.set_xlabel('mmHg', alpha=0.5)

    ax2 = fig.add_subplot(122)
    ax2.set_title('$End_{tidal}$ isoflurane', color='tab:purple')
    ax2.hist(data.aaExp.dropna(), bins=50, color='tab:purple', 
             range=(0.5, 2), edgecolor='tab:purple', alpha=.8)
    ax2.set_xlabel('%', alpha=0.5)
    
    axes = [ax1, ax2]
    quart=True
    if quart:
        for i, item in enumerate(['co2exp', 'aaExp']):
            try:
                q25, q50, q75 = np.percentile(data[item].dropna(), [25, 50, 75])
                axes[i].axvline(q50, linestyle='dashed', linewidth=2, color='k', alpha=0.8)
#                axes[i].axvline(q25, linestyle='dashed', linewidth=1, color='k', alpha=0.5)
 #               axes[i].axvline(q75, linestyle='dashed', linewidth=1, color='k', alpha=0.5)
            except:
                print(item, 'not used')

    for ax in axes:
        #call
        color_axis(ax, 'bottom', 'tab:grey')
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for locs in ['top', 'right', 'left']:
            ax.spines[locs].set_visible(False)
        #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    if save:
        fig_name = 'hist_co2_iso'+ str(param['item'])
        name = os.path.join(param['path'], fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(param['path'], fig_name)

    return fig


#---------------------------------------------------------------------------------------------------
def cardiovasc(data, param={}):
    """
    cardiovascular plot
    input = 
        data = pandas.DataFrame, keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
        param : dict(save: boolean, path['save'], xmin, xmax, unit,
                     dtime = boolean for time display in HH:MM format)
    output = 
        pyplot figure
    """
    if 'hr' not in data.columns:
        print('no pulseRate in the recording')
        return
    #global timeUnit
    dtime = param.get('dtime', False)
    save = param.get('save', False)
    if dtime : 
        df = data[['datetime', 'ip1m', 'ip1d', 'ip1s', 'hr']].set_index('datetime')
    else:
        df = data[['ip1m', 'ip1d', 'ip1s', 'hr']]
    xmin = param.get('xmin', None)
    xmax = param.get('xmax', None)
    unit = param.get('unit', '')
    
    fig = plt.figure()
    # fig.suptitle('cardiovascular')
    axL = fig.add_subplot(111)
    # axL.set_xlabel('time (' + unit +')')
    axL.set_ylabel('arterial Pressure', color='tab:red')
    #call
    color_axis(axL, 'left', 'tab:red')
    for spine in ['top', 'right']:
        axL.spines[spine].set_visible(False)
    axL.plot(df.ip1m, '-', color='red', label='arterial pressure', linewidth=2)
    axL.fill_between(df.index, df.ip1d, df.ip1s, color='tab:red', alpha=0.5)
    axL.set_ylim(30, 150)
    axL.axhline(70, linewidth=1, linestyle='dashed', color='tab:red')

    axR = axL.twinx()
    axR.set_ylabel('heart Rate')
    axR.set_ylim(20, 100)
    axR.plot(df.hr, color='tab:grey', label='heart rate', linewidth=2)
    #call
    color_axis(axR, 'right', 'tab:grey')
    axR.yaxis.label.set_color('black')
    for spine in ['top', 'left']:
        axR.spines[spine].set_visible(False)

    for ax in fig.get_axes():
        #call
        color_axis(ax, 'bottom', 'tab:grey')
        #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    if xmin and xmax:
        axR.set_xlim(xmin,xmax)

    if dtime:
        myFmt = mdates.DateFormatter('%H:%M')
        axR.xaxis.set_major_formatter(myFmt)

    if param['save']:
        path = param['path']
        fig_name = 'cardiovasc'+ str(param['item'])
        name = os.path.join(path, fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(path, fig_name)

    return fig

#---------------------------------------------------------------------------------------------------
def co2iso(data, param={}):
    """
    anesth plot (CO2/iso)
    input = 
        data = pandas.DataFrame, keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
        param : dict(save: boolean, path['save'], xmin, xmax, unit,
                     dtime = boolean for time display in HH:MM format)
    output = 
        pyplot figure
    """
    if 'co2exp' not in data.columns:
        print('no co2exp in the recording')
        return
    dtime = param.get('dtime', False)
    if dtime:
        df = data[['datetime', 'co2insp', 'co2exp',
                   'aaInsp', 'aaExp']].set_index('datetime')
    else:
        df = data[['co2insp', 'co2exp', 'aaInsp', 'aaExp']]
    # x = data.index
    # etCO2 = data.co2exp
    # inspCO2 = data.co2insp
    path = param.get('path','')
    xmin = param.get('xmin', None)
    xmax = param.get('xmax', None)
    unit = param.get('unit', '')
    save = param.get('save', False)
    #rr = data['CO2 RR‘]
    # inspO2 = data.o2insp
    # etO2 = data.o2exp
    # inspIso = data.aaInsp
    # etIso = data.aaExp

    fig = plt.figure()
    # fig.suptitle('$CO_2$ isoflurane')
    axL = fig.add_subplot(111)
#    axL.set_xlabel('time (' + unit +')')

    axL.set_ylabel('$CO_2$')
    # call
    color_axis(axL, 'left', 'tab:blue')

    axL.plot(df.co2exp, color='tab:blue')
    axL.plot(df.co2insp, color='tab:blue')
    axL.fill_between(df.index, df.co2exp, df.co2insp, 
                     color='tab:blue', alpha=0.5)
    axL.axhline(38, linewidth=2, linestyle='dashed', color='tab:blue')

    axR = axL.twinx()
    axR.set_ylabel('isoflurane')
    color_axis(axR, 'right', 'tab:purple')
    # func(axR, x, etIso, inspIs, color='m', x0=38)
    axR.plot(df.aaExp, color='tab:purple')
    axR.plot(df.aaInsp, color='tab:purple')
    axR.fill_between(df.index, df.aaExp, df.aaInsp, 
                     color='tab:purple', alpha=0.5)
    axR.set_ylim(0, 3)

    if dtime:
        myFmt = mdates.DateFormatter('%H:%M')
        axR.xaxis.set_major_formatter(myFmt)

    for ax in [axL, axR]:
        color_axis(ax, 'bottom', 'tab:grey')
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
        #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()

    if save:
        fig_name = 'co2iso'+ str(param['item'])
        name = os.path.join(path, fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(path, fig_name)

    return fig

# proposition de yann pour simplifier le code (à implémenter)
def func(ax, x, y1, y2, color='tab:blue', x0=38):
    ax.plot(x, y1, color=color)
    ax.plot(x, y2, color=color)
    ax.fill_between(x, y1, y2, color=color, alpha=0.1)
    ax.axhline(x0, linewidth=1, linestyle='dashed', color=color)

#---------------------------------------------------------------------------
def co2o2(data, param):
    """
    respiratory plot (CO2 and Iso)
    input = 
        data = pandas.DataFrame, keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
        param : dict(save: boolean, path['save'], xmin, xmax, unit,
                     dtime = boolean for time display in HH:MM format)
    output = 
        pyplot figure
    """
    try:
        etCO2 = data.co2exp
    except:
        print('no CO2 records in this recording')
        return
    try:
        data.o2exp
    except:
        print('no O2 records in this recording')
        return
    
    path = param.get('path', '')
    xmin = param.get('xmin', None)
    xmax = param.get('xmax', None)
    unit = param.get('unit', '')
    dtime = param.get('dtime', False)
    if dtime:
        df = data[['datetime', 'co2insp', 'co2exp', 
                  'o2insp', 'o2exp']].set_index('datetime')
    else:
        df = data[['co2insp', 'co2exp', 'o2insp', 'o2exp']]

    fig = plt.figure()
    # fig.suptitle('$CO_2$ & $O_2$ (insp & $End_{tidal}$)')
    axL = fig.add_subplot(111)
    axL.set_ylabel('$CO_2$')
    # axL.set_xlabel('time (' + unit +')')
    color_axis(axL, 'left', 'tab:blue')
    axL.plot(df.co2exp, color='tab:blue')
    axL.plot(df.co2insp, color='tab:blue')
    axL.fill_between(df.index, df.co2exp, df.co2insp, 
                     color='tab:blue', alpha=0.5)
    axL.axhline(38, linestyle='dashed', linewidth=2, color='tab:blue')

    axR = axL.twinx()
    axR.set_ylabel('$0_2$')
    color_axis(axR, 'right', 'tab:green')
    axR.plot(df.o2insp, color='tab:green')
    axR.plot(df.o2exp, color='tab:green')
    axR.fill_between(df.index, df.o2insp, df.o2exp, 
                     color='tab:green', alpha=0.5)
    axR.set_ylim(21, 80)
    axR.axhline(30, linestyle='dashed', linewidth=3, color='tab:olive')

    if dtime:
        myFmt = mdates.DateFormatter('%H:%M')
        axR.xaxis.set_major_formatter(myFmt)

    axes = [axL, axR]
    for ax in axes:
        color_axis(ax, 'bottom', 'tab:grey')
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
        #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()

    if param['save']:
        fig_name = 'co2o2'+ str(param['item'])
        name = os.path.join(path, fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(path, fig_name)
    return fig

#---------------------------------------------------------------------------------------
def ventil(data, param):
    """
    ventilation plot (.tvInsp, .pPeak, .pPlat, .peep, .minVexp, .co2RR, .co2exp )
    input = 
        data = pandas.DataFrame, keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
        param : dict(save: boolean, path['save'], xmin, xmax, unit,
                     dtime = boolean for time display in HH:MM format)
    output = 
        pyplot figure
    """
    path = param.get('path', '')
    xmin = param.get('xmin', None)
    xmax = param.get('xmax', None)
    unit = param.get('unit', '')
    dtime = param.get('dtime', False)
    if dtime:
        df = data.set_index('datetime')
    else:
        df = data
#    if 'tvInsp' not in data.columns:
#        print('no spirometry data in the recording')
#        return

    fig = plt.figure(figsize=(8.5, 5))
    # fig.suptitle('ventilation')

    ax1 = fig.add_subplot(211)
    ax1.set_ylabel('tidal volume')
    color_axis(ax1, 'left', 'tab:olive')
    ax1.yaxis.label.set_color('k')
    try:
        ax1.plot(df.tvInsp, color='tab:olive', linewidth=2)
    except:
        print('no spirometry data in the recording')
    ax1R = ax1.twinx()
    ax1R.set_ylabel('pression')
    color_axis(ax1R, 'right', 'tab:red')
    try:
        ax1R.plot(df.pPeak, color='tab:red', linewidth=1, linestyle='-')
        ax1R.plot(df.pPlat, color='tab:red', linewidth=1, linestyle=':')
        ax1R.plot(df.peep, color='tab:red', linewidth=1, linestyle='-')
        ax1R.fill_between(df.index, df.peep, df.pPeak, color='tab:red', alpha=0.1)
    except:
        print('no spirometry data in the recording')
    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel('MinVol & RR')
    try:
        ax2.plot(df.minVexp, color='tab:olive', linewidth=2)
        ax2.plot(df.co2RR, color='black', linewidth=1, linestyle='--')
    except:
        print('no spirometry data recorded')
    # ax2.set_xlabel('time (' + unit +')')

    ax2R = ax2.twinx()
    ax2R.set_ylabel('Et $CO_2$')
    color_axis(ax2R, 'right', 'tab:blue')
    try:
        ax2R.plot(df.co2exp, color='tab:blue', linewidth=2, linestyle='-')
    except:
        print('no capnometry in the recording')
    ax1R.set_ylim(0, 50)
    ax1.set_ylim(500, 2000)

    axes = [ax1, ax1R, ax2, ax2R]
    for ax in axes:
        if dtime:
            myFmt = mdates.DateFormatter('%H:%M')
            ax.xaxis.set_major_formatter(myFmt)
        color_axis(ax, 'bottom', 'tab:grey')
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
        #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    if param['save']:
        fig_name = 'ventil'+ str(param['item'])
        name = os.path.join(path, fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(path, fig_name)
    return fig

#------------------------------------------------------------------------
def recrut(data, param):
    """
    to show a recrut manoeuver (.pPeak, .pPlat, .peep, .tvInsp)
    input = 
        data = pandas.DataFrame, keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
        param : dict(save: boolean, path['save'], xmin, xmax, unit,
                     dtime = boolean for time display in HH:MM format)
    output = 
        pyplot figure
    """
    
    path = param.get('path', '')
    xmin = param.get('xmin', None)
    xmax = param.get('xmax', None)
    unit = param.get('unit', '')
    dtime = param.get('dtime', False)
    if dtime:
        df = data.set_index('datetime').copy()
    else:
        df = data.copy()

    fig = plt.figure()
    # fig.suptitle('recrutement')

    ax1 = fig.add_subplot(111)
    # ax1.set_xlabel('time (' + unit +')')
    ax1.spines["top"].set_visible(False)
    ax1.set_ylabel('peep & Peak')
    color_axis(ax1, 'left', 'tab:red')
    ax1.spines["right"].set_visible(False)
    ax1.plot(df.pPeak, color='tab:red', linewidth=2, linestyle='-')
    ax1.plot(df.pPlat, color='tab:red', linewidth=1, linestyle=':')
    ax1.plot(df.peep, color='tab:red', linewidth=2, linestyle='-')
    ax1.fill_between(df.index, df.peep, df.pPeak, color='tab:red', alpha=0.1)
    ax1.set_ylim(0, 50)

    ax2 = ax1.twinx()
    ax2.set_ylabel('volume')
    color_axis(ax2, 'right', 'tab:olive')
    ax2.spines["left"].set_visible(False)
    ax2.yaxis.label.set_color('black')
    ax2.plot(df.tvInsp, color='tab:olive', linewidth=2)

    ax1.set_xlim(xmin, xmax)
    #ax2.set_xlim(xmin, xmax)

    if dtime:
        myFmt = mdates.DateFormatter('%H:%M')
        ax1.xaxis.set_major_formatter(myFmt)

    axes = [ax1, ax2]
    for ax in axes:
        color_axis(ax, 'bottom', 'tab:grey')
        ax.spines["top"].set_visible(False)
    #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    if param['save']:
        fig_name = 'recrut'+ str(param['item'])
        name = os.path.join(path, fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
#        saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(path, fig_name)
    return fig


def ventil_cardio(data, param):
    """
        input = 
        data = pandas.DataFrame, keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
        param : dict(save: boolean, path['save'], xmin, xmax, unit,
                     dtime = boolean for time display in HH:MM format)
    output = 
        pyplot figure
    """
    path = param.get('path', '')
    xmin = param.get('xmin', None)
    xmax = param.get('xmax', None)
    unit = param.get('unit', '')
    dtime = param.get('dtime', False)
    if dtime:
        df = data.set_index('datetime').copy()
    else:
        df = data.copy()

    if 'tvInsp' not in data.columns:
        print('no spirometry data in the recording')

    fig = plt.figure(figsize=(6,12))
    # fig.suptitle('ventilation & cardiovasc')

    ax1 = fig.add_subplot(211)
    ax1.set_ylabel('tidal vol.')
    color_axis(ax1, 'left', 'tab:olive')
    ax1.yaxis.label.set_color('k')
    ax1.plot(df.tvInsp, color='tab:olive', linewidth=2)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.tick_params('x')    
    
    ax1R = ax1.twinx()
    ax1R.set_ylabel('P_resp')
    color_axis(ax1R, 'right', 'tab:red')
    ax1R.plot(df.pPeak, color='tab:red', linewidth=1, linestyle='-')
    ax1R.plot(df.pPlat, color='tab:red', linewidth=1, linestyle=':')
    ax1R.plot(df.peep, color='tab:red', linewidth=1, linestyle='-')
    ax1R.fill_between(df.index, df.peep, df.pPeak, color='tab:red', alpha=0.1)
    ax1R.spines['left'].set_visible(False)
    ax1R.spines['bottom'].set_visible(False)

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel('P_art')
    color_axis(ax2, 'left', 'tab:red')
    ax2.spines['right'].set_visible(False)    
    ax2.plot(df.ip1m, color='tab:red', linewidth=1, linestyle='-')
    ax2.plot(df.ip1s, color='tab:red', linewidth=0, linestyle='-')
    ax2.plot(df.ip1d, color='tab:red', linewidth=0, linestyle='-')
    ax2.fill_between(df.index, df.ip1s, df.ip1d, color='tab:red', alpha=0.2)
    
    # ax2.set_xlabel('time (' + unit +')')

    # ax1.set_xlim(108, 114)
    # ax2.set_ylim(35, 95)
    # ax1R.set_ylim(5, 45)
    # ax2.set_ylim(40, 95)
    # ax2.set_ylim(40, 90)
    # ax2.set_ylim(35, 95)

    if dtime:
        myFmt = mdates.DateFormatter('%H:%M')
        ax1.xaxis.set_major_formatter(myFmt)

    axes = [ax1, ax1R, ax2]
    for ax in axes:
        ax.grid()
        color_axis(ax, 'bottom', 'tab:grey')
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()

    #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    return fig


#------------------------------------------------------------------------
def save_distri(data, path):
    """save as '0_..' the 4 distributions graphs for cardiovasc annd respi"""
    bpgas(data).savefig((path['sFig'] + '0_bpgas.png'), bbox_inches='tight')
    hist_co2_iso(data).savefig((path['sFig']+ '0_hist_co2_iso.png'), bbox_inches='tight')
    bppa(data).savefig((path['sFig'] + '0_bppa.png'), bbox_inches='tight')
    hist_cardio(data).savefig((path['sFig']+ '0_hist_cardio.png'), bbox_inches='tight')

def fig_memo(path, fig_name):
    """
    append latex citation commands in a txt file inside the fig folder
    create the file iif it doesn't exist
    """
    includeText = "\\begin{frame}{fileName}\n\t\\includegraphics[width = \\textwidth]{bg/" + fig_name + "} \n\end{frame} \n %----------------- \n \\n"

    figInsert = os.path.join(path, 'figIncl.txt')
    with open(figInsert, 'a') as file:
        file.write(includeText +'\n')
        file.close()
