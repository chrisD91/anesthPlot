# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 09:08:56 2016

functions to plot the trend data

@author: cdesbois

"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#import utils
font_size = 'medium' # large, medium
params = {'font.sans-serif': ['Arial'],
          'font.size': 14,
          'legend.fontsize': font_size,
          'figure.figsize': (8.5, 3),
          'axes.labelsize': font_size,
          'axes.titlesize': font_size,
          'xtick.labelsize': font_size,
          'ytick.labelsize': font_size,
          'axes.xmargin': 0}
plt.rcParams.update(params)
plt.rcParams['axes.xmargin'] = 0            # no gap between axes and traces

bright = {
        'blue' : [x/256 for x in [0, 119, 170]],
        'cyan' : [x/256 for x in [102, 204, 238]],
        'green' : [x/256 for x in [34, 136, 51]],
        'yellow' : [x/256 for x in [204, 187, 68]],
        'red' : [x/256 for x in [238, 103, 119]],
        'purple' : [x/256 for x in [170, 51, 119]],
        'grey' : [x/256 for x in [187, 187, 187]]
        }

colors = bright

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
    if param['save']:
        fig_name = 'header'+ str(param['item'])
        name = os.path.join(param['path'], fig_name)
        utils.saveGraph(name, ext='png', close=False, verbose=True)
        # saveGraph(name, ext='png', close=False, verbose=True)
        if param['memo']:
            fig_memo(param['path'], fig_name)
    return fig


def hist_pam(data, param={}):
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
    ax1.set_title('arterial pressure', color=colors['red']) 
    ax1.set_xlabel('mmHg', alpha=0.5)
    ax1.axvspan(70, 80, -0.1, 1, color=colors['grey'], alpha=0.5)
    ax1.hist(data.ip1m.dropna(), bins=50, color=colors['red'],
             edgecolor='r')
    ax1.axvline(70, color=colors['grey'], alpha=1)
    ax1.axvline(80, color=colors['grey'], alpha=1)
    ax2 = fig.add_subplot(122)
    ax2.hist(data.hr.dropna(), bins=50, range=(25, 65), color=colors['grey'],
             edgecolor='k')
    ax2.set_title('heart rate', color='k')
    ax2.set_xlabel('bpm', alpha=0.5)
    axes = [ax1, ax2]
    quart = True
    if quart:
        for i, item in enumerate(['ip1m', 'hr']):
            try:
                q25, q50, q75 = np.percentile(data[item].dropna(), [25, 50, 75])
                axes[i].axvline(q50, linestyle='dashed', linewidth=2, color='k', alpha=0.5)
             #   axes[i].axvline(q25, linestyle='dashed', linewidth=1, color='k', alpha=0.5)
              #  axes[i].axvline(q75, linestyle='dashed', linewidth=1, color='k', alpha=0.5)
            except:
                print('no arterial pressure recorded')
    for ax in axes:
        #call
        color_axis(ax, 'bottom', colors['grey'])
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for locs in ['top', 'right', 'left']:
            ax.spines[locs].set_visible(False)
    fig.tight_layout()
    if save:
        fig_name = 'hist_pam'+ str(param['item'])
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
    ax1.set_title('$End_{tidal}$ $CO_2$', color=colors['blue'])
    ax1.axvspan(35, 45, color=colors['grey'], alpha=0.5)
    ax1.hist(data.co2exp.dropna(), bins=50, 
             color=colors['blue'], edgecolor='blue', alpha=.8)
    ax1.axvline(35, color=colors['grey'], alpha=1)
    ax1.axvline(45, color=colors['grey'], alpha=1)
    ax1.set_xlabel('mmHg', alpha=0.5)

    ax2 = fig.add_subplot(122)
    ax2.set_title('$End_{tidal}$ isoflurane', color=colors['purple'])
    ax2.hist(data.aaExp.dropna(), bins=50, color=colors['purple'], 
             range=(0.5, 2), edgecolor='k', alpha=.8)
    ax2.set_xlabel('%', alpha=0.5)
    
    axes = [ax1, ax2]
    quart=True
    if quart:
        for i, item in enumerate(['co2exp', 'aaExp']):
            try:
                q25, q50, q75 = np.percentile(data[item].dropna(), [25, 50, 75])
                axes[i].axvline(q50, linestyle='dashed', linewidth=2, color='k', alpha=0.5)
