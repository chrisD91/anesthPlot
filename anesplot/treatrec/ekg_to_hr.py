#!/usr/bin/env python3
"""Created on Wed Feb 12 16:52:00 2020
@author: cdesbois

function used to treat an EKG signal and extract the heart rate
typically (copy, paste and execute line by line)

(
 NB templates are available in the anesplot/guide folder

you can execute line by line in a file the following process

.. code-block:: python

    import anesplot.record_main as rec
    paths = rec.paths
    rec.get_guide(paths)
    -> fill the choice in the ipython terminal
    -> paste the template in the file

)

0. after
--------
.. code-block:: python

    import pandas as pd

    import anesplot.loadrec.export_reload as io
    import anesplot.treatrec.ekg_to_hr as tohr
    import anesplot.treatrec.wave_func as wf
    from anesplot.slow_waves import MonitorTrend
    from anesplot.fast_waves import MonitorWave

1. load the data in a pandas dataframe:
-----------------------------------------
# through classes rec.MonitorTrend & rec.MonitorWave
# get filename::

    trendname = ''  # fullname
    or
    trendname = rec.choosefile_gui()

# load the data::

    mtrends = rec.MonitorTrend(trendname)
    mwaves = rec.MonitorWave(mtrends.wavename())

# format the name ::

    name = mtrends.header['Patient Name'].title().replace(' ', '')
    name = name[0].lower() + name[1:]

2. treat the ekg wave:
----------------------
# get parameters build a dataframe to work with (waves)
# low pass filtering
# build the beat locations (beat based dataFrame)::

    import anesplot.treatrec.ekg_to_hr as tohr
    from anesplot.treatrec.wave_func import fix_baseline_wander

    params = mwaves.param
    ekg_df = pd.DataFrame(mwaves.data.wekg)
    ekg_df['wekg_lowpass'] = fix_baseline_wander(ekg_df.wekg,
                                                        waves.param['sampling_freq'])
    beatloc_df = tohr.detect_beats(ekg_df.wekg_lowpass, threshold=-1)

3. perform the manual adjustments required:
-------------------------------------------
# based on a graphical display of beat locations, an rr values
# build a container for the manual corrections::

    figure = tohr.plot_beats(ekg_df.wekg_lowpass, beatloc_df)
    beats_tochange_df = pd.DataFrame(columns=beatloc_df.columns.insert(0, 'action'))

# remove or add peaks : zoom on the figure to observe only one peak, then::

    beats_tochange_df = tohr.remove_a_beat(beatloc_df, beats_tochange_df, figure)
    or
    beats_tochange_df = tohr.remove_allbeats(beatloc_df, beats_tochange_df, figure)
    or
    beats_tochange_df = tohr.append_a_beat(ekg_df, beats_tochange_df, figure, yscale=-1)

# combine to update the beat_df with the manual changes::

    beat_df = tohr.update_beat_df(beatloc_df, beats_tochange_df,
                                      path_to_file="", from_file=False)

# save the peaks locations::

    tohr.save_beats(beat_df, beats_tochange_df, savename='', dirpath=None)
    (# or reload
    beatloc_df = pd.read_hdf('beatloc_df.hdf', key='beatlocdf') )

4. go from points values to continuous time:
--------------------------------------------
::

    beatloc_df = tohr.point_to_time_rr(beatloc_df)
    ahr_df = tohr.interpolate_rr(beatloc_df)
    tohr.plot_rr(ahr_df, params)

5. append intantaneous heart rate to the initial data:
------------------------------------------------------
::

    ekg_df = tohr.append_rr_and_ihr_to_wave(ekg_df, ahr_df)
    mwaves.data = tohr.append_rr_and_ihr_to_wave(mwaves.data, ahr_df)
    mtrends.data = tohr.append_ihr_to_trend(mtrends.data, mwaves.data, ekg_df)
    mtrends.data.rename(columns={'hr': 'thr', 'ihr': 'hr'}, inplace=True)

6. save:
--------
::
#    io.export_data_to_hdf(savename=savename, mtrend=mtrends, ttrend= None, mwave=mwaves)
#   tohr.save_trends_data(mtrends.data, savename=name, dirpath='data')
#    tohr.save_waves_data(mwaves.data, savename=name, dirpath='data')
"""
import os
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# import pyperclip
import scipy.signal as sg
from scipy.interpolate import interp1d

