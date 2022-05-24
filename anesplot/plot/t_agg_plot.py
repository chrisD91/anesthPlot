# !/usr/bin/env python3
"""
Created on Wed Apr 27 15:46:14 2022

@author: cdesbois

list of function to choose, manipulate and combine the trends plot functions

"""
import sys
from typing import Callable, Any, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget

import anesplot.plot.trend_plot as tplot


# %%
def get_trend_roi(
    fig: plt.Figure, datadf: pd.DataFrame, params: dict[str, Any]
) -> dict[str, Any]:
    """
    Use the drawn figure to extract the x and x limits.

    Parameters
    ----------
    fig : plt.Figure
        the figure to get data from.
    datadf : pd.DataFrame
        waves recording.
    params : dict of parameters

    Returns
    -------
    dict :
        containing ylims, xlims(point, dtime and sec)
    """
    ylims = tuple(_.get_ylim() for _ in fig.get_axes())
    # xlims
    ax = fig.get_axes()[0]
    if params["dtime"]:  # datetime in the x axis
        dtime_lims = [pd.to_datetime(mdates.num2date(_)) for _ in ax.get_xlim()]
        dtime_lims = [_.tz_localize(None) for _ in dtime_lims]
        # i_lims = [bisect(datadf.datetime, _) for _ in dtime_lims]fig
        i_lims = [
            datadf.set_index("datetime").index.get_indexer([_], method="nearest")
            for _ in dtime_lims
        ]
    else:  # index = sec
        i_lims = [
            datadf.set_index("eTime").index.get_indexer([_], method="nearest")
            for _ in dtime_lims
        ]
    i_lims = [i_lims[0][0], i_lims[1][-1]]
    if "point" not in datadf.columns:
        datadf["point"] = datadf.index
    roidict = {}
    for abbr, col in {"dt": "datetime", "pt": "point", "sec": "eTime"}.items():
        if col in datadf.reset_index().columns:
            lims = tuple(datadf.iloc[_][[col]].values[0] for _ in i_lims)
        else:
            # no dt values for televet
            lims = (np.nan, np.nan)
        roidict[abbr] = lims
    print(f"{'-' * 10} defined a trend_roi")
    # append ylims and traces
    roidict["ylims"] = ylims
    return roidict


# %% build half white


def retrieve_function(name: str) -> Any:
    """Get the function from it's name."""
    func_list = [
        tplot.ventil,
        tplot.co2o2,
        tplot.co2iso,
        tplot.cardiovasc,
        tplot.hist_co2_iso,
        tplot.hist_cardio,
        tplot.sat_hr,
    ]
    return [_ for _ in func_list if _.__name__ == name][0]


def build_half_white(
    inifig: plt.figure,
    name: str,
    datadf: pd.DataFrame,
    param: dict[str, Any],
    roi: dict[str, Any],
) -> tuple[plt.Figure, tuple[float, float], plt.Figure]:
    """
    Build a half white figure for teaching.

    Parameters
    ----------
    inifig : plt.figure
        the figure to begin with.
    name : str
        the function used to build the figure.
    datadf : the pd.DataFrame
        the trend data
    param : dictionary
        the drawing parameters.

    Returns
    -------
    halffig : plt.Figure
        the half-white figure.
    fulllims : the limits
        the xscale.
    fullfig : plt.Figure
        the full scale (previous + next xscale)
    """
    if roi is None:
        print("please build a roi using the .save_roi method")
        return plt.Figure(), (), plt.Figure()

    # iniax = inifig.get_axes()[0]
    if param["dtime"]:
        # xcale <-> datetime
        lims = roi["dt"]
        shortdf = (
            datadf.set_index("datetime").loc[lims[0] : lims[1]].reset_index().copy()
        )
    else:
        # xscale <-> elapsed time
        lims = roi["sec"]
        shortdf = (
            datadf.set_index("eTimeMin").loc[lims[0] : lims[1]].reset_index().copy()
        )
    # build half white figure
    func = retrieve_function(name)
    halffig = func(shortdf, param)
    halfax = halffig.get_axes()[0]
    fulllims = (lims[0], lims[1] + (lims[1] - lims[0]))
    halfax.set_xlim(fulllims)
    # halfax.axvline(lims[1], color="tab:grey")
    texts = [
        "1: que se passe-t-il ?",
        "2: que va-t-il se passer ?",
        "3: c'est grave docteur ?",
        "4: que feriez vous ?",
    ]
    positions = [(0.15, 0.9), (0.6, 0.9), (0.6, 0.7), (0.6, 0.5)]
    for pos, txt in zip(positions, texts):
        halfax.text(
            pos[0],
            pos[1],
            txt,
            horizontalalignment="left",
            fontsize=16,
            verticalalignment="center",
            transform=halfax.transAxes,
        )
    fullfig = func(datadf, param)
    fullfig.get_axes()[0].set_xlim(fulllims)

    size = inifig.get_size_inches()
    for fig in [halffig, fullfig]:
        for i, ylim in enumerate(roi.get("ylims")):  # type: ignore
            ax = fig.get_axes()[i]
            ax.set_ylim(ylim)
            ax.axvline(lims[1], color="tab:grey")
        fig.set_size_inches(size)
        fig.tight_layout()
        fig.show()

    return halffig, fulllims, fullfig


