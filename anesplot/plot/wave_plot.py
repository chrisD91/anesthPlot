# !/usr/bin/env python3
"""
Created on Tue Apr 19 09:08:56 2016

@author: cdesbois

collection of functions to plot the wave data

"""

# import os

# from bisect import bisect
# from math import ceil, floor
from typing import Any, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# import numpy as np
import pandas as pd

from anesplot.plot import pfunc

# from . import pfunc

pfunc.update_pltparams()


# %%
def build_default_parameters(keys: list[str]) -> dict[str, list[str]]:
    """
    Build a dictionary with key: [legend, color, unit].

    Parameters
    ----------
    keys : list(str)
        the columns labels.

    Returns
    -------
    dict(str, list(str)
        key: [legend, color, unit].

    """
    keydict = dict(
        wekg=["ECG", "tab:blue", "mVolt"],
        wco2=["expired CO2", "tab:blue", "mmHg"],
        wawp=["airway pressure", "tab:red", "cmH2O"],
        wflow=["expiratory flow", "tab:green", "flow"],
        wap=["arterial pressure", "tab:red", "mmHg"],
        wvp=["venous pressure", "tab:blue", "mmHg"],
        ihr=["instanous heart rate", "tab:blue", "bpm"],
    )
    # colors for missing keys
    if set(keys) - keydict.keys():
        for key in set(keys) - keydict.keys():
            keydict[key] = [key, "tab:blue", ""]
            if key.startswith("rr"):
                keydict[key] = [key, "tab:green", ""]
    return keydict


def restrict_wavedf(
    keys: list[str], datadf: pd.DataFrame, parm: dict[str, Any]
) -> pd.DataFrame:
    """
    Return a dataframe with adequate index and only selected columns.

    Parameters
    ----------
    keys : list[str]
        columns to use.
    datadf : pd.DataFrame
        the wave data.
    param : dict[str, Any]
        the description of the recording.

    Returns
    -------
    plotdf : ps.DataFrame
        the restricted dataframe.

    """
    ilims = [parm.get("mini", datadf.index[0]), parm.get("maxi", datadf.index[-1])]
    if not datadf.index[0] <= ilims[0] <= datadf.index[-1]:
        print("mini value not in range, replaced by start time value")
        ilims[0] = datadf.index[0]
    if not datadf.index[0] <= ilims[1] <= datadf.index[-1]:
        print("maxi value not in range, replaced by end time value")
        ilims[1] = datadf.index[-1]
    # datetime or elapsed time sec
    dtime = parm.get("dtime", False)
    if dtime and "dtime" not in datadf.columns:
        print("no dtime values, changed dtime to False")
        dtime = False
        parm["dtime"] = False
    cols = list(set(keys))
    if dtime:
        cols.insert(0, "dtime")
        plotdf = datadf[cols].copy()
        plotdf = plotdf.iloc[ilims[0] : ilims[1]].set_index("dtime")
        parm["unit"] = "dtime"
    else:
        cols.insert(0, "etimesec")
        plotdf = datadf[cols].copy()
        plotdf = plotdf.iloc[ilims[0] : ilims[1]].set_index("etimesec")
        parm["unit"] = "sec"
    return plotdf


def plot_on_one_ax(
    ax: plt.Axes, ser: pd.Series, key: str, names: list[str], dtime: bool
) -> tuple[plt.Axes, plt.Line2D]:
    """
    Plot using the provided ax.

    Parameters
    ----------
    ax : plt.Axes
        DESCRIPTION.
    df : pd.Series
        the data related key.
    key : str
        the selected columns.
    name : str
        the parameters to use for display.
    dtime : bool
        use datetime or elapsed time.

    Returns
    -------
    ax : TYPE
        plt.Axes.
    list
        list of the displayed line 2D objects.

    """
    _, color, unit = names
    (line,) = ax.plot(ser, color=color, alpha=0.6)
    ax.axhline(0, alpha=0.3)
    ax.set_ylabel(unit)
    if ser.quantile(0.01) < 0:
        lims = 1.2 * ser.quantile(0.01), 1.2 * ser.quantile(0.99)
    else:
        lims = 0.8 * ser.quantile(0.01), 1.2 * ser.quantile(0.99)
    if lims[0] != lims[1]:
        ax.set_ylim(lims)
    if dtime:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    if key == "wco2":
        ax.axhlines(38, linestyle="dashed", alpha=0.5)
        ax.set_ylim(0, 50)
    elif key == "wekg":
        ax.grid()
        ax.set_ylim(-0.5 + ser.quantile(0.01), 0.5 + ser.quantile(0.99))
    elif key == "wap":
        ax.axhline(70, color=color, linestyle="dashed", alpha=0.5)
        lims = (40, 1.10 * ser.quantile(0.99))
        if not (pd.isna(lims[0]) or pd.isna(lims[1])):
            ax.set_ylim(40, 1.10 * ser.quantile(0.99))
    elif key == "wflow":
        # ax.fill_between(set.index, set[key], where = set[key] > 0,
        #           color = names[key][1], alpha=0.4)
        pass
    ax.get_xaxis().tick_bottom()

    for spine in ["left", "bottom"]:
        pfunc.color_axis(ax, spine=spine, color="tab:grey")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    if not dtime:
        ax.set_xlabel("time (sec)")

    return ax, line


