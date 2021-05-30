# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 12:46:41 2017

@author: cdesbois
"""
# import pandas as pd
import matplotlib.pyplot as plt

# import os
import numpy as np
from scipy.signal import medfilt


# //////////////////////////////////////////////// cardio
def fix_baseline_wander(data, fs=500):
    """BaselineWanderRemovalMedian.m from ecg-kit.  Given a list of amplitude values
    (data) and sample rate (sr), it applies two median filters to data to
    compute the baseline.  The returned result is the original data minus this
    computed baseline.
    """
    # source : https://pypi.python.org/pypi/BaselineWanderRemoval/2017.10.25
    print("source = Python port of BaselineWanderRemovalMedian.m from ECG-kit")
    print("Alex Page, alex.page@rochester.edu")
    print("https://bitbucket.org/atpage/baselinewanderremoval/src/master/")

    data = np.array(data)
    winsize = int(round(0.2 * fs))
    # delayBLR = round((winsize-1)/2)
    if winsize % 2 == 0:
        winsize += 1
    baseline_estimate = medfilt(data, kernel_size=winsize)
    winsize = int(round(0.6 * fs))
    # delayBLR = delayBLR + round((winsize-1)/2)
    if winsize % 2 == 0:
        winsize += 1
    baseline_estimate = medfilt(baseline_estimate, kernel_size=winsize)
    ecg_blr = data - baseline_estimate
    return ecg_blr.tolist()


def rol_mean(ser, win_lengh=1, fs=500):
    """
    return a rolling mean of a RR serie
    input:  ser= pd.Serie, win_lengh= window lenght for averaging (in sec),
            fs= sampling frequency

    """
    # moving average
    mov_avg = ser.rolling(window=int(win_lengh * fs), center=False).mean()
    # replace the initial values by the mean
    avg_hr = np.mean(ser)
    mov_avg = [avg_hr if np.isnan(x) else x for x in mov_avg]
    return mov_avg


# =============================================================================
# moved to wave_plot
# def plot_wave(df, keys=[], mini=None, maxi=None):
#     """
#     plot the waves recorded (from as5)
#     input:  df= dataFrame
#             keys= list of one or two of
#                 'wekg','ECG','wco2','wawp','wflow','wap'
#             mini, maxi : limits in point value
#     output: plt.figure
#     (Nb plot data/index, but the xscale is indicated as sec)
#     """
#     names = {'wekg': ['ECG', 'b', 'mVolt'],
#              'wco2' : ['expired CO2', 'b', 'mmHg'],
#              'wawp': ['airway pressure', 'r', 'cmH2O'],
#              'wflow': ['expiratory flow', 'g', 'flow'],
#              'wap': ['arterial pressure', 'r', 'mmHg']}
#     if not mini:
#         mini = df.index[0]
#     if not maxi:
#         maxi = df.index[-1]
#     if not df.index[0] <= mini <= df.index[-1]:
#         print('mini value not in range, replaced by start time value')
#         mini = df.index[0]
#     if not df.index[0] <= maxi <= df.index[-1]:
#         print('maxi value not in range, replaced by end time value')
#         maxi = df.index[-1]
#     for key in keys:
#         if key not in names.keys():
#             print(key, 'is not in ', names.keys())
#             return
#     if len(keys) not in [1, 2]:
#         print('only one or two keys are allowed ', keys, 'were used')
#
#     lines = []
#     # one wave
#     if len(keys) == 1:
#         for key in keys:
#             fig = plt.figure(figsize=(10, 4))
#             fig.suptitle(names[key][0])
#             ax = fig.add_subplot(111)
#             ax.margins(0)
#             line, = ax.plot(df[key], color=names[key][1], alpha=0.6)
#             lines.append(line)
# #            ax.set_xlim(set.sec.min(), set.sec.max())
# #            ax.set_xlim(df.sec.min(), df.sec.max()) # thats sec values, not pt values
# #            ax.set_xlim(set.index.min(), set.index.max())
#             lims = ax.get_xlim()
#             ax.hlines(0, lims[0], lims[1], alpha=0.3)
#             ax.set_ylabel(names[key][2])
#             if key == 'wco2':
#                 ax.hlines(38, lims[0], lims[1], linestyle='dashed', alpha=0.5)
#                 ax.set_ylim(0, 50)
#             if key == 'wekg':
#                 ax.grid()
#             if key == 'wap':
#                 ax.hlines(70, lims[0], lims[1], linestyle='dashed', alpha=0.5)
#             if key == 'wflow':
# #                ax.fill_between(set.index, set[key], where = set[key] > 0,
# #                                color = names[key][1], alpha=0.4)
#                 pass
#         for loca in ['top', 'right']:
#             ax.spines[loca].set_visible(False)
# #        ax.set_xlim(0, win)
#         ax.get_xaxis().tick_bottom()
#         ax.set_xticklabels(np.linspace(df.sec.loc[mini], df.sec.loc[maxi],
#                                        len(ax.get_xticklabels())).astype(int).astype(str).tolist())
#         ax.set_xlabel('time (sec)')
#     #two waves
#     elif len(keys) == 2:
#         fig = plt.figure(figsize=(10, 4))
#         ax_list = []
#         ax1 = fig.add_subplot(2, 1, 1)
#         ax1.margins(0)
#         ax_list.append(ax1)
#         ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
#         ax2.margins(0)
#         ax_list.append(ax2)
#         for i, key in enumerate(keys):
#             ax = ax_list[i]
#             ax.set_title(names[key][0])
#             line, = ax.plot(df[key], color=names[key][1], alpha=0.6)
#             lines.append(line)
#             lims = ax.get_xlim()
#             ax.hlines(0, lims[0], lims[1], alpha=0.3)
#             ax.set_ylabel(names[key][2])
#             if key == 'wco2':
#                 ax.hlines(38, lims[0], lims[1], linestyle='dashed',
#                           color=names[key][1], alpha=0.5)
#                 ax.set_ylim(0, 50)
#             if key == 'wekg':
#                 ax.grid()
#             if key == 'wflow':
# #                ax.fill_between(set.index, set[key], where = set[key] > 0,
# #                                color = names[key][1], alpha=0.4)
#                 pass
#             if key == 'wap':
#                 ax.hlines(70, lims[0], lims[1], color=names[key][1],
#                           linestyle='dashed', alpha=0.5)
#                 ax.set_ylim(50, 110)
#             ax.get_xaxis().tick_bottom()
#             if i > 0:
# #                ax.set_xlim(0, win)
#                 ax.get_xaxis().tick_bottom()
#                 ax.set_xticklabels(np.linspace(df.sec.loc[mini], df.sec.loc[maxi],
#                                                len(ax.get_xticklabels())).astype(int).astype(str).tolist())
#                 ax.set_xlabel('time (sec)')
#         for ax in ax_list:
#             for loca in ['top', 'right']:
#                 ax.spines["top"].set_visible(False)
#                 ax.spines["right"].set_visible(False)
#     fig.tight_layout()
#     return fig, lines
# =============================================================================


