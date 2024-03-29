#!/usr/bin/env python3
"""
Created on Tue Mar 29 13:00:08 2022

@author: cdesbois

a collection of functions to work with arterial pressure waves

"""


import os
from math import ceil, floor
from typing import Tuple, Union, Optional, Any, Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks


import anesplot.plot.pfunc

# from anesplot.plot.pfunc import color_axis
from anesplot.treatrec.wave_func import fix_baseline_wander

# from .wave_func import fix_baseline_wander
# from ..plot.wave_plot import color_axis

# %%


def get_peaks(
    ser: pd.Series, upp: bool = True, annotations: bool = False
) -> pd.DataFrame:
    """
    Extract a peak location from an arterial time series.

    Parameters
    ----------
    ser : pd.Series
        arterial time series (val = arterial wave, index = sec).
    up : bool, optional (default is True)
        extraction of the 'up' peaks. (false -> 'down peaks')
    annotations : bool, optional (default is False)
        plot annotations peak and indications.

    Returns
    -------
    peaksdf : pd.DataFrame that contains
        'ploc' & 'sloc' : point and second based beat location
        'wap' & 'peak_heights' : the arterials values
        'local_max' & 'local_min' : boolean for local maxima and minima
    """
    quantile = 0.9
    distance = 300
    width = 1  # just to have a width measure in the output
    low_width = 45  # to remove the artefacts (narrow peaks)
    # replaced in the code by 80* of median width value

    ser_detrended = fix_baseline_wander(ser, 300)
    height = ser_detrended.quantile(q=quantile)
    # find the (up) peaks
    peaksdf = pd.DataFrame()
    if upp:
        peaksdf["ploc"], properties = find_peaks(
            ser_detrended, height=height, distance=distance, width=width
        )
    else:
        peaksdf["ploc"], properties = find_peaks(
            -ser_detrended, height=-height, distance=distance, width=width
        )
    peaksdf["sloc"] = ser.index[peaksdf.ploc]
    for k, v in properties.items():
        peaksdf[k] = v
    if annotations:
        fig = plt.figure()
        fig.suptitle("arterial_func.get_peaks (trace = detrended one's)")
        # trend
        ax0 = fig.add_subplot(211)
        ax0.plot(ser_detrended, "-r")
        ax0.axhline(height)
        # ax0.plot(peaks, ser_detrended.iloc[peaks], "og")
        ax0.plot(peaksdf.sloc, ser_detrended.loc[peaksdf.sloc], "og")
        ax0.set_ylim(
            floor(min(ser_detrended) / 10) * 10, ceil(max(ser_detrended) / 10) * 10
        )
        for spine in ["top", "right"]:
            ax0.spines[spine].set_visible(False)
        # txt values
        ax1 = fig.add_subplot(212)
        ax1.text(
            0, 0.8, f"{quantile=}", transform=ax1.transAxes, color="tab:blue", ha="left"
        )
        ax1.text(0, 0.6, f"{distance=}", transform=ax1.transAxes, ha="left")

        for i, (k, v) in enumerate(properties.items()):
            txt = f"{k}: {np.median(v):.2f}"
            print(i, txt)
            if i / 5 < 1:
                ax1.text(0.2, i / 5, txt, transform=ax1.transAxes, ha="left")
            else:
                ax1.text(0.4, i / 5 - 1, txt, transform=ax1.transAxes, ha="left")
        ax1.text(0.6, 0.4, f"{low_width=}", transform=ax1.transAxes, ha="left")
        for spine in ["left", "top", "right", "bottom"]:
            ax1.spines[spine].set_visible(False)
        ax1.xaxis.set_visible(False)
        ax1.yaxis.set_visible(False)
        # annotations
        fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
        fig.tight_layout()
    # remove artefact:
    low_width = 0.8 * np.median(properties["widths"])
    artefact = np.where(peaksdf.widths < low_width)[0]
    if annotations:
        ax0.plot(artefact, ser_detrended.iloc[artefact], "or")
        ax1.text(0.7, 0.2, f"{artefact=}", transform=ax1.transAxes, ha="left")
    peaksdf.drop(labels=artefact, inplace=True)
    peaksdf.reset_index(inplace=True)
    # get local min max
    peaksdf["wap"] = ser[peaksdf.sloc].values
    peaksdf["local_max"] = False
    peaksdf["local_min"] = False
    # get local max
    maxis_loc, _ = find_peaks(peaksdf.wap)
    peaksdf.loc[maxis_loc, "local_max"] = True
    # get local min
    minis_loc, _ = find_peaks(-peaksdf.wap)
    peaksdf.loc[minis_loc, "local_min"] = True

    if not upp:
        peaksdf.peak_heights = -1 * peaksdf.peak_heights
        peaksdf.rename(columns={"local_max": "local_min", "local_min": "local_max"})

    return peaksdf


