#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Apr 19 09:08:56 2016
@author: cdesbois

collection of functions to plot the trend data

____
"""

import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# import utils
FONTSIZE = "medium"  # large, medium
params = {
    "font.sans-serif": ["Arial"],
    "font.size": 12,
    "legend.fontsize": FONTSIZE,
    "figure.figsize": (12, 3.1),
    "axes.labelsize": FONTSIZE,
    "axes.titlesize": FONTSIZE,
    "xtick.labelsize": FONTSIZE,
    "ytick.labelsize": FONTSIZE,
    "axes.xmargin": 0,
}
plt.rcParams.update(params)
plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces


# ------------------------------------------------------
def remove_outliers(datadf: pd.DataFrame, key: str, limits: dict = None) -> pd.Series:
    """
    remove outliers

    Parameters
    ----------
    datadf : pd.DataFrame
        the data.
    key : str
        a column label to extract the trace.
    limits : dict, optional
        {limLow: val, limHigh:val} (default is None).

    Returns
    -------
    ser : pandas.Series
        data without the outliers.
    """

    if limits is None:
        limits = {
            "co2exp": (20, 80),
            "aaExp": (0.2, 3.5),
            "ip1m": (15, 160),
            "hr": (10, 100),
        }

    if key not in datadf.columns:
        return pd.Series()

    if key not in limits:
        print(f"{key} limits are not defined")
    ser = datadf[key].copy()
    ser[ser < limits[key][0]] = np.nan
    ser[ser > limits[key][1]] = np.nan
    ser = ser.dropna()
    return ser


def color_axis(ax0: plt.Axes, spine: str = "bottom", color: str = "r"):
    """
    change the color of the label & tick & spine.

    Parameters
    ----------
    ax : plt.Axes
        the axis to work on.
    spine : str, optional (default is "bottom")
        optional location in ['bottom', 'left', 'top', 'right'] .
    color : str, optional (default is "r")
        the color to use.

    Returns
    -------
    None.

    """

    ax0.spines[spine].set_color(color)
    if spine == "bottom":
        ax0.xaxis.label.set_color(color)
        ax0.tick_params(axis="x", colors=color)
    elif spine in ["left", "right"]:
        ax0.yaxis.label.set_color(color)
        ax0.tick_params(axis="y", colors=color)


def append_loc_to_fig(ax0: plt.Axes, dt_list: list, label: str = "g") -> dict:
    """
    append vertical lines to indicate a time location 'for eg: arterial blood gas'

    Parameters
    ----------
    ax0 : plt.Axes
        the axis to add on.
    dt_list : list
        list of datetime values.
    label : str, optional (default is 'g')
        a key to add to the label.

    Returns
    -------
    dict
        a dictionary containing the locations.

    """

    num_times = mdates.date2num(dt_list)
    res = {}
    for i, num_time in enumerate(num_times):
        txt = label + str(i + 1)
        ax0.axvline(num_time, color="tab:blue")
        ax0.text(num_time, ax0.get_ylim()[1], txt, color="tab:blue")
        res[i] = num_time
    return res


def save_graph(path: str, ext: str = "png", close: bool = True, verbose: bool = True):
    """
    Save a figure from pyplot

    Parameters
    ----------
    path : str
        The path (and filename, without the extension) to save the
        figure to.
    ext : str, optional (default='png')
        The file extension. This must be supported by the active
        matplotlib backend (see matplotlib.backends module).  Most
        backends support 'png', 'pdf', 'ps', 'eps', and 'svg'.
    close : bool, optional (default=True)
        Whether to close the figure after saving.  If you want to save
        the figure multiple times (e.g., to multiple formats), you
        should NOT close it in between saves or you will have to
        re-plot it.
    verbose : bool, optional (default=True)
        Whether to print information about when and where the image
        has been saved.
    Returns
    -------
    None.

    """

    # Extract the directory and filename from the given path
    directory = os.path.split(path)[0]
    # filename = "%s.%s" % (os.path.split(path)[1], ext)
    filename = ".".join([os.path.split(path)[1], ext])
    if directory == "":
        directory = "."
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    # The final path to save to
    savepath = os.path.join(directory, filename)
    if verbose:
        print(f"Saving figure to {savepath}")
    # Actually save the figure
    plt.savefig(savepath)
    # Close it
    if close:
        plt.close()
    if verbose:
        print("Done")


# %%
def plot_header(descr: dict, param: dict = None) -> plt.Figure:
    """
    plot the header of the file.

    Parameters
    ----------
    descr : dict
        header of the recording.
    param : dict, optional (default is None)
        dictionary of parameters. .

    Returns
    -------
    fig : pyplot.Figure
        plot of the header.

    """

    if param is None:
        param = {"save": False}

    hcell = 2
    wcell = 2
    wpad = 0.2
    #    nbrows = 11
    nbcol = 2
    hpad = 0.1
    txt = []
    for key in descr.keys():
        value = descr[key]
        if key == "Weight":
            value *= 10
        txt.append([key, value])
    # ['Age', 'Sex', 'Weight', 'Version', 'Date', 'Patient Name', 'Sampling Rate',
    # 'Height', 'Patient ID', 'Equipment', 'Procedure']
    fig = plt.figure(figsize=(nbcol * hcell + hpad, nbcol * wcell + wpad))
    ax0 = fig.add_subplot(111)
    ax0.axis("off")
    ax0.xaxis.set_visible(False)
    ax0.yaxis.set_visible(False)
    table = ax0.table(cellText=txt, loc="center", fontsize=18, bbox=[0, 0, 1, 1])
    # table.auto_set_font_size(False)
    table.set_fontsize(10)
    # table.set_zorder(10)
    for spineval in ax0.spines.values():
        spineval.set_color("w")
        spineval.set_zorder(0)
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    return fig


# ------------------------------------------------------
def hist_cardio(data: pd.DataFrame, param: dict = None) -> plt.Figure:
    """
    mean arterial pressure histogramme using matplotlib.

    Parameters
    ----------
    data : pd.DataFrame
        the recorded trends data(keys used : 'ip1m' and 'hr),.
    param : dict, optional (default is None).
        parameters (save=bolean, 'path': path to directory).

    Returns
    -------
    TYPE
        matplotlib.pyplot.figure.

    """

    if param is None:
        param = {}

    if "ip1m" not in data.columns:
        print("no ip1 in the data")
        return plt.Figure()
    if "hr" not in data.columns:
        print("no hr in the data")
        return plt.Figure()
    save = param.get("save", False)

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
    axes = axes.flatten()

    ax0 = axes[0]
    ax0.set_title("arterial pressure", color="tab:red")
    ax0.set_xlabel("mmHg", alpha=0.5)
    ser = remove_outliers(data, "ip1m")
    if len(ser) > 0:
        ax0.hist(ser.dropna(), bins=30, color="tab:red", edgecolor="red", alpha=0.7)
        q50 = np.percentile(ser, [50])
        ax0.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
        for lim in [70, 80]:
            ax0.axvline(lim, color="tab:grey", alpha=1)
        ax0.axvspan(70, 80, -0.1, 1, color="tab:grey", alpha=0.5)
        ax0.set_xlabel("mmHg", alpha=0.5)
    else:
        ax0.text(
            0.5,
            0.5,
            "no data \n (arterial pressure)",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax0.transAxes,
        )

    ax1 = axes[1]
    ax1.set_title("heart rate", color="k")
    ser = remove_outliers(data, "hr")
    if len(ser) > 0:
        ax1.hist(
            ser, bins=30, color="tab:grey", edgecolor="tab:grey", alpha=0.8,
        )
        ax1.set_xlabel("bpm", alpha=0.5)
        q50 = np.percentile(ser, [50])
        ax1.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
    else:
        ax1.text(
            0.5,
            0.5,
            "no data \n (heart rate)",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax1.transAxes,
        )

    for axe in axes:
        # call
        color_axis(axe, "bottom", "tab:grey")
        axe.get_yaxis().set_visible(False)
        axe.get_xaxis().tick_bottom()
        for locs in ["top", "right", "left"]:
            axe.spines[locs].set_visible(False)
        # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    if save:
        fig_name = "hist_cardio" + str(param["item"])
        name = os.path.join(param["path"], fig_name)
        save_graph(name, ext="png", close=False, verbose=True)
        # saveGraph(name, ext='png', close=False, verbose=True)
        if param["memo"]:
            fig_memo(param["path"], fig_name)
    return fig


# ------------------------------------------------------
def plot_one_over_time(x, y, colour: str) -> plt.Figure:
    """
    plot y over x using colour

    Parameters
    ----------
    x : float
    y : float
    colour : str
        matplotlib.pyplot color

    Returns
    -------
    fig : pyplot.figure()

    """

    fig = plt.figure()
    axe = fig.add_subplot(111)
    axe.plot(x, y, color=colour)
    axe.spines["top"].set_visible(False)
    axe.spines["right"].set_visible(False)
    fig.tight_layout()
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    # fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    return fig


# ------------------------------------------------------
def hist_co2_iso(data: pd.DataFrame, param: dict = None) -> plt.Figure:
    """plot CO2 and iso histogramme
    (NB CO2 should have been converted from % to mmHg)

    Parameters
    ----------
    data : pd.DataFrame
        the recorded data.
    param : dict, optional (default is None).
        parameters.

    Returns
    -------
    TYPE
        matplotlib.pyplot.Figure.

    """

    if param is None:
        param = {}
    if "co2exp" not in data.columns:
        print("no co2exp in the data")
        return plt.figure()
    save = param.get("save", False)
    # fig = plt.figure(figsize=(15,8))
    fig = plt.figure(figsize=(12, 5))

    ax1 = fig.add_subplot(121)
    ax1.set_title("$End_{tidal}$ $CO_2$", color="tab:blue")
    # call
    ser = remove_outliers(data, "co2exp")
    if len(ser) > 0:
        ax1.axvspan(35, 45, color="tab:grey", alpha=0.5)
        ax1.hist(ser, bins=20, color="tab:blue", edgecolor="tab:blue", alpha=0.8)
        for limit in [35, 45]:
            ax1.axvline(limit, color="tab:grey", alpha=1)
        q50 = np.percentile(ser, [50])
        ax1.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
        ax1.set_xlabel("mmHg", alpha=0.5)
    else:
        ax1.text(
            0.5,
            0.5,
            "no data \n (co2exp)",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax1.transAxes,
        )

    ax2 = fig.add_subplot(122)
    ax2.set_title("$End_{tidal}$ isoflurane", color="tab:purple")
    ser = remove_outliers(data, "aaExp")
    if len(ser) > 1:
        ax2.hist(
            ser,
            bins=20,
            color="tab:purple",
            range=(0.5, 2),
            edgecolor="tab:purple",
            alpha=0.8,
        )
        ax2.set_xlabel("%", alpha=0.5)
        _, q50, _ = np.percentile(ser.dropna(), [25, 50, 75])
        ax2.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
    else:
        ax2.text(
            0.5,
            0.5,
            "no data \n (aaExp)",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax2.transAxes,
        )

    for axe in [ax1, ax2]:
        # call
        color_axis(axe, "bottom", "tab:grey")
        axe.get_yaxis().set_visible(False)
        axe.get_xaxis().tick_bottom()
        for locs in ["top", "right", "left"]:
            axe.spines[locs].set_visible(False)
        # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    if save:
        fig_name = "hist_co2_iso" + str(param["item"])
        name = os.path.join(param["path"], fig_name)
        save_graph(name, ext="png", close=False, verbose=True)
        #        saveGraph(name, ext='png', close=False, verbose=True)
        if param["memo"]:
            fig_memo(param["path"], fig_name)

    return fig


# ------------------------------------------------------
def cardiovasc(datadf: pd.DataFrame, param: dict = None) -> plt.Figure:
    """
    cardiovascular plot

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
        param = {}
    if "hr" not in datadf.columns:
        print("no pulseRate in the recording")
        return plt.figure()
    if "ip1m" not in datadf.columns:
        print("no arterial pressure in the recording")
        return plt.figure()
    # global timeUnit
    dtime = param.get("dtime", False)
    if dtime:
        pressuredf = datadf.set_index("datetime")[["ip1m", "ip1d", "ip1s", "hr"]]
    else:
        pressuredf = datadf.set_index("eTimeMin")[["ip1m", "ip1d", "ip1s", "hr"]]

    xmin = param.get("xmin", None)
    xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    save = param.get("save", False)
    file = param.get("file", "")

    fig = plt.figure()
    ax_l = fig.add_subplot(111)
    # ax_l.set_xlabel('time (' + unit +')')
    ax_l.set_ylabel("arterial Pressure", color="tab:red")
    # call
    color_axis(ax_l, "left", "tab:red")
    # for spine in ["top", "right"]:
    #     ax_l.spines[spine].set_visible(False)
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
    # call
    color_axis(ax_r, "right", "tab:grey")
    # ax_r.yaxis.label.set_color("black")
    # for spine in ["top", "left"]:
    #     ax_r.spines[spine].set_visible(False)

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax_l.xaxis.set_major_formatter(my_fmt)
        xlims = ax_l.get_xlim()
        ax_l.set_xlim(datadf.iloc[0].datetime, xlims[1])
    else:
        ax_l.set_xlabel("etime (min)")
        xlims = ax_l.get_xlim()
        ax_l.set_xlim(datadf.iloc[0].eTimeMin, xlims[1])

    for i, axe in enumerate(fig.get_axes()):
        # call
        color_axis(axe, "bottom", "tab:grey")
        # color_axis(ax, "right", "tab:grey")
        for spine in ["top"]:
            axe.spines[spine].set_visible(False)
        if i == 0:
            axe.spines["right"].set_visible(False)
        else:
            ax_r.spines["left"].set_visible(False)

    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, file, ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    if xmin and xmax:
        ax_r.set_xlim(xmin, xmax)

    if save:
        path = param["path"]
        fig_name = "cardiovasc" + str(param["item"])
        name = os.path.join(path, fig_name)
        save_graph(name, ext="png", close=False, verbose=True)
        #        saveGraph(name, ext='png', close=False, verbose=True)
        if param["memo"]:
            fig_memo(path, fig_name)

    return fig


# ------------------------------------------------------
def cardiovasc_p1p2(datadf: pd.DataFrame, param: dict = None) -> pd.DataFrame:
    """
    cardiovascular plot with central venous pressure (p2)

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
        param = {}
    if "hr" not in datadf.columns:
        print("no pulseRate in the recording")
        return plt.figure()
    if "ip1m" not in datadf.columns:
        print("no arterial pressure in the recording")
        return plt.figure()
    if "ip2m" not in datadf.columns:
        print("no venous pressure in the recording")
        return plt.figure()
    # global timeUnit
    dtime = param.get("dtime", False)
    if dtime:
        pressuredf = datadf.set_index("datetime")[
            ["ip1m", "ip1d", "ip1s", "hr", "ip2s", "ip2d", "ip2m"]
        ]
    else:
        pressuredf = datadf.set_index("eTimeMin")[
            ["ip1m", "ip1d", "ip1s", "hr", "ip2s", "ip2d", "ip2m"]
        ]
    xmin = param.get("xmin", None)
    xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    save = param.get("save", False)
    file = param.get("file", "")

    fig, axes = plt.subplots(figsize=(12, 6), ncols=1, nrows=2, sharex=True)
    axes = axes.flatten()

    ax_l = axes[0]
    # ax_l.set_xlabel('time (' + unit +')')
    ax_l.set_ylabel("arterial Pressure", color="tab:red")
    # call
    color_axis(ax_l, "left", "tab:red")
    # for spine in ["top", "right"]:
    #     ax_l.spines[spine].set_visible(False)
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
    # call
    color_axis(ax_r, "right", "tab:grey")
    # ax_r.yaxis.label.set_color("black")
    # for spine in ["top", "left"]:
    #     ax_r.spines[spine].set_visible(False)

    ax1 = axes[1]
    ax1.set_ylabel("venous Pressure", color="tab:blue")
    # call
    color_axis(ax1, "left", "tab:blue")
    # for spine in ["top", "right"]:
    #     ax_l.spines[spine].set_visible(False)
    ax1.plot(pressuredf.ip2m, "-", color="blue", label="venous pressure", linewidth=2)
    ax1.fill_between(
        pressuredf.index, pressuredf.ip2d, pressuredf.ip2s, color="tab:blue", alpha=0.5
    )
    ax1.set_ylim(-5, 15)
    ax1.axhline(0, linewidth=1, linestyle="-", color="tab:gray")

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax_l.xaxis.set_major_formatter(my_fmt)
    else:
        ax_l.set_xlabel("etime (min)")

    for i, axe in enumerate(fig.get_axes()):
        # call
        color_axis(axe, "bottom", "tab:grey")
        # color_axis(ax, "right", "tab:grey")
        for spine in ["top"]:
            axe.spines[spine].set_visible(False)
        if i == 0:
            axe.spines["right"].set_visible(False)
        else:
            ax_r.spines["left"].set_visible(False)

        # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, file, ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    if xmin and xmax:
        ax_r.set_xlim(xmin, xmax)

    if save:
        path = param["path"]
        fig_name = "cardiovasc" + str(param["item"])
        name = os.path.join(path, fig_name)
        save_graph(name, ext="png", close=False, verbose=True)
        #        saveGraph(name, ext='png', close=False, verbose=True)
        if param["memo"]:
            fig_memo(path, fig_name)

    return fig


# ------------------------------------------------------
def co2iso(data: pd.DataFrame, param: dict = None) -> plt.Figure:
    """
    plot CO2/iso over time

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
        param = {}
    if "co2exp" not in data.columns:
        print("no co2exp in the recording")
        return plt.figure()
    if "aaExp" not in data.columns:
        print("no aaExp in the recording")
        return plt.figure()

    dtime = param.get("dtime", False)
    if dtime:
        df = data.set_index("datetime")[["co2insp", "co2exp", "aaInsp", "aaExp"]]
    else:
        df = data.set_index("eTimeMin")[["co2insp", "co2exp", "aaInsp", "aaExp"]]
    # x = data.index
    # etCO2 = data.co2exp
    # inspCO2 = data.co2insp
    path = param.get("path", "")
    xmin = param.get("xmin", None)
    xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    save = param.get("save", False)
    # rr = data['CO2 RR‘]
    # inspO2 = data.o2insp
    # etO2 = data.o2exp
    # inspIso = data.aaInsp
    # etIso = data.aaExp

    fig = plt.figure()
    # fig.suptitle('$CO_2$ isoflurane')
    ax_l = fig.add_subplot(111)
    #    ax_l.set_xlabel('time (' + unit +')')

    ax_l.set_ylabel("$CO_2$")
    # call
    color_axis(ax_l, "left", "tab:blue")

    ax_l.plot(df.co2exp, color="tab:blue")
    ax_l.plot(df.co2insp, color="tab:blue")
    ax_l.fill_between(df.index, df.co2exp, df.co2insp, color="tab:blue", alpha=0.5)
    ax_l.axhline(38, linewidth=2, linestyle="dashed", color="tab:blue")

    ax_r = ax_l.twinx()
    ax_r.set_ylabel("isoflurane")
    color_axis(ax_r, "right", "tab:purple")
    # func(ax_r, x, etIso, inspIs, color='m', x0=38)
    ax_r.plot(df.aaExp, color="tab:purple")
    ax_r.plot(df.aaInsp, color="tab:purple")
    ax_r.fill_between(df.index, df.aaExp, df.aaInsp, color="tab:purple", alpha=0.5)
    ax_r.set_ylim(0, 3)

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax_r.xaxis.set_major_formatter(my_fmt)
    else:
        ax_l.set_xlabel("etime (min)")

    for ax in [ax_l, ax_r]:
        color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
        # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()

    if save:
        fig_name = "co2iso" + str(param["item"])
        name = os.path.join(path, fig_name)
        save_graph(name, ext="png", close=False, verbose=True)
        #        saveGraph(name, ext='png', close=False, verbose=True)
        if param["memo"]:
            fig_memo(path, fig_name)

    return fig


# proposition de yann pour simplifier le code (à implémenter)
def func(ax, x, y1, y2, color="tab:blue", x0=38):
    ax.plot(x, y1, color=color)
    ax.plot(x, y2, color=color)
    ax.fill_between(x, y1, y2, color=color, alpha=0.1)
    ax.axhline(x0, linewidth=1, linestyle="dashed", color=color)


# ------------------------------------------------------
def co2o2(data: pd.DataFrame, param: dict) -> plt.Figure:
    """
    respiratory plot : CO2 and Iso

    Parameters
    ----------
    data : pd.DataFrame
        recorded trends data columns used :["co2insp", "co2exp", "o2insp", "o2exp"].
    param : dict
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format).

    Returns
    -------
    TYPE
        maplotlib.pyplot.Figure

    """

    try:
        data.co2exp
    except KeyError:
        print("no CO2 records in this recording")
        return plt.figure()
    try:
        data.o2exp
    except KeyError:
        print("no O2 records in this recording")
        return plt.figure()

    path = param.get("path", "")
    xmin = param.get("xmin", None)
    xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    dtime = param.get("dtime", False)
    if dtime:
        df = data.set_index("datetime")[["co2insp", "co2exp", "o2insp", "o2exp"]]
    else:
        df = data.set_index("eTimeMin")[["co2insp", "co2exp", "o2insp", "o2exp"]]

    fig = plt.figure()
    # fig.suptitle('$CO_2$ & $O_2$ (insp & $End_{tidal}$)')
    ax_l = fig.add_subplot(111)
    ax_l.set_ylabel("$CO_2$")
    # ax_l.set_xlabel('time (' + unit +')')
    color_axis(ax_l, "left", "tab:blue")
    ax_l.plot(df.co2exp, color="tab:blue")
    ax_l.plot(df.co2insp, color="tab:blue")
    ax_l.fill_between(df.index, df.co2exp, df.co2insp, color="tab:blue", alpha=0.5)
    ax_l.axhline(38, linestyle="dashed", linewidth=2, color="tab:blue")

    ax_r = ax_l.twinx()
    ax_r.set_ylabel("$0_2$")
    color_axis(ax_r, "right", "tab:green")
    ax_r.plot(df.o2insp, color="tab:green")
    ax_r.plot(df.o2exp, color="tab:green")
    ax_r.fill_between(df.index, df.o2insp, df.o2exp, color="tab:green", alpha=0.5)
    ax_r.set_ylim(21, 80)
    ax_r.axhline(30, linestyle="dashed", linewidth=3, color="tab:olive")

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax_r.xaxis.set_major_formatter(my_fmt)
    else:
        ax_l.set_xlabel("etime (min)")

    axes = [ax_l, ax_r]
    for ax in axes:
        color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
        # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()

    if param["save"]:
        fig_name = "co2o2" + str(param["item"])
        name = os.path.join(path, fig_name)
        save_graph(name, ext="png", close=False, verbose=True)
        #        saveGraph(name, ext='png', close=False, verbose=True)
        if param["memo"]:
            fig_memo(path, fig_name)
    return fig


# ------------------------------------------------------
def ventil(data: pd.DataFrame, param=dict) -> plt.Figure:
    """
    plot ventilation

    Parameters
    ----------
    data : pd.DataFrame
        recorded trend data
        columns used : (tvInsp, pPeak, pPlat, peep, minVexp, co2RR, co2exp )
    param : dict, optional
        param: dict(save: boolean, path['save'], xmin, xmax, unit,
                    dtime = boolean for time display in HH:MM format)

    Returns
    -------
    fig : matplotlib.pyplot.Figure

    """

    path = param.get("path", "")
    xmin = param.get("xmin", None)
    xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    dtime = param.get("dtime", False)
    if dtime:
        df = data.set_index("datetime")
    else:
        df = data.set_index("eTimeMin")
    #    if 'tvInsp' not in data.columns:
    #        print('no spirometry data in the recording')
    #        return

    fig = plt.figure(figsize=(12, 5))
    # fig.suptitle('ventilation')

    ax1 = fig.add_subplot(211)
    ax1.set_ylabel("tidal volume")
    color_axis(ax1, "left", "tab:olive")
    ax1.yaxis.label.set_color("k")
    if "tvInsp" in df.columns:  # datex
        # comparison with the taphonius data ... to be improved
        # calib = ttrend.data.tvInsp.mean() / taph_trend.data.tv.mean()
        calib = 187
        ax1.plot(df.tvInsp / calib, color="tab:olive", linewidth=2, label="tvInsp")
    elif "tv" in df.columns:  # taph
        ax1.plot(df.tv, color="tab:olive", linewidth=1, linestyle=":", label="tv")
        try:
            ax1.plot(df.tvCc, color="tab:olive", linewidth=2, label="tvCc")
        except AttributeError:
            print("no ventilation started")
    else:
        print("no spirometry data in the recording")
    ax1_r = ax1.twinx()
    ax1_r.set_ylabel("pression")
    color_axis(ax1_r, "right", "tab:red")

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
    elif {"pip", "peep1", "peep"} < set(df.columns):
        toplot = {"peak": "pip", "peep": "peep1"}
    else:
        print("no spirometry data in the recording")

    if toplot:
        style = ["-", "-", ":"]
        for k, s in zip(toplot, style):
            ax1_r.plot(
                df[toplot[k]], color="tab:red", linewidth=1, linestyle=s, label=k
            )
        ax1_r.fill_between(
            df.index, df[toplot["peak"]], df[toplot["peep"]], color="tab:red", alpha=0.1
        )

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel("MinVol & RR")
    # monitor
    monitor_items = {"minVexp", "co2RR"}
    taph_items = {"co2RR", "rr"}
    if monitor_items < set(df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        ax2.plot(df.minVexp, color="tab:olive", linewidth=2, label="minVexp")
        ax2.plot(df.co2RR, color="tab:blue", linewidth=1, linestyle="--", label="co2RR")
    elif taph_items < set(df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        # ax2.plot(df.minVexp, color="tab:olive", linewidth=2)
        ax2.plot(df.co2RR, color="tab:blue", linewidth=2, linestyle="--", label="co2RR")
        ax2.plot(df.rr, color="black", linewidth=1, linestyle=":", label="rr")
    else:
        print("no spirometry data recorded")
    # ax2.set_xlabel('time (' + unit +')')

    ax2_r = ax2.twinx()
    ax2_r.set_ylabel("Et $CO_2$")
    color_axis(ax2_r, "right", "tab:blue")
    try:
        ax2_r.plot(df.co2exp, color="tab:blue", linewidth=2, linestyle="-")
    except KeyError:
        print("no capnometry in the recording")
    ax1_r.set_ylim(0, 50)
    # ax1.set_ylim(500, 2000)

    axes = [ax1, ax1_r, ax2, ax2_r]
    for ax in axes:
        if dtime:
            my_fmt = mdates.DateFormatter("%H:%M")
            ax.xaxis.set_major_formatter(my_fmt)
        else:
            ax.set_xlabel("etime (min)")
        color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.set_xlim(xmin, xmax)
        # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    if param["save"]:
        fig_name = "ventil" + str(param["item"])
        name = os.path.join(path, fig_name)
        save_graph(name, ext="png", close=False, verbose=True)
        #        saveGraph(name, ext='png', close=False, verbose=True)
        if param["memo"]:
            fig_memo(path, fig_name)
    return fig


# ------------------------------------------------------
def recrut(data: pd.DataFrame, param: dict) -> plt.Figure:
    """
    display a recrut manoeuver

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

    path = param.get("path", "")
    xmin = param.get("xmin", None)
    xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    dtime = param.get("dtime", False)
    if dtime:
        df = data.set_index("datetime").copy()
    else:
        df = data.set_index("eTimeMin").copy()

    fig = plt.figure()
    # fig.suptitle('recrutement')

    ax1 = fig.add_subplot(111)
    # ax1.set_xlabel('time (' + unit +')')
    ax1.spines["top"].set_visible(False)
    ax1.set_ylabel("peep & Peak")
    color_axis(ax1, "left", "tab:red")
    ax1.spines["right"].set_visible(False)
    ax1.plot(df.pPeak, color="tab:red", linewidth=2, linestyle="-")
    ax1.plot(df.pPlat, color="tab:red", linewidth=1, linestyle=":")
    ax1.plot(df.peep, color="tab:red", linewidth=2, linestyle="-")
    ax1.fill_between(df.index, df.peep, df.pPeak, color="tab:red", alpha=0.1)
    ax1.set_ylim(0, 50)

    ax2 = ax1.twinx()
    ax2.set_ylabel("volume")
    color_axis(ax2, "right", "tab:olive")
    ax2.spines["left"].set_visible(False)
    ax2.yaxis.label.set_color("black")
    ax2.plot(df.tvInsp, color="tab:olive", linewidth=2)

    ax1.set_xlim(xmin, xmax)
    # ax2.set_xlim(xmin, xmax)

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax1.xaxis.set_major_formatter(my_fmt)
    else:
        ax1.set_xlabel("etime (min)")

    axes = [ax1, ax2]
    for ax in axes:
        color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    if param["save"]:
        fig_name = "recrut" + str(param["item"])
        name = os.path.join(path, fig_name)
        save_graph(name, ext="png", close=False, verbose=True)
        #        saveGraph(name, ext='png', close=False, verbose=True)
        if param["memo"]:
            fig_memo(path, fig_name)
    return fig


def ventil_cardio(datadf: pd.DataFrame, param: dict) -> plt.Figure:
    """
    build ventilation and cardiovascular plot

    Parameters
    ----------
    datadf : pd.DataFrame
        trend data. Columns used : ['ip1s', 'ip1m', 'ip1d', 'hr']
    param : dict
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format).

    Returns
    -------
    fig : matplotlib.pyplot.Figure

    """

    # path = param.get("path", "")
    # xmin = param.get("xmin", None)
    # xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    dtime = param.get("dtime", False)
    if dtime:
        df = datadf.set_index("datetime").copy()
    else:
        df = datadf.set_index("eTimeMin").copy()

    if "tvInsp" not in datadf.columns:
        print("no spirometry data in the recording")

    fig = plt.figure(figsize=(12, 5))
    # fig.suptitle('ventilation & cardiovasc')

    ax1 = fig.add_subplot(211)
    ax1.set_ylabel("tidal vol.")
    color_axis(ax1, "left", "tab:olive")
    ax1.yaxis.label.set_color("k")
    ax1.plot(df.tvInsp, color="tab:olive", linewidth=2)
    ax1.spines["right"].set_visible(False)
    ax1.spines["bottom"].set_visible(False)
    ax1.tick_params("x")

    ax1_r = ax1.twinx()
    ax1_r.set_ylabel("P_resp")
    color_axis(ax1_r, "right", "tab:red")
    ax1_r.plot(df.pPeak, color="tab:red", linewidth=1, linestyle="-")
    ax1_r.plot(df.pPlat, color="tab:red", linewidth=1, linestyle=":")
    ax1_r.plot(df.peep, color="tab:red", linewidth=1, linestyle="-")
    ax1_r.fill_between(df.index, df.peep, df.pPeak, color="tab:red", alpha=0.1)
    ax1_r.spines["left"].set_visible(False)
    ax1_r.spines["bottom"].set_visible(False)

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel("P_art")
    color_axis(ax2, "left", "tab:red")
    ax2.spines["right"].set_visible(False)
    ax2.plot(df.ip1m, color="tab:red", linewidth=1, linestyle="-")
    ax2.plot(df.ip1s, color="tab:red", linewidth=0, linestyle="-")
    ax2.plot(df.ip1d, color="tab:red", linewidth=0, linestyle="-")
    ax2.fill_between(df.index, df.ip1s, df.ip1d, color="tab:red", alpha=0.2)

    # ax2.set_xlabel('time (' + unit +')')

    # ax1.set_xlim(108, 114)
    # ax2.set_ylim(35, 95)
    # ax1_r.set_ylim(5, 45)
    # ax2.set_ylim(40, 95)
    # ax2.set_ylim(40, 90)
    # ax2.set_ylim(35, 95)

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax1.xaxis.set_major_formatter(my_fmt)
    else:
        ax1.set_xlabel("etime (min)")

    axes = [ax1, ax1_r, ax2]
    for axe in axes:
        axe.grid()
        color_axis(axe, "bottom", "tab:grey")
        axe.spines["top"].set_visible(False)
        axe.get_xaxis().tick_bottom()

    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    return fig


def sat_hr(datadf: pd.DataFrame, param: dict) -> plt.Figure:
    """
    plot a sat and sat_hr over time

    Parameters
    ----------
    taphdata : pd.DataFrame
        the taph recording
    dtime : boolean, optional (default is True)
        plot over datetime (or elapsed time)

    Returns
    -------
    fig : TYPE
        DESCRIPTION.

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
    axl = fig.add_subplot(111)
    axr = axl.twinx()

    for axe, trace, color, style in zip(
        [axl, axr], ["sat", "spo2Hr"], ["tab:red", "tab:grey"], ["-", ":"]
    ):

        axe.plot(
            satdf[trace], color=color, linestyle=style, linewidth=2,
        )
        if dtime:
            my_fmt = mdates.DateFormatter("%H:%M")
            axe.xaxis.set_major_formatter(my_fmt)

        axe.spines["top"].set_visible(False)
        axe.set_ylabel(trace)
        axe.yaxis.label.set_color(color)
        axe.tick_params(axis="y", colors=color)
        axe.tick_params(axis="x", colors="tab:grey")
        axe.xaxis.label.set_color("tab:grey")

    axl.set_ylim(60, 100)
    axr.set_ylim(25, 70)
    axl.axhline(90, color="tab:red", linestyle=":", alpha=0.8)
    axr.spines["left"].set_visible(False)

    # annotations
    file = param.get("file", "")
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, file, ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()
    return fig


# ------------------------------------------------------
def save_distri(data: pd.DataFrame, path: dict):
    """
    save as 'O_..' the 4 distributions graphs for cardiovasc annd respi

    Parameters
    ----------
    data : pd.DataFrame
        trends data.
    path : dict
        dict(save: boolean, path['save'], xmin, xmax, unit,
                        dtime = boolean for time display in HH:MM format)..

    Returns
    -------
    None.

    """

    #    bpgas(data).savefig((path["sFig"] + "O_bpgas.png"), bbox_inches="tight")
    hist_co2_iso(data).savefig(
        (path["sFig"] + "O_hist_co2_iso.png"), bbox_inches="tight"
    )
    #   bppa(data).savefig((path["sFig"] + "O_bppa.png"), bbox_inches="tight")
    hist_cardio(data).savefig((path["sFig"] + "O_hist_cardio.png"), bbox_inches="tight")


def fig_memo(apath: str, fig_name: str):
    """
    append latex frame command in a txt file inside the fig folder
    create the file if it doesn't exist

    Parameters
    ----------
    apath : str
        dirname to export to.
    fig_name : str
        figure short name.

    Returns
    -------
    None.

    """

    include_text = (
        "\\begin{frame}{fileName}\n\t\\includegraphics[width = \\textwidth]{bg/"
        + fig_name
        + "} \n\end{frame} \n %----------------- \n \\n"
    )

    fig_insert = os.path.join(apath, "figIncl.txt")
    with open(fig_insert, "a", encoding="utf-8") as file:
        file.write(include_text + "\n")
        file.close()