# import anesthPlot.treatrec.wave_func as wf
# TODO import the paths construction

# TODO shift the ihr of one beat (ie ihr should be on the end of the interval)

# %%


def detect_beats(
    ser: pd.Series, fs: int = 300, species: str = "horse", threshold: float = -1
) -> pd.DataFrame:
    """
    Detect the peak locations of the beats.

    Parameters
    ----------
    ser : pd.Series
        the EKG time series.
    fs : int, optional (default is 300)
        sampling frequency.
    species : str, optional (default is "horse")
        the species.
    threshold : float, optional (default is -1)
        correction for qRs amplitude. (positive means higher than, negative means lower than)

    Returns
    -------
    df : pandas.DataFrame
    """
    beatlocdf = pd.DataFrame()
    # fs = param.get('fs', 300)
    if species == "horse":
        height = 1.0  # mini
        hr_max = 120  # bpm
        distance = fs * 60 / hr_max  # sec
        prominence = 1.0  # mini/surrounding
        #    width=(2,15)
        #    plateau_size= 1
    else:
        print("no parametrisation performed ... to be done")
        return beatlocdf
    # correcttion
    height *= abs(threshold)
    prominence *= abs(threshold)
    # detect
    sign = threshold / abs(threshold)  # +1 or -1 to invert the signal
    ploc, beats_params = sg.find_peaks(
        ser * sign, height=height, distance=distance, prominence=prominence
    )
    beatlocdf["p_loc"] = ploc
    beatlocdf["x_loc"] = ser.index[beatlocdf.p_loc]
    for key in beats_params.keys():
        beatlocdf[key] = beats_params[key]
    if "peak_heights" in beatlocdf.columns:
        beatlocdf = beatlocdf.rename(columns={"peak_heights": "y_loc"})
        beatlocdf.y_loc *= -1  # inverted trace <-> horse R wave
    return beatlocdf


# ekg_df.wekg_lowpass, beat_df)
def plot_beats(ekgdf: pd.DataFrame, beatlocdf: pd.DataFrame) -> plt.Figure:
    """
    Mark the beat locations on the ekg display and plot rr values over time.

    Parameters
    ----------
    ekgdf : pd.DataFrame.
        waves data (wekg & wekg_lowpass)
    beatlocdf : pd.DataFrame
        the location of the beats (columns used are [p_loc and y_loc]).

    Returns
    -------
    fig : plt.Figure
    """
    fig = plt.figure(figsize=(13, 5))
    fig.suptitle("verify the accuracy of the beat detection")
    ax0 = fig.add_subplot(211)
    ax0.plot(ekgdf.values, label="ekg")
    ax0.set_ylabel("ekg (mV)")
    ax0.set_xlabel("pt value")
    ax0.plot(beatlocdf.p_loc, beatlocdf.y_loc, "o", color="orange", label="R")

    ax1 = fig.add_subplot(212, sharex=ax0)
    ax1.plot(beatlocdf.p_loc[:-1], np.diff(beatlocdf.p_loc), "r-", label="rr")
    ax1.set_ylabel("rr (pt value)")
    ax1.set_xlabel("pt value")
    fig.legend()
    for ax in fig.get_axes():
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
    fig.tight_layout()
    txt0 = "locate the peak to add : zoom and use"
    txt1 = "beats_tochange_df = tohr.add_beat(ekg_df, beats_tochange_df, figure, yscale=-1)"
    fig.text(0.99, 0.03, txt0, ha="right", va="bottom", alpha=0.5)
    fig.text(0.99, 0.00, txt1, ha="right", va="bottom", alpha=0.5, size="small")
    txt0 = "locate the peak to remove : zoom and use"
    txt1 = (
        "beats_tochange_df = tohr.remove_a_beat(beatloc_df, beats_tochange_df, figure)"
    )
    fig.text(0.01, 0.03, txt0, ha="left", va="bottom", alpha=0.5)
    fig.text(0.01, 0.00, txt1, ha="left", va="bottom", alpha=0.5, size="small")
    return fig