def compute_systolic_variation(ser: pd.Series) -> float:
    """Return the systolic variation : (maxi - mini) / mean."""
    maxi, mini, mean = ser.agg(["max", "min", "mean"])
    var = (maxi - mini) / mean
    return float(var)


def plot_roi_systolic_pressure_variation(
    mwave: Any,
    teach: bool = False,
    annotations: bool = False,
    lims: Optional[Tuple[int, int]] = None,
) -> tuple[plt.Figure, pd.DataFrame]:
    """
    Extract and plot the systolic pressure variation.

    Parameters
    ----------
    mwave : monitor trend object
        the monitor recording
    teach : boolean (default is False)
        if true added markers on the most relevant differences
    annotations : boolean(default False)
        if true plot all detected pulse
    lims : tuple, optional (default is None)
        the limits to use (in sec)
        If None the mwave.roi will be used
    Returns
    -------
    fig : plt.Figure
        the matplotlib figure.
    """

    def deltavar(ser: pd.Series, median: bool = False) -> float:
        """Compute the delta variation with med or mean base."""
        maxi, mini, mean, med = ser.agg(["max", "min", "mean", "median"])
        if median:
            return float((maxi - mini) / med)
        return float((maxi - mini) / mean)

    datadf = mwave.data[["etimesec", "wap"]].dropna().copy()
    if lims is None:
        lims = mwave.roi["sec"]
    datadf = datadf.set_index("etimesec").loc[lims[0] : lims[1]]

    # plot the arterial pressure data
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(datadf, "-r")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.set_ymargin(0.1)

    # find the (up) peaks
    ser = datadf.wap.dropna()
    peak_df = get_peaks(ser, upp=True, annotations=annotations)
    systolic_variation = deltavar(peak_df.wap, median=True)
    sys_var = f"{systolic_variation = :.2f}"
    print(sys_var)

    # plot
    if annotations:
        ax.plot(peak_df.set_index("sloc").wap, "or", alpha=0.5)
    inter_beat = round((peak_df.sloc - peak_df.sloc.shift(1)).mean())
    beat_loc_df = peak_df.set_index("sloc")
    for sloc, yloc in beat_loc_df.loc[
        beat_loc_df.local_max + beat_loc_df.local_min, "wap"
    ].iteritems():
        ax.hlines(
            yloc, sloc - 0.7 * inter_beat, sloc + 0.7 * inter_beat, color="tab:grey"
        )

    # compute delta_PP
    peak_df_dwn = get_peaks(ser, upp=False)
    peak_df_dwn.columns = [_ + "_dwn" for _ in peak_df_dwn.columns]

    pp_df = peak_df.copy()
    pp_df.columns = [_ + "_up" for _ in pp_df.columns]
    pp_df = pd.concat([pp_df, peak_df_dwn], axis=1)
    pp_df["delta"] = pp_df.peak_heights_up - pp_df.peak_heights_dwn
    delta_variation = deltavar(pp_df.delta, median=False)
    delta_var = f"{delta_variation = :.2f}"
    print(delta_var)

    if teach:  # plot mesure intervals
        # sys_var
        sloc, yloc = beat_loc_df.wap.agg(["idxmax", "max"])
        ax.hlines(
            yloc,
            sloc - 0.7 * inter_beat,
            sloc + 0.7 * inter_beat,
            color="k",
            linewidth=3,
        )
        sloc, yloc = beat_loc_df.wap.agg(["idxmin", "min"])
        ax.hlines(yloc, sloc - inter_beat, sloc + inter_beat, color="k", linewidth=3)
        # delta_PP
        plocs = [
            pp_df.set_index("ploc_up").delta.idxmax(),
            pp_df.set_index("ploc_up").delta.idxmin(),
        ]
        for ploc in plocs:
            # ploc = heights.index[i]
            sec_up, val_up, val_dwn = pp_df.set_index("ploc_up").loc[
                ploc, ["sloc_up", "peak_heights_up", "peak_heights_dwn"]
            ]
            ax.vlines(sec_up, val_up, val_dwn, color="k", linewidth=2)
            for val in [val_up, val_dwn]:
                ax.hlines(
                    val,
                    sec_up - 0.5 * inter_beat,
                    sec_up + 0.5 * inter_beat,
                    color="k",
                    linewidth=3,
                    alpha=0.6,
                )

    title = sys_var + "     " + delta_var
    fig.suptitle(title)
    ax.set_ylabel("arterial pressure")
    ax.set_xlabel("time (sec)")
    anesplot.plot.pfunc.color_axis(ax, "left", "red")
    anesplot.plot.pfunc.color_axis(ax, "bottom", "grey")
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, mwave.param["file"], ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()
    plt.show()

    return fig, pp_df


