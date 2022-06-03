#!/usr/bin/env python3

"""
Created on Tue Apr 19 09:08:56 2016
@author: cdesbois

collection of functions to plot the trend data

____
"""

from typing import Any, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd

from . import pfunc

# import pfunc

pfunc.update_pltparams()
# pfunc.update_pltparams()


# %%
def plot_header(
    header: dict[str, Any], param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Plot the header of the file.

    Parameters
    ----------
    descr : dict
        header of the recording.
    param : dict, optional (default is None)
        dictionary of parameters.

    Returns
    -------
    fig : plt.Figure
        plot of the header.
    """
    if not header:
        print("empty header")
        return plt.figure()
    if param is None:
        param = {"save": False, "file": ""}
    hcell = 2
    wcell = 2
    wpad = 0.2
    #    nbrows = 11
    nbcol = 2
    hpad = 0.1
    txt = []
    for key, val in header.items():
        if key == "Weight":
            val *= 10
        txt.append([key, val])
    # ['Age', 'Sex', 'Weight', 'Version', 'Date', 'Patient Name', 'Sampling Rate',
    # 'Height', 'Patient ID', 'Equipment', 'Procedure']
    fig = plt.figure(figsize=(nbcol * hcell + hpad, nbcol * wcell + wpad))
    fig.__name__ = "header"
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    table = ax.table(cellText=txt, loc="center", fontsize=18, bbox=[0, 0, 1, 1])
    # table.auto_set_font_size(False)
    table.set_fontsize(10)
    # table.set_zorder(10)
    for spineval in ax.spines.values():
        spineval.set_color("w")
        spineval.set_zorder(0)
    # annotations
    pfunc.add_baseline(fig, param)
    # pfunc.add_baseline(fig, param)
    return fig


# ------------------------------------------------------
def hist_cardio(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Mean arterial pressure histogramme using matplotlib.

    Parameters
    ----------
    data : pd.DataFrame
        the recorded trends data (keys used : 'ip1m' and 'hr),.
    param : dict, optional (default is None).
        parameters (save=bolean, 'path': path to directory).

    Returns
    -------
    plt.Figure
    """
    if param is None:
        param = {}

    keys = {"ip1m", "hr"}
    if not keys.issubset(set(datadf.columns)):
        print(f"{set(keys) - set(datadf.columns)} is/are missing in the data")
        return plt.figure()

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
    fig.__name__ = "hist_cardio"
    ax = axes[0]
    ax.set_title("arterial pressure", color="tab:red")
    ax.set_xlabel("mmHg", alpha=0.5)
    ser = pfunc.remove_outliers(datadf, "ip1m")
    if len(ser) > 0:
        ax.hist(ser.dropna(), bins=30, color="tab:red", edgecolor="red", alpha=0.7)
        q50 = np.percentile(ser, [50])
        ax.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
        for lim in [70, 80]:
            ax.axvline(lim, color="tab:grey", alpha=1)
        ax.axvspan(70, 80, -0.1, 1, color="tab:grey", alpha=0.5)
        ax.set_xlabel("mmHg", alpha=0.5)
    else:
        ax.text(
            0.5,
            0.5,
            "no data \n (arterial pressure)",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax.transAxes,
        )

    ax = axes[1]
    ax.set_title("heart rate", color="k")
    ser = pfunc.remove_outliers(datadf, "hr")
    if len(ser) > 0:
        ax.hist(
            ser,
            bins=30,
            color="tab:grey",
            edgecolor="tab:grey",
            alpha=0.8,
        )
        ax.set_xlabel("bpm", alpha=0.5)
        q50 = np.percentile(ser, [50])
        ax.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
    else:
        ax.text(
            0.5,
            0.5,
            "no data \n (heart rate)",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax.transAxes,
        )

    for ax in axes:
        # call
        pfunc.color_axis(ax, "bottom", "tab:grey")  # call
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for spine in ["top", "right", "left"]:
            ax.spines[spine].set_visible(False)
    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def hist_co2_iso(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Plot CO2 and iso histogram.

    (NB CO2 should have been converted from % to mmHg)

    Parameters
    ----------
    data : pd.DataFrame
        the recorded data.
    param : dict, optional (default is None).
        parameters.

    Returns
    -------
    matplotlib.pyplot.Figure.
    """
    if param is None:
        param = {}
    keys = {"co2exp", "aaExp"}
    if not keys.issubset(set(datadf.columns)):
        print(f"{set(keys) - set(datadf.columns)} is/are missing in the data")
        return plt.figure()
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
    fig.__name__ = "hist_co2_iso"
    ax = axes[0]
    ax.set_title("$End_{tidal}$ $CO_2$", color="tab:blue")
    # call
    ser = pfunc.remove_outliers(datadf, "co2exp")
    if len(ser) > 0:
        ax.axvspan(35, 45, color="tab:grey", alpha=0.5)
        ax.hist(ser, bins=20, color="tab:blue", edgecolor="tab:blue", alpha=0.8)
        for limit in [35, 45]:
            ax.axvline(limit, color="tab:grey", alpha=1)
        q50 = np.percentile(ser, [50])
        ax.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
        ax.set_xlabel("mmHg", alpha=0.5)
    else:
        ax.text(
            0.5,
            0.5,
            "no data \n (co2exp)",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax.transAxes,
        )
    ax = axes[1]
    ax.set_title("$End_{tidal}$ isoflurane", color="tab:purple")
    ser = pfunc.remove_outliers(datadf, "aaExp")
    if len(ser) > 1:
        ax.hist(
            ser,
            bins=20,
            color="tab:purple",
            range=(0.5, 2),
            edgecolor="tab:purple",
            alpha=0.8,
        )
        ax.set_xlabel("%", alpha=0.5)
        _, q50, _ = np.percentile(ser.dropna(), [25, 50, 75])
        ax.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
    else:
        ax.text(
            0.5,
            0.5,
            "no data \n (aaExp)",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax.transAxes,
        )

    for ax in axes:
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for spine in ["top", "right", "left"]:
            ax.spines[spine].set_visible(False)
        # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def cardiovasc(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Cardiovascular plot.

    Parameters
    ----------
    data : pd.DataFrame
        the recorded trends data, columns used :['ip1s', 'ip1m', 'ip1d', 'hr'].
    param : dict, optional (default is None)
        dict(save: boolean, path['save'], xmin, xmax, unit,
                         dtime = boolean for time display in HH:MM format)

    Returns
    -------
    matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}  # type : dict[str, Any]

    cardiac_items = {"ip1m", "ip1d", "ip1s", "hr"}
    if not cardiac_items.issubset(set(datadf.columns)):
        diff = cardiac_items - set(datadf.columns)
        print("unable to perform the cardiovacular plot")
        print(f"{diff} are not present in the data")
        return plt.figure()

    # global timeUnit
    timebase = "datetime" if param.get("dtime", False) else "eTimeMin"
    pressuredf = datadf.set_index(timebase)[list(cardiac_items)]

    fig = plt.figure()
    fig.__name__ = "cardiovascular"
    ax_l = fig.add_subplot(111)
    ax_l.plot(pressuredf.ip1m, "-", color="red", label="arterial pressure", linewidth=2)
    ax_l.fill_between(
        pressuredf.index, pressuredf.ip1d, pressuredf.ip1s, color="tab:red", alpha=0.5
    )
    pfunc.color_axis(ax_l, "left", "tab:red")  # call
    ax_l.set_ylabel("arterial Pressure", color="tab:red")
    ax_l.set_ylim(30, 150)
    ax_l.axhline(70, linewidth=1, linestyle="dashed", color="tab:red")

    ax_r = ax_l.twinx()
    ax_r.plot(pressuredf.hr, color="tab:grey", label="heart rate", linewidth=2)
    ax_r.set_ylabel("heart Rate")
    ax_r.set_ylim(20, 100)
    pfunc.color_axis(ax_r, "right", "tab:grey")  # call

    ax_l.set_xlim(datadf.iloc[0][timebase], ax_l.get_xlim()[1])
    ax_l.spines["right"].set_visible(False)
    ax_r.spines["left"].set_visible(False)
    if timebase == "datetime":
        ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax_l.set_xlabel("etime (min)")

    for ax in fig.get_axes():
        pfunc.color_axis(ax, "bottom", "tab:grey")  # call
        ax.spines["top"].set_visible(False)

    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    xlims = (param.get("xmin", None), param.get("xmax", None))
    if all(xlims):
        ax_r.set_xlim(*xlims)
    return fig


# ------------------------------------------------------
def cardiovasc_p1p2(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Cardiovascular plot with central venous pressure (p2).

    Parameters
    ----------
    data : pd.DataFrame
        the trends recorded data
            columns used :['ip1s', 'ip1m', 'ip1d', 'hr', 'ip2s', 'ip2m', 'ip2d'].
    param : dict, optional (default is None)
        dict(save: boolean, path['save'], xmin, xmax, unit,
            dtime = boolean for time display in HH:MM format).

    Returns
    -------
    TYPE
        matplotlib.pyplot.Figure.
    """
    if param is None:
        param = {}  # type : dict[str, Any]

    cardiac_items = {"ip1m", "ip1d", "ip1s", "hr", "ip2s", "ip2d", "ip2m"}
    if not cardiac_items.issubset(set(datadf.columns)):
        diff = cardiac_items - set(datadf.columns)
        print("unable to perform the cardiovac_p1p2 plot")
        print(f"{diff} are not present in the data")
        return plt.figure()

    # global timeUnit
    timebase = "datetime" if param.get("dtime", False) else "eTimeMin"
    pressuredf = datadf.set_index(timebase)[list(cardiac_items)]

    fig, axes = plt.subplots(figsize=(12, 6), ncols=1, nrows=2, sharex=True)
    fig.__name__ = "cardiovascular_p1p2"
    ax_l = axes[0]
    ax_l.set_ylabel("arterial Pressure", color="tab:red")
    pfunc.color_axis(ax_l, "left", "tab:red")
    ax_l.plot(pressuredf.ip1m, "-", color="red", label="arterial pressure", linewidth=2)
    ax_l.fill_between(
        pressuredf.index, pressuredf.ip1d, pressuredf.ip1s, color="tab:red", alpha=0.5
    )
    ax_l.set_ylim(30, 150)
    ax_l.axhline(70, linewidth=1, linestyle="dashed", color="tab:red")

    ax_r = ax_l.twinx()
    ax_r.set_ylabel("heart Rate")
    ax_r.set_ylim(20, 100)
    ax_r.plot(pressuredf.hr, color="tab:grey", label="heart rate", linewidth=2)
    pfunc.color_axis(ax_r, "right", "tab:grey")  # call

    ax = axes[1]
    ax.set_ylabel("venous Pressure", color="tab:blue")
    pfunc.color_axis(ax, "left", "tab:blue")  # call
    ax.plot(pressuredf.ip2m, "-", color="blue", label="venous pressure", linewidth=2)
    ax.fill_between(
        pressuredf.index, pressuredf.ip2d, pressuredf.ip2s, color="tab:blue", alpha=0.5
    )
    ax.set_ylim(-5, 15)
    ax.axhline(0, linewidth=1, linestyle="-", color="tab:gray")

    if timebase == "datetime":
        ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax_l.set_xlabel("etime (min)")

    for i, ax in enumerate(fig.get_axes):
        pfunc.color_axis(ax, "bottom", "tab:grey")  # call
        ax.spines["top"].set_visible(False)
        if i == 0:
            ax.spines["right"].set_visible(False)
        else:
            ax_r.spines["left"].set_visible(False)

    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()

    xlims = (param.get("xmin", None), param.get("xmin", None))
    if all(xlims):
        ax_r.set_xlim(*xlims)
    return fig


# ------------------------------------------------------
def co2iso(datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None) -> plt.Figure:
    """
    Plot CO2/iso over time.

    Parameters
    ----------
    data : pd.DataFrame
        the recorded data. Columns used :['ip1s', 'ip1m', 'ip1d', 'hr'].
    param : dict, optiona (default is None).
        dict(save: boolean, path['save'], xmin, xmax, unit,
             dtime = boolean for time display in HH:MM format)

    Returns
    -------
    matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}  # type : dict[str, Any]

    plot_items = {"co2insp", "co2exp", "aaInsp", "aaExp"}
    if not plot_items.issubset(set(datadf.columns)):
        diff = plot_items - set(datadf.columns)
        print("unable to perform the cardiovacular plot")
        print(f"{diff} are not present in the data")
        return plt.figure()

    # global timeUnit
    timebase = "datetime" if param.get("dtime", False) else "eTimeMin"
    plot_df = datadf.set_index(timebase)[list(plot_items)]

    fig = plt.figure()
    fig.__name__ = "co2iso"
    ax_l = fig.add_subplot(111)

    ax_l.set_ylabel("$CO_2$")
    # call
    pfunc.color_axis(ax_l, "left", "tab:blue")

    ax_l.plot(plot_df.co2exp, color="tab:blue")
    ax_l.plot(plot_df.co2insp, color="tab:blue")
    ax_l.fill_between(
        plot_df.index, plot_df.co2exp, plot_df.co2insp, color="tab:blue", alpha=0.5
    )
    ax_l.axhline(38, linewidth=2, linestyle="dashed", color="tab:blue")

    ax_r = ax_l.twinx()
    ax_r.set_ylabel("isoflurane")
    pfunc.color_axis(ax_r, "right", "tab:purple")
    # func(ax_r, x, etIso, inspIs, color='m', x0=38)
    ax_r.plot(plot_df.aaExp, color="tab:purple")
    ax_r.plot(plot_df.aaInsp, color="tab:purple")
    ax_r.fill_between(
        plot_df.index, plot_df.aaExp, plot_df.aaInsp, color="tab:purple", alpha=0.5
    )
    ax_r.set_ylim(0, 3)

    ax_l.set_xlim(datadf.iloc[0][timebase], ax_l.get_xlim()[1])
    ax_l.spines["right"].set_visible(False)
    ax_r.spines["left"].set_visible(False)
    if timebase == "datetime":
        ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax_l.set_xlabel("etime (min)")

    for ax in fig.get_axes():
        pfunc.color_axis(ax, "bottom", "tab:grey")  # call
        ax.spines["top"].set_visible(False)

    if param.get("xmin", None) and param.get("xmax", None):
        ax_r.set_xlim(param.get("xmin"), param.get("xmax"))

    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def co2o2(datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None) -> plt.Figure:
    """
    Respiratory plot : CO2 and Iso.

    Parameters
    ----------
    data : pd.DataFrame
        recorded trends data columns used :["co2insp", "co2exp", "o2insp", "o2exp"].
    param : dict, optional(default is None)
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format).

    Returns
    -------
    TYPE
        maplotlib.pyplot.Figure
    """
    if param is None:
        param = {}
    plot_items = {"co2insp", "co2exp", "o2insp", "o2exp"}
    if not plot_items.issubset(set(datadf.columns)):
        diff = plot_items - set(datadf.columns)
        print("unable to perform the cardiovacular plot")
        print(f"{diff} are not present in the data")
        return plt.figure()

    xmin = param.get("xmin", None)
    xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    dtime = param.get("dtime", False)

    # global timeUnit
    timebase = "datetime" if dtime else "eTimeMin"
    plot_df = datadf.set_index(timebase)[list(plot_items)]

    fig = plt.figure()
    fig.__name__ = "co2o2"
    ax_l = fig.add_subplot(111)
    ax_l.set_ylabel("$CO_2$")
    # ax_l.set_xlabel('time (' + unit +')')
    pfunc.color_axis(ax_l, "left", "tab:blue")
    ax_l.plot(plot_df.co2exp, color="tab:blue")
    ax_l.plot(plot_df.co2insp, color="tab:blue")
    ax_l.fill_between(
        plot_df.index, plot_df.co2exp, plot_df.co2insp, color="tab:blue", alpha=0.5
    )
    ax_l.axhline(38, linestyle="dashed", linewidth=2, color="tab:blue")

    ax_r = ax_l.twinx()
    ax_r.set_ylabel("$0_2$")
    pfunc.color_axis(ax_r, "right", "tab:green")
    ax_r.plot(plot_df.o2insp, color="tab:green")
    ax_r.plot(plot_df.o2exp, color="tab:green")
    ax_r.fill_between(
        plot_df.index, plot_df.o2insp, plot_df.o2exp, color="tab:green", alpha=0.5
    )
    ax_r.set_ylim(21, 80)
    ax_r.axhline(30, linestyle="dashed", linewidth=3, color="tab:olive")

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax_r.xaxis.set_major_formatter(my_fmt)
    else:
        ax_l.set_xlabel("etime (min)")

    for ax in [ax_l, ax_r]:
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


# ------------------------------------------------------
def ventil(
    datadf: pd.DataFrame, param: Optional[dict["str", Any]] = None
) -> plt.Figure:
    """
    Plot ventilation.

    Parameters
    ----------
    datadf : pd.DataFrame
        recorded trend data
        columns used : (tvInsp, pPeak, pPlat, peep, minVexp, co2RR, co2exp )
    param : dict, optional (default is None)
        param: dict(save: boolean, path['save'], xmin, xmax, unit,
                    dtime = boolean for time display in HH:MM format)

    Returns
    -------
    fig : matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}
    xlims = (param.get("xmin", None), param.get("xmax", None))
    # unit = param.get("unit", "")
    dtime = param.get("dtime", False)
    # global timeUnit
    timebase = "datetime" if dtime else "eTimeMin"
    plot_df = datadf.set_index(timebase)

    fig = plt.figure(figsize=(12, 5))
    fig.__name__ = "ventil"

    ax1 = fig.add_subplot(211)
    ax1.set_ylabel("tidal volume")
    pfunc.color_axis(ax1, "left", "tab:olive")
    ax1.yaxis.label.set_color("k")
    if "tvInsp" in plot_df.columns:  # datex
        # comparison with the taphonius data ... to be improved
        # calib = ttrend.data.tvInsp.mean() / taph_trend.data.tv.mean()
        calib = 187
        ax1.plot(plot_df.tvInsp / calib, color="tab:olive", linewidth=2, label="tvInsp")
    elif "tv" in plot_df.columns:  # taph
        ax1.plot(plot_df.tv, color="tab:olive", linewidth=1, linestyle=":", label="tv")
        try:
            ax1.plot(plot_df.tvCc, color="tab:olive", linewidth=2, label="tvCc")
        except AttributeError:
            print("no ventilation started")
    else:
        print("no spirometry data in the recording")
    ax1_r = ax1.twinx()
    ax1_r.set_ylabel("pression")
    pfunc.color_axis(ax1_r, "right", "tab:red")

    toplot = {}
    # monitor
    if {"pPeak", "pPlat", "peep"} < set(plot_df.columns):
        toplot = {"peak": "pPeak", "peep": "peep", "plat": "pPlat"}
        # correction if spirometry tubes have been inverted (plateau measure is false)
        if plot_df.peep.mean() > plot_df.pPlat.mean():
            toplot["peep"] = "pPlat"
            toplot.pop("plat")
    # taph
    # TODO fix end of file peak pressure
    elif {"pip", "peep1", "peep"} < set(plot_df.columns):
        toplot = {"peak": "pip", "peep": "peep1"}
    else:
        print("no spirometry data in the recording")

    if toplot:
        styles = ["-", "-", ":"]
        for label, style in zip(toplot, styles):
            ax1_r.plot(
                plot_df[toplot[label]],
                color="tab:red",
                linewidth=1,
                linestyle=style,
                label=label,
            )
        ax1_r.fill_between(
            plot_df.index,
            plot_df[toplot["peak"]],
            plot_df[toplot["peep"]],
            color="tab:red",
            alpha=0.1,
        )

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel("MinVol & RR")
    # monitor
    monitor_items = {"minVexp", "co2RR"}
    taph_items = {"co2RR", "rr"}
    if monitor_items < set(plot_df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        ax2.plot(plot_df.minVexp, color="tab:olive", linewidth=2, label="minVexp")
        ax2.plot(
            plot_df.co2RR, color="tab:blue", linewidth=1, linestyle="--", label="co2RR"
        )
    elif taph_items < set(plot_df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        # ax2.plot(df.minVexp, color="tab:olive", linewidth=2)
        ax2.plot(
            plot_df.co2RR, color="tab:blue", linewidth=2, linestyle="--", label="co2RR"
        )
        ax2.plot(plot_df.rr, color="black", linewidth=1, linestyle=":", label="rr")
    else:
        print("no spirometry data recorded")
    # ax2.set_xlabel('time (' + unit +')')

    ax2_r = ax2.twinx()
    ax2_r.set_ylabel("Et $CO_2$")
    pfunc.color_axis(ax2_r, "right", "tab:blue")
    try:
        ax2_r.plot(plot_df.co2exp, color="tab:blue", linewidth=2, linestyle="-")
    except KeyError:
        print("no capnometry in the recording")
    ax1_r.set_ylim(0, 50)

    for ax in [ax1, ax1_r, ax2, ax2_r]:
        if dtime:
            my_fmt = mdates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(my_fmt)
        else:
            ax.set_xlabel("etime (min)")
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(*xlims)
        # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    # if param["save"]:
    #     fig_name = "ventil" + str(param["item"])
    #     name = os.path.join(path, fig_name)
    #     pfunc.save_graph(name, ext="png", close=False, verbose=True)
    return fig


# ------------------------------------------------------
def recrut(datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None) -> plt.Figure:
    """
    Display a recrut manoeuver.

    Parameters
    ----------
    data : pd.DataFrame
        recorded trend data. Columns used : (pPeak, pPlat, peep, tvInsp)
    param : dict
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format)

    Returns
    -------
    fig : matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}
    xlims = (param.get("xmin", None), param.get("xmax", None))
    # unit = param.get("unit", "")
    dtime = param.get("dtime", False)
    df = (
        datadf.set_index("datetime").copy()
        if dtime
        else datadf.set_index("eTimeMin").copy()
    )

    fig = plt.figure()
    fig.__name__ = "recrut"
    ax1 = fig.add_subplot(111)
    # ax1.set_xlabel('time (' + unit +')')
    ax1.spines["top"].set_visible(False)
    ax1.set_ylabel("peep & Peak")
    pfunc.color_axis(ax1, "left", "tab:red")
    ax1.spines["right"].set_visible(False)
    pfunc.plot_minimeanmax_traces(
        ax1,
        df,
        traces=["peep", "pPlat", "pPeak"],
        color="tab:red",
        styles=[":"] * 3,
        widths=[1] * 3,
    )
    ax1.set_ylim(0, 50)

    ax2 = ax1.twinx()
    ax2.set_ylabel("volume")
    pfunc.color_axis(ax2, "right", "tab:olive")
    ax2.spines["left"].set_visible(False)
    ax2.yaxis.label.set_color("black")
    ax2.plot(df.tvInsp, color="tab:olive", linewidth=2)

    ax1.set_xlim(*xlims)

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax1.xaxis.set_major_formatter(my_fmt)
    else:
        ax1.set_xlabel("etime (min)")

    axes = [ax1, ax2]
    for ax in axes:
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


def ventil_cardio(
    datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None
) -> plt.Figure:
    """
    Build ventilation and cardiovascular plot.

    Parameters
    ----------
    datadf : pd.DataFrame
        trend data. Columns used : ['ip1s', 'ip1m', 'ip1d', 'hr']
    param : dict Optional (default is None)
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format).

    Returns
    -------
    fig : matplotlib.pyplot.Figure
    """
    if param is None:
        param = {}
    dtime = param.get("dtime", False)

    df = (
        datadf.set_index("datetime").copy()
        if dtime
        else datadf.set_index("eTimeMin").copy()
    )

    if "tvInsp" not in datadf.columns:
        print("no spirometry data in the recording")

    fig = plt.figure(figsize=(12, 5))
    fig.__name__ = "ventil_cardio"
    ax1 = fig.add_subplot(211)
    ax1.set_ylabel("tidal vol.")
    pfunc.color_axis(ax1, "left", "tab:olive")
    ax1.yaxis.label.set_color("k")
    ax1.plot(df.tvInsp, color="tab:olive", linewidth=2)
    ax1.spines["right"].set_visible(False)
    ax1.spines["bottom"].set_visible(False)
    ax1.tick_params("x")

    ax1_r = ax1.twinx()
    ax1_r.set_ylabel("P_resp")
    pfunc.color_axis(ax1_r, "right", "tab:red")
    pfunc.plot_minimeanmax_traces(
        ax1_r,
        df,
        traces=["peep", "pPlat", "pPeak"],
        widths=[
            1,
        ]
        * 3,
        color="tab:red",
        styles=["-", ":", "-"],
    )
    ax1_r.spines["left"].set_visible(False)
    ax1_r.spines["bottom"].set_visible(False)

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel("P_art")
    pfunc.color_axis(ax2, "left", "tab:red")
    ax2.spines["right"].set_visible(False)
    pfunc.plot_minimeanmax_traces(
        ax2,
        df,
        traces=["ip1s", "ip1m", "ip1d"],
        widths=[0, 2, 0],
        color="tab:red",
        styles=["-"] * 3,
    )

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax1.xaxis.set_major_formatter(my_fmt)
    else:
        ax1.set_xlabel("etime (min)")

    for ax in [ax1, ax1_r, ax2]:
        ax.grid()
        pfunc.color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()

    # annotations
    pfunc.add_baseline(fig, param)
    fig.tight_layout()
    return fig


def sat_hr(datadf: pd.DataFrame, param: Optional[dict[str, Any]] = None) -> plt.Figure:
    """
    Plot a sat and sat_hr over time.

    Parameters
    ----------
    taphdata : pd.DataFrame
        the taph recording
    dtime : boolean, optional (default is True)
        plot over datetime (or elapsed time)

    Returns
    -------
    fig : plt.Figure
    """
    if param is None:
        param = {}

    if "sat" not in datadf.columns:
        print("no saturation in the recording")
        return plt.figure()
    if "spo2Hr" not in datadf.columns:
        print("no satHr in the recording")
        return plt.figure()
    # global timeUnit
    dtime = param.get("dtime", False)
    if dtime:
        satdf = datadf.set_index("datetime")[["sat", "spo2Hr"]]
    else:
        satdf = datadf.set_index("eTimeMin")[["sat", "spo2Hr"]]

    fig = plt.figure()
    fig.__name__ = "sat_hr"
    axl = fig.add_subplot(111)
    axr = axl.twinx()

    for ax, trace, color, style in zip(
        [axl, axr], ["sat", "spo2Hr"], ["tab:red", "tab:grey"], ["-", ":"]
    ):

        ax.plot(
            satdf[trace],
            color=color,
            linestyle=style,
            linewidth=2,
        )
        if dtime:
            my_fmt = mdates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(my_fmt)

        ax.spines["top"].set_visible(False)
        ax.set_ylabel(trace)
        ax.yaxis.label.set_color(color)
        ax.tick_params(axis="y", colors=color)
        ax.tick_params(axis="x", colors="tab:grey")
        ax.xaxis.label.set_color("tab:grey")

    axl.set_ylim(60, 100)
    axr.set_ylim(25, 70)
    axl.axhline(90, color="tab:red", linestyle=":", alpha=0.8)
    axr.spines["left"].set_visible(False)

    # annotations
    pfunc.add_baseline(fig, param)

    fig.tight_layout()
    return fig