def append_a_beat(
    ekgdf: pd.DataFrame,
    beatstochangedf: pd.DataFrame,
    fig: plt.Figure,
    ptxlim: Optional[tuple[int, int]] = None,
    yscale: float = -1,
) -> pd.DataFrame:
    """
    Tag the beat of the figure as append to the beatstochangedf.action.

    Parameters
    ----------
    ekgdf : pd.Dataframe
        waves data (wekg_lowpass).
    beatstochangedf : pd.Dataframe
        the beat to add or remove (point based toAppend & toRemove)
    fig : plt.Figure
        the figure to get the location.
    ptxlim : tuple, optional (default is None)
        ptBasedLim optional to give it manually
    yscale : float, optional (default is -1)
        amplitude mutliplication factor for detection.

    Returns
    -------
    beatstochangedf : pd.DataFrame
        incremented changedf (pt location).

    """
    # find the limits of the figure
    if ptxlim is None:
        ptxlims = fig.get_axes()[0].get_xlim()
        ptxlim = (int(ptxlims[0]), int(ptxlims[1]))
    # restrict area around the undetected pic (based on pt x val)
    # locate the beat (external call)
    onepoint_beatlocdf = detect_beats(
        ekgdf.wekg_lowpass.loc[ptxlim[0] : ptxlim[1]], threshold=yscale
    )
    onepoint_beatlocdf["action"] = "append"
    if len(onepoint_beatlocdf) < 1:
        print("no beat founded")
        return beatstochangedf
    found_loc = onepoint_beatlocdf.p_loc.values[0]
    y_loc = onepoint_beatlocdf.y_loc.values[0]
    # reassign the pt value
    p_loc = ekgdf.wekg_lowpass.loc[ptxlim[0] : ptxlim[1]].index[found_loc]
    onepoint_beatlocdf["p_loc"] = p_loc
    print("founded ", p_loc)
    # append to figure
    fig.get_axes()[0].plot(p_loc, y_loc, "og")
    onepoint_beatlocdf.p_loc = p_loc
    onepoint_beatlocdf.left_bases += p_loc - found_loc
    onepoint_beatlocdf.right_bases.values[0] += p_loc - found_loc
    # insert in the beatstochangedf
    beatstochangedf = pd.concat(
        [beatstochangedf, onepoint_beatlocdf], ignore_index=True
    )
    return beatstochangedf


def remove_a_beat(
    beatlocdf: pd.DataFrame,
    beatstochangedf: pd.DataFrame,
    fig: plt.Figure,
    ptxlim: Optional[tuple[int, int]] = None,
) -> pd.DataFrame:
    """
    Tag the beat of the figure as 'remove' to the beatstochangedf.action.

    Parameters
    ----------
    beatlocdf : pd.Dataframe
        beat position (point based location : p_locs)
    beatstochangedf : pd.Dataframe
        the beat to add or remove (point based toAppend & toRemove)
    fig : plt.Figure
         the figure to get the location.
    ptxlim : tuple, optional (default is None)
         ptBasedLim optional to give it manually

    Returns
    -------
    beatstochangedf : pd.DataFrame
        incremented changedf (pt location).
    """
    # find the limits of the figure
    if ptxlim is None:
        ptxlims = fig.get_axes()[0].get_xlim()
        ptxlim = (int(ptxlims[0]), int(ptxlims[1]))

    toremove = beatlocdf.loc[
        (ptxlim[0] < beatlocdf.p_loc) & (beatlocdf.p_loc < ptxlim[1])
    ]
    if len(toremove) > 1:
        print("several beats detected")
        return beatstochangedf
    # mark on plot
    ax = fig.get_axes()[0]
    for ploc, yloc in toremove[["p_loc", "y_loc"]].values:
        ax.plot(ploc, yloc, "Xr")
    # append to beatstochangedf
    toremove.insert(loc=0, column="action", value="remove")
    beatstochangedf = pd.concat([beatstochangedf, toremove], ignore_index=True)
    print(f"{len(toremove)} beats to remove : {toremove.p_loc.values} ")
    return beatstochangedf