# initial
def median_filter(num_std: int = 3) -> Callable[[Any], Any]:
    """median filtering"""

    def _median_filter(arr: np.ndarray) -> Any:
        _median = np.median(arr)
        _std = np.std(arr)
        val = arr[-1]
        return (
            val
            if _median - num_std * _std <= val <= _median + num_std * _std
            else np.nan
        )

    return _median_filter


# def median_filter(num_std: int = 3) -> float:
#     """Basic median filter."""

#     def _median_filter(ser: pd.Windows) -> float:
#         _median = np.median(ser)
#         _std = np.std(ser)
#         s = ser[-1]
#         fval = (
#             s if (_median - num_std * _std) <= s <= (_median + num_std * _std) else np.nan
#         )
#         print(float(fval))
#         return float(fval)
#         # return (
#         #     s if (_median - num_std * _std) <= s <= (_median + num_std * _std) else np.nan
#         # )

#     return _median_filter


# def median_filter2(ser: pd.Series, num_std: int = 3) -> float:
# def median_filter2(ser: pd.Series, num_std: int = 3) -> float:
#     _median = np.median(ser)
#     _std = np.std(ser)
#     s = ser[-1]
#     fval = s if (_median - num_std * _std) <= s <= (_median + num_std * _std) else np.nan

#     return fval

#     # return (
#     #     s
#     #     if (_median - num_std * _std) <= s <= (_median + num_std * _std)
#     #     else np.nan
#     # )


