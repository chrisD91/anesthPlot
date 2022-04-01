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
    ser_detrended = rec.wf.fix_baseline_wander(ser, 300)
    threshold = ser_detrended.quantile(q=0.82)
    # find the (up) peaks
    if up:
        peaks, properties = find_peaks(ser_detrended, height=threshold, distance=300)
    else:
        peaks, properties = find_peaks(-ser_detrended, height=-threshold, distance=300)
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
    maxis_loc, _ = find_peaks(peaksdf.wap)
    peaksdf.loc[maxis_loc, "local_max"] = True
    # get local min
    minis_loc, _ = find_peaks(-peaksdf.wap)
    peaksdf.loc[minis_loc, "local_min"] = True

    if not up:
        peaksdf.peak_heights = -1 * peaksdf.peak_heights
        peaksdf.rename(columns={"local_max": "local_min", "local_min": "local_max"})

    return peaksdf


def compute_systolic_variation(ser: pd.Series) -> float:
    """return the systolic variation : (maxi - mini) / mean """

    maxi, mini, mean = ser.agg(["max", "min", "mean"])
    return (maxi - mini) / mean


def plot_sample_systolic_pressure_variation(
    mwave, lims: Tuple = None, teach: bool = False
):
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
    # ax.plot(peak_df.set_index("sloc").wap, "-r", alpha=0.2)
    inter_beat = round((peak_df.sloc - peak_df.sloc.shift(1)).mean())
    beat_loc_df = peak_df.set_index("sloc")
    for sloc, yloc in beat_loc_df.loc[
        beat_loc_df.local_max + beat_loc_df.local_min, "wap"
    ].iteritems():
        ax.hlines(
            yloc, sloc - 0.7 * inter_beat, sloc + 0.7 * inter_beat, color="tab:grey"
        )

    # compute delta_PP
    peak_df_dwn = get_peaks(ser, up=False)
    peak_df_dwn.columns = [_ + "_dwn" for _ in peak_df_dwn.columns]

    pp_df = peak_df.copy()
    pp_df.columns = [_ + "_up" for _ in pp_df.columns]
    pp_df = pd.concat([pp_df, peak_df_dwn], axis=1)
    pp_df["delta"] = pp_df.peak_heights_up - pp_df.peak_heights_dwn

    maxi, mini, mean = pp_df["delta"].agg(["max", "min", "mean"])
    delta_variation = (maxi - mini) / mean
    delta_var = f"{delta_variation = :.2f}"
    print(delta_var)

    if teach:  # plot mesure intervals
        # sys_var
        sloc, yloc = beat_loc_df.wap.agg(["idxmax", "max"])
        ax.hlines(
            yloc,
            sloc - 0.7 * inter_beat,
            sloc + 0.7 * inter_beat,
            color="k",
            linewidth=3,
        )
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


def median_filter(num_std=3):
    def _median_filter(x):
        _median = np.median(x)
        _std = np.std(x)
        s = x[-1]
        return (
            s
            if s >= _median - num_std * _std and s <= _median + num_std * _std
            else np.nan
        )

    return _median_filter


def plot_record_systolic_variation(mwave):

    df = get_peaks(mwave.data.set_index("sec").wap.dropna())

    df["sys_var"] = np.nan
    # fs = int(mwaves.param["sampling_freq"])
    # start = df.index.min()
    end = df.index.max()
    indexes = list(df.loc[df.local_max].index)
    for b1, b2 in zip([0,] + indexes, indexes + [end,]):
        df.loc[b1:b2, "sys_var"] = compute_systolic_variation(df.loc[b1:b2, "wap"])
    df["i_pr"] = (1 / (df.sloc - df.sloc.shift(1))) * 60

    fig = plt.figure()
    fig.suptitle("systolic variation over time")
    ax = fig.add_subplot(111)
    ax.plot(mwaves.data.set_index("sec").wap, "-r", label="arterial pressure")
    # TODO append median filterin
    axT = ax.twinx()
    # heart rate
    ser = (
        df.set_index("sloc").i_pr.rolling(10).apply(median_filter(num_std=3), raw=True)
    )
    ser = df.set_index("sloc").i_pr
    ser = ser.fillna(method="bfill").fillna(method="ffill")
    axT.plot(ser.rolling(10, center=True).mean(), ":k", linewidth=2)
    # sys_var
    ser = df.set_index("sloc").sys_var * 100
    ser = ser.rolling(50).apply(median_filter(num_std=3), raw=True)
    ser = ser.fillna(method="bfill").fillna(method="ffill")
    axT.plot(ser.dropna().rolling(10).mean(), "-b", label="sys_var med_rolmean")
    ax.set_ylim(50, 150)
    axT.set_ylim(0, 40)
    ax.set_xlabel("time (sec)")
    ax.set_ylabel("arterial pressure (mmHg)")
    axT.set_ylabel("systolic variation (%)")
    for ax in fig.get_axes():
        for spine in ["top"]:
            ax.spines[spine].set_visible(False)
    fig.tight_layout()

    return fig, df


# %%


if __name__ == "__main__":
    import numpy as np
    import anesplot.record_main as rec
    from anesplot.loadrec.export_reload import build_obj_from_hdf

    DIRNAME = "/Users/cdesbois/enva/clinique/recordings/casClin/220315/data"
    FILE = "qDonUnico.hdf"
    filename = os.path.join(DIRNAME, FILE)
    _, _, mwaves = build_obj_from_hdf(filename)

    samp_figure, _ = plot_sample_systolic_pressure_variation(mwaves, (4100, 4160))
    record_figure, peaks_df = plot_record_systolic_variation(mwaves)


def hampel_filter_pandas(input_series, window_size, n_sigmas=3):
    # https://towardsdatascience.com/outlier-detection-with-hampel-filter-85ddf523c73d

    k = 1.4826  # scale factor for Gaussian distribution
    new_series = input_series.copy()

    # helper lambda function
    MAD = lambda x: np.median(np.abs(x - np.median(x)))

    rolling_median = input_series.rolling(window=2 * window_size, center=True).median()
    rolling_mad = k * input_series.rolling(window=2 * window_size, center=True).apply(
        MAD
    )
    diff = np.abs(input_series - rolling_median)

    indices = list(np.argwhere(diff > (n_sigmas * rolling_mad)).flatten())
    new_series[indices] = rolling_median[indices]

    return new_series, indices
