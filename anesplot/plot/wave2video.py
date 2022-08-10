#!/usr/bin/env python3
"""
Created on Wed Jun  1 16:18:25 2022

@author: cdesbois
"""
import logging
import os
from math import ceil, floor
from typing import Any, Union

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import animation

import anesplot.plot.wave_plot

matplotlib.use("qt5Agg")


def create_video(
    data: pd.DataFrame,
    param: dict[str, Any],
    roi: dict[str, Any],
    speed: int = 1,
    save: bool = False,
    savename: str = "example",
    savedir: str = "~",
) -> Any:
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
        xlims : tuple (xmin, xmax)
            on a sec basis (mwaves.roi[sec])

        Returns
        -------
        sub_df : pandas.DataFrame
        """
        sub_df = datadf.loc[datadf.etimesec.between(*xlims)]
        return sub_df.set_index("etimesec")[keys].copy()

    def init(
        data: pd.DataFrame,
        param: dict[str, Any],
        keys: list[str],
        xlims: tuple[int, ...],
        ylims: list[tuple[int, int]],
    ) -> Union[plt.figure, list[plt.Line2D]]:
        """Build a new figure and associated line2D objects."""
        plt.close("all")
        dtime = param["dtime"]
        param["dtime"] = False
        fig, lines = anesplot.plot.wave_plot.plot_wave(data, keys, param)
        for ax, ylim in zip(fig.get_axes(), ylims):
            ax.set_ylim(ylim)
            ax.set_xlim(xlims)
        # restaure dtime
        param["dtime"] = dtime
        return fig, lines

    def animate(
        i: int, df: pd.DataFrame, keys: list[str], nbpoint: int
    ) -> Union[tuple[plt.Line2D], tuple[plt.Line2D, plt.Line2D]]:
        """
        Animate the plot.

        Parameters
        ----------
        i : int
            frame indice.
        df : pd.DataFrame
            the restricted data to use.
        keys : list
            the columns key_dict.
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

    # global ANI
    anim = animation.FuncAnimation(
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
        logging.warning(f"{'-' * 10} building video : {savename}.png and .mp4")
        anim.save(filename + ".mp4")
        fig.savefig(filename + ".png")
        logging.warning(f"{'-' * 10} saved {savename}.png and .mp4")
        logging.warning(f" -> {filename.split('.')[0]}")
    # plt.show()
    return anim


# %%
if __name__ == "__main__":
    pass
    # import anesplot.config.load_recordrc
    # import anesplot.fast_waves

    # paths = anesplot.config.load_recordrc.build_paths()
    # test_filename = os.path.join(
    #     paths["cwd"], "example_files", "M2021_4_16-8_44_38Wave.csv"
    # )

    # mwaves = anesplot.fast_waves.MonitorWave(test_filename)
    # mwaves.plot_wave(["wekg", "wap"])
    # # zoom in
    # mwaves.save_roi()
    # anim_ = create_video(
    #     mwaves.data,
    #     mwaves.param,
    #     mwaves.roi,
    #     speed=50,
    #     save=False,
    #     savename="example",
    #     savedir="~",
    # )
