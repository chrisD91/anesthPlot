#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Wed Feb 12 16:52:00 2020
@author: cdesbois

function used to treat an EKG signal and extract the heart rate
typically (copy, paste and execute line by line)

(
 NB templates are available in the anesplot/guide folder
 from the main entry port use get_guide())


0. after
--------
::
    import pandas as pd

    import anesplot.record_main as rec
    from anesplot.treatrec import ekg_to_hr as tohr

1. load the data in a pandas dataframe:
---------------------------------------

(through classes rec.MonitorTrend & rec.MonitorWave)

::

    trendname = ''  # fullname
    or
    trendname = rec.choosefile_gui()

::

    wavename = rec.trendname_to_wavename(trendname)
    -
    # load the data
    trends = rec.MonitorTrend(trendname)
    waves = rec.MonitorWave(wavename)
    -
    # format the name
    name = trends.header['Patient Name'].title().replace(' ', '')
    name = name[0].lower() + name[1:]

2. treat the ekg wave:
----------------------

    - get parameters
    - build a dataframe to work with (waves)
    - low pass filtering
    - build the beat locations (beat based dataFrame)::

        params = waves.param
        ekg_df = pd.DataFrame(waves.data.wekg)
        ekg_df['wekg_lowpass'] = rec.wf.fix_baseline_wander(ekg_df.wekg,
                                                waves.param['sampling_freq'])
        beat_df = tohr.detect_beats(ekg_df.wekg_lowpass, threshold=1)

3. perform the manual adjustments required:
-------------------------------------------

    - based on a graphical display of beat locations, an rr values
    - build a container for the manual corrections::

        figure = tohr.plot_beats(ekg_df.wekg_lowpass, beat_df)
        to_change_df = pd.DataFrame(columns=beat_df.columns.insert(0, 'action'))

    - remove or add peaks : zoom on the figure to observe only one peak, then::

        to_change_df = tohr.remove_beat(beat_df, ekg_df, to_change_df, figure)
        or
        to_change_df = tohr.append_beat(beat_df, ekg_df, to_change_df, figure,
                                        yscale=1)

    - combine to update the beat_df with the manual changes::

        beat_df = tohr.update_beat_df(beat_df, to_change_df,
                                      path_to_file="", from_file=False)

    - save the peaks locations::

        tohr.save_beats(beat_df, to_change_df, savename='', dirpath=None)
        (# or reload
        beat_df = pd.read_hdf('beatDf.hdf', key='beatDf') )

4. go from points values to continuous time:
--------------------------------------------
::

    beat_df = tohr.compute_rr(beat_df)
    ahr_df = tohr.interpolate_rr(beat_df)
    tohr.plot_rr(ahr_df, params)

5. append intantaneous heart rate to the initial data:
------------------------------------------------------
::

    ekg_df = tohr.append_rr_and_ihr_to_wave(ekg_df, ahr_df)
    waves.data = tohr.append_rr_and_ihr_to_wave(waves.data, ahr_df)
    trends.data = tohr.append_ihr_to_trend(trends.data, waves.data, ekg_df)

6. save:
--------
::

    tohr.save_trends_data(trends.data, savename=name, dirpath='data')
    tohr.save_waves_data(waves.data, savename=name, dirpath='data')

