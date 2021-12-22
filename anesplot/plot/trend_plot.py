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

# import utils
font_size = "medium"  # large, medium
params = {
    "font.sans-serif": ["Arial"],
    "font.size": 12,
    "legend.fontsize": font_size,
    "figure.figsize": (12, 3.1),
    "axes.labelsize": font_size,
    "axes.titlesize": font_size,
    "xtick.labelsize": font_size,
    "ytick.labelsize": font_size,
    "axes.xmargin": 0,
}
plt.rcParams.update(params)
plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces


# ////////////////////////////////////////////////////////////////
def remove_outliers(df, key, limits=None):
    """remove outliers
    input:
        df : pandas.Dataframe
        key : a column label
        limits : dictionary of key:(limLow, limHigh)
    output:
        pandas.series without the outliers
    """
    if limits is None:
        limits = {
            "co2exp": (20, 80),
            "aaExp": (0.2, 3.5),
            "ip1m": (15, 160),
            "hr": (10, 100),
        }
    if key not in limits:
        print("{} limits are not defined".format(key))
    ser = df[key].copy()
    ser[ser < limits[key][0]] = np.nan
    ser[ser > limits[key][1]] = np.nan
    ser = ser.dropna()
    return ser


def color_axis(ax, spine="bottom", color="r"):
    """change the color of the label & tick & spine.

    :param matplotlib.pyplot.axis ax: the axis
    :param str spine: optional location in ['bottom', 'left', 'top', 'right']
    :param str colors: optional color
    """
    ax.spines[spine].set_color(color)
    if spine == "bottom":
        ax.xaxis.label.set_color(color)
        ax.tick_params(axis="x", colors=color)
    elif spine in ["left", "right"]:
        ax.yaxis.label.set_color(color)
        ax.tick_params(axis="y", colors=color)


def append_loc_to_fig(ax, dt_list, label="g"):
    """append vertical lines to indicate a location 'eg: arterial blood gas'

    :param matplotlib.pyplot.axis ax: the axis
    :param [datetime] dt_list: list of datetime values
    :param str label: a key to add to the label (default is 'g')

    :returns res: a dictionary containing the locations
    :rtype: dict
    """
    num_times = mdates.date2num(dt_list)
    res = {}
    for i, num_time in enumerate(num_times):
        st = label + str(i + 1)
        ax.axvline(num_time, color="tab:blue")
        ax.text(num_time, ax.get_ylim()[1], st, color="tab:blue")
        res[i] = num_time
    return res


def save_graph(path, ext="png", close=True, verbose=True):
    """Save a figure from pyplot.
    Parameters
    ----------
    path : string
        The path (and filename, without the extension) to save the
        figure to.
    ext : string (default='png')
        The file extension. This must be supported by the active
        matplotlib backend (see matplotlib.backends module).  Most
        backends support 'png', 'pdf', 'ps', 'eps', and 'svg'.
    close : boolean (default=True)
        Whether to close the figure after saving.  If you want to save
        the figure multiple times (e.g., to multiple formats), you
        should NOT close it in between saves or you will have to
        re-plot it.
    verbose : boolean (default=True)
        Whether to print information about when and where the image
        has been saved.
    """
    # Extract the directory and filename from the given path
    directory = os.path.split(path)[0]
    filename = "%s.%s" % (os.path.split(path)[1], ext)
    if directory == "":
        directory = "."
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    # The final path to save to
    savepath = os.path.join(directory, filename)
    if verbose:
        print("Saving figure to '%s'..." % savepath),
    # Actually save the figure
    plt.savefig(savepath)
    # Close it
    if close:
        plt.close()
    if verbose:
        print("Done")


