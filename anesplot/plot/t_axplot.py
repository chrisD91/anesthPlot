#!/usr/bin/env python3
"""
Created on Mon Jun 20 14:44:08 2022

@author: cdesbois

trend_axis_plot :
    a series of functions taking plt.axes and pd.dataframe as argument
    and append the plot to the provided axes
"""

import matplotlib.pyplot as plt
import pandas as pd

# from . import pfunc


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
        calib = 187
        ax.plot(df.tvInsp / calib, color="tab:orange", linewidth=2, label="tvInsp")
    elif "tv_spont" in df.columns:  # taph
        ax.plot(
            df.tv_spont,
            color="tab:olive",
            linewidth=1,
            linestyle="-",
            label="tv_spont",
        )
        try:
            ax.plot(df.tv_control, color="tab:orange", linewidth=2, label="tv_control")
            ax.plot(
                df.set_tv,
                color="k",
                linewidth=1,
                linestyle=":",
                label="set_tv",
            )
        except AttributeError:
            print("no ventilation started")
    else:
        print("no spirometry data in the recording")
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
    ax.set_ylabel("pression")
    toplot = {}
    # monitor
    if {"pPeak", "pPlat", "peep"} < set(df.columns):
        toplot = {"peak": "pPeak", "peep": "peep", "plat": "pPlat"}
        # correction if spirometry tubes have been inverted (plateau measure is false)
        if df.peep.mean() > df.pPlat.mean():
            toplot["peep"] = "pPlat"
            toplot.pop("plat")
    # taph
    # TODO fix end of file peak pressure
    elif {"set_peep"} < set(df.columns):
        toplot = {"peak": "pPeak", "peep": "peep"}
    else:
        print("no spirometry data in the recording")

    if toplot:
        styles = ["-", "-", ":"]
        for label, style in zip(toplot, styles):
            ax.plot(
                df[toplot[label]],
                color="tab:red",
                linewidth=1,
                linestyle=style,
                label=label,
            )
        ax.fill_between(
            df.index,
            df[toplot["peak"]],
            df[toplot["peep"]],
            color="tab:red",
            alpha=0.1,
        )
        try:
            ax.plot(
                df.set_peep,
                color="k",
                linewidth=1,
                linestyle=":",
                label="set_peep",
            )
        except AttributeError:
            print("not on the taph")


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
    ax.set_ylabel("MinVol & RR")
    # monitor
    monitor_items = {"minVexp", "co2RR"}
    taph_items = {"set_rr", "rr", "calc_minVol"}
    if monitor_items < set(df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        ax.plot(df.minVexp, color="tab:olive", linewidth=2, label="minVexp")
        ax.plot(df.co2RR, color="tab:blue", linewidth=1, linestyle="--", label="co2RR")
    elif taph_items < set(df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        # ax2.plot(df.minVexp, color="tab:olive", linewidth=2)
        ax.plot(df.rr, color="tab:gray", linewidth=2, linestyle="--", label="rr")
        ax.plot(df.set_rr, color="black", linewidth=1, linestyle=":", label="set_rr")
        ax.plot(
            df.calc_minVol,
            color="k",
            linewidth=1,
            linestyle=":",
            label="calc_minV",
        )
    else:
        print("no spirometry data recorded")
    # ax2.set_xlabel('time (' + unit +')')


def axplot_etco2(ax: plt.axes, df: pd.DataFrame) -> None:
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
    ax.set_ylabel("Et $CO_2$")
    try:
        ax.plot(df.co2exp, color="tab:blue", linewidth=2, linestyle="-")
        ax.plot(df.co2insp, color="tab:blue", linewidth=1, linestyle="-")
        ax.fill_between(
            df.index,
            df.co2exp,
            df.co2insp,
            color="tab:blue",
            alpha=0.1,
        )
    # except KeyError:
    #     print("")
    except AttributeError:
        print("no capnometry in the recording")
        ax.text(
            0.5,
            0.5,
            "no capnometry",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
        )


def axplot_iso(ax: plt.axes, df: pd.DataFrame) -> None:
    """
    Plot iso on the provided axes.

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
    ax.set_ylabel("isoflurane")
    try:
        ax.plot(df.aaExp, color="tab:purple", linewidth=2, linestyle="-")
        ax.plot(df.aaInsp, color="tab:purple", linewidth=2, linestyle="-")
        ax.fill_between(
            df.index,
            df.aaExp,
            df.aaInsp,
            color="tab:blue",
            alpha=0.2,
        )
        ax.set_ylim(0, 3)
    # except KeyError:
    #     print("")
    except AttributeError:
        print("no anesthetic agent in the recording")
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
    ax.set_ylabel("oxygen")
    try:
        ax.plot(df.o2insp, color="tab:green", linewidth=2, linestyle="-")
        ax.plot(df.o2exp, color="tab:green", linewidth=2, linestyle="-")
        ax.fill_between(
            df.index,
            df.o2insp,
            df.o2exp,
            color="tab:green",
            alpha=0.2,
        )
        ax.set_ylim(21, 80)
        ax.axhline(30, linestyle="dashed", linewidth=3, color="tab:olive")
        ax.set_ylim(0, 3)
    # except KeyError:
    #     print("")
    except AttributeError:
        print("no oxygen measure in the recording")
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
    if key == "ip1":
        label = "arterial pressure"
        color = "tab:red"
        mini = 70
        traces = ["ip1" + _ for _ in ["m", "d", "s"]]
        ylims = [30, 150]

    elif key == "ip2":
        label = "venuous pressure"
        color = "tab:blue"
        mini = 10
        traces = ["ip2" + _ for _ in ["m", "d", "s"]]
        ylims = [0, 20]
    else:
        txt = "key should be in [ip1, ip2]"
        ax.text(0.5, 0.5, txt)
        return

    ax.plot(df[traces[0]], color=color, label=label, linewidth=2)
    ax.fill_between(df.index, df[traces[1]], df[traces[2]], color=color, alpha=0.5)
    ax.set_ylim(*ylims)
    ax.axhline(mini, linewidth=1, linestyle="dashed", color=color)


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
    ax.plot(df.hr, color="tab:grey", label="heart rate", linewidth=2)
    ax.set_ylabel("heart Rate")
    ax.set_ylim(20, 100)