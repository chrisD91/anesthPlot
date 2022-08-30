#!/usr/bin/env python3
"""
Created on Wed Jul 31 16:05:29 2019

@author: cdesbois

scan folders and check for hypotension

"""
import os
import logging
from datetime import datetime
from typing import Any, Optional

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle

import anesplot.loadrec.dialogs as dlg
from anesplot.slow_waves import MonitorTrend

# import anesplot.slow_waves

# from anesplot.plot.plot_func import update_pltparams
# update_pltparams()
plt.rcParams.update({"figure.max_open_warning": 0})

# %%

plt.close("all")


def get_trendfile(basename: Optional[str] = None) -> str:
    """
    Select the file to scan.

    Parameters
    ----------
    basename : Optional[str], optional (default is None)
        the directory to begin the selection

    Returns
    -------
    str
        the filename (fullname).

    """
    if basename is None:
        basename = os.path.expanduser("~")
    filename = dlg.choose_file(basename, title="choose a trendfile", filtre="*.csv")
    if "Wave" in os.path.basename(filename):
        print("this is not a monitorTrend file")
        return ""
    if not os.path.basename(filename).startswith("M"):
        print("this is not a monitorTrend file")
        return ""
    return filename


def get_dir(basename: Optional[str] = None) -> str:
    """
    Select the directory to scan.

    Parameters
    ----------
    basename : Optional[str], optional (default is None)
        the directory to begin the selection

    Returns
    -------
    str
        the directory name (fullname).

    """
    if basename is None:
        basename = os.path.expanduser("~")
    dirname = dlg.choose_directory(basename, title="choose a folder", see_question=True)
    return dirname


def list_files(dirname: str) -> list[str]:
    """
    List all the monitorTrend files in a folder.

    Parameters
    ----------
    dirname : str
        The directory path (fullname) to scan.

    Returns
    -------
    list[str]
        list of monitor (sorted) trend filenames

    """
    filedico: dict[str, str] = {}
    # nb date decoding because months include one digit code (eg '2' and '11')
    for file in os.listdir(dirname):
        if "Wave" in file:
            continue
        if file.startswith("."):
            continue
        if os.path.isfile(os.path.join(dirname, file)):
            date = os.path.basename(file).strip(".csv").strip("M")
            dtime = datetime.strptime(date, "%Y_%m_%d-%H_%M_%S")
            twodigitmonth_date = dtime.strftime("%Y_%m_%d-%H:%M")
            filedico[twodigitmonth_date] = os.path.join(dirname, file)
    filedico = dict(sorted(filedico.items()))
    return list(filedico.values())


def extract_hypotension(
    df: pd.DataFrame, param: Optional[dict[str, Any]] = None, pamin: int = 70
) -> pd.DataFrame:
    """
    Return start and end location hypotension phases.

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
        txt = f"empty data for {atrend.param['file']}"
        logging.warning(txt)
        print(txt)
        return plt.Figure()
    if "ip1m" not in datadf.columns:
        txt = f"no ip1m column in the data for {atrend.param['file']}"
        print(txt)
        logging.warning(txt)
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
    ax.set_ylim(0, 140)
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
        logging.warning("no hypotension extracted")
        return plt.figure()
    fig = plt.figure(figsize=(8, 6))
    fig.suptitle("hypotension episodes")
    ax = fig.add_subplot(111)
    # >>>
    ax.set_xmargin(0.1)

    ax.set_ymargin(0.1)
    # <<<<<
    ax.axvline(0, color="tab:grey")
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
    #   ax.set_xlim(-5, xlims[1])
    if xlims[1] < 20:
        ax.set_xlim(xlims[0], 20)
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
    for spine in ["left", "top", "right"]:
        ax.spines[spine].set_visible(False)
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.show()
    return fig


def main(
    folder: bool = True,
    scatter: bool = False,
    dirpath: Optional[str] = None,
) -> str:
    """Run function."""
    # analyse all the recordings present in a folder
    if dirpath is None:
        dirpath = os.path.expanduser("~")

    if folder:
        dir_name = get_dir(dirpath)
        file_list = list_files(dir_name)
        for file_name in file_list:
            mtrend = MonitorTrend(file_name)
            # if not trends.data is None:
            if mtrend.data.empty:
                logging.warning(f"{file_name} contains no data ")
                continue
            if "ip1m" not in mtrend.data.columns:
                logging.warning(f"{file_name} doesn't contains ip1m")
                continue
            dur_df = extract_hypotension(mtrend.data, mtrend.param, pamin=70)
            if scatter:
                print(f"main {scatter=}")
                scatter_length_meanhypo(mtrend, dur_df)
            else:
                plot_hypotension(mtrend, dur_df)
    else:
        # analyse just a file
        file_name = get_trendfile(dirpath)
        if not file_name:
            return ""
        mtrends = MonitorTrend(file_name)
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

    import argparse
    from anesplot.config.load_recordrc import build_paths

    paths = build_paths()

    parser = argparse.ArgumentParser(
        description="analyse a file or a folder for peroperative hypotension",
    )

    parser.add_argument("-f", "--filename", help="file to analyse", type=str)

    parser.add_argument(
        "-d",
        "--directory",
        help="choose a directory scan (default is a file analysis)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-s",
        "--scatter",
        help="choose a scatterplot (default is a trendplot)",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()
    main(folder=args.directory, scatter=args.scatter, dirpath=paths["mon_data"])
