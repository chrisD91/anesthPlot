# Any !/usr/bin/env python3
"""
Created on Wed Apr 27 15:46:14 2022

@author: cdesbois

list of function to choose, manipulate and combine the trends plot functions

"""
import logging

# import sys
from typing import Any, Callable, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import anesplot.plot.trend_plot as tplot
import anesplot.loadrec.dialogs as dlg


# app = QApplication.instance()
# logging.info(f"t_agg_plot.py : {__name__=}")
# if app is None:
#    logging.info("N0 QApplication instance - - - - - - - - - - - - - > creating one")
#    app = QApplication([])
# else:
#    logging.warning(f"QApplication instance already exists: {QApplication.instance()}")


# %%
def get_roi(
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
            datadf.set_index("dtime").index.get_indexer([_], method="nearest")
            for _ in dtime_lims
        ]
    else:  # index = sec
        sec_lims = ax.get_xlim()
        i_lims = [
            datadf.set_index("etimesec").index.get_indexer([_], method="nearest")
            for _ in sec_lims
        ]
    i_lims = [i_lims[0][0], i_lims[1][-1]]
    if "point" not in datadf.columns:
        datadf["point"] = datadf.index
    roidict = {}
    for abbr, col in {"dt": "dtime", "pt": "point", "sec": "etimesec"}.items():
        if col in datadf.reset_index().columns:
            lims = tuple(datadf.iloc[_][[col]].values[0] for _ in i_lims)
        else:
            # no dt values for televet
            lims = (np.nan, np.nan)
        roidict[abbr] = lims
    logging.info(f"{'-' * 10} defined a trend_roi")
    # append ylims and traces
    roidict["ylims"] = ylims
    return roidict


# %% build half white


def retrieve_function(name: str) -> Any:
    """Get the function from it's name."""
    func_list = [
        tplot.plot_ventil,
        tplot.plot_co2o2,
        tplot.plot_co2aa,
        tplot.plot_cardiovasc,
        tplot.hist_co2aa,
        tplot.hist_cardio,
        tplot.plot_sathr,
    ]
    return [_ for _ in func_list if _.__name__ == name][0]


def anotate_half_white(halffig: plt.Figure, lang: str = "fr") -> plt.Figure:
    """Annotate the half fig."""
    ax = halffig.get_axes()[0]
    questions = {
        "fr": [
            "1: que se passe-t-il ?",
            "2: que va-t-il se passer ?",
            "3: c'est grave docteur ?",
            "4: que feriez vous ?",
        ],
        "en": [
            "1: what is going on?",
            "2: what is going to happen?",
            "3: is it serious ?",
            "4: what would you do ?",
        ],
    }
    for question, pos in zip(
        questions.get(lang, questions["en"]),
        [(0.15, 0.9), (0.6, 0.9), (0.6, 0.7), (0.6, 0.5)],
    ):
        ax.text(
            pos[0],
            pos[1],
            question,
            horizontalalignment="left",
            fontsize=16,
            verticalalignment="center",
            transform=ax.transAxes,
        )
    return halffig


def build_half_white(
    inifig: plt.Figure,
    name: str,
    datadf: pd.DataFrame,
    param: dict[str, Any],
    roi: Optional[dict[str, Any]],
    lang: str = "fr",
) -> tuple[plt.Figure, Optional[tuple[float, float]], plt.Figure]:
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
    half_fig : plt.Figure
        the half-white figure (previous + 50% blank.
    full_lims : the limits
        the xscale.
    full_fig : plt.Figure
        the full scale figure (previous + 50% filled)
    """
    if roi is None:
        logging.warning("please build a roi using the .save_roi method")
        return plt.figure(), None, plt.figure()

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
    half_fig = func(shortdf, param)
    full_lims = (lims[0], lims[1] + (lims[1] - lims[0]))
    half_fig.get_axes()[0].set_xlim(full_lims)
    half_fig = anotate_half_white(half_fig, lang)

    full_fig = func(datadf, param)
    full_fig.get_axes()[0].set_xlim(full_lims)

    # size = inifig.get_size_inches()
    for fig in [half_fig, full_fig]:
        for ax, ylim in zip(fig.get_axes(), roi.get("ylims")):  # type: ignore
            ax.set_ylim(ylim)
            ax.axvline(lims[1], color="tab:grey")
        fig.set_size_inches(inifig.get_size_inches())
        fig.tight_layout()
        # fig.show()

    return half_fig, full_lims, full_fig


def plot_a_trend(
    datadf: pd.DataFrame, param_dico: dict[str, Any]
) -> tuple[plt.Figure, str]:
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
    # plotting
    func_list = [
        tplot.plot_ventil,
        tplot.plot_co2o2,
        tplot.plot_co2aa,
        tplot.plot_cardiovasc,
        tplot.hist_co2aa,
        tplot.hist_cardio,
    ]
    # clean the data for taph monitoring
    if param_dico["source"] == "taphTrend":
        func_list.insert(0, tplot.plot_sathr)
        if "co2exp" in datadf.columns.values:
            datadf.loc[datadf["co2exp"] < 20, "co2exp"] = np.NaN
        # test ip1m
        if ("ip1m" in datadf.columns) and not datadf.ip1m.isnull().all():
            datadf.loc[datadf["ip1m"] < 20, "ip1m"] = np.NaN
        else:
            logging.warning("no pressure tdata recorded")
    # choose (NB dialog doesnt allow to use a list of functions -> use str
    names = [_.__name__ for _ in func_list]
    question = "choose the function to use"
    name = dlg.choose_in_alist(names, question)
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
            logging.warning("no pressure tdata recorded")
    afig_list = []
    # plotting
    plot_func_list: list[Callable[[pd.DataFrame, dict[str, Any]], plt.Figure]] = [
        tplot.plot_ventil,
        tplot.plot_co2o2,
        tplot.plot_co2aa,
        tplot.plot_cardiovasc,
        tplot.hist_co2aa,
        tplot.hist_cardio,
    ]
    if param_dico["source"] == "taphTrend":
        plot_func_list.insert(0, tplot.plot_sathr)
    logging.info("building figures")
    for func in plot_func_list:
        afig_list.append(func(datadf, param_dico))
    if header:
        afig_list.append(tplot.plot_header(header, param_dico))
    # logging.info("plt.show")
    plt.show()
    names = [st.__name__ for st in plot_func_list]
    if header:
        names.append("header")
    fig_dico = dict(zip(names, afig_list))
    return fig_dico


# %%

# if __name__ == "__main__":
#     pass
# import anesplot.record_main as rec
# from anesplot.slow_waves import MonitorTrend

# mtrends = MonitorTrend()
# figure, tracename = mtrends.plot_trend()
# logging.warning("now scale the figure please")
# # %%
# mtrends.save_roi()
# # scale the figure
# ahalf_fig, anew_lims, afull_fig = build_half_white(
#     figure,
#     name=tracename,
#     datadf=mtrends.data,
#     param=mtrends.param,
#     roi=mtrends.roi,
# )
# # change the scale for third
# figure.get_axes()[0].set_xlim(anew_lims)