____
"""

import os
import pyperclip
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.signal as sg
from scipy.interpolate import interp1d

# import anesthPlot.treatrec.wave_func as wf
# TODO import the paths construction

# TODO shift the ihr of one beat (ie ihr should be on the end of the interval)

# %%


def detect_beats(
    ser: pd.Series, fs: int = 300, species: str = "horse", threshold: float = 1
) -> pd.DataFrame:
    """
    detect the peak locations of the beats

    Parameters
    ----------
    ser : pd.Series
        the EKG time series.
    fs : int, optional (default is 300)
        sampling frequency.
    species : str, optional (default is "horse")
        the species.
    threshold : float, optional (default is 1)
        correction for qRs amplitude.

    Returns
    -------
    df : pandas.DataFrame

    """

    df = pd.DataFrame()
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
        return df
    # correcttion
    height *= threshold
    prominence *= threshold
    # detect
    pk, beats_params = sg.find_peaks(
        ser * -1, height=height, distance=distance, prominence=prominence
    )
    df["p_loc"] = pk
    for key in beats_params.keys():
        df[key] = beats_params[key]
    if "peak_heights" in df.columns:
        df = df.rename(columns={"peak_heights": "y_loc"})
        df.y_loc *= -1  # inverted trace <-> horse R wave
    return df


# ekg_df.wekg_lowpass, beat_df)
def plot_beats(ekgdf: pd.DataFrame, beatdf: pd.DataFrame) -> plt.Figure:
    """
    plot beat location on ekg display and rr values over time

    Parameters
    ----------
    ekgdf : pd.DataFrame.
        waves data (wekg & wekg_lowpass)
    beatdf : pd.DataFrame
        the location of the beats (columns used are [p_loc and y_loc]).

    Returns
    -------
    fig : matplotlib.pyplot.Figure

    """

    fig = plt.figure(figsize=(13, 5))
    fig.suptitle("verify the accuracy of the beat detection")
    ax0 = fig.add_subplot(211)
    ax0.plot(ekgdf.values, label="ekg")
    ax0.set_ylabel("ekg (mV)")
    ax0.set_xlabel("pt value")
    ax0.plot(beatdf.p_loc, beatdf.y_loc, "o", color="orange", label="R")

    ax1 = fig.add_subplot(212, sharex=ax0)
    ax1.plot(beatdf.p_loc[:-1], np.diff(beatdf.p_loc), "r-", label="rr")
    ax1.set_ylabel("rr (pt value)")
    ax1.set_xlabel("pt value")
    fig.legend()
    for ax in fig.get_axes():
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
    fig.tight_layout()
    txt0 = "locate the peak to add : zoom and use"
    txt1 = "to_change_df = tohr.add_beat(beat_df, ekg_df, to_change_df, figure)"
    fig.text(0.99, 0.03, txt0, ha="right", va="bottom", alpha=0.5)
    fig.text(0.99, 0.00, txt1, ha="right", va="bottom", alpha=0.5, size="small")
    txt0 = "locate the peak to remove : zoom and use"
    txt1 = "to_change_df = tohr.remove_beat(beat_df, ekg_df, to_change_df, figure, scale=1)"
    fig.text(0.01, 0.03, txt0, ha="left", va="bottom", alpha=0.5)
    fig.text(0.01, 0.00, txt1, ha="left", va="bottom", alpha=0.5, size="small")
    return fig


def append_beat(
    beatdf: pd.DataFrame,
    ekgdf: pd.DataFrame,
    tochangedf: pd.DataFrame,
    fig: plt.Figure,
    lim: Tuple = None,
    yscale: float = 1,
) -> pd.DataFrame:
    """
    append a beat coordonate from the figure to the tochangedf['toAppend']

    Parameters
    ----------
    beatdf : pd.Dataframe
        beat position (point based location : p_locs)
    ekgdf : pd.Dataframe
        waves data (wekg_lowpass).
    tochangedf : pd.Dataframe
        the beat to add or remove (point based toAppend & toRemove)
    fig : plt.Figure
        the figure to get the location.
    lim : TYPE, optional (default is None)
        ptBasedLim optional to give it manually
    yscale : TYPE, optional (default is 1)
        amplitude mutliplication factor for detection.

    Returns
    -------
    tochangedf : pd.DataFrame
        incremented changedf (pt location).


    methods :

        locate the beat in the figure, append to a dataframe['toAppend']
        0.: if not present : build a dataframe:
            >>> to_change_df = pd.DataFrame(columns=['toAppend', 'toRemove'])

        1.: locate the extra beat in the figure (cf plot_beats())
            and zoom to observe only a negative peak

        2.: call the function:
            >>> to_change_df = remove_beat(beatdf, ekgdf, tochangedf, fig)
            -> the beat parameters will be added the dataFrame

        .in the end of the manual check, update the beat_df
              - first : save beat_df and to_change_df
              - second : run:
                  >>> beat_df = update_beat_df())
    """

    # find the limits of the figure
    if lim is None:
        lims = fig.get_axes()[0].get_xlim()
        lim = (int(lims[0]), int(lims[1]))
    # restrict area around the undetected pic (based on pt x val)
    df = ekgdf.wekg_lowpass.loc[lim[0] : lim[1]]
    # locate the beat (external call)
    onepoint_beatdf = detect_beats(df, threshold=yscale)
    onepoint_beatdf["action"] = "append"
    if len(onepoint_beatdf) < 1:
        print("no beat founded")
        return tochangedf
    found_loc = onepoint_beatdf.p_loc.values[0]
    y_loc = onepoint_beatdf.y_loc.values[0]
    # reassign the pt value
    p_loc = ekgdf.wekg_lowpass.loc[lim[0] : lim[1]].index[found_loc]
    onepoint_beatdf["p_loc"] = p_loc
    print("founded ", p_loc)
    # append to figure
    fig.get_axes()[0].plot(p_loc, y_loc, "og")
    onepoint_beatdf.p_loc = p_loc
    onepoint_beatdf.left_bases += p_loc - found_loc
    onepoint_beatdf.right_bases.values[0] += p_loc - found_loc
    # insert in the tochangedf
    # beatdf = beatdf.drop_duplicates('p_loc')
    tochangedf = tochangedf.append(onepoint_beatdf)
    # beware : a copy of the dataframe is returned
    return tochangedf


def remove_beat(
    beatdf: pd.DataFrame,
    ekgdf: pd.DataFrame,
    tochangedf: pd.DataFrame,
    fig: plt.figure,
    lim: Tuple = None,
) -> pd.DataFrame:
    """
    remove a beat coordinate from the figure to the tochangedf['toRemove']

    Parameters
    ----------
    beatdf : pd.Dataframe
        beat position (point based location : p_locs)
    ekgdf : pd.Dataframe
        waves data (wekg_lowpass).
    tochangedf : pd.Dataframe
        the beat to add or remove (point based toAppend & toRemove)
    fig : plt.Figure
         the figure to get the location.
    lim : TYPE, optional (default is None)
         ptBasedLim optional to give it manually
    yscale : TYPE, optional (default is 1)
        amplitude mutliplication factor for detection.

    Returns
    -------
    tochangedf : pd.DataFrame
    incremented changedf (pt location).

    locate the beat in the figure, append to a dataframe['toRemove']

    0.: if not present build a dataframe:
        >>> to_change_df = pd.DataFrame(columns=['toAppend', 'toRemove'])

    1.: locate the extra beat in the figure (cf plot_beats())
        and zoom to observe only a negative peak

    2.: call the function:::
        >>> to_change_df = remove_beat(beatdf, ekgdf, tochangedf, fig)
        -> the beat parameters will be added the dataFrame

    .(in the end of the manual check, update the beat_df

        - first : save beat_df and to_change_df

        - second : run
            >>> beat_df = update_beat_df())
    """

    # find the limits of the figure
    if lim is None:
        lims = fig.get_axes()[0].get_xlim()
        lim = (int(lims[0]), int(lims[1]))
    position = beatdf.p_loc[(lim[0] < beatdf.p_loc) & (beatdf.p_loc < lim[1])]
    iloc = position.index.values[0]
    ptloc = position.values  # pt values of the peak
    if len(ptloc) > 1:
        print("several beats detected")
        return tochangedf
    pos = int(ptloc[0])  # array -> value
    # mark on the graph
    p_loc, y_loc = beatdf.loc[iloc, ["p_loc", "y_loc"]]
    p_loc = int(p_loc)
    ax = fig.get_axes()[0]
    ax.plot(p_loc, y_loc, "Xr")
    # mark to remove
    onepoint_beatdf = beatdf.loc[iloc].copy()
    onepoint_beatdf["action"] = "remove"
    tochangedf = tochangedf.append(onepoint_beatdf, ignore_index=True)
    # beatdf.loc[pos, ['y_loc']] = np.NaN
    print("position is ", pos)
    return tochangedf


# TODO append the missing R in case of BAV2


def save_beats(
    beatdf: pd.DataFrame,
    tochangedf: pd.DataFrame,
    savename: str = "",
    dirpath: str = None,
    csv: bool = False,
):
    """
    save the beats locations as csv and hd5 file

    parameters
    ----------
    beatdf : pd.dataframes
    tochangedf : pandas.dataframe
    savename : filename
    dirpath : path to save in
    csv: bool (to save as csv)

    output
    ------
    hdf file, key='beatDf'
    """
    if dirpath is None:
        dirpath = os.getcwd()
    filename = savename + "_" + "beatDf"
    if filename.startswith("_"):
        filename = filename[1:]
    name = os.path.join(dirpath, filename)
    beatdf.to_hdf(name + ".hdf", mode="w", key="beatDf")
    tochangedf.to_hdf(name + ".hdf", mode="a", key="tochangeDf")
    if csv:
        beatdf.to_csv(name + ".csv")
        filename = savename + "_" + "tochangedf"
        if filename.startswith("_"):
            filename = filename[1:]
        name = os.path.join(dirpath, filename)
        tochangedf.to_csv(name + ".csv")


# %% apply changes to the beatdf


def update_beat_df(
    beatdf: pd.DataFrame,
    tochangedf: pd.DataFrame,
    path_to_file: str = "",
    from_file: bool = False,
):
    """
    implement in the beat location the manual corrections

    Parameters
    ----------
    beatdf : pd.DataFrame
        beat position (point based location : p_locs)
    tochangedf : pd.DataFrame
        the beat to add or remove (point based toAppend & toRemove)
    path_to_file : str, optional (default is "")
        dirpath to the saved file.
    from_file : bool, optional (default is False)
        fromFile = True force the disk loading of the dataframes

    Returns
    -------
    beatdf : pd.DataFrame
        updated beat position

    """

    if from_file:
        name = os.path.join(path_to_file, "beatDf.csv")
        try:
            beatdf = pd.read_csv(name, index_col=0)
        except FileNotFoundError:
            print(f"file is not present ({name})")
        name = os.path.join(path_to_file, "toChange.csv")
        tochangedf = pd.read_csv(name, index_col=0)
    for col in ["p_loc", "left_bases", "right_bases"]:
        tochangedf[col] = tochangedf[col].astype(int)
    # remove
    to_remove = tochangedf.loc[tochangedf["action"] == "remove", ["p_loc"]]
    to_remove = to_remove.values.flatten().tolist()
    beatdf = beatdf.set_index("p_loc").drop(to_remove, errors="ignore")
    beatdf.reset_index(inplace=True)
    # append
    temp_df = tochangedf.loc[tochangedf["action"] == "append"].set_index("action")
    beatdf = beatdf.append(temp_df, ignore_index=True)
    # rebuild
    beatdf.drop_duplicates(keep=False, inplace=True)
    beatdf = beatdf.sort_values(by="p_loc").reset_index(drop=True)
    return beatdf


# beat_df = update_beat_df(beat_df, to_change_df)

# %% =========================================
def compute_rr(beatdf: pd.DataFrame, fs: int = None) -> pd.DataFrame:
    """
    compute rr intervals (from pt to time)

    Parameters
    ----------
    beatdf : pd.DataFrame
        beat position (point based location : p_locs)
    fs : int, optional (default is None -> 300)
        the sampling frequency

    Returns
    -------
    beatdf : pd.DataFrame
        beat position updated with rrvalues:
        'rr' =  rr duration
        'rrDiff' = rrVariation
        'rrSqDiff' = rrVariation^2
    """

    if fs is None:
        fs = 300
    # compute rr intervals
    #    beat_df['rr'] = np.diff(beat_df.p_loc)
    beatdf["rr"] = beatdf.p_loc.shift(-1) - beatdf.p_loc  # pt duration
    beatdf.rr = beatdf.rr / fs * 1_000  # time duration
    # remove outliers (HR < 20)
    if len(beatdf.loc[beatdf.rr > 20_000]) > 0:
        beatdf.loc[beatdf.rr > 20_000, ["rr"]] = np.nan
    beatdf = beatdf.interpolate()
    beatdf = beatdf.dropna(how="all")
    beatdf = beatdf.dropna(axis=1, how="all")
    # compute variation
    beatdf["rrDiff"] = abs(beatdf.rr.shift(-1) - beatdf.rr)
    beatdf["rrSqDiff"] = (beatdf.rr.shift(-1) - beatdf.rr) ** 2
    return beatdf


def interpolate_rr(beatdf: pd.DataFrame, kind: str = None) -> pd.DataFrame:
    """
    interpolate the beat_df (pt -> time values)

    Parameters
    ----------
    beatdf : pd.DataFrame
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
    beatdf = beatdf.sort_values(by="p_loc")
    beatdf = beatdf.drop_duplicates("p_loc")

    first_beat_pt = int(beatdf.iloc[0].p_loc)
    last_beat_pt = int(beatdf.iloc[-2].p_loc)  # last interval
    newx = np.arange(first_beat_pt, last_beat_pt)
    # interpolate rr
    rrx = beatdf.p_loc[:-1].values  # rr locations
    rry = beatdf.rr[:-1].values  # rr values
    f = interp1d(rrx, rry, kind=kind)
    newy = f(newx)
    ahr_df["espts"] = newx
    ahr_df["rrInterpol"] = newy
    # interpolate rrDiff
    rry = beatdf.rrDiff[:-1].values
    f = interp1d(rrx, rry, kind=kind)
    newy = f(newx)
    ahr_df["rrInterpolDiff"] = newy
    # interpolate rrSqrDiff
    rry = beatdf.rrSqDiff[:-1].values
    f = interp1d(rrx, rry, kind=kind)
    newy = f(newx)
    ahr_df["rrInterpolSqDiff"] = newy
    return ahr_df