def remove_allbeats(
    beatlocdf: pd.DataFrame,
    beatstochangedf: pd.DataFrame,
    fig: plt.Figure,
    ptxlim: Optional[tuple[int, int]] = None,
) -> pd.DataFrame:
    """
    Tag all beats in the figure as 'remove' in beatstochangedf.action.

    Parameters
    ----------
    beatlocdf : pd.Dataframe
        beat position (point based location : p_locs)
    beatstochangedf : pd.Dataframe
        the beat to add or remove (point based toAppend & toRemove)
    fig : plt.Figure
         the figure to get the location.
    ptxlim : TYPE, optional (default is None)
         ptBasedLim optional to give it manually
    yscale : TYPE, optional (default is -1)
        amplitude threshold for detection.

    Returns
    -------
    beatstochangedf : pd.DataFrame
    incremented changedf (pt location).

    """
    # find the limits of the figure
    if ptxlim is None:
        ptxlims = fig.get_axes()[0].get_xlim()
        ptxlim = (int(ptxlims[0]), int(ptxlims[1]))
    toremove = beatlocdf.loc[
        (ptxlim[0] < beatlocdf.p_loc) & (beatlocdf.p_loc < ptxlim[1])
    ]
    # mark on plot
    ax = fig.get_axes()[0]
    for ploc, yloc in toremove[["p_loc", "y_loc"]].values:
        ax.plot(ploc, yloc, "Xr")
    # append to beatstochangedf
    toremove.insert(loc=0, column="action", value="remove")
    beatstochangedf = pd.concat([beatstochangedf, toremove], ignore_index=True)
    print(f"{len(toremove)} beats to remove : {toremove.p_loc.values} ")
    return beatstochangedf


# TODO append the missing R in case of BAV2


def save_beats(
    beatlocdf: pd.DataFrame,
    beatstochangedf: pd.DataFrame,
    savename: str = "",
    dirpath: Optional[str] = None,
    csv: bool = False,
) -> None:
    """
    Save the beats locations as csv and hd5 file.

    Parameters
    ----------
    beatlocdf : pd.dataframes
    beatstochangedf : pandas.dataframe
    savename : filename
    dirpath : path to save in
    csv: bool (to save as csv)

    output
    ------
    None
        hdf file, key='beatlocdf'
    """
    subf = ""
    if dirpath is None:
        dirpath = os.getcwd()
        if not os.path.basename(os.getcwd()) == "data":
            subf = "data"
            if not os.path.isdir("data"):
                os.mkdir("data")
    filename = "_".join([savename, "beatlocdf"]).strip("_")
    name = os.path.join(dirpath, subf, filename)
    beatlocdf.to_hdf(name + ".hdf", mode="w", key="beatlocdf")
    beatstochangedf.to_hdf(name + ".hdf", mode="a", key="beatstochangedf")
    if csv:
        beatlocdf.to_csv(name + ".csv")
        filename = "_".join([savename, "beatstochangedf"]).strip("_")
        name = os.path.join(dirpath, subf, filename)
        beatstochangedf.to_csv(name + ".csv")


# %% apply changes to the beatlocdf


def adjust_type(beatdf: pd.DataFrame) -> pd.DataFrame:
    """
    adjust the types for the beat dataframes

    Parameters
    ----------
    beatdf : pd.DataFrame
        the input.

    Returns
    -------
    beatdf : ps.DataFrame
        the output.

    """
    for col in ["p_loc", "left_bases", "right_bases"]:
        if col in beatdf.columns:
            beatdf[col] = beatdf[col].astype(int)
    for col in ["action"]:
        if col in beatdf.columns:
            beatdf[col] = beatdf[col].astype(str)
    for col in ["x_loc", "y_loc", "prominences"]:
        if col in beatdf.columns:
            beatdf[col] = beatdf[col].astype(float)
    return beatdf


