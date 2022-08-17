#!/usr/bin/env python3
"""
Created on Mon Jun 20 14:44:08 2022

@author: cdesbois

trend_axis_plot :
    a series of functions taking plt.axes and pd.dataframe as argument
    and append the plot to the provided axes
"""
import logging
from types import SimpleNamespace as sn

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from anesplot.plot.ctes_plot import ctes_dico


def axplot_hist(ax: plt.axes, ser: pd.Series, key: str = "ip1") -> None:
    """
    Draw an histogram on the specified axes.

    Parameters
    ----------
    ax : plt.axes
        the axes to draw on.
    ser : pd.Series
        the data.
    key : str, optional (default is "ip1")
        key to load the presets

    Returns
    -------
    None.

    """
    defined = ["ip1", "ip2", "hr", "co2", "iso", "sevo", "aa"]
    if key not in defined:
        logging.warning(f"key should be in {defined} ({key} was used)")
    try:
        ctes = sn(**(ctes_dico[key]))  # get the drawing constants
    except KeyError:
        logging.warning(f"{key=} not defined in the constants")
        ctes = sn(**(ctes_dico["default"]))  # get the drawing constants

    ax.set_title(ctes.label, color=ctes.color)
    if len(ser) > 0:
        ax.hist(
            ser.dropna(), bins=30, color=ctes.color, edgecolor=ctes.edgecolor, alpha=0.7
        )
        q50 = np.percentile(ser, [50])
        ax.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
        for goal in ctes.goals:
            ax.axvline(goal, color="tab:grey", alpha=1)
        if ctes.goals:
            ax.axvspan(
                ctes.goals[0], ctes.goals[1], -0.1, 1, color="tab:grey", alpha=0.3
            )
        ax.set_xlabel(ctes.unit, alpha=0.5)
    else:
        ax.text(
            0.5,
            0.5,
            f"no data \n ({ctes.label})",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax.transAxes,
        )