def plot_rr(ahr_df: pd.DataFrame, param: dict, HR: bool = False) -> plt.Figure:
    """
    plot RR vs pt values + rrSqDiff

    Parameters
    ----------
    ahr_df : pd.DataFrame
        DESCRIPTION.
    param : dict
        containing 'sampling_freq' as key.
    HR : bool, optional (default is False)
        to display HR instead of rr
    Returns
    -------
    fig : plt.Figure

    """

    fs = param["sampling_freq"]

    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(211)
    ax.set_title("RR duration")
    xvals = ahr_df.espts.values / fs / 60
    ax.plot(xvals, ahr_df.rrInterpol.values)
    ax.set_ylabel("RR (msec)")
    ax.set_xlabel("min (fs  " + str(fs) + ")")
    ax.grid()
    lims = ahr_df.rrInterpol.quantile([0.01, 0.99])
    ax.set_ylim(lims)
    ax2 = fig.add_subplot(212, sharex=ax)
    if HR:
        ax2.set_title("heart rate")
        yvals = 1 / ahr_df.rrInterpol.values * 60 * 1000
        ax2.plot(xvals, yvals, "-g")
        lims = (
            np.quantile(1 / ahr_df.rrInterpol.values * 60 * 1000, q=0.01),
            np.quantile(1 / ahr_df.rrInterpol.values * 60 * 1000, q=0.99),
        )
        ax2.set_ylim(lims)
    else:
        ax2.set_title("RR sqVariation")
        ax2.plot(xvals, ahr_df.rrInterpolSqDiff.values, "-g")
        lims = (0, ahr_df.rrInterpolSqDiff.quantile(0.98))
        ax2.set_ylim(lims)
    for loca in ["top", "right"]:
        ax.spines[loca].set_visible(False)
        ax2.spines[loca].set_visible(False)
    #    file = os.path.basename(filename)
    fig.text(0.99, 0.01, param["file"], ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, "anesthPlot", ha="left", va="bottom", alpha=0.4)
    fig.tight_layout()
    return fig


