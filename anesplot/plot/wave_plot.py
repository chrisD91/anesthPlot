# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 09:08:56 2016

@author: cdesbois
"""
import matplotlib.dates as mdates
#import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt

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

# bright = {
#         'blue' : [x/256 for x in [0, 119, 170]],
#         'cyan' : [x/256 for x in [102, 204, 238]],
#         'green' : [x/256 for x in [34, 136, 51]],
#         'yellow' : [x/256 for x in [204, 187, 68]],
#         'red' : [x/256 for x in [238, 103, 119]],
#         'purple' : [x/256 for x in [170, 51, 119]],
#         'grey' : [x/256 for x in [187, 187, 187]]
#         }

# colors = bright

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
#def plot_wave(df, keys=[], mini=None, maxi=None, datetime=False):
def plot_wave(data, keys=[], param={}):
    """
    plot the waves recorded (from as5)
    input:  df= dataFrame
            keys= list of one or two of
                'wekg','ECG','wco2','wawp','wflow','wap'
            mini, maxi : limits in point value (index)
    output: plt.figure, line2D
    (Nb plot data/index, but the xscale is indicated as sec)
    """
    for key in keys:
        try:
            key in data.columns
        except:
            print('the trace {} is not in the data'.format(key))
            return
    if len(keys) not in [1, 2]:
        print('only one or two keys are allowed ', keys, 'were used')
        return
    names = dict(
        wekg = ['ECG', 'tab:blue', 'mVolt'],
        wco2 = ['expired CO2', 'tab:blue', 'mmHg'],
        wawp = ['airway pressure', 'tab:red', 'cmH2O'],
        wflow = ['expiratory flow', 'tab:green', 'flow'],
        wap = ['arterial pressure', 'tab:red', 'mmHg'],
        wvp = ['venous pressure', 'tab:blue', 'mmHg']
        )
    # time scaling (index value)
    mini = param.get('mini', data.index[0])
    maxi = param.get('maxi', data.index[-1])
    if not data.index[0] <= mini <= data.index[-1]:
        print('mini value not in range, replaced by start time value')
        mini = data.index[0]
    if not data.index[0] <= maxi <= data.index[-1]:
        print('maxi value not in range, replaced by end time value')
        maxi = data.index[-1]
    # datetime or elapsed time sec
    dtime = param.get('dtime', False)
    if dtime:
        cols = keys[:]
        cols.append('datetime')
        df = data[cols].copy()        
        df = df.iloc[mini : maxi].set_index('datetime')
    else:
        cols = keys.copy()
        cols.append('sec')
        df = data[cols].copy()
        df = df.iloc[mini : maxi].set_index('sec')    
    lines = []
    # one wave
    if len(keys) == 1:
        for key in keys:
            fig = plt.figure(figsize=(10, 4))
            fig.suptitle(names[key][0], color='tab:grey')
            ax = fig.add_subplot(111)
            ax.margins(0)
            line, = ax.plot(df[key], color=names[key][1], alpha=0.6)
            lines.append(line)
            ax.axhline(0, alpha=0.3)
            ax.set_ylabel(names[key][2])
            if dtime:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            if key == 'wco2':
                ax.axhlines(38, linestyle='dashed', alpha=0.5)
                ax.set_ylim(0, 50)
            if key == 'wekg':
                ax.grid()
            if key == 'wap':
                ax.axhline(70, linestyle='dashed', alpha=0.5)
            if key == 'wflow':
#                ax.fill_between(set.index, set[key], where = set[key] > 0,
#                                color = names[key][1], alpha=0.4)
                pass
        for spine in ['left', 'bottom']:
            color_axis(ax, spine=spine, color='tab:grey')
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        if not dtime:
            ax.set_xlabel('time (sec)')
    #two waves
    elif len(keys) == 2:
        fig = plt.figure(figsize=(10, 4))
        ax_list = []
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.margins(0)
        ax_list.append(ax1)
        ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
        ax2.margins(0)
        ax_list.append(ax2)
        for i, key in enumerate(keys):
            ax = ax_list[i]
            # ax.set_title(names[key][0])
            ax.set_ylabel(names[key][0], size='small')
            line, = ax.plot(df[key], color=names[key][1], alpha=0.6)
            lines.append(line)
            lims = ax.get_xlim()
            ax.hlines(0, lims[0], lims[1], alpha=0.3)
            #ax.set_ylabel(names[key][2])
            if key == 'wco2':
                ax.hlines(38, lims[0], lims[1], linestyle='dashed',
                          color=names[key][1], alpha=0.5)
                ax.set_ylim(0, 50)
            if key == 'wekg':
                ax.grid()
                ax.set_ylim(1.05 * df['wekg'].quantile(.001),  
                            1.05 * df['wekg'].quantile(.999))
            if key == 'wflow':
#                ax.fill_between(set.index, set[key], where = set[key] > 0,
#                                color = names[key][1], alpha=0.4)
                pass
            if key == 'wap':
                ax.hlines(70, lims[0], lims[1], color=names[key][1],
                          linestyle='dashed', alpha=0.5)
                ax.set_ylim(40, 1.10 * df['wap'].quantile(.99))
            ax.get_xaxis().tick_bottom()
            if i > 0:
                if not dtime:
                    ax.set_xlabel('time (sec)')
        for ax in ax_list:
            if dtime:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            for spine in ['left', 'right', 'bottom']:
                color_axis(ax, spine=spine, color='tab:grey')
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
    #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    return fig, lines

#%%