def plot_a_trend(
    datadf: pd.DataFrame, header: dict[str, Any], param_dico: dict[str, Any]
) -> plt.figure:
    """
    Choose and generate a trend plot.

    Parameters
    ----------
    datadf : pd.DataFrame
        recorded data (MonitorTrend.data or TaphTrend.data).
    header : dict
        recording parameters (MonitorTrend.header or TaphTrend.header).
    param_dico : dict
        plotting parameters (MonitorTrend.param or TaphTrend.param).

    Returns
    -------
    plt.figure
        the builded figure
    """
    # clean the data for taph monitoring
    if param_dico["source"] == "taphTrend":
        if "co2exp" in datadf.columns.values:
            datadf.loc[datadf["co2exp"] < 20, "co2exp"] = np.NaN
        # test ip1m
        if ("ip1m" in datadf.columns) and not datadf.ip1m.isnull().all():
            datadf.loc[datadf["ip1m"] < 20, "ip1m"] = np.NaN
        else:
            print("no pressure tdata recorded")
    # plotting
    func_list = [
        tplot.ventil,
        tplot.co2o2,
        tplot.co2iso,
        tplot.cardiovasc,
        tplot.hist_co2_iso,
        tplot.hist_cardio,
    ]
    if param_dico["source"] == "taphTrend":
        func_list.insert(0, tplot.sat_hr)
    # choose
    if "app" not in dir():
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
    question = "choose the function to use"
    widg = QWidget()
    names = [st.__name__ for st in func_list[::-1]]
    name, ok_pressed = QInputDialog.getItem(widg, "select", question, names, 0, False)
    if not ok_pressed and name:
        return plt.figure()
    func = [_ for _ in func_list if _.__name__ == name][0]
    # plot
    fig = func(datadf, param_dico)
    plt.show()
    return fig, name


def plot_trenddata(
    datadf: pd.DataFrame, header: Optional[dict[str, Any]], param_dico: dict[str, Any]
) -> dict[str, plt.Figure]:
    """
    Generate a series of plots for anesthesia debriefing purposes.

    Parameters
    ----------
    datadf : pd.DataFrame
        recorded data (MonitorTrend.data or TaphTrend.data).
    header : dict
        recording parameters (MonitorTrend.header or TaphTrend.header).
    param_dico : dict
        plotting parameters (MonitorTrend.param or TaphTrend.param).

    Returns
    -------
    dict
        afig_dico : {names:fig_obj} of displayed figures

    """
    # clean the data for taph monitoring
    if param_dico["source"] == "taphTrend":
        if "co2exp" in datadf.columns.values:
            datadf.loc[datadf["co2exp"] < 20, "co2exp"] = np.NaN
        # test ip1m
        if ("ip1m" in datadf.columns) and not datadf.ip1m.isnull().all():
            datadf.loc[datadf["ip1m"] < 20, "ip1m"] = np.NaN
        else:
            print("no pressure tdata recorded")
    afig_list = []
    # plotting
    plot_func_list: list[Callable[[pd.DataFrame, dict[str, Any]], plt.Figure]] = [
        tplot.ventil,
        tplot.co2o2,
        tplot.co2iso,
        tplot.cardiovasc,
        tplot.hist_co2_iso,
        tplot.hist_cardio,
    ]
    if param_dico["source"] == "taphTrend":
        plot_func_list.insert(0, tplot.sat_hr)
    print("building figures")
    for func in plot_func_list:
        afig_list.append(func(datadf, param_dico))
    if header:
        afig_list.append(tplot.plot_header(header, param_dico))
    # print("plt.show")
    plt.show()
    names = [st.__name__ for st in plot_func_list]
    if header:
        names.append("header")
    fig_dico = dict(zip(names, afig_list))
    return fig_dico


# %%

if __name__ == "__main__":
    # import anesplot.record_main as rec
    from anesplot.slow_waves import MonitorTrend

    mtrends = MonitorTrend()
    figure, tracename = mtrends.plot_trend()
    print("now scale the figure please")
    # %%
    mtrends.save_roi()
    # scale the figure
    half_fig, new_lims, full_fig = build_half_white(
        figure,
        name=tracename,
        datadf=mtrends.data,
        param=mtrends.param,
        roi=mtrends.roi,
    )
    # change the scale for third
    figure.get_axes()[0].set_xlim(new_lims)
