#!/usr/bin/env python3
"""
Created on Wed Jul 31 16:05:29 2019

@author: cdesbois

scan folders and check for hypotension

"""
import os
from typing import Any, Optional

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle

# import anesplot.loadrec.dialogs as dialogs

# from anesplot.slow_waves import MonitorTrend
import anesplot.slow_waves

# from anesplot.plot.plot_func import update_pltparams
# update_pltparams()

# %%

plt.close("all")


def extract_hypotension(
    df: pd.DataFrame, param: Optional[dict[str, Any]] = None, pamin: int = 70
) -> pd.DataFrame:
    """
    Return a dataframe with the beginning and ending phases of hypotension.

    Parameters
    ----------
    atrend : pd.DataFrame

    pamin : float= threshold de define hypotension on mean arterial pressure
    (default is 70)

    Returns
    -------
    durdf : pandas DataFrame containing
        transitionts (up and down, in  seconds from beginning)
        and duration in the hypotension state (in seconds)


    Parameters
    ----------
    df : pd.DataFrame
        the recorded data.
    param : Optional[dict[str, Any]], optional (default is None)
        the parameters (trends.param)
    pamin : int, optional (default is 70)
        the minimal arterial pressure value

    Returns
    -------
    durdf : pd.DataFrame
        a pandas dataframe containing the hypotension durations

    """
    datadf = df.copy()
    if "ip1m" not in datadf.columns:
        print("no ip1m recording in the data")
        return pd.DataFrame()
    # datadf = pd.DataFrame(datadf.set_index(datadf.etimemin.astype(int))["ip1m"])
    # datadf["low"] = datadf.ip1m < pamin  # -> True/False
    # datadf["trans"] = datadf.low - datadf.low.shift(-1)  # -1, 0, 1

    datadf = df[["dtime", "etimemin", "ip1m"]]
    datadf.loc[datadf.ip1m < 0] = np.nan
    datadf = datadf.dropna()
    # df = pd.DataFrame(df)
    datadf["hypo"] = datadf.ip1m < 70
    datadf["trans"] = datadf.hypo.shift(1) - datadf.hypo
    if datadf.loc[datadf.index[0]]["hypo"]:
        datadf.loc[datadf.index[0], ["trans"]] = -1
    else:
        datadf.loc[datadf.index[0], ["trans"]] = 1

    # extract changes
    if len(datadf.trans.dropna().value_counts()) > 1:
        down = datadf.loc[datadf.trans == -1, ["dtime"]].squeeze().rename("down")
        up = datadf.loc[datadf.trans == 1, ["dtime"]].squeeze().rename("up")
        durdf = pd.concat(
            [up.reset_index(drop=True), down.reset_index(drop=True)],
            ignore_index=False,
            axis=1,
        )
        if (up.iloc[0] - down.iloc[0]).total_seconds() < 0:
            # up is before down -> higher pressure
            up.drop(up.index[0])
            print("before")
        while len(up) > len(down):
            up.drop(up.index[-1])
            print("up >")
        while len(up) < len(down):
            down.drop(up.index[-1])
            print("down >")

        if len(durdf) > 0:
            # mean duration
            durdf["hypo_dur"] = durdf.up - durdf.down
            durdf.hypo_dur = durdf.hypo_dur.apply(lambda x: x.total_seconds() / 60)
            # mean values
            values = pd.DataFrame()
            for i, (start, end) in durdf[["down", "up"]].iterrows():
                ip1med = (
                    datadf.set_index("dtime").loc[start:end].iloc[:-1].ip1m.median()
                )
                mstart = datadf.loc[datadf.dtime == start, "etimemin"].to_list()[0]
                mend = datadf.loc[datadf.dtime == end, "etimemin"].to_list()[0]
                values[i] = [mstart, mend, ip1med]
            values = values.T
            values.columns = ["mstart", "mend", "ip1med"]
            durdf = pd.concat([durdf, values], axis=1)
    return durdf


def plot_hypotension(
    atrend: Any, durdf: pd.DataFrame, durmin: int = 15, pamin: int = 70
) -> plt.Figure:
    """
    Plot the hypotentions phases.

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
    datadf = atrend.data.copy()
    if len(datadf) < 1:
        print(f"empty data for {atrend.param['file']}")
        return pd.DataFrame()
    datadf = pd.DataFrame(datadf.set_index(datadf.etimemin))

    fig = plt.figure()
    fig.suptitle("peroperative hypotension")
    ax = fig.add_subplot(111)
    ax.plot(datadf.ip1m, "-", color="tab:red", alpha=0.8)
    ax.axhline(y=70, color="tab:grey", alpha=0.5)
    if len(durdf) > 0:
        # for down_s, up_s, dur_s, *_ in durdf.loc[durdf.hypo_duration > 60].values:
        for start_m, end_m, dur_m in durdf.loc[
            durdf.hypo_dur > 1, ["mstart", "mend", "hypo_dur"]
        ].values:
            # ax.vlines(a, ymin=50, ymax=70, color='tab:red', alpha = 0.5)
            # ax.vlines(b, ymin=50, ymax=70, color='tab:green', alpha = 0.5)
            ax.add_patch(
                Rectangle(
                    xy=(start_m, 70),
                    width=(end_m - start_m),
                    height=-30,
                    color="tab:blue",
                    fc="tab:blue",
                    ec=None,
                    zorder=1,
                    fill=False,
                )
            )
            if dur_m > 15:
                ax.axvspan(xmin=start_m, xmax=end_m, color="tab:red", alpha=0.3)
        numb = len(durdf[durdf.hypo_dur > (durmin)])
        txt = f"{numb} period(s) of significative hypotension \n \
        (longer than {durmin} min & below {pamin} mmHg)"
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
        durations = list(durdf.loc[durdf.hypo_dur > 15, ["hypo_dur"]].values.flatten())
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
    fig.tight_layout()
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, atrend.param["file"], ha="left", va="bottom", alpha=0.4)
    return fig


def scatter_length_meanhypo(atrend: Any, durdf: pd.DataFrame) -> plt.Figure:
    """
    Draw a scatter plot (hypotensive arterial value vs duration of hypotension).

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


def plot_all_dir_hypo(dirname: Optional[str] = None, scatter: bool = False) -> str:
    """
    Walk throught the folder and plot the values.

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
        mtrend = anesplot.slow_waves.MonitorTrend(filename)
        # if not trends.data is None:
        if mtrend.data is None:
            continue
        if "ip1m" not in mtrend.data.columns:
            continue
        dur_df = extract_hypotension(mtrend, pamin=70)
        if scatter:
            scatter_length_meanhypo(mtrend, dur_df)
        else:
            plot_hypotension(mtrend, dur_df)
    # in case of pb
    return filename


# %%
plt.close("all")
# folder or file
FOLDER = False  # folder or file ?
if __name__ == "__main__":

    # analyse all the recordings present in a folder
    from anesplot.config.load_recordrc import build_paths

    paths = build_paths()
    if FOLDER:
        dir_name = paths["mon_data"]
        # (
        #     "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        # )
        YEAR = ""
        dir_name = os.path.join(dir_name, YEAR)
        file_name = plot_all_dir_hypo(dir_name, scatter=False)
    else:
        # analyse just a file
        mtrends = anesplot.slow_waves.MonitorTrend()
        file_name = mtrends.filename
        if mtrends.data is not None:
            duration_df = extract_hypotension(mtrends.data, mtrends.param, pamin=70)
            figure = plot_hypotension(mtrends, duration_df)
            # fig = scatter_length_meanhypo(trends, dur_df)
        else:
            print("no data")
