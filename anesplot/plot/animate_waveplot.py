#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 15:03:44 2021

@author: cdesbois
"""

import os

from matplotlib import animation
import matplotlib.pyplot as plt
import pandas as pd

import anesplot.record_main as rec

#%% choose a plot
plt.close("all")
if not "waves" in dir():
    waves = rec.MonitorWave()
if not "paths" in dir():
    paths = {}

waves.param["dtime"] = False
keys = ["wawp", "wflow"]
fig, lines = waves.plot_wave(keys)

#%% choose an area of interest (roi)
roi = waves.define_a_roi()

#%% select subdata
def select_sub_dataframe(waves):
    """extract subdataframe corresponding to the roi

    :param waves: wave recording
    :type waves: rec.MonitorWave (with a defined roi attribute)
    :return: df
    :rtype: pandas.dataframe

    """
    roi = waves.roi
    sub_df = waves.data[roi["sec"][0] < waves.data.sec]
    sub_df = sub_df[sub_df.sec < roi["sec"][1]]
    sub_df = sub_df.set_index("sec")
    sub_df = sub_df[keys].copy()
    return sub_df


df = select_sub_dataframe(waves)

#%% build animation


def animate(i):
    """
    animate frame[i], add 10 points to the lines
    return the two lines2D objects
    """
    #    print(i, len(df)/10)
    #    bol = (i > (len(df)/10 -40))
    #    print(bol)
    #    if bol:
    #        line0.set_data([],[])
    #        return line0,
    if len(keys) == 1:
        trace_name = keys[0]
        line0.set_data(
            df.iloc[0 : 10 * i].index, df.iloc[0 : 10 * i][trace_name].values
        )
        return (line0,)
    trace_name = keys[0]
    line0.set_data(df.iloc[0 : 10 * i].index, df.iloc[0 : 10 * i][trace_name].values)
    trace_name = keys[1]
    line1.set_data(df.iloc[0 : 10 * i].index, df.iloc[0 : 10 * i][trace_name].values)
    return (
        line0,
        line1,
    )


# NB lag for co2 ie around -480 points
anim = True
save = False
speed = 5  # speed of the animation

savename = "example"
paths["save"] = "/Users/cdesbois/toPlay"
fileName = os.path.join(paths["save"], savename)


if anim:
    for line in lines:
        line.set_data([], [])
    line0 = lines[0]
    try:
        line1 = lines[1]
    except:
        line1 = None
    #
    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=int(len(df) / 10),
        interval=30 / speed,
        repeat=False,
        blit=True,
        save_count=int(len(df) / 10),
    )
    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)
    if save:
        ani.save(fileName + ".mp4")
        fig.savefig(fileName + ".png")
plt.show()
