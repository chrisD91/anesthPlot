# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 09:08:56 2016

@author: cdesbois
"""

import os
from math import floor, ceil

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import animation
import numpy as np
import pandas as pd

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

font_size = "medium"  # large, medium
fig_params = {
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
plt.rcParams.update(fig_params)
plt.rcParams["axes.xmargin"] = 0  # no gap between axes and traces

# bright = {
#         'blue' : [x/256 for x in [0, 119, 170]],
#         'cyan' : [x/256 for x in [102, 204, 238]],
#         'green' : [x/256 for x in [34, 136, 51]],
#         'yellow' : [x/256 for x in [204, 187, 68]],
#         'red' : [x/256 for x in [238, 103, 119]],
#         'purple' : [x/256 for x in [170, 51, 119]],
#         'grey' : [x/256 for x in [187, 187, 187]]
#         }

# colors = bright

# ////////////////////////////////////////////////////////////////
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


#%%
# def plot_wave(df, keys=[], mini=None, maxi=None, datetime=False):
def plot_wave(data, keys, param):
    """plot the waves recorded (from as5)

    :param pandas.DataFrame data: the recorded trends data
    :param list keys: one or two in ['wekg','ECG','wco2','wawp','wflow','wap']
    :param dict {mini: limits in point value (index), maxi: limits in point value (index)}

    :returns fig: plt.figure  the plot
    :returns lines: plt.line2D the line to animate

    (Nb plot data/index, but the xscale is indicated as sec)
    """
    # test wave in dataframe
    for key in keys:
        try:
            key in data.columns
        except KeyError:
            print("the trace {} is not in the data".format(key))
            return
    if len(keys) not in [1, 2]:
        print("only one or two keys are allowed ", keys, "were used")
        return
    # default plotting
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
    for key in keys:
        if not key in names:
            names[key] = [key, "tab:blue", ""]
            if key.startswith("rr"):
                names[key] = [key, "tab:green", ""]
    # time scaling (index value)
    mini = param.get("mini", data.index[0])
    maxi = param.get("maxi", data.index[-1])
    if not data.index[0] <= mini <= data.index[-1]:
        print("mini value not in range, replaced by start time value")
        mini = data.index[0]
    if not data.index[0] <= maxi <= data.index[-1]:
        print("maxi value not in range, replaced by end time value")
        maxi = data.index[-1]
    # datetime or elapsed time sec
    dtime = param.get("dtime", False)
    if dtime and "datetime" not in data.columns:
        print("no datetime values, changed dtime to False")
        dtime = False
    cols = set(keys)
    if dtime:
        cols.add("datetime")
        df = data[cols].copy()
        df = df.iloc[mini:maxi].set_index("datetime")
    else:
        cols.add("sec")
        df = data[cols].copy()
        df = df.iloc[mini:maxi].set_index("sec")
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
            (line,) = ax.plot(df[key], color=color, alpha=0.6)
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
                #                ax.fill_between(set.index, set[key], where = set[key] > 0,
                #                                color = names[key][1], alpha=0.4)
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
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.margins(0)
        ax_list.append(ax1)
        ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
        ax2.margins(0)
        ax_list.append(ax2)
        for i, key in enumerate(keys):
            ax = ax_list[i]
            # ax.set_title(names[key][0])
            ax.set_ylabel(names[key][0], size="small")
            color = names[key][1]
            (line,) = ax.plot(df[key], color=color, alpha=0.6)
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
                    1.05 * df["wekg"].quantile(0.001), 1.05 * df["wekg"].quantile(0.999)
                )
            if key == "wflow":
                #                ax.fill_between(set.index, set[key], where = set[key] > 0,
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
                ax.set_ylim(40, 1.10 * df["wap"].quantile(0.99))
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


#%%


def get_roi(waves):
    """use the drawn figure to extract the relevant data in order to build an animation

    :param waves: a wave recording
    :type waves: MonitorWave object
    :return: a dictionary containing ylims, xlims(point, dtime and sec),
    traces used to build the plot, the fig object
    :rtype: dictionary

    """

    fig = waves.fig
    df = waves.data
    params = waves.param
    # ylims
    ylims = [_.get_ylim() for _ in fig.get_axes()]
    # xlims
    ax = fig.get_axes()[0]
    if params["dtime"]:
        dtime_lims = [pd.to_datetime(mdates.num2date(_)) for _ in ax.get_xlim()]
        # remove timezone
        dtime_lims = [_.tz_localize(None) for _ in dtime_lims]

        i_lims = [
            df.set_index("datetime").index.get_loc(_, method="nearest")
            for _ in dtime_lims
        ]
    else:
        # index = sec
        i_lims = [
            df.set_index("sec").index.get_loc(_, method="nearest")
            for _ in ax.get_xlim()
        ]
    roidict = {}
    for k, v in {"dt": "datetime", "pt": "point", "sec": "sec"}.items():
        if v in df.columns:
            lims = tuple([df.iloc[_][[v]].values[0] for _ in i_lims])
        else:
            # no dt values for televet
            lims = (np.nan, np.nan)
        roidict[k] = lims
    print("{} {}".format("-" * 10, "defined a roi"))
    # append ylims and traces
    roidict.update({"ylims": ylims})
    return roidict


#%% select subdata


def create_video(waves, speed=1, save=False, savename="example", savedir="~"):
    """create a video from a figure
    input:
        waves : waves object
        speed : integer, speed of the display
        save : boolean (default=False)
        savename : str (default='example')
        savedir : str (path, default='~'
    return:
        .mp4 file
        .png file
    """

    def select_sub_dataframe(datadf, keys, xlims):
        """extract subdataframe corresponding to the roi

        :param waves: wave recording
        :type waves: rec.MonitorWave (with a defined roi attribute)
        :return: df
        :rtype: pandas.dataframe

        """
        sub_df = datadf[xlims[0] < datadf.sec]
        sub_df = sub_df[sub_df.sec < xlims[1]]
        sub_df = sub_df.set_index("sec")
        sub_df = sub_df[keys].copy()
        return sub_df

    def init(waves, keys, xlims, ylims):
        plt.close("all")
        dtime = waves.param["dtime"]
        waves.param["dtime"] = False
        fig, lines, _ = waves.plot_wave(keys)
        for ax, ylim in zip(fig.get_axes(), ylims):
            ax.set_ylim(ylim)
            ax.set_xlim(xlims)
        waves.param["dtime"] = dtime
        return fig, lines

    def animate(i, df, keys, nbpoint):
        """
        animate frame[i], add 10 points to the lines
        return the two lines2D objects
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

    traces = waves.roi["traces"]
    x_lims = tuple([int(_) for _ in waves.roi["sec"]])
    y_lims = [(floor(a), ceil(b)) for a, b in waves.roi["ylims"]]
    fs = waves.sampling_freq
    interval = 100
    # speed = 2  # speed of the animation
    nb_of_points = speed * round(fs / interval) * 10

    df = select_sub_dataframe(waves.data, traces, x_lims)
    fig, lines = init(waves, traces, x_lims, y_lims)

    for line in lines:
        line.set_data([], [])
    line0 = lines[0]
    line1 = lines[1] if len(lines) > 1 else None

    global ani
    ani = animation.FuncAnimation(
        fig,
        animate,
        # init_func = init_wave,
        # frames=int(len(df) / 10),
        interval=interval,
        fargs=[df, traces, nb_of_points],
        repeat=False,
        blit=True,
        #        save_count=int(len(df) / 10),
    )

    if save:
        # TODO : the saved video finish before the end of the display
        savename = savename
        if savedir == "~":
            savedir = os.path.expanduser("~")
        filename = os.path.join(savedir, savename)

        ani.save(filename + ".mp4")
        fig.savefig(filename + ".png")
    plt.show()


ani = "global_to_maintain animation"
