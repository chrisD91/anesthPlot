# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from anesplot.record_main import MonitorTrend

# import utils
font_size = "medium"  # large, medium
params = {
    "font.sans-serif": ["Arial"],
    "font.size": 12,
    "legend.fontsize": font_size,
    "figure.figsize": (12, 3.1),
    "axes.labelsize": font_size,
    "axes.titlesize": font_size,
    "xtick.labelsize": font_size,
    "ytick.labelsize": font_size,
    "axes.xmargin": 0,
}
plt.rcParams.update(params)
plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces

# df = trends.data
#%%

plt.close("all")


def extract_hypotension(atrend, pamin=70):
    """
    return a dataframe with the beginning and ending phses of hypotension

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
    df = atrend.data.copy()
    if "ip1m" not in df.columns:
        print("no ip1m recording in the data")
        return atrend.param["file"]
    df = pd.DataFrame(df.set_index(df.eTime.astype(int))["ip1m"])
    df["low"] = df.ip1m < pamin
    df["trans"] = df.low - df.low.shift(-1)
    # extract changes
    durdf = pd.DataFrame()
    # monotonic
    if len(df.trans.dropna().value_counts()) > 1:
        durdf["down"] = df.loc[df.trans == -1].index.to_list()
        up = df.loc[df.trans == 1].index.to_list()
        durdf = durdf.join(pd.Series(name="up", data=up))
        if len(durdf) > 0:
            a, b = durdf.iloc[0]
            if a > b:
                durdf.up = durdf.up.shift(-1)
            durdf["hypo_duration"] = durdf.up - durdf.down
            # mean value
            hypos = []
            for i in durdf.index:
                a, b = durdf.loc[i, ["down", "up"]]
                hypo = df.loc[a:b, ["ip1m"]].mean()[0]
                hypos.append(hypo)
            durdf["hypo_value"] = hypos
        durdf = durdf.dropna()
    return durdf


def plot_hypotension(atrend, durdf, durmin=15, pamin=70):
    """
    plot the hupotentions phases

    Parameters
    ----------
    atrend : TYPE
        DESCRIPTION.
    durdf : TYPE
        DESCRIPTION.
    durmin : TYPE, optional
        DESCRIPTION. The default is 15.

    Returns
    -------
    fig : TYPE
        DESCRIPTION.

    """
    param = atrend.param
    df = atrend.data.copy()
    if len(df) < 1:
        print("empty data for {}".format(param["file"]))
        return param["file"]
    df = pd.DataFrame(df.set_index(df.eTime.astype(int))["ip1m"])

    fig = plt.figure()
    fig.suptitle("peroperative hypotension")
    ax = fig.add_subplot(111)
    ax.plot(df.ip1m, "-", color="tab:red", alpha=0.8)
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
            txt = "hypotensions={} min".format(durations)
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


def scatter_length_meanhypo(atrend, durdf):
    """
    draw a scatter plot (hypotensive arterial value vs duration of hypotension)
    Parameters
    ----------
    trends : MonitorTrend
    durdf : pandas dataframe containing the value and duration
    Returns
    -------
    fig : matplotlib.pyplot figure
    """
    param = atrend.param
    if "hypo_duration" not in durdf:
        return
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


def plot_all_dir_hypo(dirname=None, scatter=False):
    """ walk throught the folder and plot the values """
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
        if not "ip1m" in atrend.data.columns:
            continue
        dur_df = extract_hypotension(atrend, pamin=70)
        if scatter:
            scatter_length_meanhypo(atrend, dur_df)
        else:
            plot_hypotension(atrend, dur_df)
    # in case of pb
    return filename


#%%
# filename = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded/M2021_3_8-9_9_48.csv'
# trends = rec.MonitorTrend(filename)
plt.close("all")
# folder or file
folder = True  # folder or file ?
if __name__ == "__main__":
    # analyse all the recordings present in a folder
    if folder:
        dir_name = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
        file_name = plot_all_dir_hypo(dir_name, scatter=False)
        # analyse just a file
    else:
        file_name = None
        trends = MonitorTrend(file_name)
        if not trends.data is None:
            duration_df = extract_hypotension(trends, pamin=70)
            figure = plot_hypotension(trends, duration_df)
            # fig = scatter_length_meanhypo(trends, dur_df)

        else:
            print("no data")
