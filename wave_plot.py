# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 09:08:56 2016

@author: cdesbois
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
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
#%%
def plot_wave(df, keys=[], mini=None, maxi=None):
    """
    plot the waves recorded (from as5)
    input:  df= dataFrame
            keys= list of one or two of
                'wekg','ECG','wco2','wawp','wflow','wap'
            mini, maxi : limits in point value
    output: plt.figure
    (Nb plot data/index, but the xscale is indicated as sec)
    """
    names = {'wekg': ['ECG', 'b', 'mVolt'],
             'wco2' : ['expired CO2', 'b', 'mmHg'],
             'wawp': ['airway pressure', 'r', 'cmH2O'],
             'wflow': ['expiratory flow', 'g', 'flow'],
             'wap': ['arterial pressure', 'r', 'mmHg']}
    if not mini:
        mini = df.index[0]
    if not maxi:
        maxi = df.index[-1]
    if not df.index[0] <= mini <= df.index[-1]:
        print('mini value not in range, replaced by start time value')
        mini = df.index[0]
    if not df.index[0] <= maxi <= df.index[-1]:
        print('maxi value not in range, replaced by end time value')
        maxi = df.index[-1]
    for key in keys:
        if key not in names.keys():
            print(key, 'is not in ', names.keys())
            return
    if len(keys) not in [1, 2]:
        print('only one or two keys are allowed ', keys, 'were used')

    lines = []
    # one wave
    if len(keys) == 1:
        for key in keys:
            fig = plt.figure(figsize=(10, 4))
            fig.suptitle(names[key][0])
            ax = fig.add_subplot(111)
            ax.margins(0)
            line, = ax.plot(df[key], color=names[key][1], alpha=0.6)
            lines.append(line)
#            ax.set_xlim(set.sec.min(), set.sec.max())
#            ax.set_xlim(df.sec.min(), df.sec.max()) # thats sec values, not pt values
#            ax.set_xlim(set.index.min(), set.index.max())
            lims = ax.get_xlim()
            ax.hlines(0, lims[0], lims[1], alpha=0.3)
            ax.set_ylabel(names[key][2])
            if key == 'wco2':
                ax.hlines(38, lims[0], lims[1], linestyle='dashed', alpha=0.5)
                ax.set_ylim(0, 50)
            if key == 'wekg':
                ax.grid()
            if key == 'wap':
                ax.hlines(70, lims[0], lims[1], linestyle='dashed', alpha=0.5)
            if key == 'wflow':
#                ax.fill_between(set.index, set[key], where = set[key] > 0,
#                                color = names[key][1], alpha=0.4)
                pass
        for loca in ['top', 'right']:
            ax.spines[loca].set_visible(False)
#        ax.set_xlim(0, win)
        ax.get_xaxis().tick_bottom()
        ax.set_xticklabels(np.linspace(df.sec.loc[mini], df.sec.loc[maxi],
                                       len(ax.get_xticklabels())).astype(int).astype(str).tolist())
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
            ax.set_title(names[key][0])
            line, = ax.plot(df[key], color=names[key][1], alpha=0.6)
            lines.append(line)
            lims = ax.get_xlim()
            ax.hlines(0, lims[0], lims[1], alpha=0.3)
            ax.set_ylabel(names[key][2])
            if key == 'wco2':
                ax.hlines(38, lims[0], lims[1], linestyle='dashed',
                          color=names[key][1], alpha=0.5)
                ax.set_ylim(0, 50)
            if key == 'wekg':
                ax.grid()
            if key == 'wflow':
#                ax.fill_between(set.index, set[key], where = set[key] > 0,
#                                color = names[key][1], alpha=0.4)
                pass
            if key == 'wap':
                ax.hlines(70, lims[0], lims[1], color=names[key][1],
                          linestyle='dashed', alpha=0.5)
                ax.set_ylim(50, 110)
            ax.get_xaxis().tick_bottom()
            if i > 0:
#                ax.set_xlim(0, win)
                ax.get_xaxis().tick_bottom()
                ax.set_xticklabels(np.linspace(df.sec.loc[mini], df.sec.loc[maxi],
                                               len(ax.get_xticklabels())).astype(int).astype(str).tolist())
                ax.set_xlabel('time (sec)')
        for ax in ax_list:
            for loca in ['top', 'right']:
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig, lines

#%%