def return_points(df, fig):
    """
    return a tupple containing the point values of ROI
    input :anesthesia record dataframe
    output: ROI dict
    """
    ax = fig.get_axes()[0]
    # point Value
    lims = ax.get_xlim()
    limpt = (int(lims[0]), int(lims[1]))
    # sec value
    limsec = (df.sec.loc[limpt[0]], df.sec.loc[limpt[1]])
    limdatetime = (df.datetime.loc[limpt[0]], df.datetime.loc[limpt[1]])
    #    mini = wData.sec.get_loc(mini, method='nearest')
    #    mini = (df.sec - lims[0]).abs().argsort()[:1][0]
    #    maxi = (df.sec - lims[1]).abs().argsort()[:1][0]
    print()
    print("duration =", limsec[1] - limsec[0], "sec")
    print("time = ", limdatetime)
    print("limsec= (", limsec[0], ",", limsec[1], ")")
    print("limpt= (", limpt[0], ",", limpt[1], ")")
    print("mini:", int(limsec[0] / 60), "min :", limsec[0] % 60, "sec")
    print("maxi:", int(limsec[1] / 60), "min :", limsec[1] % 60, "sec")
    roidict = {"sec": limsec, "pt": limpt, "dt": limdatetime}
    return roidict


def restrict_time_area(df1, mini=None, maxi=None):
    """
    return a new dataframe with reindexation
    input : dataFrame, miniPointValue, maxiPointValue
    output: dataFrame
    """
    try:
        "sec" in df1.columns
    except:
        print("'sec' should be in the dataframe columns")
        return
    df2 = df1.iloc[np.arange(mini, maxi)].reset_index()
    df2.sec = df2.sec - df2.iloc[0].sec
    return df2
