#!/usr/bin/env python3
"""
Created on Wed Jul 31 16:05:29 2019

@author: cdesbois

scan folders and check for hypotension

"""
import os
import logging
from typing import Any, Optional

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle

# import anesplot.loadrec.dialogs as dialogs

from anesplot.slow_waves import MonitorTrend

# import anesplot.slow_waves

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
    # TODO filter the data to remove data below 0 (at least)
    if param is None:
        param = {"file": "toto"}
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
    if len(datadf.trans.dropna().value_counts()) < 2:
        logging.warning(f"no transision detected ({param.get('file')})")
        return pd.DataFrame()
    # status at begining
    if datadf.loc[datadf.index[0]]["hypo"]:
        datadf.loc[datadf.index[0], ["trans"]] = -1
    else:
        datadf.loc[datadf.index[0], ["trans"]] = 1

    # extract changes
    # down = datadf.loc[datadf.trans == -1, ["dtime"]].squeeze().rename("down")
    # up = datadf.loc[datadf.trans == 1, ["dtime"]].squeeze().rename("up")
    down = pd.Series(
        name="down", data=datadf.loc[datadf.trans == -1, ["dtime"]].squeeze()
    )
    up = pd.Series(name="up", data=datadf.loc[datadf.trans == 1, ["dtime"]].squeeze())
    # test up and down matches
    if (up.iloc[0] - down.iloc[0]).total_seconds() < 0:
        # up is before down -> higher pressure
        up.drop(up.index[0], inplace=True)
        logging.warning(
            "up transition before the down one, removed the first transision"
        )
    while len(up) > len(down):
        up.drop(up.index[-1], inplace=True)
        logging.warning(
            "number of up transitions higher than down, removed the last up detection"
        )
    while len(up) < len(down):
        down.drop(down.index[-1], inplace=True)
        logging.warning(
            "number of down transitions higher than down ones : removed the last down detection"
        )
    durdf = pd.concat(
        [up.reset_index(drop=True), down.reset_index(drop=True)],
        ignore_index=False,
        axis=1,
    )
    if not durdf.empty:
        # mean duration
        durdf["hypo_dur"] = durdf.up - durdf.down
        durdf.hypo_dur = durdf.hypo_dur.apply(lambda x: x.total_seconds() / 60)
        # mean values
        # values = pd.DataFrame()
        indicises = []
        ip1meds = []
        mstarts = []
        mends = []
        for i, (start, end) in durdf[["down", "up"]].iterrows():
            indicises.append(i)
            ip1meds.append(
                datadf.set_index("dtime").loc[start:end].iloc[:-1].ip1m.median()
            )
            mstarts.append(datadf.loc[datadf.dtime == start, "etimemin"].to_list()[0])
            mends.append(datadf.loc[datadf.dtime == end, "etimemin"].to_list()[0])

        durdf["ip1med"] = ip1meds
        durdf["mstart"] = mstarts
        durdf["mend"] = mends
        #     ip1med = (
        #         datadf.set_index("dtime").loc[start:end].iloc[:-1].ip1m.median()
        #         )
        #     mstart = datadf.loc[datadf.dtime == start, "etimemin"].to_list()[0]
        #     mend = datadf.loc[datadf.dtime == end, "etimemin"].to_list()[0]
        #     values[i] = [mstart, mend, ip1med]
        # values = values.T
        # values.columns = ["mstart", "mend", "ip1med"]
        # durdf = pd.concat([durdf, values], axis=1)

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
        return plt.Figure()
    if "ip1m" not in datadf.columns:
        txt = f"no ip1m column in the data for {atrend.param['file']}"
        print(txt)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, txt, ha="center", va="center", transform=ax.transAxes)
        return fig
    datadf = pd.DataFrame(datadf.set_index(datadf.etimemin))
    ser = datadf.ip1m.copy()
    ser[ser > 140] = np.nan
    ser[ser < 0] = np.nan

    fig = plt.figure()
    fig.suptitle("peroperative hypotension")
    ax = fig.add_subplot(111)
    # ax.plot(datadf.ip1m, "-", color="tab:red", alpha=0.8)
    ax.plot(ser, "-", color="tab:red", alpha=0.8)
    ax.axhline(y=70, color="tab:grey", alpha=0.5)
    if durdf.empty:
        txt = "no hypotension phases detected"
        ax.text(
            0.5,
            0.9,
            txt,
            ha="center",
            va="bottom",
            transform=ax.transAxes,
            color="tab:grey",
        )
    else:
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
    if "hypo_dur" not in durdf:
        return plt.figure()
    fig = plt.figure(figsize=(8, 6))
    fig.suptitle("hypotension episodes")
    ax = fig.add_subplot(111)
    ax.scatter(
        durdf.hypo_dur,
        durdf.ip1med,
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
    fig.show()
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
    # >>>>>>>>>>>>>>>> list files
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

    # >>>>>>>>>>>>>>>>>> load data
    for file in files:
        filename = os.path.join(dirname, file)
        mtrend = MonitorTrend(filename)
        # if not trends.data is None:
        if mtrend.data.empty:
            print(f"{file} contains no data ")
            continue
        # >>>>>>>>>>>>>>>>>>> extract hypotension
        if "ip1m" not in mtrend.data.columns:
            continue
        dur_df = extract_hypotension(mtrend.data, mtrend.param, pamin=70)
        # >>>>>>>>>>>>>>>>>>> plot
        if scatter:
            scatter_length_meanhypo(mtrend, dur_df)
        else:
            plot_hypotension(mtrend, dur_df)
    # in case of pb
    return filename


def main(folder: bool = False) -> str:
    """Run function."""
    # analyse all the recordings present in a folder
    from anesplot.config.load_recordrc import build_paths

    paths = build_paths()
    if folder:
        dir_name = paths["mon_data"]
        # (
        #     "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        # )
        YEAR = "2021"
        dir_name = os.path.join(dir_name, YEAR)
        file_name = plot_all_dir_hypo(dir_name, scatter=False)
    else:
        # analyse just a file
        mtrends = MonitorTrend()
        # mtrends = MonitorTrend('/Users/cdesbois/enva/clinique/recordings/anesthRecords
        # /onPanelPcRecorded/M2022_8_18-15_18_17.csv')
        file_name = mtrends.filename
        if mtrends.data is not None:
            duration_df = extract_hypotension(mtrends.data, mtrends.param, pamin=70)
            figure = plot_hypotension(mtrends, duration_df)
            figure.show()
            # fig = scatter_length_meanhypo(trends, dur_df)
        else:
            print("no data")
    plt.show()
    return file_name


# %%
plt.close("all")
# folder or file
if __name__ == "__main__":
    # folder or file ?
    main(folder=False)