def axplot_ventiltidal(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Append a tidal volume to the subplot provided.

    Parameters
    ----------
    ax : plt.axes
        the subplot to draw on.
    df : pd.DataFrame
        the data.

    Returns
    -------
    None
        if added plot data.

    """
    ax.set_ylabel("tidal volume")
    if "tvInsp" in df.columns:  # datex
        # comparison with the taphonius data ... to be improved
        # calib = ttrend.data.tvInsp.mean() / taph_trend.data.tv.mean()
        # calib = 187
        # ax.plot(df.tvInsp / calib, color="tab:orange", linewidth=2, label="tvInsp")
        ctes = sn(**ctes_dico["tvinsp"])
        calib = ctes.calib
        ax.plot(df.tvInsp / calib, color=ctes.color, linewidth=2, label=ctes.label)
    elif "tv_spont" in df.columns:  # taph
        ctes = sn(**ctes_dico["tvspont"])
        ax.plot(
            df.tv_spont,
            color=ctes.color,
            linewidth=1,
            linestyle="-",
            label=ctes.label,
        )
        try:
            ctes = sn(**ctes_dico["tvcontrol"])
            ax.plot(df.tv_control, color=ctes.color, linewidth=2, label=ctes.label)
            ctes = sn(**ctes_dico["settv"])
            ax.plot(
                df.set_tv,
                color=ctes.color,
                linewidth=1,
                linestyle=ctes.style,
                label=ctes.label,
            )
        except AttributeError:
            logging.warning("no ventilation started")
    else:
        logging.warning("no spirometry data in the recording")
        ax.text(
            0.5,
            0.5,
            "no spirometry",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
        )


def axplot_ventilpressure(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Append a ventilation pressure to the subplot provided.

    Parameters
    ----------
    ax : plt.axes
        the Axe to use to plot on.
    df : pd.DataFrame
        the data.

    Returns
    -------
    None
        if drawn.

    """
    ax.set_ylabel("pressure")
    columns = {}
    # monitor
    if {"pPeak", "pPlat", "peep"} < set(df.columns):
        columns = {"peak": "pPeak", "plat": "pPlat", "peep": "peep"}
        # correction if spirometry tubes have been inverted (plateau measure is false)
        if df.peep.mean() > df.pPlat.mean():
            columns["peep"] = "pPeak"
            columns["pPeak"] = "peep"
            columns.pop("plat")
    # taph
    # TODO fix end of file peak pressure
    elif {"set_peep"} < set(df.columns):
        columns = {"peak": "pPeak", "peep": "peep"}
    else:
        logging.warning("no spirometry data in the recording")

    keys = list(columns.values())

    if keys:
        for key in keys:
            ctes = sn(**ctes_dico[key])
            ax.plot(
                df[key],
                color=ctes.color,
                linewidth=1,
                linestyle=ctes.style,
                label=ctes.label,
            )
        ax.fill_between(
            df.index,
            df[keys[0]],
            df[keys[-1]],
            color="tab:red",
            alpha=0.2,
        )
        try:
            ctes = sn(**ctes_dico["setpeep"])
            ax.plot(
                df.set_peep,
                color=ctes.color,
                linewidth=1,
                linestyle=ctes.style,
                label=ctes.label,
            )
        except AttributeError:
            logging.warning("not on the taph")


def axplot_minvol_rr(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Append minute volume and respiratory rate to the provided axes.

    Parameters
    ----------
    ax : plt.axers
        the axis to draw on.
    df : pd.DataFrame
        the data.

    Returns
    -------
    None.

    """
    ax.set_ylabel("'minVol' & RR")
    minvol = sn(**ctes_dico["minvol"])
    if "co2_rr" in df.columns:
        co2rr = sn(**ctes_dico["co2rr"])
        ax.plot(
            df.co2_rr,
            color=co2rr.color,
            linewidth=2,
            linestyle=co2rr.style,
            label=co2rr.label,
        )
    if "minVexp" in df.columns:  # monitor
        ax.plot(df.minVexp, color=minvol.color, linewidth=2, label=minvol.label)
    if "set_rr" in df.columns:  # taph
        setrr = sn(**ctes_dico["setrr"])
        ax.plot(
            df.set_rr,
            color=setrr.color,
            linewidth=1,
            linestyle=setrr.style,
            label=setrr.label,
        )
    if "calc_minVol" in df.columns:  # taph
        ax.plot(
            df.calc_minVol / 10,
            color=minvol.color,
            linewidth=2,
            linestyle=minvol.style,
            label=minvol.label,
        )
    else:
        logging.warning("no spirometry data recorded")


def axplot_co2(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Plot etC02 on the provided axes.

    Parameters
    ----------
    ax : plt.axes
        the matplotlib axe to draw on.
    df : pd.DataFrame
        the data.

    Returns
    -------
    None.

    """
    co2 = sn(**ctes_dico["co2"])  # get the drawing constants
    ax.set_ylabel(co2.label)
    try:
        ax.plot(df.co2exp, color=co2.color, linewidth=2, linestyle="-")
        ax.plot(df.co2insp, color=co2.color, linewidth=1, linestyle="-")
        ax.fill_between(
            df.index,
            df.co2exp,
            df.co2insp,
            color=co2.color,
            alpha=co2.fillalpha,
        )
    # except KeyError:
    #     logging.warning("")
    except AttributeError:
        logging.warning("no capnometry in the recording")
        ax.text(
            0.5,
            0.5,
            "no capnometry",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
        )


def axplot_aa(ax: plt.axes, df: pd.DataFrame, key: str = "iso") -> None:
    """
    Plot iso on the provided axes.

    Parameters
    ----------
    ax : plt.axes
        the matplotlib axe to draw on.
    df : pd.DataFrame
        the data.
    key : str (default is 'iso')
        the anaethetic agent

    Returns
    -------
    None.

    """
    if key not in ["iso", "sevo", "aa"]:
        logging.warning("key should be in ['iso', 'sevo', 'aa']")
        return
    try:
        aa = sn(**ctes_dico[key])  # get the drawing constants
    except KeyError:
        logging.warning(f"{key=} not defined in the constants")
        aa = sn(**(ctes_dico["default"]))  # get the drawing constants
    ax.set_ylabel(aa.label)
    try:
        ax.plot(df.aaExp, color=aa.color, linewidth=2, linestyle="-")
        ax.plot(df.aaInsp, color=aa.color, linewidth=2, linestyle="-")
        ax.fill_between(
            df.index,
            df.aaExp,
            df.aaInsp,
            color=aa.color,
            alpha=aa.fillalpha,
        )
        if aa.ylims:
            ax.set_ylim(aa.ylims)
        if "mac" in dir(aa):
            ax.axhline(aa.mac, linestyle="--", color=aa.color, linewidth=2)
    # except KeyError:
    #     logging.warning("")
    except AttributeError:
        logging.warning("no anesthetic agent in the recording")
        ax.text(
            0.5,
            0.5,
            "no anesthetic agent",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
        )


def axplot_o2(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Plot oxygen  on the provided axes.

    Parameters
    ----------
    ax : plt.axes
        the matplotlib axe to draw on.
    df : pd.DataFrame
        the data.

    Returns
    -------
    None.

    """
    oxy = sn(**ctes_dico["o2"])  # get the drawing constants
    ax.set_ylabel(oxy.label)
    try:
        ax.plot(df.o2insp, color=oxy.color, linewidth=2, linestyle="-")
        ax.plot(df.o2exp, color=oxy.color, linewidth=2, linestyle="-")
        ax.fill_between(
            df.index,
            df.o2insp,
            df.o2exp,
            color=oxy.color,
            alpha=oxy.fillalpha,
        )
        ax.set_ylim(*oxy.ylims)
        ax.axhline(oxy.ylims[0], linestyle="dashed", linewidth=3, color=oxy.color)
    except AttributeError:
        logging.warning("no oxygen measure in the recording")
        ax.text(
            0.5,
            0.5,
            "no oxygen measure",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
        )


def axplot_arterialpressure(ax: plt.axes, df: pd.DataFrame, key: str = "ip1") -> None:
    """
    Plot pressure on the given axes.

    Parameters
    ----------
    ax : plt.axes
        the axes to use.
    df : pd.DataFrame
        the data.
    key : the trace to use (in ['ip1', 'ip2'])

    Returns
    -------
    None.

    """
    if key in ["ip1", "ip2"]:
        press = sn(**ctes_dico[key])  # get the drawing constants
    else:
        txt = "key should be in [ip1, ip2]"
        logging.warning(txt)
        ax.text(0.5, 0.5, txt)
        return

    ax.plot(df[press.traces[0]], color=press.color, label=press.label, linewidth=2)
    ax.fill_between(
        df.index,
        df[press.traces[1]],
        df[press.traces[2]],
        color=press.color,
        alpha=press.fillalpha,
    )
    ax.set_ylim(*press.ylims)
    ax.axhline(press.goals[0], linewidth=1, linestyle="dashed", color=press.color)
    ax.set_ylabel(press.label)


def axplot_sat(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Plot heart rate on the given axes.

    Parameters
    ----------
    ax : plt.axes
        the axes to use.
    df.pd.DataFrame : TYPE
        the data.

    Returns
    -------
    None

    """
    sat = sn(**ctes_dico["sat"])  # get the drawing constants
    ax.plot(df.sat, color=sat.color, label=sat.label, linewidth=2)
    ax.set_ylabel(sat.label)
    ax.set_ylim(*sat.ylims)
    ax.axhline(
        sat.goals[0],
        linewidth=1,
        linestyle="dashed",
        color=sat.color,
        alpha=sat.tracealpha,
    )


def axplot_hr(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Plot heart rate on the given axes.

    Parameters
    ----------
    ax : plt.axes
        the axes to use.
    df.pd.DataFrame : TYPE
        the data.

    Returns
    -------
    None

    """
    hrate = sn(**ctes_dico["hr"])  # get the drawing constants
    ax.plot(
        df.hr, color=hrate.color, label=hrate.label, linewidth=2, linestyle=hrate.style
    )
    ax.set_ylabel(hrate.label)
    ax.set_ylim(*hrate.ylims)


def axplot_sathr(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Plot sat_heart rate on the given axes.

    Parameters
    ----------
    ax : plt.axes
        the axes to use.
    df.pd.DataFrame : TYPE
        the data.

    Returns
    -------
    None

    """
    sathrate = sn(**ctes_dico["sathr"])  # get the drawing constants
    ax.plot(
        df.spo2Hr,
        color=sathrate.color,
        label=sathrate.label,
        linewidth=2,
        linestyle=sathrate.style,
    )
    ax.set_ylabel(sathrate.label)
    ax.set_ylim(*sathrate.ylims)
