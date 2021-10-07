#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 15:03:44 2021

@author: cdesbois
"""

import os
from math import floor, ceil

from matplotlib import animation
import matplotlib.pyplot as plt
import pandas as pd

import anesplot.record_main as rec


#%% select subdata


def create_video(waves, speed=1, save=False, savedir="~"):
    def select_sub_dataframe(datadf, keys, xlims):
        """extract subdataframe corresponding to the roi

        :param waves: wave recording
        :type waves: rec.MonitorWave (with a defined roi attribute)
        :return: df
        :rtype: pandas.dataframe

        """
        sub_df = datadf[xlims[0] < datadf.sec]
        sub_df = sub_df[sub_df.sec < xlims[1]]
        sub_df = sub_df.set_index("sec")
        sub_df = sub_df[keys].copy()
        return sub_df

    def init(waves, keys, xlims, ylims):
        plt.close("all")
        dtime = waves.param["dtime"]
        waves.param["dtime"] = False
        fig, lines, _ = waves.plot_wave(keys)
        for ax, ylim in zip(fig.get_axes(), ylims):
            ax.set_ylim(ylim)
            ax.set_xlim(xlims)
        waves.param["dtime"] = dtime
        return fig, lines

    def animate(i, df, keys, nbpoint):
        """
        animate frame[i], add 10 points to the lines
        return the two lines2D objects
        """
        if len(keys) == 1:
            trace_name = keys[0]
            line0.set_data(
                df.iloc[0 : nbpoint * i].index,
                df.iloc[0 : nbpoint * i][trace_name].values,
            )
            return (line0,)
        trace_name = keys[0]
        line0.set_data(
            df.iloc[0 : nbpoint * i].index, df.iloc[0 : nbpoint * i][trace_name].values
        )
        trace_name = keys[1]
        line1.set_data(
            df.iloc[0 : nbpoint * i].index, df.iloc[0 : nbpoint * i][trace_name].values
        )
        return (line0, line1)

    traces = waves.roi["traces"]
    x_lims = tuple([int(_) for _ in waves.roi["sec"]])
    y_lims = [(floor(a), ceil(b)) for a, b in waves.roi["ylims"]]
    fs = waves.fs
    interval = 100
    # speed = 2  # speed of the animation
    nb_of_points = speed * round(fs / interval) * 10

    df = select_sub_dataframe(waves.data, traces, x_lims)
    fig, lines = init(waves, traces, x_lims, y_lims)

    for line in lines:
        line.set_data([], [])
    line0 = lines[0]
    line1 = lines[1] if len(lines) > 1 else None

    global ani
    ani = animation.FuncAnimation(
        fig,
        animate,
        # init_func = init_wave,
        # frames=int(len(df) / 10),
        interval=interval,
        fargs=[df, traces, nb_of_points],
        repeat=False,
        blit=True,
        #        save_count=int(len(df) / 10),
    )

    if save:
        savename = "example"
        if savedir == "~":
            savedir = os.path.expanduser("~")
        fileName = os.path.join(savedir, savename)

        ani.save(fileName + ".mp4")
        fig.savefig(fileName + ".png")
    plt.show()


#%%
if __name__ == "__main__":
    # choose a plot
    plt.close("all")
    if not "waves" in dir():
        waves = rec.MonitorWave()
    if not "paths" in dir():
        paths = rec.build_paths()

    waves.param["dtime"] = False
    fig, lines, keys = waves.plot_wave()

    # choose an area of interest (roi)
    roi = waves.define_a_roi()

    create_video(waves, speed=1, save=False, savedir="~")