#                axes[i].axvline(q25, linestyle='dashed', linewidth=1, color='k', alpha=0.5)
 #               axes[i].axvline(q75, linestyle='dashed', linewidth=1, color='k', alpha=0.5)
            except:
                print(item, 'not used')

    for ax in axes:
        #call
        color_axis(ax, 'bottom', colors['grey'])
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for locs in ['top', 'right', 'left']:
            ax.spines[locs].set_visible(False)
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
    axL.set_ylabel('arterial Pressure', color='red')
    #call
    color_axis(axL, 'left', colors['red'])
    for spine in ['top', 'right']:
        axL.spines[spine].set_visible(False)
    axL.plot(df.ip1m, '-', color='red', label='arterial pressure', linewidth=2)
    axL.fill_between(df.index, df.ip1d, df.ip1s, color = colors['red'], alpha=0.5)
    axL.set_ylim(30, 150)
    axL.axhline(70, linewidth=1, linestyle='dashed', color=colors['red'])

    axR = axL.twinx()
    axR.set_ylabel('heart Rate')
    axR.set_ylim(20, 100)
    axR.plot(df.hr, color = colors['grey'], label='heart rate', linewidth=2)
    #call
    color_axis(axR, 'right', colors['grey'])
    axR.yaxis.label.set_color('black')
    for spine in ['top', 'left']:
        axR.spines[spine].set_visible(False)

    for ax in fig.get_axes():
        #call
        color_axis(ax, 'bottom', colors['grey'])
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
    color_axis(axL, 'left', colors['blue'])

    axL.plot(df.co2exp, color=colors['blue'])
    axL.plot(df.co2insp, color=colors['blue'])
    axL.fill_between(df.index, df.co2exp, df.co2insp, 
                     color=colors['blue'], alpha=0.5)
    axL.axhline(38, linewidth=2, linestyle='dashed', color=colors['blue'])

    axR = axL.twinx()
    axR.set_ylabel('isoflurane')
    color_axis(axR, 'right', colors['purple'])
    # func(axR, x, etIso, inspIs, color='m', x0=38)
    axR.plot(df.aaExp, color=colors['purple'])
    axR.plot(df.aaInsp, color=colors['purple'])
    axR.fill_between(df.index, df.aaExp, df.aaInsp, 
                     color=colors['purple'], alpha=0.5)
    axR.set_ylim(0, 3)

    if dtime:
        myFmt = mdates.DateFormatter('%H:%M')
        axR.xaxis.set_major_formatter(myFmt)

    for ax in [axL, axR]:
        color_axis(ax, 'bottom', colors['grey'])
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
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
def func(ax, x, y1, y2, color=colors['blue'], x0=38):
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
    color_axis(axL, 'left', colors['blue'])
    axL.plot(df.co2exp, color=colors['blue'])
    axL.plot(df.co2insp, color=colors['blue'])
    axL.fill_between(df.index, df.co2exp, df.co2insp, 
                     color=colors['blue'], alpha=0.5)
    axL.axhline(38, linestyle='dashed', linewidth=2, color=colors['blue'])

    axR = axL.twinx()
    axR.set_ylabel('$0_2$')
    color_axis(axR, 'right', colors['green'])
    axR.plot(df.o2insp, color=colors['green'])
    axR.plot(df.o2exp, color=colors['green'])
    axR.fill_between(df.index, df.o2insp, df.o2exp, 
                     color=colors['green'], alpha=0.5)
    axR.set_ylim(21, 80)
    axR.axhline(30, linestyle='dashed', linewidth=3, color=colors['yellow'])

    if dtime:
        myFmt = mdates.DateFormatter('%H:%M')
        axR.xaxis.set_major_formatter(myFmt)

    axes = [axL, axR]
    for ax in axes:
        color_axis(ax, 'bottom', colors['grey'])
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
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
    color_axis(ax1, 'left', colors['yellow'])
    ax1.yaxis.label.set_color('k')
    try:
        ax1.plot(df.tvInsp, color=colors['yellow'], linewidth=2)
    except:
        print('no spirometry data in the recording')
    ax1R = ax1.twinx()
    ax1R.set_ylabel('pression')
    color_axis(ax1R, 'right', colors['red'])
    try:
        ax1R.plot(df.pPeak, color=colors['red'], linewidth=1, linestyle='-')
        ax1R.plot(df.pPlat, color=colors['red'], linewidth=1, linestyle=':')
        ax1R.plot(df.peep, color=colors['red'], linewidth=1, linestyle='-')
        ax1R.fill_between(df.index, df.peep, df.pPeak, color=colors['red'], alpha=0.1)
    except:
        print('no spirometry data in the recording')
    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel('MinVol & RR')
    try:
        ax2.plot(df.minVexp, color=colors['yellow'], linewidth=2)
        ax2.plot(df.co2RR, color='black', linewidth=1, linestyle='--')
    except:
        print('no spirometry data recorded')
    # ax2.set_xlabel('time (' + unit +')')

    ax2R = ax2.twinx()
    ax2R.set_ylabel('Et $CO_2$')
    color_axis(ax2R, 'right', colors['blue'])
    try:
        ax2R.plot(df.co2exp, color=colors['blue'], linewidth=1, linestyle='-')
    except:
        print('no capnometry in the recording')
    ax1R.set_ylim(0, 50)
    ax1.set_ylim(500, 2000)

    axes = [ax1, ax1R, ax2, ax2R]
    for ax in axes:
        if dtime:
            myFmt = mdates.DateFormatter('%H:%M')
            ax.xaxis.set_major_formatter(myFmt)
        color_axis(ax, 'bottom', colors['grey'])
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
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
    ax1.set_ylabel('peep & Peak, (cmH2O)')
    color_axis(ax1, 'left', colors['red'])
    ax1.spines["right"].set_visible(False)
    ax1.plot(df.pPeak, color=colors['red'], linewidth=1, linestyle='-')
    ax1.plot(df.pPlat, color=colors['red'], linewidth=1, linestyle=':')
    ax1.plot(df.peep, color=colors['red'], linewidth=2, linestyle='-')
    ax1.fill_between(df.index, df.peep, df.pPeak, color=colors['red'], alpha=0.1)
    ax1.set_ylim(0, 50)

    ax2 = ax1.twinx()
    ax2.set_ylabel('volume')
    color_axis(ax2, 'right', colors['yellow'])
    ax2.spines["left"].set_visible(False)
    ax2.yaxis.label.set_color('black')
    ax2.plot(df.tvInsp, color=colors['yellow'], linewidth=2)

    ax1.set_xlim(xmin, xmax)
    #ax2.set_xlim(xmin, xmax)

    if dtime:
        myFmt = mdates.DateFormatter('%H:%M')
        ax1.xaxis.set_major_formatter(myFmt)

    axes = [ax1, ax2]
    for ax in axes:
        color_axis(ax, 'bottom', colors['grey'])
        ax.spines["top"].set_visible(False)

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

    fig = plt.figure()
    # fig.suptitle('ventilation & cardiovasc')

    ax1 = fig.add_subplot(211)
    ax1.set_ylabel('tidal vol.')
    color_axis(ax1, 'left', colors['yellow'])
    ax1.yaxis.label.set_color('k')
    ax1.plot(df.tvInsp, color=colors['yellow'], linewidth=2)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.tick_params('x')    
    
    ax1R = ax1.twinx()
    ax1R.set_ylabel('P_resp')
    color_axis(ax1R, 'right', colors['red'])
    ax1R.plot(df.pPeak, color=colors['red'], linewidth=1, linestyle='-')
    ax1R.plot(df.pPlat, color=colors['red'], linewidth=1, linestyle=':')
    ax1R.plot(df.peep, color=colors['red'], linewidth=1, linestyle='-')
    ax1R.fill_between(df.index, df.peep, df.pPeak, color=colors['red'], alpha=0.1)
    ax1R.spines['left'].set_visible(False)
    ax1R.spines['bottom'].set_visible(False)

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel('P_art')
    color_axis(ax2, 'left', colors['red'])
    ax2.spines['right'].set_visible(False)    
    ax2.plot(df.ip1m, color=colors['red'], linewidth=1, linestyle='-')
    ax2.plot(df.ip1s, color=colors['red'], linewidth=0, linestyle='-')
    ax2.plot(df.ip1d, color=colors['red'], linewidth=0, linestyle='-')
    ax2.fill_between(df.index, df.ip1s, df.ip1d, color=colors['red'], alpha=0.2)
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
        color_axis(ax, 'bottom', colors['grey'])
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()

    fig.tight_layout()
    return fig

#------------------------------------------------------------------------
def save_distri(data, path):
    """save as '0_..' the 4 distributions graphs for cardiovasc annd respi"""
    bpgas(data).savefig((path['sFig'] + '0_bpgas.png'), bbox_inches='tight')
    hist_co2_iso(data).savefig((path['sFig']+ '0_hist_co2_iso.png'), bbox_inches='tight')
    bppa(data).savefig((path['sFig'] + '0_bppa.png'), bbox_inches='tight')
    hist_pam(data).savefig((path['sFig']+ '0_hist_pam.png'), bbox_inches='tight')

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
