# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import anesplot.record_main as rec

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




filename = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded/M2021_3_8-9_9_48.csv'
trends = rec.MonitorTrend(filename)

df = trends.data
#%%

plt.close('all')

def extract_hypotension(trends, pamin=70):
    df = trends.data.copy()
    df = pd.DataFrame(df.set_index(df.eTime.astype(int))['ip1m'])
    df['low'] = df.ip1m < pamin
    df['trans'] = df.low - df.low.shift(-1)

    # extract changes
    durdf = pd.DataFrame()
    durdf['to_down'] = df.loc[df.trans == -1].index.to_list()
    durdf['to_up'] = df.loc[df.trans == 1].index.to_list()
    durdf.to_up = durdf.to_up.shift(-1)
    durdf['time_hypo'] = durdf.to_up - durdf.to_down
    durdf = durdf.dropna()

    return durdf


def plot_hypotension(trends, durdf, durmin=15):
    df = trends.data.copy()
    df = pd.DataFrame(df.set_index(df.eTime.astype(int))['ip1m'])
    param = trends.param
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(df.ip1m, '-', color='tab:red', alpha=0.8)
    ax.axhline(y=70, color='tab:grey', alpha=0.5)
    for a,b,t  in durdf.loc[durdf.time_hypo > 60].values:
        ax.vlines(a, ymin=50, ymax=70, color='tab:blue', alpha = 0.5)
        ax.vlines(b, ymin=50, ymax=70, color='tab:blue', alpha = 0.5)
        if t > 15 * 60:
            ax.axvspan(xmin=a, ymin=b, color='tab:red', alpha=0.5)
            
    nb = len(durdf[durdf.time_hypo > (durmin * 60)])
    txt = 'higher than {} minutes hypotension periods = {}'.format(durmin, nb)
    ax.text(0.5, 0.1, txt, ha='center', va='bottom', transform=ax.transAxes,
            color='tab:grey')
    
    #annotations
    fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4, size=12)
    fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)

    return fig



dur_df = extract_hypotension(trends, pamin=70)

fig = plot_hypotension(trends, dur_df)
    