def update_beatloc_df(
    beatlocdf: pd.DataFrame,
    beatstochangedf: pd.DataFrame,
    path_to_file: str = "",
    from_file: bool = False,
) -> pd.DataFrame:
    """
    Implement in the beat location the manual corrections.

    Parameters
    ----------
    beatlocdf : pd.DataFrame
        beat position (point based location : p_locs)
    beatstochangedf : pd.DataFrame
        the beat to add or remove (point based toAppend & toRemove)
    path_to_file : str, optional (default is "")
        dirpath to the saved file.
    from_file : bool, optional (default is False)
        fromFile = True force the disk loading of the dataframes

    Returns
    -------
    beatlocdf : pd.DataFrame
        updated beat position
    """
    if from_file:
        name = os.path.join(path_to_file, "beatlocdf.csv")
        try:
            beatlocdf = pd.read_csv(name, index_col=0)
        except FileNotFoundError:
            print(f"file is not present ({name})")
        name = os.path.join(path_to_file, "toChange.csv")
        beatstochangedf = pd.read_csv(name, index_col=0)
    beatstochangedf = adjust_type(beatstochangedf)
    beatstochangedf = beatstochangedf.set_index("action")
    to_remove = beatstochangedf.loc["remove"].p_loc
    beatlocdf = beatlocdf.set_index("p_loc").drop(to_remove, errors="ignore")
    beatlocdf.reset_index(inplace=True)
    # append
    to_append = beatstochangedf.loc["append"]
    beatlocdf = pd.concat([beatlocdf, to_append], ignore_index=True)
    # rebuild
    beatlocdf.drop_duplicates(keep=False, inplace=True)
    beatlocdf = beatlocdf.sort_values(by="p_loc").reset_index(drop=True)
    beatlocdf = adjust_type(beatlocdf)
    return beatlocdf


# %% =========================================
def point_to_time_rr(beatlocdf: pd.DataFrame, fs: Optional[int] = None) -> pd.DataFrame:
    """
    Compute rr intervals (from pt to time).

    Parameters
    ----------
    beatlocdf : pd.DataFrame
        beat position (point based location : p_locs)
    fs : int, optional (default is None -> 300)
        the sampling frequency

    Returns
    -------
    beatlocdf : pd.DataFrame
        beat position updated with rrvalues:
        'rr' =  rr duration
        'rrDiff' = rrVariation
        'rrSqDiff' = rrVariation^2
    """
    if fs is None:
        fs = 300
    # compute rr intervals
    #    beat_df['rr'] = np.diff(beat_df.p_loc)
    beatlocdf["rr"] = beatlocdf.p_loc.shift(-1) - beatlocdf.p_loc  # pt duration
    beatlocdf.rr = beatlocdf.rr / fs * 1_000  # time duration
    # remove outliers (HR < 20)
    if len(beatlocdf.loc[beatlocdf.rr > 20_000]) > 0:
        beatlocdf.loc[beatlocdf.rr > 20_000, ["rr"]] = np.nan
    beatlocdf = beatlocdf.interpolate()
    beatlocdf = beatlocdf.dropna(how="all")
    beatlocdf = beatlocdf.dropna(axis=1, how="all")
    # compute variation
    beatlocdf["rrDiff"] = abs(beatlocdf.rr.shift(-1) - beatlocdf.rr)
    beatlocdf["rrSqDiff"] = (beatlocdf.rr.shift(-1) - beatlocdf.rr) ** 2
    return beatlocdf


def interpolate_rr(beatlocdf: pd.DataFrame, kind: Optional[str] = None) -> pd.DataFrame:
    """
    Interpolate the beat_df (pt -> time values).

    Parameters
    ----------
    beatlocdf : pd.DataFrame
        beat position (point based location : p_locs).
    kind : str, optional (default is None -> "cubic")
        interpolation (in ['linear', 'cubic']

    Returns
    -------
    ahr_df : pd.DataFrame
        evenly spaced data with 'espts' = evenly spaced points & 'rrInterpol' = interpolated rr
    """
    if kind is None:
        kind = "cubic"
    ahr_df = pd.DataFrame()
    # prepare = sorting and removing possible duplicates
    beatlocdf = beatlocdf.sort_values(by="p_loc")
    beatlocdf = beatlocdf.drop_duplicates("p_loc")

    first_beat_pt = int(beatlocdf.iloc[0].p_loc)
    last_beat_pt = int(beatlocdf.iloc[-2].p_loc)  # last interval
    newx = np.arange(first_beat_pt, last_beat_pt)
    # interpolate rr
    rrx = beatlocdf.p_loc[:-1].values  # rr locations
    rry = beatlocdf.rr[:-1].values  # rr values
    interp = interp1d(rrx, rry, kind=kind)
    newy = interp(newx)
    ahr_df["espts"] = newx
    ahr_df["rrInterpol"] = newy
    # interpolate rrDiff
    rry = beatlocdf.rrDiff[:-1].values
    interp = interp1d(rrx, rry, kind=kind)
    newy = interp(newx)
    ahr_df["rrInterpolDiff"] = newy
    # interpolate rrSqrDiff
    rry = beatlocdf.rrSqDiff[:-1].values
    interp = interp1d(rrx, rry, kind=kind)
    newy = interp(newx)
    ahr_df["rrInterpolSqDiff"] = newy
    return ahr_df


