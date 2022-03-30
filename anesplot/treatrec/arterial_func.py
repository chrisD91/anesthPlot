#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 13:00:08 2022

@author: cdesbois
"""


import os

import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as sg
from typing import Tuple

import anesplot.record_main as rec
from anesplot.loadrec.export_reload import build_obj_from_hdf


plt.close("all")
dirname = "/Users/cdesbois/enva/clinique/recordings/casClin/220315/data"
file = "qDonUnico.hdf"
filename = os.path.join(dirname, file)
_, _, mwaves = build_obj_from_hdf(filename)
# mwaves.param["dtime"] = False
# fig, *_ = mwaves.plot_wave(["wap"])
# ax = fig.get_axes()[0]
# ax.set_xlim(4100, 4160)

# lims = (4100, 4200)
# df = mwaves.data[["sec", "wap"]].copy()
# # df = mwaves.data.set_index('sec')
# # df = mwaves.data.set_index('sec').wap.iloc[lims[0]:lims[1]]

# df = df.set_index("sec").loc[lims[0] : lims[1]]
# %%
plt.close("all")

# peaks_vals = pd.DataFrame()


def plot_systolic_pressure_variation(mwave, lims: Tuple = None):
    """
    extract and plot the systolic pressure variation"

    Parameters
    ----------
    mwave : monitor trend object
        the monitor recording
    lims : tuple, (default is none)
        the limits to use (in sec) If none is provided, a 60 sec window
            will be used starting at the beginning of the record

    Returns
    -------
    fig : plt.Figure
        the matplotlib figure.

    """

    df = mwave.data[["sec", "wap"]].dropna().copy()
    if lims is None:
        lims = (df.iloc[0].sec, df.iloc[0].sec + 60)
    df = df.set_index("sec").loc[lims[0] : lims[1]]

    # plot the arterial pressure data
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(df, "-r")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    # find the (up) peaks
    q = df.wap.quantile(q=0.8)
    # ax.axhline(q, color="tab:green", alpha=0.5)
    peaks_up, properties = sg.find_peaks(df.wap, height=q)
    ax.plot(df.iloc[peaks_up], "or", alpha=0.2)

    peaks_vals = df.iloc[peaks_up].copy()  # to keep the index ('sec')
    peaks_vals = peaks_vals.reset_index()
    peaks_vals["local_max"] = False
    peaks_vals["local_min"] = False

    maxi, mini, mean = peaks_vals["wap"].agg(["max", "min", "mean"])
    systolic_variation = (maxi - mini) / mean
    mes = f"{systolic_variation = :.2f}"
    print(mes)

    # get local max
    maxis_loc, _ = sg.find_peaks(properties["peak_heights"])
    peaks_vals.loc[maxis_loc, "local_max"] = True
    # ax.plot(peaks_vals.loc[peaks_vals.local_max, ["sec", "wap"]].set_index("sec"), "rD")

    # get local min
    minis_loc, _ = sg.find_peaks(-properties["peak_heights"])
    peaks_vals.loc[minis_loc, "local_min"] = True
    # ax.plot(peaks_vals.loc[peaks_vals.local_min, ["sec", "wap"]].set_index("sec"), "bD")

    inter_beat = round(peaks_vals.sec - peaks_vals.sec.shift(1)).mean()
    beat_loc_df = peaks_vals.set_index("sec")
    for i, loc in beat_loc_df.loc[
        beat_loc_df.local_max + beat_loc_df.local_min, "wap"
    ].iteritems():
        ax.hlines(loc, i - inter_beat, i + inter_beat, color="tab:grey")

    title = "cyclic arterial pressure variation"
    fig.suptitle(title)
    ax.set_ylabel("arterial pressure")
    ax.set_xlabel("time(sec)")
    ax.text(
        1,
        1,
        mes,
        horizontalalignment="right",
        verticalalignment="bottom",
        transform=ax.transAxes,
    )

    fig.tight_layout()

    return fig


figure = plot_systolic_pressure_variation(mwaves, (4100, 4160))

# %%
