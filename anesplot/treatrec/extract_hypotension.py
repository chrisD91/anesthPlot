#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 16:05:29 2019

@author: cdesbois

scan folders and check for hypotension
"""
import os

import matplotlib.pyplot as plt

# import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

from anesplot.record_main import MonitorTrend

# import utils
FONT_SIZE = "medium"  # large, medium
params = {
    "font.sans-serif": ["Arial"],
    "font.size": 12,
    "legend.fontsize": FONT_SIZE,
    "figure.figsize": (12, 3.1),
    "axes.labelsize": FONT_SIZE,
    "axes.titlesize": FONT_SIZE,
    "xtick.labelsize": FONT_SIZE,
    "ytick.labelsize": FONT_SIZE,
    "axes.xmargin": 0,
}
plt.rcParams.update(params)
plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces

# df = trends.data
# %%

plt.close("all")


def extract_hypotension(atrend, pamin: int = 70) -> pd.DataFrame:
    """
    return a dataframe with the beginning and ending phases of hypotension

    Parameters
    ----------
    atrend : MonitorTrend object
    pamin : float= threshold de define hypotension on mean arterial pressure
    (default is 70)
    Returns
    -------
    durdf : pandas DataFrame containing
        transitionts (up and down, in  seconds from beginning)
        and duration in the hypotension state (in seconds)
    """
    datadf = atrend.data.copy()
    if "ip1m" not in datadf.columns:
        print("no ip1m recording in the data")
        return atrend.param["file"]
    datadf = pd.DataFrame(datadf.set_index(datadf.eTime.astype(int))["ip1m"])
    datadf["low"] = datadf.ip1m < pamin
    datadf["trans"] = datadf.low - datadf.low.shift(-1)
    # extract changes
    durdf = pd.DataFrame()
    # monotonic
    if len(datadf.trans.dropna().value_counts()) > 1:
        durdf["down"] = datadf.loc[datadf.trans == -1].index.to_list()
        uplist = datadf.loc[datadf.trans == 1].index.to_list()
        durdf = durdf.join(pd.Series(name="up", data=uplist))
        if len(durdf) > 0:
            down_index, up_index = durdf.iloc[0]
            if down_index > up_index:
                durdf.up = durdf.up.shift(-1)
            durdf["hypo_duration"] = durdf.up - durdf.down
            # mean value
            hypos = []
            for i in durdf.index:
                down_index, up_index = durdf.loc[i, ["down", "up"]]
                hypo = datadf.loc[down_index:up_index, ["ip1m"]].mean()[0]
                hypos.append(hypo)
            durdf["hypo_value"] = hypos
        durdf = durdf.dropna()
    return durdf


def plot_hypotension(
    atrend, durdf: pd.DataFrame, durmin: int = 15, pamin: int = 70
) -> plt.Figure:
    """
    plot the hypotentions phases

    Parameters
    ----------
    atrend : MonitorTrend
        trend data.
    durdf : pd.DataFrame
        hypotension duration data.
    durmin : int, optional (default is 15)
        The minimal duration of an hypotension period

    Returns
    -------
    fig : plt.Figure

    """
    param = atrend.param
    datadf = atrend.data.copy()
    if len(datadf) < 1:
        print(f"empty data for {param['file']}")
        return param["file"]
    datadf = pd.DataFrame(datadf.set_index(datadf.eTime.astype(int))["ip1m"])

    fig = plt.figure()
    fig.suptitle("peroperative hypotension")
    ax = fig.add_subplot(111)
    ax.plot(datadf.ip1m, "-", color="tab:red", alpha=0.8)
    ax.axhline(y=70, color="tab:grey", alpha=0.5)
    if len(durdf) > 0:
        for a, b, t, *_ in durdf.loc[durdf.hypo_duration > 60].values:
            # ax.vlines(a, ymin=50, ymax=70, color='tab:red', alpha = 0.5)
            # ax.vlines(b, ymin=50, ymax=70, color='tab:green', alpha = 0.5)
            ax.add_patch(
                Rectangle(
                    xy=(a, 70),
                    width=(b - a),
                    height=-30,
                    color="tab:blue",
                    fc="tab:blue",
                    ec=None,
                    zorder=1,
                    fill=False,
                )
            )
            # min=a, xmax=b, ymin=0.4, ymax=0.6, color='tab:red', alpha=0.3)

            if t > 15 * 60:
                ax.axvspan(xmin=a, xmax=b, color="tab:red", alpha=0.3)
        nb = len(durdf[durdf.hypo_duration > (durmin * 60)])
        txt = "{} period(s) of significative hypotension \n \
        (longer than {} min below {} mmHg)".format(
            nb, durmin, pamin
        )
        ax.text(
            0.5,
            0.1,
            txt,
            ha="center",
            va="bottom",
            transform=ax.transAxes,
            color="tab:grey",
        )
        txt = "hypotension lasting longer than 15 minutes \
            are represented as red rectangles "
        ax.text(
            0.5,
            0.95,
            txt,
            ha="center",
            va="bottom",
            transform=ax.transAxes,
            color="tab:grey",
        )
        durations = list(
            durdf.loc[durdf.hypo_duration > 15 * 60, ["hypo_duration"]].values.flatten()
            / 60
        )
        if len(durations) > 0:
            durations = [round(_) for _ in durations]
            txt = f"hypotensions={durations} min"
            ax.text(
                0.5,
                0.03,
                txt,
                ha="center",
                va="bottom",
                transform=ax.transAxes,
                color="k",
            )
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    return fig


def scatter_length_meanhypo(atrend, durdf: pd.DataFrame) -> plt.Figure:
    """
    draw a scatter plot (hypotensive arterial value vs duration of hypotension)

    Parameters
    ----------
    atrend : MonitorTrend
        the recorded trend data.
    durdf : pd.DataFrame
        value and duration of the hypotension periods.

    Returns
    -------
    plt.Figure
        scatter plot.

    """

    param = atrend.param
    if "hypo_duration" not in durdf:
        return plt.figure()
    fig = plt.figure(figsize=(8, 6))
    fig.suptitle("hypotension episodes")
    ax = fig.add_subplot(111)
    ax.scatter(
        durdf.hypo_duration / 60,
        durdf.hypo_value,
        marker="o",
        color="tab:red",
        s=200,
        alpha=0.8,
    )
    ax.set_ylabel("mean hypotension value (mmHg)")
    ax.set_xlabel("duration of episode (min)")
    ax.axhline(y=70, color="tab:gray", alpha=0.8)
    ax.axhline(y=50, color="tab:blue", alpha=0.8)
    xlims = ax.get_xlim()
    ylims = (0, 80)
    ax.set_ylim(ylims)
    ax.set_xlim(0, xlims[1])
    if xlims[1] < 20:
        ax.set_xlim(0, 20)
    xlims = ax.get_xlim()
    ylims = ax.get_ylim()
    ax.add_patch(
        Rectangle(
            xy=(15, ylims[0]),
            width=(xlims[1] - 15),
            height=70 - ylims[0],
            color="tab:grey",
            fc="tab:blue",
            ec=None,
            zorder=1,
            fill=True,
            alpha=0.3,
        )
    )
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    return fig


def plot_all_dir_hypo(dirname: str = None, scatter: bool = False) -> str:
    """
    walk throught the folder and plot the values

    Parameters
    ----------
    dirname : str, optional (default is None)
        The name of the directory to scan
    scatter : bool, optional (default is False)
        generate a scatter plot or not

    Returns
    -------
    filename : str

    """

    if dirname is None:
        dirname = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
    files = []
    for file in os.listdir(dirname):
        if os.path.isfile(os.path.join(dirname, file)):
            files.append(file)
    files = [_ for _ in files if "Wave" not in _]
    files = [_ for _ in files if not _.startswith(".")]
    for file in files:
        filename = os.path.join(dirname, file)
        atrend = MonitorTrend(filename)
        # if not trends.data is None:
        if atrend.data is None:
            continue
        if "ip1m" not in atrend.data.columns:
            continue
        dur_df = extract_hypotension(atrend, pamin=70)
        if scatter:
            scatter_length_meanhypo(atrend, dur_df)
        else:
            plot_hypotension(atrend, dur_df)
    # in case of pb
    return filename


# %%
plt.close("all")
# folder or file
FOLDER = True  # folder or file ?
if __name__ == "__main__":
    # analyse all the recordings present in a folder
    if FOLDER:
        dir_name = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
        dir_name = os.path.join(dir_name, "2021")
        file_name = plot_all_dir_hypo(dir_name, scatter=False)
    else:
        # analyse just a file
        file_name = None
        trends = MonitorTrend(file_name)
        if not trends.data is None:
            duration_df = extract_hypotension(trends, pamin=70)
            figure = plot_hypotension(trends, duration_df)
            # fig = scatter_length_meanhypo(trends, dur_df)

        else:
            print("no data")
