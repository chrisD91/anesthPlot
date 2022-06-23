#!/usr/bin/env python3
"""
Created on Mon Jun 20 14:44:08 2022

@author: cdesbois

trend_axis_plot :
    a series of functions taking plt.axes and pd.dataframe as argument
    and append the plot to the provided axes
"""
from types import SimpleNamespace as sn
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_cte(key: str = "default") -> dict[str, Any]:
    """
    Build a dico containing the drawing constants.

    Parameters
    ----------
    key : str, optional (default is 'default')
        key for the display

    Returns
    -------
    cte : dict
        the 'constants' to be used to build the plot.

    """
    dicos: dict[str, dict[str, Any]] = {
        "default": dict(
            key="",
            label="",
            color="blue",
            edgecolor="blue",
            unit="",
            goals=[],
            traces=[],
            ylims=[None, None],
        ),
        "o2": dict(
            key="o2",
            label="oxygen",
            color="tab:green",
            fillalpha=0.2,
            edgecolor="tab:green",
            unit="%",
            goals=[30, 50],
            traces=[],
            ylims=[20, 80],
        ),
        "co2": dict(
            key="co2",
            label="end tidal co2",
            color="tab:blue",
            fillalpha=0.2,
            edgecolor="tab:blue",
            unit="mmHg",
            goals=[35, 45],
            traces=[],
            ylims=[30, 150],
        ),
        "iso": dict(
            key="iso",
            label="isoflurane",
            color="tab:purple",
            fillalpha=0.2,
            edgecolor="tab:purple",
            unit="%",
            goals=[1.2, 1.4],
            traces=[],
            ylims=[0, 2],
        ),
        "tvinsp": dict(
            # datex
            key="tvinsp",
            label="tidalVolume insp",
            color="tab:orange",
            fillalpha=0.2,
            style="-",
            edgecolor="tab:orange",
            unit="l",
            goals=[5, 6],
            traces=[],
            ylims=[0, 7],
            calib=187,
        ),
        "tvspont": dict(
            # taph
            key="tvspont",
            label="tidalVolume spont",
            color="tab:olive",
            fillalpha=0.2,
            style="-",
            edgecolor="tab:olive",
            unit="l",
            goals=[5, 6],
            traces=[],
            ylims=[0, 7],
        ),
        "tvcontrol": dict(
            # taph
            key="tvcontrol",
            label="tidalVolume control",
            color="tab:orange",
            fillalpha=0.2,
            style="-",
            edgecolor="tab:orange",
            unit="l",
            goals=[5, 6],
            traces=[],
            ylims=[0, 7],
        ),
        "pPeak": dict(
            # taph
            key="tvcontrol",
            label="tidalVolume control",
            color="tab:red",
            fillalpha=0.2,
            style="-",
            edgecolor="tab:red",
            unit="l",
            goals=[5, 6],
            traces=[],
            ylims=[0, 7],
        ),
        "peep": dict(
            # taph
            key="tvcontrol",
            label="tidalVolume control",
            color="tab:red",
            fillalpha=0.2,
            style="-",
            edgecolor="tab:red",
            unit="l",
            goals=[5, 6],
            traces=[],
            ylims=[0, 7],
        ),
        "pPlat": dict(
            # taph
            key="tvcontrol",
            label="tidalVolume control",
            color="tab:red",
            fillalpha=0.2,
            style="-",
            edgecolor="tab:red",
            unit="l",
            goals=[5, 6],
            traces=[],
            ylims=[0, 7],
        ),
        "settv": dict(
            # taph
            key="settv",
            label="set_tidalVolume",
            color="k",
            fillalpha=1,
            style=":",
            edgecolor="tab:orange",
            unit="l",
            goals=[5, 6],
            traces=[],
            ylims=[0, 7],
        ),
        "setpeep": dict(
            # taph
            key="setpeep",
            label="set_peep",
            color="k",
            fillalpha=1,
            style=":",
            edgecolor="tab:red",
            unit="l",
            goals=[5, 6],
            traces=[],
            ylims=[0, 7],
        ),
        "sat": dict(
            key="sat",
            label="sp02",
            color="tab:red",
            tracealpha=0.8,
            edgecolor="tab:red",
            unit="%",
            goals=[90, 100],
            traces=[],
            ylims=[60, 100],
        ),
        "sathr": dict(
            key="sathr",
            label="spO2 heart rate",
            color="tab:gray",
            edgecolor="tab:gray",
            unit="bpm",
            goals=[30, 50],
            traces=[],
            ylims=[20, 100],
        ),
        "hr": dict(
            key="hr",
            label="heart rate",
            color="tab:gray",
            edgecolor="tab:gray",
            unit="bpm",
            goals=[30, 50],
            traces=[],
            ylims=[20, 100],
        ),
        "ip1": dict(
            key="ip1",
            label="arterial pressure",
            color="tab:red",
            edgecolor="red",
            unit="mmHg",
            goals=[70, 80],
            traces=["ip1" + _ for _ in ["m", "d", "s"]],
            ylims=[30, 150],
            fillalpha=0.5,
        ),
        "ip2": dict(
            key="ip2",
            label="venous pressure",
            color="tab:blue",
            edgecolor="blue",
            unit="mmHg",
            goals=[10, 20],
            traces=["ip2" + _ for _ in ["m", "d", "s"]],
            ylims=[0, 20],
            fillalpha=0.4,
        ),
    }
    if key in dicos:
        dico = dicos[key]
        out_dico = dicos["default"] | dico
    else:
        print(f"no cts defined for {key}, used default")
        out_dico = dicos["default"]
    return out_dico


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
    defined = ["ip1", "ip2", "hr", "co2", "iso"]
    if key not in defined:
        print(f"key should be in {defined} ({key} was used)")
    cts = sn(**get_cte(key))  # get the drawing constants
    ax.set_title(cts.label, color=cts.color)
    if len(ser) > 0:
        ax.hist(
            ser.dropna(), bins=30, color=cts.color, edgecolor=cts.edgecolor, alpha=0.7
        )
        q50 = np.percentile(ser, [50])
        ax.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
        for goal in cts.goals:
            ax.axvline(goal, color="tab:grey", alpha=1)
        ax.axvspan(cts.goals[0], cts.goals[1], -0.1, 1, color="tab:grey", alpha=0.3)
        ax.set_xlabel(cts.unit, alpha=0.5)
    else:
        ax.text(
            0.5,
            0.5,
            f"no data \n ({cts.label})",
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
        cts = sn(**get_cte("tvinsp"))
        calib = cts.calib
        ax.plot(df.tvInsp / calib, color=cts.color, linewidth=2, label=cts.label)
    elif "tv_spont" in df.columns:  # taph
        cts = sn(**get_cte("tvspont"))
        ax.plot(
            df.tv_spont,
            color=cts.color,
            linewidth=1,
            linestyle="-",
            label=cts.label,
        )
        try:
            cts = sn(**get_cte("tvcontrol"))
            ax.plot(df.tv_control, color=cts.color, linewidth=2, label=cts.label)
            cts = sn(**get_cte("settv"))
            ax.plot(
                df.set_tv,
                color=cts.color,
                linewidth=1,
                linestyle=cts.style,
                label=cts.label,
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
    columns = {}
    # monitor
    if {"pPeak", "pPlat", "peep"} < set(df.columns):
        columns = {"peak": "pPeak", "peep": "peep", "plat": "pPlat"}
        # correction if spirometry tubes have been inverted (plateau measure is false)
        if df.peep.mean() > df.pPlat.mean():
            columns["peep"] = "pPlat"
            columns.pop("plat")
    # taph
    # TODO fix end of file peak pressure
    elif {"set_peep"} < set(df.columns):
        columns = {"peak": "pPeak", "peep": "peep"}
    else:
        print("no spirometry data in the recording")

    keys = list(columns.values())

    if keys:
        for key in keys:
            cts = sn(**get_cte(key))
            ax.plot(
                df[key],
                color=cts.color,
                linewidth=1,
                linestyle=cts.style,
                label=cts.label,
            )
        ax.fill_between(
            df.index,
            df[keys[0]],
            df[keys[-1]],
            color="tab:red",
            alpha=0.1,
        )
        try:
            cts = sn(**get_cte("setpeep"))
            ax.plot(
                df.set_peep,
                color=cts.color,
                linewidth=1,
                linestyle=cts.style,
                label=cts.label,
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
    ax.set_ylabel("'MinVol' & RR")
    # monitor
    monitor_items = {"minVexp", "co2RR"}
    taph_items = {"set_rr", "rr", "calc_minVol"}
    if monitor_items < set(df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        ax.plot(df.minVexp, color="tab:olive", linewidth=2, label="minVexp")
        ax.plot(df.co2RR, color="tab:blue", linewidth=2, linestyle="--", label="co2RR")
    elif taph_items < set(df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        # ax2.plot(df.minVexp, color="tab:olive", linewidth=2)
        ax.plot(df.rr, color="tab:gray", linewidth=2, linestyle="--", label="rr")
        ax.plot(df.set_rr, color="black", linewidth=1, linestyle=":", label="set_rr")
        ax.plot(
            df.calc_minVol / 10,
            color="tab:olive",
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
    co2 = sn(**get_cte("co2"))  # get the drawing constants
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
    iso = sn(**get_cte("iso"))  # get the drawing constants
    ax.set_ylabel(iso.label)
    try:
        ax.plot(df.aaExp, color=iso.color, linewidth=2, linestyle="-")
        ax.plot(df.aaInsp, color=iso.color, linewidth=2, linestyle="-")
        ax.fill_between(
            df.index,
            df.aaExp,
            df.aaInsp,
            color=iso.color,
            alpha=iso.fillalpha,
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
    oxy = sn(**get_cte("o2"))  # get the drawing constants
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
    if key in ["ip1", "ip2"]:
        press = sn(**get_cte(key))  # get the drawing constants
    else:
        txt = "key should be in [ip1, ip2]"
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
    sat = sn(**get_cte("sat"))  # get the drawing constants
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
    hrate = sn(**get_cte("hr"))  # get the drawing constants
    ax.plot(df.hr, color=hrate.color, label=hrate.label, linewidth=2, linestyle=":")
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
    sathrate = sn(**get_cte("sathr"))  # get the drawing constants
    ax.plot(
        df.spo2Hr,
        color=sathrate.color,
        label=sathrate.label,
        linewidth=2,
        linestyle=":",
    )
    ax.set_ylabel(sathrate.label)
    ax.set_ylim(*sathrate.ylims)
