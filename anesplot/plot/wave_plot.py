# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 09:08:56 2016

@author: cdesbois
"""

import os
from bisect import bisect
from math import floor, ceil
from typing import Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import animation
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

FONT_SIZE = "medium"  # large, medium
fig_params = {
    "font.sans-serif": ["Arial"],
    "font.size": 12,
    "legend.fontsize": FONT_SIZE,
    "figure.figsize": (12, 3.1),
    "axes.labelsize": FONT_SIZE,
    "axes.titlesize": FONT_SIZE,
    "xtick.labelsize": FONT_SIZE,
    "ytick.labelsize": FONT_SIZE,
    "axes.xmargin": 0,
}
plt.rcParams.update(fig_params)
plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces


def color_axis(ax: plt.Axes, spine: str = "bottom", color: str = "r"):
    """
    change the color of the label & tick & spine.

    Parameters
    ----------
    ax : plt.Axes
        the axis to work on.
    spine : str, optional (default is "bottom")
        location in ['bottom', 'left', 'top', 'right']
    color : str, optional (default is "r")
        color to use

    Returns
    -------
    None.

    """
    ax.spines[spine].set_color(color)
    if spine == "bottom":
        ax.xaxis.label.set_color(color)
        ax.tick_params(axis="x", colors=color)
    elif spine in ["left", "right"]:
        ax.yaxis.label.set_color(color)
        ax.tick_params(axis="y", colors=color)


# %%
def plot_wave(datadf: pd.DataFrame, keys: list, param: dict) -> plt.Figure:
    """
    plot the waves recorded (from as5)
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

    """

    # test wave in dataframe
    if not set(keys) < set(datadf.columns):
        print(f"the traces {set(keys) - set(datadf.columns)} is not in the data")
        return plt.figure()
    if len(keys) not in [1, 2]:
        print(f"only one or two keys are allowed ({keys} were used)")
        return plt.figure()
    # default plotting labels
    names = dict(
        wekg=["ECG", "tab:blue", "mVolt"],
        wco2=["expired CO2", "tab:blue", "mmHg"],
        wawp=["airway pressure", "tab:red", "cmH2O"],
        wflow=["expiratory flow", "tab:green", "flow"],
        wap=["arterial pressure", "tab:red", "mmHg"],
        wvp=["venous pressure", "tab:blue", "mmHg"],
        ihr=["instanous heart rate", "tab:blue", "bpm"],
    )
    # colors for missing keys
    if set(keys) - names.keys():
        for key in set(keys) - names.keys():
            names[key] = [key, "tab:blue", ""]
            if key.startswith("rr"):
                names[key] = [key, "tab:green", ""]
    # time scaling (index value)
    mini = param.get("mini", datadf.index[0])
    maxi = param.get("maxi", datadf.index[-1])
    if not datadf.index[0] <= mini <= datadf.index[-1]:
        print("mini value not in range, replaced by start time value")
        mini = datadf.index[0]
    if not datadf.index[0] <= maxi <= datadf.index[-1]:
        print("maxi value not in range, replaced by end time value")
        maxi = datadf.index[-1]
    # datetime or elapsed time sec
    dtime = param.get("dtime", False)
    if dtime and "datetime" not in datadf.columns:
        print("no datetime values, changed dtime to False")
        dtime = False
    cols = list(set(keys))
    if dtime:
        cols.insert(0, "datetime")
        plotdf = datadf[cols].copy()
        plotdf = plotdf.iloc[mini:maxi].set_index("datetime")
    else:
        cols.insert(0, "sec")
        plotdf = datadf[cols].copy()
        plotdf = plotdf.iloc[mini:maxi].set_index("sec")
    lines = []
    # one wave
    if len(keys) == 1:
        for key in keys:
            fig = plt.figure(figsize=(12, 4))
            title = names[key][0]
            fig.suptitle(title, color="tab:grey")
            ax = fig.add_subplot(111)
            ax.margins(0)
            color = names[key][1]
            (line,) = ax.plot(plotdf[key], color=color, alpha=0.6)
            lines.append(line)
            ax.axhline(0, alpha=0.3)
            ax.set_ylabel(names[key][2])
            if dtime:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            if key == "wco2":
                ax.axhlines(38, linestyle="dashed", alpha=0.5)
                ax.set_ylim(0, 50)
            if key == "wekg":
                ax.grid()
            if key == "wap":
                ax.axhline(70, linestyle="dashed", alpha=0.5)
            if key == "wflow":
                # ax.fill_between(set.index, set[key], where = set[key] > 0,
                #           color = names[key][1], alpha=0.4)
                pass
        for spine in ["left", "bottom"]:
            color_axis(ax, spine=spine, color="tab:grey")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        if not dtime:
            ax.set_xlabel("time (sec)")
    # two waves
    elif len(keys) == 2:
        fig = plt.figure(figsize=(10, 4))
        ax_list = []
        ax0 = fig.add_subplot(2, 1, 1)
        ax_list.append(ax0)
        ax_list.append(fig.add_subplot(2, 1, 2, sharex=ax0))
        for i, key in enumerate(keys):
            ax = ax_list[i]
            ax.margins(0)
            # ax.set_title(names[key][0])
            ax.set_ylabel(names[key][0], size="small")
            color = names[key][1]
            (line,) = ax.plot(plotdf[key], color=color, alpha=0.6)
            lines.append(line)
            lims = ax.get_xlim()
            ax.hlines(0, lims[0], lims[1], alpha=0.3)
            # ax.set_ylabel(names[key][2])
            if key == "wco2":
                ax.hlines(
                    38,
                    lims[0],
                    lims[1],
                    linestyle="dashed",
                    color=names[key][1],
                    alpha=0.5,
                )
                ax.set_ylim(0, 50)
            if key == "wekg":
                ax.grid()
                ax.set_ylim(
                    1.05 * plotdf["wekg"].quantile(0.001),
                    1.05 * plotdf["wekg"].quantile(0.999),
                )
            if key == "wflow":
                # ax.fill_between(set.index, set[key], where = set[key] > 0,
                #                                color = names[key][1], alpha=0.4)
                pass
            if key == "wap":
                ax.hlines(
                    70,
                    lims[0],
                    lims[1],
                    color=names[key][1],
                    linestyle="dashed",
                    alpha=0.5,
                )
                ax.set_ylim(40, 1.10 * plotdf["wap"].quantile(0.99))
            ax.get_xaxis().tick_bottom()
            if i > 0:
                if not dtime:
                    ax.set_xlabel("time (sec)")
        for ax in ax_list:
            if dtime:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            for spine in ["left", "right", "bottom"]:
                color_axis(ax, spine=spine, color="tab:grey")
            for spine in ["top", "right"]:
                ax.spines[spine].set_visible(False)
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    return fig, lines


# %%


def get_roi(fig: plt.Figure, datadf: pd.DataFrame, params: dict) -> dict:
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

    ylims = tuple([_.get_ylim() for _ in fig.get_axes()])
    # xlims
    ax = fig.get_axes()[0]
    if params["dtime"]:  # datetime in the x axis
        dtime_lims = [pd.to_datetime(mdates.num2date(_)) for _ in ax.get_xlim()]
        dtime_lims = [_.tz_localize(None) for _ in dtime_lims]
        i_lims = [bisect(datadf.datetime, _) for _ in dtime_lims]
    else:  # index = sec
        i_lims = [bisect(datadf.sec, _) for _ in dtime_lims]
    roidict = {}
    for k, v in {"dt": "datetime", "pt": "point", "sec": "sec"}.items():
        if v in datadf.columns:
            lims = tuple([datadf.iloc[_][[v]].values[0] for _ in i_lims])
        else:
            # no dt values for televet
            lims = (np.nan, np.nan)
        roidict[k] = lims
    print(f"{'-' * 10} defined a roi")
    # append ylims and traces
    roidict["ylims"] = ylims
    return roidict


# %%
def plot_systolic_pressure_variation(mwave, lims: Tuple = None, teach: bool = False):
    """
    extract and plot the systolic pressure variation"

    Parameters
    ----------
    mwave : monitor trend object
        the monitor recording
    lims : tuple, (default is None)
        the limits to use (in sec)
        If none the mwave.roi will be used
    teach : boolean (default is False)
        if true added markers on the most relevant differences
    Returns
    -------
    fig : plt.Figure
        the matplotlib figure.

    """

    datadf = mwave.data[["sec", "wap"]].dropna().copy()
    if lims is None:
        lims = mwave.roi["sec"]
        # lims = (df.iloc[0].sec, df.iloc[0].sec + 60)
    datadf = datadf.set_index("sec").loc[lims[0] : lims[1]]

    # plot the arterial pressure data
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(datadf, "-r")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.set_ymargin(0.1)
    # find the (up) peaks
    threshold = datadf.wap.quantile(q=0.82)
    # ax.axhline(threshold, color="tab:green", alpha=0.5)
    # added a distance to avoid double detection
    peaks_up, properties_up = find_peaks(datadf.wap, height=threshold, distance=300)
    ax.plot(datadf.iloc[peaks_up], "or", alpha=0.2)

    peaks_vals = datadf.iloc[peaks_up].copy()  # to keep the index ('sec')
    peaks_vals = peaks_vals.reset_index()
    peaks_vals["local_max"] = False
    peaks_vals["local_min"] = False

    maxi, mini, med = peaks_vals["wap"].agg(["max", "min", "median"])
    systolic_variation = (maxi - mini) / med
    sys_var = f"{systolic_variation = :.2f}"
    print(sys_var)

    # get local max
    maxis_loc, _ = find_peaks(properties_up["peak_heights"])
    peaks_vals.loc[maxis_loc, "local_max"] = True
    # get local min
    minis_loc, _ = find_peaks(-properties_up["peak_heights"])
    peaks_vals.loc[minis_loc, "local_min"] = True
    # plot
    inter_beat = round((peaks_vals.sec - peaks_vals.sec.shift(1)).mean())
    beat_loc_df = peaks_vals.set_index("sec")
    for sloc, yloc in beat_loc_df.loc[
        beat_loc_df.local_max + beat_loc_df.local_min, "wap"
    ].iteritems():
        ax.hlines(yloc, sloc - inter_beat, sloc + inter_beat, color="tab:grey")

    # compute delta_PP
    _, properties_dwn = find_peaks(-datadf.wap, height=-threshold, distance=300)
    # ax.plot(datadf.iloc[peaks_dwn], "ob", alpha=0.2)
    heights = pd.DataFrame()
    heights["pt_up"] = peaks_up
    heights["sec_up"] = datadf.iloc[peaks_up].index
    heights["val_up"] = properties_up["peak_heights"]
    if len(heights) < len(properties_dwn["peak_heights"]):
        properties_dwn["peak_heights"] = properties_dwn["peak_heights"][:-1]
    heights["val_dwn"] = -1 * properties_dwn["peak_heights"]
    heights["delta"] = heights.val_up - heights.val_dwn
    maxi, mini, med = heights["delta"].agg(["max", "min", "median"])
    delta_variation = (maxi - mini) / med
    delta_var = f"{delta_variation = :.2f}"
    print(delta_var)

    if teach:
        # sys_var
        sloc, yloc = beat_loc_df.wap.agg(["idxmax", "max"])
        ax.hlines(yloc, sloc - inter_beat, sloc + inter_beat, color="k", linewidth=3)
        sloc, yloc = beat_loc_df.wap.agg(["idxmin", "min"])
        ax.hlines(yloc, sloc - inter_beat, sloc + inter_beat, color="k", linewidth=3)
        # delta_PP
        plocs = [heights.delta.idxmax(), heights.delta.idxmin()]
        for ploc in plocs:
            # ploc = heights.index[i]
            sec_up, val_up, val_dwn = heights.loc[ploc, ["sec_up", "val_up", "val_dwn"]]
            ax.vlines(sec_up, val_up, val_dwn, color="k", linewidth=2)
            for val in [val_up, val_dwn]:
                ax.hlines(
                    val,
                    sec_up - 0.5 * inter_beat,
                    sec_up + 0.5 * inter_beat,
                    color="k",
                    linewidth=3,
                )

    title = sys_var + "     " + delta_var
    fig.suptitle(title)
    ax.set_ylabel("arterial pressure")
    ax.set_xlabel("time (sec)")
    color_axis(ax, "left", "red")
    color_axis(ax, "bottom", "grey")
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, mwave.param["file"], ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()
    plt.show()

    return fig


# %% select subdata


def create_video(
    data: pd.DataFrame,
    param: dict,
    roi: dict,
    speed: int = 1,
    save: bool = False,
    savename: str = "example",
    savedir: str = "~",
):
    """
    create a video from a figure

    Parameters
    ----------
    data : pd.DataFrame
        waves data.
    param : dict
        recording parameters.
    roi : dict
        containing ylims, xlims(point, dtime and sec).
    speed : int, optional (default is 1).
        speed of the video.
    save : bool, optional (default is False)
        to save or not to save.
    savename : str, optional (default is "example").
        save (short) name.
    savedir : str, optional (default is "~").
        save dirname (full).

    Returns
    -------
    .mp4 file
    .png file

    """

    def select_sub_dataframe(
        datadf: pd.DataFrame, keys: list, xlims: tuple
    ) -> pd.DataFrame:
        """
        extract subdataframe corresponding to the roi

        Parameters
        ----------
        datadf : pd.DataFrame
            wave recording.
        keys : list
            list of columns to use (max : 2).
        xlims : tuple
            (xmin, xmax).

        Returns
        -------
        sub_df : pandas.DataFrame

        """

        sub_df = datadf[xlims[0] < datadf.sec]
        sub_df = sub_df[sub_df.sec < xlims[1]]
        sub_df = sub_df.set_index("sec")
        sub_df = sub_df[keys].copy()
        return sub_df

    def init(data: pd.DataFrame, param: dict, keys: list, xlims: tuple, ylims: list):
        """build a new figure and associated line2D objects"""
        plt.close("all")
        dtime = param["dtime"]
        param["dtime"] = False
        fig, lines = plot_wave(data, keys, param)
        for ax, ylim in zip(fig.get_axes(), ylims):
            ax.set_ylim(ylim)
            ax.set_xlim(xlims)
        # restaure dtime
        param["dtime"] = dtime
        return fig, lines

    def animate(i: int, df: pd.DataFrame, keys: list, nbpoint: int) -> tuple:
        """
        animate the plot

        Parameters
        ----------
        i : int
            frame indice.
        df : pd.DataFrame
            the restricted data to use.
        keys : list
            the columns names.
        nbpoint : int
            nb of point to add in each new frame.

        Returns
        -------
        tuple
            the two lines2D objects.

        """

        if len(keys) == 1:
            trace_name = keys[0]
            line0.set_data(
                df.iloc[0 : nbpoint * i].index,
                df.iloc[0 : nbpoint * i][trace_name].values,
            )
            return (line0,)
        trace_name = keys[0]
        line0.set_data(
            df.iloc[0 : nbpoint * i].index, df.iloc[0 : nbpoint * i][trace_name].values
        )
        trace_name = keys[1]
        line1.set_data(
            df.iloc[0 : nbpoint * i].index, df.iloc[0 : nbpoint * i][trace_name].values
        )
        return (line0, line1)

    traces = roi["traces"]
    x_lims = tuple([int(_) for _ in roi["sec"]])
    y_lims = [(floor(a), ceil(b)) for a, b in roi["ylims"]]
    fs = param.get("sampling_freq", 1)
    interval = 100
    nb_of_points = speed * round(fs / interval) * 10  # nb of points per frame

    df = select_sub_dataframe(data, traces, x_lims)
    fig, lines = init(data, param, traces, x_lims, y_lims)

    for line in lines:
        line.set_data([], [])
    line0 = lines[0]
    line1 = lines[1] if len(lines) > 1 else None

    global ANI
    ani = animation.FuncAnimation(
        fig,
        animate,
        # init_func = init_wave,
        frames=int(len(df) / nb_of_points) + 1,
        interval=interval,  # 100
        fargs=[df, traces, nb_of_points],  # 30
        repeat=False,
        blit=True,
    )

    if save:
        if savedir == "~":
            savedir = os.path.expanduser("~")
        filename = os.path.join(savedir, savename)
        print(f"{'-' * 10} building video : {savename}.png and .mp4")
        ani.save(filename + ".mp4")
        fig.savefig(filename + ".png")
        print(f"{'-' * 10} saved {savename}.png and .mp4")
    plt.show()


# ANI = "global_to_maintain animation"
ANI = None

# %%