def plot_record_systolic_variation(
    mwave: Any, annotations: bool = False
) -> Union[plt.Figure, pd.DataFrame]:
    """
    Plot systolic variation over the whole record.

    Parameters
    ----------
    mwave : rec.MonitorWave object
        a monitor recording containing an arterial ('wap') recording.
    annotations: bool (default=False)
        add indications of peak detection in the graph
    Returns
    -------
    fig : pyplot.Figure
        pressure, sys_var and hr plot
    df : pandas.DataFrame
        peaks locations and description.
    """
    if "wap" not in mwave.data.columns:
        print("please provide a MonitorWave object that contains an arterial record")
        return plt.figure(), pd.DataFrame()
    ap_ser = mwave.data.set_index("sec").wap.dropna()
    # TODO filtering process?
    # ser = ser.rolling(10).apply(median_filter(num_std=3), raw=True)
    df = get_peaks(ap_ser, annotations=annotations)
    # df = get_peaks(mwave.data.set_index("sec").wap.dropna())

    df["sys_var"] = np.nan
    # fs = int(mwaves.param["sampling_freq"])
    # start = df.index.min()
    end = df.index.max()
    indexes = list(df.loc[df.local_max].index)
    for bb1, bb2 in zip(
        [
            0,
        ]
        + indexes,
        indexes
        + [
            end,
        ],
    ):
        df.loc[bb1:bb2, "sys_var"] = compute_systolic_variation(df.loc[bb1:bb2, "wap"])
    df["i_pr"] = (1 / (df.sloc - df.sloc.shift(1))) * 60

    fig = plt.figure()
    fig.suptitle("systolic variation over time")
    ax = fig.add_subplot(111)
    ax.plot(ap_ser, "-r", label="arterial pressure")
    # check the precise location
    if annotations:
        ax.plot(df.set_index("sloc").wap, "og")
    ax_t = ax.twinx()
    # heart rate
    ser = (
        df.set_index("sloc").i_pr.rolling(10).apply(median_filter(num_std=3), raw=True)
    )
    ser = df.set_index("sloc").i_pr
    ser = ser.fillna(method="bfill").fillna(method="ffill")
    ax_t.plot(ser.rolling(10, center=True).mean(), ":k", linewidth=2)
    # sys_var
    ser = df.set_index("sloc").sys_var * 100
    ser = ser.rolling(50).apply(median_filter(num_std=3), raw=True)
    ser = ser.fillna(method="bfill").fillna(method="ffill")
    ax_t.plot(ser.dropna().rolling(10).mean(), "-b", label="sys_var med_rolmean")
    ax.set_ylim(50, 150)
    ax_t.set_ylim(0, 40)
    anesplot.plot.pfunc.color_axis(ax, spine="left", color="r")
    anesplot.plot.pfunc.color_axis(ax_t, spine="right", color="b")
    anesplot.plot.pfunc.color_axis(ax, spine="bottom", color="tab:grey")
    ax.set_xlabel("time (sec)")
    ax.set_ylabel("arterial pressure (mmHg)")
    ax_t.set_ylabel("systolic variation (%) & hr (bpm)")
    for ax in fig.get_axes():
        for spine in ["top"]:
            ax.spines[spine].set_visible(False)
    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, mwave.param["file"], ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()

    return fig, df


def get_xlims() -> Any:
    """return the xlim of the top figure"""
    fig = plt.gcf()  # plt.figure
    ax = fig.get_axes()[0]
    return ax.get_xlim()


# TODO save the df in a file (cf ekg2HR)
# %%


if __name__ == "__main__":

    # import anesplot.record_main as rec
    from anesplot.loadrec.export_reload import build_obj_from_hdf

    DIRNAME = "/Users/cdesbois/enva/clinique/recordings/casClin/220315/data"
    FILE = "qDonUnico.hdf"
    filename = os.path.join(DIRNAME, FILE)
    _, _, mwaves = build_obj_from_hdf(filename)

    limits = (4100, 4160)
    samp_figure, samp_peak_df = plot_roi_systolic_pressure_variation(
        mwaves, lims=limits, annotations=False
    )
    record_figure, peaks_df = plot_record_systolic_variation(mwaves, annotations=False)

    def hampel_filter_pandas(
        input_series: pd.Series, window_size: float, n_sigmas: int = 3
    ) -> tuple[pd.Series, list[float]]:
        """https://towardsdatascience.com/outlier-detection-with-hampel-filter-85ddf523c73d"""
        k = 1.4826  # scale factor for Gaussian distribution
        new_series = input_series.copy()

        # helper lambda function
        mad_f = lambda x: np.median(np.abs(x - np.median(x)))

        rolling_median = input_series.rolling(
            window=2 * window_size, center=True
        ).median()
        rolling_mad = k * input_series.rolling(
            window=2 * window_size, center=True
        ).apply(mad_f)
        diff = np.abs(input_series - rolling_median)

        indices = list(np.argwhere(diff > (n_sigmas * rolling_mad)).flatten())
        new_series[indices] = rolling_median[indices]

        return new_series, indices
