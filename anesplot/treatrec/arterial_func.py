#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 13:00:08 2022

@author: cdesbois
"""


import os
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import find_peaks

# %%
plt.close("all")


def get_peaks(ser: pd.Series, up: bool = True) -> pd.DataFrame:
    """
    extract a peak location from an arterial time series

    Parameters
    ----------
    ser : pd.Series
        arterial time series (val = arterial wave, index = sec).
    up : bool, optional (default is True)
        extraction of the 'up' peaks. (false -> 'down peaks')

    Returns
    -------
    peaksdf : pd.DataFrame that contains
        'ploc' & 'sloc' : point and second based beat location
        'wap' & 'peak_heights' : the arterials values
        'local_max' & 'local_min' : boolean for local maxima and minima

    """

    # find the (up) peaks
    threshold = ser.quantile(q=0.82)
    # ax.axhline(threshold, color="tab:green", alpha=0.5)
    # added a distance to avoid double detection
    if up:
        peaks, properties = find_peaks(ser, height=threshold, distance=300)
    else:
        peaks, properties = find_peaks(-ser, height=-threshold, distance=300)
    # ser -> peak_df (ie restrict index)
    peaksdf = ser.reset_index().loc[peaks]
    peaksdf = peaksdf.rename(columns={"sec": "sloc"})
    peaksdf.index.name = "ploc"
    peaksdf = peaksdf.reset_index()
    # append heights
    for key in properties:
        peaksdf[key] = properties[key]

    # get local min max
    peaksdf["local_max"] = False
    peaksdf["local_min"] = False
    # get local max
    maxis_loc, _ = find_peaks(peaksdf.peak_heights)
    peaksdf.loc[maxis_loc, "local_max"] = True
    # get local min
    minis_loc, _ = find_peaks(-peaksdf.peak_heights)
    peaksdf.loc[minis_loc, "local_min"] = True

    if not up:
        peaksdf.peak_heights = -1 * peaksdf.peak_heights
        peaksdf.rename(columns={"local_max": "local_min", "local_min": "local_max"})

    return peaksdf


def plot_systolic_pressure_variation(mwave, lims: Tuple = None, teach: bool = False):
    """
    extract and plot the systolic pressure variation"

    Parameters
    ----------
    mwave : monitor trend object
        the monitor recording
    lims : tuple, (default is None)
        the limits to use (in sec)
        If none the mwave.roi will be used
    teach : boolean (default is False)
        if true added markers on the most relevant differences
    Returns
    -------
    fig : plt.Figure
        the matplotlib figure.

    """

    datadf = mwave.data[["sec", "wap"]].dropna().copy()
    if lims is None:
        lims = mwave.roi["sec"]
        # lims = (df.iloc[0].sec, df.iloc[0].sec + 60)
    datadf = datadf.set_index("sec").loc[lims[0] : lims[1]]

    # plot the arterial pressure data
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(datadf, "-r")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.set_ymargin(0.1)

    # find the (up) peaks
    ser = datadf.wap.dropna()
    peak_df = get_peaks(ser, up=True)

    maxi, mini, med = peak_df["wap"].agg(["max", "min", "median"])
    systolic_variation = (maxi - mini) / med
    sys_var = f"{systolic_variation = :.2f}"
    print(sys_var)

    # plot
    ax.plot(peak_df.set_index("sloc").wap, "or", alpha=0.2)
    inter_beat = round((peak_df.sloc - peak_df.sloc.shift(1)).mean())
    beat_loc_df = peak_df.set_index("sloc")
    for sloc, yloc in beat_loc_df.loc[
        beat_loc_df.local_max + beat_loc_df.local_min, "wap"
    ].iteritems():
        ax.hlines(yloc, sloc - inter_beat, sloc + inter_beat, color="tab:grey")

    # compute delta_PP
    peak_df_dwn = get_peaks(ser, up=False)
    peak_df_dwn.columns = [_ + "_dwn" for _ in peak_df_dwn.columns]

    pp_df = peak_df.copy()
    pp_df.columns = [_ + "_up" for _ in pp_df.columns]
    pp_df = pd.concat([pp_df, peak_df_dwn], axis=1)
    pp_df["delta"] = pp_df.peak_heights_up - pp_df.peak_heights_dwn

    maxi, mini, med = pp_df["delta"].agg(["max", "min", "median"])
    delta_variation = (maxi - mini) / med
    delta_var = f"{delta_variation = :.2f}"
    print(delta_var)

    if teach:  # plot mesure intervals
        # sys_var
        sloc, yloc = beat_loc_df.wap.agg(["idxmax", "max"])
        ax.hlines(yloc, sloc - inter_beat, sloc + inter_beat, color="k", linewidth=3)
        sloc, yloc = beat_loc_df.wap.agg(["idxmin", "min"])
        ax.hlines(yloc, sloc - inter_beat, sloc + inter_beat, color="k", linewidth=3)
        # delta_PP
        plocs = [
            pp_df.set_index("ploc_up").delta.idxmax(),
            pp_df.set_index("ploc_up").delta.idxmin(),
        ]
        for ploc in plocs:
            # ploc = heights.index[i]
            sec_up, val_up, val_dwn = pp_df.set_index("ploc_up").loc[
                ploc, ["sloc_up", "peak_heights_up", "peak_heights_dwn"]
            ]
            ax.vlines(sec_up, val_up, val_dwn, color="k", linewidth=2)
            for val in [val_up, val_dwn]:
                ax.hlines(
                    val,
                    sec_up - 0.5 * inter_beat,
                    sec_up + 0.5 * inter_beat,
                    color="k",
                    linewidth=3,
                    alpha=0.6,
                )

    title = sys_var + "     " + delta_var
    fig.suptitle(title)
    ax.set_ylabel("arterial pressure")
    ax.set_xlabel("time (sec)")
    # color_axis(ax, "left", "red")
    # color_axis(ax, "bottom", "grey")
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, mwave.param["file"], ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()
    plt.show()

    return fig, pp_df


# TODO : compute measure for a complete file
# (ie median value over 60 sec for example, or a measure in every cycle)

# %%

if __name__ == "__main__":
    import anesplot.record_main as rec
    from anesplot.loadrec.export_reload import build_obj_from_hdf

    DIRNAME = "/Users/cdesbois/enva/clinique/recordings/casClin/220315/data"
    FILE = "qDonUnico.hdf"
    filename = os.path.join(DIRNAME, FILE)
    _, _, mwaves = build_obj_from_hdf(filename)
    figure, _ = plot_systolic_pressure_variation(mwaves, (4100, 4160))