def plot_rr(
    ahr_df: pd.DataFrame, param: dict[str, Any], showhr: bool = False
) -> plt.Figure:
    """
    Plot RR vs pt values + rrSqDiff.

    Parameters
    ----------
    ahr_df : pd.DataFrame
        DESCRIPTION.
    param : dict
        containing 'sampling_freq' as key.
    showhr : bool, optional (default is False)
        to display HR instead of rr
    Returns
    -------
    fig : plt.Figure
    """
    fs = param["sampling_freq"]

    fig = plt.figure(figsize=(13, 5))
    ax = fig.add_subplot(211)
    ax.set_title("RR duration")
    xvals = ahr_df.espts.values / fs / 60
    ax.plot(xvals, ahr_df.rrInterpol.values, color="tab:blue", alpha=0.8)
    ax.set_ylabel("msec")
    ax.grid()
    lims = ahr_df.rrInterpol.quantile([0.01, 0.99])
    ax.set_ylim(lims)
    ax2 = fig.add_subplot(212, sharex=ax)
    if showhr:
        ax2.set_title("heart rate")
        yvals = 1 / ahr_df.rrInterpol.values * 60 * 1000
        ax2.plot(xvals, yvals, "-", color="tab:green", alpha=0.8)
        lims = (
            np.quantile(1 / ahr_df.rrInterpol.values * 60 * 1000, q=0.01),
            np.quantile(1 / ahr_df.rrInterpol.values * 60 * 1000, q=0.99),
        )
        ax2.set_ylim(lims)
        ax2.set_ylabel("BPM")
    else:
        ax2.set_title("RR sqVariation")
        ax2.plot(
            xvals, ahr_df.rrInterpolSqDiff.values, "-", color="tab:green", alpha=0.8
        )
        lims = (0, ahr_df.rrInterpolSqDiff.quantile(0.98))
        ax2.set_ylim(lims)
    ax2.set_xlabel(f"min (fs= {int(fs)}))")
    ax.spines["bottom"].set_visible(False)
    ax.get_xaxis().set_visible(False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
        ax2.spines[spine].set_visible(False)
    #    file = os.path.basename(filename)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.tight_layout()
    return fig


# %% heart rate

# TOTO = correct wave.datetime (multiple repetitions of the same value)


def append_rr_and_ihr_to_wave(ekgdf: pd.DataFrame, ahrdf: pd.DataFrame) -> pd.DataFrame:
    """
    Append rr and ihr to the waves based on pt value (ie index).

    Parameters
    ----------
    ekgdf : pd.DataFrame
        waves data
    ahrdf : pd.DataFrame
        evenly spaced interpolated data.

    Returns
    -------
    df : pd.DataFrame
        added iHR to ekgdf.
    """
    df = pd.concat([ekgdf, ahrdf.set_index("espts")], axis=1)
    df["ihr"] = 1 / df.rrInterpol * 60 * 1000
    print("added instantaneous heart rate to a Wave dataframe")
    return df


def plot_agreement(trenddf: pd.DataFrame) -> plt.Figure:
    """Plot ip1HR & ihr to check agreement."""
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(trenddf.hr)
    ax.plot(trenddf.hr, label="ip1pr")
    ax.plot(trenddf.ihr, label="ihr")
    ax.legend()
    return fig


def append_ihr_to_trend(
    trenddf: pd.DataFrame, wavedf: pd.DataFrame, ekgdf: pd.DataFrame
) -> pd.DataFrame:
    """
    Append 'ihr' (instataneous heart rate) to the trends.

    Parameters
    ----------
    trenddf : pd.DataFrame
        a monitor trend recording data (typically a MonitorTrend.data).
    wavedf : pd.DataFrame
        a monitor wave recording data (typillay a MonitorWave.data).
    ekgdf : pd.DataFrame
        the ekg dataframe.

    Returns
    -------
    trenddf : pd.DataFrame
        the updated trend recording data.
    """
    # build a new index
    ratio = len(wavedf) / len(trenddf)
    ser = (wavedf.index.to_series() / ratio).astype(int)
    # fill the data
    ihrdf = pd.DataFrame()
    ihrdf["ihr"] = 1 / ekgdf.rrInterpol * 60 * 1000
    # downsample
    ihrdf = ihrdf["ihr"].groupby(ser).median()
    # concatenate
    if "ihr" in trenddf.columns:
        trenddf.drop("ihr", axis=1, inplace=True)
    trenddf = pd.concat([trenddf, ihrdf], axis=1)
    print("added instantaneous heart rate to a TREND dataframe")
    return trenddf


def save_trends_data(
    trenddf: pd.DataFrame, savename: str = "", dirpath: str = "data"
) -> None:
    """
    Save the trends data to a hd5 file, including an ihr column (key='trends_data').

    Parameters
    ----------
    trenddf : pd.DataFrame
        the (updated) trend recording.
    savename : str, optional (default is "" ->  _trendData)
        (short) file name to use
    dirpath : str, optional
        DESCRIPTION. The default is cwd.

    Returns
    -------
    None.
    """
    if dirpath is None:
        dirpath = os.getcwd()
    if not os.path.isdir(dirpath):
        print("folder {dirpath} does not exist, please build it")
        return
    for col in trenddf.columns:
        if trenddf[col].dtype == "category":
            trenddf[col] = trenddf[col].astype(str)
    filename = savename + "_" + "trendData"
    if filename.startswith("_"):
        filename = filename[1:]
    fullname = os.path.join(dirpath, filename)
    # trenddf.to_csv(fullname + ".csv")
    trenddf.to_hdf(fullname + ".hdf", mode="w", key="trends_data")
    print(f"saved trendDataframe to '{filename + '.hdf'}', key='trends_data'")


def save_waves_data(
    wavedf: pd.DataFrame, savename: str = "", dirpath: str = "data"
) -> None:
    """
    Save the waves data to a csv and hd5 file, including an ihr column (key='waves_data').

    Parameters
    ----------
    wavedf : pd.DataFrame
        the (updated) trend recording.
    savename : str, optional (default is "" ->  _trendData)
        (short) file name to use
    dirpath : str, optional (default <-> cwd)
        the path to the directory to use

    Returns
    -------
    None.
    """
    if dirpath is None:
        dirpath = os.getcwd()
    if not os.path.isdir(dirpath):
        print("folder {dirpath} does not exist, please build it")
        return
    filename = savename + "_" + "waveData"
    if filename.startswith("_"):
        filename = filename[1:]
    fullname = os.path.join(dirpath, filename)
    # wavedf.to_csv(fullname + ".csv")
    wavedf.to_hdf(fullname + ".hdf", mode="w", key="waves_data")
    print(f"saved waveDataframe to '{filename + '.hdf'}', key='waves_data'")


# ekg_df = append_rr_and_ihr_to_wave(ekg_df, ahr_df)
# waves.data = append_rr_and_ihr_to_wave(waves.data, ahr_df)
# trends.data = append_ihr_to_trend(trends.data, waves.data, ekg_df)


# ################################

# if __name__ == '__main__':
#     # view if files are loaded
#     print(check())
#     #%detect beats after record_main for monitorWave
#     params = monitorWave.param
#     #data = monitorWave.data
#     # build a dataframe to work with (waves)
#     ekg_df = pd.DataFrame(monitorWave.data.wekg)

#     #low pass filtering
#     ekg_df['wekg_lowpass'] = wf.fix_baseline_wander(ekg_df.wekg,
#                                                     monitorWave.param['fs'])
#     # beats locations (beat based dataFrame)
#     beat_df = detect_beats(ekg_df.wekg_lowpass, params)
#     #plot
#     figure = plot_beats(ekg_df.wekg_lowpass, beat_df)

#     #fs=300
#     beat_df = point_to_time_rr(beat_df, monitorWave.param)
#     hr_df = interpolate_rr(beat_df)
#     figure = plot_rr(hr_df, params, HR=True)