def plot_wave(
    datadf: pd.DataFrame, keys: list[str], param: Optional[dict[str, Any]] = None
) -> tuple[plt.Figure, list[Optional[plt.Line2D]]]:
    """
    Plot the waves recorded (from as5).

    (Nb plot datadf/index, but the xscale is indicated as sec)

    Parameters
    ----------
    datadf : pd.DataFrame
        recorded waves data.
    keys : list
        one or two in ['wekg','ECG','wco2','wawp','wflow','wap'].
    param : dict
        {mini: limits in point value (index), maxi: limits in point value (index)}.

    Returns
    -------
    matplotlib.pyplot.Figure
    list[plt.Line2D]
    """
    if param is None:
        param = {}
    if datadf.empty or len(datadf) < 5:
        print("empty dataframe")
        mes = f"empty data for {param.get('file', '')}"
        fig = pfunc.empty_data_fig(mes)
        return fig, [
            None,
        ]
    # test if wave is in the dataframe
    if not set(keys).issubset(set(datadf.columns)):
        diff = set(keys) - set(datadf.columns)
        mes = f"traces {diff} is not in the data ({param.get('file', '')})"
        print(mes)
        fig = pfunc.empty_data_fig(mes)
        return fig, [
            None,
        ]
    if len(keys) not in [1, 2]:
        print(f"only one or two keys are allowed ({keys} were used)")
        return plt.figure(), [
            None,
        ]
    dtime = param.get("dtime", False)
    # default plotting labels
    key_dict = build_default_parameters(keys)
    plotdf = restrict_wavedf(keys, datadf, param)

    # Plot
    lines: list[plt.Line2D] = []
    # one wave -> key, key_dict, plotdf[key], dtime
    if len(keys) == 1:
        fig = plt.figure(figsize=(12, 4))
        fig.suptitle(key_dict[keys[0]][0], color="tab:grey")
        ax = fig.add_subplot(111)
        ax.margins(0)
        ax, line = plot_on_one_ax(
            ax, plotdf[keys[0]], keys[0], key_dict[keys[0]], dtime
        )
        axes = [
            ax,
        ]
        lines.append(line)
    # two waves
    elif len(keys) == 2:
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 4), sharex=(True))
        for i, ax in enumerate(axes):
            ax, line = plot_on_one_ax(
                ax, plotdf[keys[i]], keys[i], key_dict[keys[i]], dtime
            )
            lines.append(line)

    for i, ax in enumerate(axes):
        if dtime:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        for spine in ["left", "right", "bottom"]:
            pfunc.color_axis(ax, spine=spine, color="tab:grey")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        if i == len("axes") - 1 and not dtime:
            ax.set_xlabel("time (sec)")
    # annotations
    pfunc.add_baseline(fig)
    # fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    # fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    return fig, lines


# %%
if __name__ == "__main__":
    pass
# =============================================================================
# def test_wave_plot():
#     """test the wave process"""
#     import random
#
#     import anesplot.loadrec.loadmonitor_waverecord
#     from anesplot.config.load_recordrc import build_paths
#
#     paths = build_paths()
#     file_name = os.path.join(paths["cwd"], "example_files", "MonitorWave.csv")
#     header = anesplot.loadrec.loadmonitor_waverecord.loadmonitor_waveheader(file_name)
#     assert isinstance(header, dict)
#     assert bool(header)
#
#     data_df = anesplot.loadrec.loadmonitor_waverecord.loadmonitor_wavedata(file_name)
#     assert isinstance(data_df, pd.DataFrame)
#     assert ~bool(data_df.empty)
#
#     columns = [_ for _ in data_df.columns if "time" not in _]
#     columns = [_ for _ in columns if _.startswith("w")]
#
#     plt.close("all")
#     for k in range(1, 3):
#         trace_keys = random.choices(columns, k=k)
#         # print(f"{k=} {trace_keys=}")
#         breakpoint
#         figure, lines2D = plot_wave(data_df, trace_keys)
#         assert isinstance(figure, plt.Figure)
#     plt.close("all")
#
# =============================================================================