#%%
def plot_header(descr, param=None):
    """plot the header of the file.

    :param dict descr: header of the recording
    :param dict param: dictionary of parameters

    :returns fig: plot of the header
    :rtype: pyplot.figure

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
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    table = ax.table(cellText=txt, loc="center", fontsize=18, bbox=[0, 0, 1, 1])
    # table.auto_set_font_size(False)
    table.set_fontsize(10)
    # table.set_zorder(10)
    for sp in ax.spines.values():
        sp.set_color("w")
        sp.set_zorder(0)
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    return fig


def hist_cardio(data, param=None):
    """mean arterial pressure histogramme using matplotlib.

    :param pandas.DataFrame data: the recorded trends data
        (keys used : 'ip1m' and 'hr),
    :param dict param: parameters
        (save=bolean, 'path': path to directory)

    :returns fig: matplotlib.pyplot.figure
    """
    if param is None:
        param = {}

    if "ip1m" not in data.columns:
        print("no ip1 in the data")
        return
    if "hr" not in data.columns:
        print("no hr in the data")
        return
    save = param.get("save", False)

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
    axes = axes.flatten()

    ax = axes[0]
    ax.set_title("arterial pressure", color="tab:red")
    ax.set_xlabel("mmHg", alpha=0.5)
    ser = remove_outliers(data, "ip1m")
    ax.hist(ser.dropna(), bins=30, color="tab:red", edgecolor="red", alpha=0.7)
    q25, q50, q75 = np.percentile(ser, [25, 50, 75])
    ax.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
    for lim in [70, 80]:
        ax.axvline(lim, color="tab:grey", alpha=1)
    ax.axvspan(70, 80, -0.1, 1, color="tab:grey", alpha=0.5)
    ax.set_xlabel("mmHg", alpha=0.5)

    ax = axes[1]
    ser = remove_outliers(data, "hr")
    ax.hist(
        ser,
        bins=30,
        color="tab:grey",
        edgecolor="tab:grey",
        alpha=0.8,
    )
    ax.set_title("heart rate", color="k")
    ax.set_xlabel("bpm", alpha=0.5)
    q25, q50, q75 = np.percentile(ser, [25, 50, 75])
    ax.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)

    for ax in axes:
        # call
        color_axis(ax, "bottom", "tab:grey")
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for locs in ["top", "right", "left"]:
            ax.spines[locs].set_visible(False)
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


# ---------------------------------------------------------------------------------------------------
def plot_one_over_time(x, y, colour):
    """plot y over x using colour"""

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, color=colour)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    # fig.text(0.01, 0.01, param['file'], ha='left', va='bottom', alpha=0.4)
    return fig


# ----------------------------------------------------------------------------------------
def hist_co2_iso(data, param=None):
    """CO2 and iso histogramme
    (NB CO2 should have been converted from % to mmHg)

    :param pandas.Dataframe data: the trends recorded data
    :param dict param: dictionary of parameters

    :returns: fig pyplot.figure
    """
    if param is None:
        param = {}
    if "co2exp" not in data.columns:
        print("no co2exp in the data")
        return
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
        q25, q50, q75 = np.percentile(ser, [25, 50, 75])
        ax1.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
        ax1.set_xlabel("mmHg", alpha=0.5)
    else:
        ax1.text(
            0.5,
            0.5,
            "no data",
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
        q25, q50, q75 = np.percentile(ser.dropna(), [25, 50, 75])
        ax2.axvline(q50, linestyle="dashed", linewidth=2, color="k", alpha=0.8)
    else:
        ax2.text(
            0.5,
            0.5,
            "no data",
            horizontalalignment="center",
            fontsize="x-large",
            verticalalignment="center",
            transform=ax2.transAxes,
        )

    for ax in [ax1, ax2]:
        # call
        color_axis(ax, "bottom", "tab:grey")
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().tick_bottom()
        for locs in ["top", "right", "left"]:
            ax.spines[locs].set_visible(False)
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


# ---------------------------------------------------------------------------------------------------
def cardiovasc(data, param=None):
    """cardiovascular plot

    :param pandas.Dataframe data: the recorded trends data
        keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
    :param dict param: dict(save: boolean, path['save'], xmin, xmax, unit,
                     dtime = boolean for time display in HH:MM format)

    :returns: fig= pyplot.figure
    """
    if param is None:
        param = {}
    if "hr" not in data.columns:
        print("no pulseRate in the recording")
        return
    if "ip1m" not in data.columns:
        print("no arterial pressure in the recording")
        return
    # global timeUnit
    dtime = param.get("dtime", False)
    if dtime:
        df = data.set_index("datetime")[["ip1m", "ip1d", "ip1s", "hr"]]
    else:
        df = data.set_index("eTimeMin")[["ip1m", "ip1d", "ip1s", "hr"]]

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
    ax_l.plot(df.ip1m, "-", color="red", label="arterial pressure", linewidth=2)
    ax_l.fill_between(df.index, df.ip1d, df.ip1s, color="tab:red", alpha=0.5)
    ax_l.set_ylim(30, 150)
    ax_l.axhline(70, linewidth=1, linestyle="dashed", color="tab:red")

    ax_r = ax_l.twinx()
    ax_r.set_ylabel("heart Rate")
    ax_r.set_ylim(20, 100)
    ax_r.plot(df.hr, color="tab:grey", label="heart rate", linewidth=2)
    # call
    color_axis(ax_r, "right", "tab:grey")
    # ax_r.yaxis.label.set_color("black")
    # for spine in ["top", "left"]:
    #     ax_r.spines[spine].set_visible(False)

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax_l.xaxis.set_major_formatter(my_fmt)
    else:
        ax_l.set_xlabel("etime (min)")

    for i, ax in enumerate(fig.get_axes()):
        # call
        color_axis(ax, "bottom", "tab:grey")
        # color_axis(ax, "right", "tab:grey")
        for spine in ["top"]:
            ax.spines[spine].set_visible(False)
        if i == 0:
            ax.spines["right"].set_visible(False)
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


# ---------------------------------------------------------------------------------------------------
def cardiovasc_p1p2(data, param=None):
    """cardiovascular plot with central venous pressure (p2)

    :param pandas.Dataframe data: the trends recorded data
        keys used :['ip1s', 'ip1m', 'ip1d', 'hr', 'ip2s', 'ip2m', 'ip2d']
    :param dict param: dict(save: boolean, path['save'], xmin, xmax, unit,
        dtime = boolean for time display in HH:MM format)

    :returns: fig= pyplot.figure
    """
    if param is None:
        param = {}
    if "hr" not in data.columns:
        print("no pulseRate in the recording")
        return
    if "ip1m" not in data.columns:
        print("no arterial pressure in the recording")
        return
    if "ip2m" not in data.columns:
        print("no venous pressure in the recording")
        return
    # global timeUnit
    dtime = param.get("dtime", False)
    if dtime:
        df = data.set_index("datetime")[
            ["ip1m", "ip1d", "ip1s", "hr", "ip2s", "ip2d", "ip2m"]
        ]
    else:
        df = data.set_index("eTimeMin")[
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
    ax_l.plot(df.ip1m, "-", color="red", label="arterial pressure", linewidth=2)
    ax_l.fill_between(df.index, df.ip1d, df.ip1s, color="tab:red", alpha=0.5)
    ax_l.set_ylim(30, 150)
    ax_l.axhline(70, linewidth=1, linestyle="dashed", color="tab:red")

    ax_r = ax_l.twinx()
    ax_r.set_ylabel("heart Rate")
    ax_r.set_ylim(20, 100)
    ax_r.plot(df.hr, color="tab:grey", label="heart rate", linewidth=2)
    # call
    color_axis(ax_r, "right", "tab:grey")
    # ax_r.yaxis.label.set_color("black")
    # for spine in ["top", "left"]:
    #     ax_r.spines[spine].set_visible(False)

    ax = axes[1]
    ax.set_ylabel("venous Pressure", color="tab:blue")
    # call
    color_axis(ax, "left", "tab:blue")
    # for spine in ["top", "right"]:
    #     ax_l.spines[spine].set_visible(False)
    ax.plot(df.ip2m, "-", color="blue", label="venous pressure", linewidth=2)
    ax.fill_between(df.index, df.ip2d, df.ip2s, color="tab:blue", alpha=0.5)
    ax.set_ylim(-5, 15)
    ax.axhline(0, linewidth=1, linestyle="-", color="tab:gray")

    if dtime:
        my_fmt = mdates.DateFormatter("%H:%M")
        ax_l.xaxis.set_major_formatter(my_fmt)
    else:
        ax_l.set_xlabel("etime (min)")

    for i, ax in enumerate(fig.get_axes()):
        # call
        color_axis(ax, "bottom", "tab:grey")
        # color_axis(ax, "right", "tab:grey")
        for spine in ["top"]:
            ax.spines[spine].set_visible(False)
        if i == 0:
            ax.spines["right"].set_visible(False)
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


# ---------------------------------------------------------------------------------------------------
def co2iso(data, param=None):
    """anesth plot (CO2/iso)

    :param pandas.Dataframe data: the recorded data
        keys used :['ip1s', 'ip1m', 'ip1d', 'hr']

    :param dictionary param: dict(save: boolean, path['save'], xmin, xmax, unit,
                                   dtime = boolean for time display in HH:MM format)

    :returns fig= pyplot.figure
    """
    if param is None:
        param = {}
    if "co2exp" not in data.columns:
        print("no co2exp in the recording")
        return
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


# ---------------------------------------------------------------------------
def co2o2(data, param):
    """respiratory plot (CO2 and Iso)

    :param pandas.DataFrame data: recorded trends data
        keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
    :param dict param: dict(save: boolean, path['save'], xmin, xmax, unit,
                    dtime = boolean for time display in HH:MM format)

    :returns: fig= pyplot.figure
    """

    try:
        data.co2exp
    except KeyError:
        print("no CO2 records in this recording")
        return
    try:
        data.o2exp
    except KeyError:
        print("no O2 records in this recording")
        return

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


# ---------------------------------------------------------------------------------------
def ventil(data, param):
    """plot ventilation parameters
    (.tvInsp, .pPeak, .pPlat, .peep, .minVexp, .co2RR, .co2exp )

    :param pandas.DataFrame data: recorded data,
        keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
    :param dict param: dict(save: boolean, path['save'], xmin, xmax, unit,
                dtime = boolean for time display in HH:MM format)

    :return: fig= pyplot.figure
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
        ax1.plot(df.tvInsp, color="tab:olive", linewidth=2, label="tvInsp")
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

    monitor_items = {"pPlat", "pPlat", "peep"}
    taph_items = {"pip", "peep1", "peep"}
    if monitor_items < set(df.columns):
        # if ("pPlat" in df.columns) and ("pPlat" in df.columns) and ("peep" in df.columns):
        ax1_r.plot(df.pPeak, color="tab:red", linewidth=1, linestyle="-", label="pPeak")
        ax1_r.plot(df.pPlat, color="tab:red", linewidth=1, linestyle=":", label="pPlat")
        ax1_r.plot(df.peep, color="tab:red", linewidth=1, linestyle="-", label="peep")
        ax1_r.fill_between(df.index, df.peep, df.pPeak, color="tab:red", alpha=0.1)
    elif taph_items < set(df.columns):
        ax1_r.plot(df.pip, color="tab:red", linewidth=1, linestyle="-", label="pip")
        ax1_r.plot(df.peep, color="tab:red", linewidth=1, linestyle=":", label="peep")
        ax1_r.plot(df.peep1, color="tab:red", linewidth=1, linestyle="-", label="peep1")
        ax1_r.fill_between(df.index, df.peep, df.pip, color="tab:red", alpha=0.1)
    else:
        print("no spirometry data in the recording")
    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.set_ylabel("MinVol & RR")
    # monitor
    monitor_items = {"minVexp", "co2RR"}
    taph_items = {"co2RR", "rr"}
    if monitor_items < set(df.columns):
        # if ("minVexp" in df.columns) and ("co2RR" in df.columns):
        ax2.plot(df.minVexp, color="tab:olive", linewidth=2, label="minVexp")
        ax2.plot(df.co2RR, color="tab:blue", linewidth=1, linestyle="--", label="co2RR")
    # TODO add taphonius minute volume
    # "minVol", "mv1", other scale
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


# ------------------------------------------------------------------------
def recrut(data, param):
    """display a recrut manoeuver (.pPeak, .pPlat, .peep, .tvInsp)

    :param pandas.DataFrame data: recorded data
        keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
    :param dict param: dict(save: boolean, path['save'], xmin, xmax, unit,
                    dtime = boolean for time display in HH:MM format)

    :returns fig= pyplot.figure
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


def ventil_cardio(data, param):
    """build ventilation and cardiovascular plot

    :param pandas.DataFrame data: teh recorded trends data
        keys used :['ip1s', 'ip1m', 'ip1d', 'hr']
    :param dict param: dict(save: boolean, path['save'], xmin, xmax, unit,
                    dtime = boolean for time display in HH:MM format)

    :returns: fig= pyplot.figure
    """
    path = param.get("path", "")
    # xmin = param.get("xmin", None)
    # xmax = param.get("xmax", None)
    # unit = param.get("unit", "")
    dtime = param.get("dtime", False)
    if dtime:
        df = data.set_index("datetime").copy()
    else:
        df = data.set_index("eTimeMin").copy()

    if "tvInsp" not in data.columns:
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
    for ax in axes:
        ax.grid()
        color_axis(ax, "bottom", "tab:grey")
        ax.spines["top"].set_visible(False)
        ax.get_xaxis().tick_bottom()

    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------------------
def save_distri(data, path):
    """save as 'O_..' the 4 distributions graphs for cardiovasc annd respi"""

    #    bpgas(data).savefig((path["sFig"] + "O_bpgas.png"), bbox_inches="tight")
    hist_co2_iso(data).savefig(
        (path["sFig"] + "O_hist_co2_iso.png"), bbox_inches="tight"
    )
    #   bppa(data).savefig((path["sFig"] + "O_bppa.png"), bbox_inches="tight")
    hist_cardio(data).savefig((path["sFig"] + "O_hist_cardio.png"), bbox_inches="tight")


def fig_memo(path, fig_name):
    """
    append latex citation commands in a txt file inside the fig folder
    create the file iif it doesn't exist
    """
    include_text = (
        "\\begin{frame}{fileName}\n\t\\includegraphics[width = \\textwidth]{bg/"
        + fig_name
        + "} \n\end{frame} \n %----------------- \n \\n"
    )

    fig_insert = os.path.join(path, "figIncl.txt")
    with open(fig_insert, "a") as file:
        file.write(include_text + "\n")
        file.close()
