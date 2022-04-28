#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 15:46:14 2022

@author: cdesbois

list of function to choose, manipulate and combine the plot functions
"""


from PyQt5.QtWidgets import QInputDialog, QWidget

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

import anesplot.plot.trend_plot as tplot


# %%
def get_trend_roi(fig: plt.Figure, datadf: pd.DataFrame, params: dict) -> dict:
    """
    use the drawn figure to extract the x and x limits

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
    # TODO add exception for hist and header in the call process
    ylims = tuple([_.get_ylim() for _ in fig.get_axes()])
    # xlims
    ax = fig.get_axes()[0]
    if params["dtime"]:  # datetime in the x axis
        dtime_lims = [pd.to_datetime(mdates.num2date(_)) for _ in ax.get_xlim()]
        dtime_lims = [_.tz_localize(None) for _ in dtime_lims]
        # i_lims = [bisect(datadf.datetime, _) for _ in dtime_lims]
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
    for k, v in {"dt": "datetime", "pt": "point", "sec": "eTime"}.items():
        if v in datadf.reset_index().columns:
            lims = tuple([datadf.iloc[_][[v]].values[0] for _ in i_lims])
        else:
            # no dt values for televet
            lims = (np.nan, np.nan)
        roidict[k] = lims
    print(f"{'-' * 10} defined a trend_roi")
    # append ylims and traces
    roidict["ylims"] = ylims
    return roidict


# %% build half white


def retrieve_function(name):
    """ get the function from it's name """
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
    fig: plt.figure, name: str, datadf: pd.DataFrame, param: dict, roi: dict
):
    """
    build a half white figure for teaching

    Parameters
    ----------
    fig : plt.figure
        the figure to begin with.
    name : str
        the function used to build the figure.
    datadf : the pd.DataFrame
        the trend data
    param : dictionary
        the drawing parameters.

    Returns
    -------
    nfig : plt.Figure
        the half-white figure.
    nlims : the limits
        the xscale.

    """
    # TODO use the ROI function
    axes = fig.get_axes()
    ax = axes[0]
    lims = ax.get_xlim()
    if ax.lines[0].get_xdata().dtype == "<M8[ns]":
        # datetime scale
        t_loc0 = mdates.num2date(lims[0]).replace(tzinfo=None)
        t_loc1 = mdates.num2date(lims[1]).replace(tzinfo=None)
        df = datadf.set_index("datetime").loc[t_loc0:t_loc1].reset_index().copy()
    else:
        # etime scale
        df = datadf.set_index("eTimeMin").loc[lims[0] : lims[1]].reset_index().copy()
    # half white figure
    func = retrieve_function(name)
    nfig = func(df, param)
    nax = nfig.get_axes()[0]
    nlims = (lims[0], lims[1] + lims[1] - lims[0])
    nax.set_xlim(nlims)
    nax.axvline(lims[1], color="tab:grey")
    txt1 = "1: que se passe-t-il ?"
    txt2 = "2: que va-t-il se passer ?"
    txt3 = "3: c'est grave docteur ?"
    txt4 = "4: vous faites quoi ?"
    nax.text(
        0.25,
        0.9,
        txt1,
        horizontalalignment="center",
        fontsize=18,
        verticalalignment="center",
        transform=ax.transAxes,
    )
    nax.text(
        0.6,
        0.9,
        txt2,
        horizontalalignment="left",
        fontsize=18,
        verticalalignment="center",
        transform=ax.transAxes,
    )
    nax.text(
        0.6,
        0.7,
        txt3,
        horizontalalignment="left",
        fontsize=18,
        verticalalignment="center",
        transform=ax.transAxes,
    )
    nax.text(
        0.6,
        0.5,
        txt4,
        horizontalalignment="left",
        fontsize=18,
        verticalalignment="center",
        transform=ax.transAxes,
    )
    nnfig = func(datadf, param)
    nnfig.get_axes()[0].set_xlim(nax.set_xlim(nlims))
    for ax, lims in zip(fig.get_axes(), roi.get("ylims")):
        ax.set_ylim(lims)
    ax.axvline(lims[1], color="tab:grey")

    return nfig, nlims, nnfig


def plot_a_trend(datadf: pd.DataFrame, header: dict, param_dico: dict) -> plt.figure:
    """
    choose and generate a trend plot

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
    global APP
    question = "choose the function to use"
    #    APP = QApplication(sys.argv)
    widg = QWidget()
    func_list.reverse()
    names = [st.__name__ for st in func_list]
    name, ok_pressed = QInputDialog.getItem(widg, "select", question, names, 0, False)
    if not ok_pressed and name:
        return plt.figure()
    func = [_ for _ in func_list if _.__name__ == name][0]
    # plot
    fig = func(datadf, param_dico)
    plt.show()
    return fig, name


def plot_trenddata(datadf: pd.DataFrame, header: dict, param_dico: dict) -> dict:
    """
    generate a series of plots for anesthesia debriefing purposes

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
    plot_func_list = [
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
    import anesplot.record_main as rec

    mtrends = rec.MonitorTrend()
    fig, name = mtrends.plot_trend()
    print("now scale the figure please")
    # scale the figure
    n_fig, n_lims = build_half_white(
        fig, name, mtrends, param=mtrends.param, roi=mtrends.roi
    )
    # change the scale for third
    fig.get_axes()[0].set_xlim(n_lims)
