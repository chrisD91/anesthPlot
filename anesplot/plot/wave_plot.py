# !/usr/bin/env python3
"""
Created on Tue Apr 19 09:08:56 2016

@author: cdesbois

collection of functions to plot the wave data

"""

import os

# from bisect import bisect
from math import ceil, floor
from typing import Union, Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# import numpy as np
import pandas as pd
from matplotlib import animation

from anesplot.plot.pfunc import update_pltparams

update_pltparams()

# FONT_SIZE = "medium"  # large, medium
# fig_params = {
#     "font.sans-serif": ["Arial"],
#     "font.size": 12,
#     "legend.fontsize": FONT_SIZE,
#     "figure.figsize": (12, 3.1),
#     "axes.labelsize": FONT_SIZE,
#     "axes.titlesize": FONT_SIZE,
#     "xtick.labelsize": FONT_SIZE,
#     "ytick.labelsize": FONT_SIZE,
#     "axes.xmargin": 0,
# }
# plt.rcParams.update(fig_params)
# plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces


def color_axis(ax: plt.Axes, spine: str = "bottom", color: str = "r") -> None:
    """
    Change the color of the label & tick & spine.

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
def plot_wave(
    datadf: pd.DataFrame, keys: list[str], param: dict[str, Any]
) -> Union[plt.Figure, list[plt.Line2D]]:
    """
    Plot the waves recorded (from as5).

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
                lims = 40, 1.10 * plotdf["wap"].quantile(0.99)
                if not (pd.isna(lims[0]) or pd.isna(lims[1])):
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


# def get_wave_roi(
#     fig: plt.Figure, datadf: pd.DataFrame, params: dict[str, Any]
# ) -> dict[str, Any]:
#     """
#     Use the drawn figure to extract the x and x limits.

#     Parameters
#     ----------
#     fig : plt.Figure
#         the figure to get data from.
#     datadf : pd.DataFrame
#         waves recording.
#     params : dict of parameters

#     Returns
#     -------
#     dict :
#         containing ylims, xlims(point, dtime and sec)
#     """
#     ylims = tuple(_.get_ylim() for _ in fig.get_axes())
#     # xlims
#     ax = fig.get_axes()[0]
#     if params["dtime"]:  # datetime in the x axis
#         dtime_lims = [pd.to_datetime(mdates.num2date(_)) for _ in ax.get_xlim()]
#         dtime_lims = [_.tz_localize(None) for _ in dtime_lims]
#         i_lims = [bisect(datadf.datetime, _) for _ in dtime_lims]
#     else:  # index = sec
#         i_lims = [bisect(datadf.sec, _) for _ in dtime_lims]
#     roidict = {}
#     for k, v in {"dt": "datetime", "pt": "point", "sec": "sec"}.items():
#         if v in datadf.columns:
#             lims = tuple(datadf.iloc[_][[v]].values[0] for _ in i_lims)
#         else:
#             # no dt values for televet
#             lims = (np.nan, np.nan)
#         roidict[k] = lims
#     print(f"{'-' * 10} defined a roi")
#     # append ylims and traces
#     roidict["ylims"] = ylims
#     return roidict


# %% select subdata


def create_video(
    data: pd.DataFrame,
    param: dict[str, Any],
    roi: dict[str, Any],
    speed: int = 1,
    save: bool = False,
    savename: str = "example",
    savedir: str = "~",
) -> None:
    """
    Create a video from a figure.

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
        datadf: pd.DataFrame, keys: list[str], xlims: tuple[int, ...]
    ) -> pd.DataFrame:
        """
        Extract subdataframe corresponding to the ROI.

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

    def init(
        data: pd.DataFrame,
        param: dict[str, Any],
        keys: list[str],
        xlims: tuple[int, ...],
        ylims: list[tuple[int, int]],
    ) -> Union[plt.figure, plt.Line2D]:
        """Build a new figure and associated line2D objects."""
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

    def animate(
        i: int, df: pd.DataFrame, keys: list[str], nbpoint: int
    ) -> Any[tuple[plt.Line2D], tuple[plt.Line2D, plt.Line2D]]:
        """
        Animate the plot.

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
    # x_lims = tuple(int(_) for _ in roi["sec"])
    x_lims = tuple(int(_) for _ in roi["sec"])  # tuple(float, float)
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