# %% heart rate

# TOTO = correct wave.datetime (multiple repetitions of the same value)


def append_rr_and_ihr_to_wave(ekgdf: pd.DataFrame, ahrdf: pd.DataFrame) -> pd.DataFrame:
    """
    append rr and ihr to the waves based on pt value (ie index)

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


def plot_agreement(trenddf: pd.DataFrame):
    """plot ip1HR & ihr to check agreement"""

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
    append 'ihr' (instataneous heart rate) to the trends

    Parameters
    ----------
    trenddf : pd.DataFrame
        DESCRIPTION.
    wavedf : pd.DataFrame
        DESCRIPTION.
    ekgdf : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    trenddf : TYPE
        DESCRIPTION.

    """

    # build a new index
    ratio = len(wavedf) / len(trenddf)
    ser = (wavedf.index.to_series() / ratio).astype(int)
    # fill the data
    df = pd.DataFrame()
    df["ihr"] = 1 / ekgdf.rrInterpol * 60 * 1000
    # downsample
    df = df["ihr"].groupby(ser).median()
    # concatenate
    if "ihr" in trenddf.columns:
        trenddf.drop("ihr", axis=1, inplace=True)
    trenddf = pd.concat([trenddf, df], axis=1)
    print("added instantaneous heart rate to a TREND dataframe")
    return trenddf


def save_trends_data(trenddf: pd.DataFrame, savename: str = "", dirpath: str = "data"):
    """
    save the trends data to a csv and hd5 file, including an ihr column (key='trends_data')

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
    filename = savename + "_" + "trendData"
    if filename.startswith("_"):
        filename = filename[1:]
    fullname = os.path.join(dirpath, filename)
    # trenddf.to_csv(fullname + ".csv")
    trenddf.to_hdf(fullname + ".hdf", mode="w", key="trends_data")


def save_waves_data(wavedf: pd.DataFrame, savename: str = "", dirpath: str = "data"):
    """
    save the waves data to a csv and hd5 file, including an ihr column (key='waves_data')

    Parameters
    ----------
    wavedf : pd.DataFrame
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
    filename = savename + "_" + "waveData"
    if filename.startswith("_"):
        filename = filename[1:]
    fullname = os.path.join(dirpath, filename)
    # wavedf.to_csv(fullname + ".csv")
    wavedf.to_hdf(fullname + ".hdf", mode="w", key="waves_data")


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
#     beat_df = compute_rr(beat_df, monitorWave.param)
#     hr_df = interpolate_rr(beat_df)
#     figure = plot_rr(hr_df, params, HR=True)
