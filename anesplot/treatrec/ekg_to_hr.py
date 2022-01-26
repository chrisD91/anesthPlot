#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Wed Feb 12 16:52:00 2020
@author: cdesbois

function used to treat an EKG signal and extract the heart rate
typically (copy, paste and execute line by line)

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
                                                waves.param['fs'])
        beat_df = tohr.detect_beats(ekg_df.wekg_lowpass, mult=1)

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

        tohr.save_beats(beat_df, to_change_df, savename='', savepath=None)
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

    tohr.save_trends_data(trends.data, savename=name, savepath='data')
    tohr.save_waves_data(waves.data, savename=name, savepath='data')

____
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.signal as sg
from scipy.interpolate import interp1d

# import anesthPlot.treatrec.wave_func as wf
# TODO import the paths construction

# TODO shift the ihr of one beat (ie ihr should be on the end of the interval)

#%%
def detect_beats(ser, fs=300, species="horse", mult=1):
    """detect the peak locations

    :param pandas.series ser: the data
    :param integer fs: sampling frequency
    :param string species: in [horse]
    :param float mult: correction / 1 for qRs amplitude
    :returns: df=pandas.Dataframe
    """

    df = pd.DataFrame()
    # fs = param.get('fs', 300)
    if species == "horse":
        height = 1  # mini
        hr_max = 120  # bpm
        distance = fs * 60 / hr_max  # sec
        prominence = 1  # mini/surrounding
        #    width=(2,15)
        #    plateau_size= 1
    else:
        print("no parametrisation performed ... to be done")
        return df
    # correcttion
    height *= mult
    prominence *= mult
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


def plot_beats(ecg, beats):
    """plot ecg waveform + beat location"""

    fig = plt.figure(figsize=(13, 5))
    fig.suptitle("verify the accuracy of the beat detection")
    ax0 = fig.add_subplot(211)
    ax0.plot(ecg.values, label="ekg")
    ax0.set_ylabel("ekg (mV)")
    ax0.set_xlabel("pt value")
    ax0.plot(beats.p_loc, beats.y_loc, "o", color="orange", label="R")

    ax1 = fig.add_subplot(212, sharex=ax0)
    ax1.plot(beats.p_loc[:-1], np.diff(beats.p_loc), "r-", label="rr")
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


def append_beat(beatdf, ekgdf, tochange_df, fig, lim=None, yscale=1):
    """locate the beat in the figure, append to a dataframe['toAppend']

    :param pandas.Dataframe beatdf: contains the point based location (p_locs)
    :param pandas dataframe ekgdf: contains the wave recording ((wekg_lowpass)
    :param pandas.Dataframa tochange_df: to store the beats toAppend or toRemove
    :param pyplot.Figure fig: figure to find time limits
    :param integer lim: ptBasedLim optional to give it manually
    :param float  yscale: amplitude mutliplication factor for detection (default=1)

    :returns: tochange_df: incremented changedf (pt location)
    :rtype: pandasDataframe

    methods :

        locate the beat in the figure, append to a dataframe['toAppend']
        0.: if not present : build a dataframe:
            >>> to_change_df = pd.DataFrame(columns=['toAppend', 'toRemove'])

        1.: locate the extra beat in the figure (cf plot_beats())
            and zoom to observe only a negative peak

        2.: call the function:
            >>> to_change_df = remove_beat(beatdf, ekgdf, tochange_df, fig)
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
    onepoint_beatdf = detect_beats(df, mult=yscale)
    onepoint_beatdf["action"] = "append"
    if len(onepoint_beatdf) < 1:
        print("no beat founded")
        return tochange_df
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
    # insert in the tochange_df
    # beatdf = beatdf.drop_duplicates('p_loc')
    tochange_df = tochange_df.append(onepoint_beatdf)
    return tochange_df


def remove_beat(beatdf, ekgdf, tochange_df, fig, lim=None):
    """locate the beat in the figure, append to a dataframe['toRemove']

    0.: if not present build a dataframe:
        >>> to_change_df = pd.DataFrame(columns=['toAppend', 'toRemove'])

    1.: locate the extra beat in the figure (cf plot_beats())
        and zoom to observe only a negative peak

    2.: call the function:::
        >>> to_change_df = remove_beat(beatdf, ekgdf, tochange_df, fig)
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
        return tochange_df
    pos = int(ptloc[0])  # array -> value
    # mark on the graph
    p_loc, y_loc = beatdf.loc[iloc, ["p_loc", "y_loc"]]
    p_loc = int(p_loc)
    ax = fig.get_axes()[0]
    ax.plot(p_loc, y_loc, "Xr")
    # mark to remove
    onepoint_beatdf = beatdf.loc[iloc].copy()
    onepoint_beatdf["action"] = "remove"
    tochange_df = tochange_df.append(onepoint_beatdf, ignore_index=True)
    # beatdf.loc[pos, ['y_loc']] = np.NaN
    print("position is ", pos)
    return tochange_df


# TODO append the missing R in case of BAV2


def save_beats(beatdf, tochangedf, savename="", dirpath=None):
    """save the beats locations as csv and hd5 file

    parameters
    ----------
    beatde : pd.dataframes
    tochangedf : pandas.dataframe
    savename : filename
    dirpath : path to save in

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
    beatdf.to_csv(name + ".csv")
    beatdf.to_hdf(name + ".hdf", mode="w", key="beatDf")
    tochangedf.to_hdf(name + ".hdf", mode="a", key="tochangeDf")
    filename = savename + "_" + "tochangedf"
    if filename.startswith("_"):
        filename = filename[1:]
    name = os.path.join(dirpath, filename)
    tochangedf.to_csv(name + ".csv")


#%% apply changes to the beatdf


def update_beat_df(beatdf, tochangedf, path_to_file="", from_file=False):
    """implement in the beat location the manual corrections
    fromFile = True force the disk loading of the dataframes
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

#%% =========================================
def compute_rr(beatdf, fs=None):
    """
    compute rr intervals (from pt to time)

    parameters
    ----------
    beatdf : pd.DataFrame
        with 'p_loc'
    fs : integer
        sampling frequency

    returns
    -------
    pd.DataFrame
        with:
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


def interpolate_rr(beatdf, kind=None):
    """
    interpolate the beat_df (pt -> time values)

    parameters
    ----------
    beatDf: pd.Dataframe
    kind : str
        'linear' or 'cubic'(default)

    returns
    -------
    pdDatatrame with evenly spaced data
        'espts' = evenly spaced points
        'rrInterpol' = interpolated rr
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


def plot_rr(ahr_df, param, HR=False):
    """
    plot RR vs pt values + rrSqDiff

    parameters:
        hr_df = pdDataFrame
        params : dict
            containing 'fs' as key
    """

    fs = param["fs"]

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


#%% heart rate

# TOTO = correct wave.datetime (multiple repetitions of the same value)


def append_rr_and_ihr_to_wave(wave, ahrdf):
    """append rr and ihr to the waves based on pt value (ie index)"""

    df = pd.concat([wave, ahrdf.set_index("espts")], axis=1)
    df["ihr"] = 1 / df.rrInterpol * 60 * 1000
    print("added instantaneous heart rate to a Wave dataframe")
    return df


def plot_agreement(trenddf):
    """plot ip1HR & ihr to check agreement"""

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(trenddf.hr)
    ax.plot(trenddf.hr, label="ip1pr")
    ax.plot(trenddf.ihr, label="ihr")
    ax.legend()
    return fig


def append_ihr_to_trend(trenddf, wavedf, ekgdf):
    """append 'ihr' (instataneous heart rate) to the trends"""

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


def save_trends_data(trenddf, savename="", dirpath="data"):
    """
    save the trends data to a csv and hd5 file, including an ihr column

    parameters
    ----------
    trenddf : pd.dataframes
    savename : str
    dirpath : str
        path to save in (default= current working directory)

    output
    ------
    hdf file, key='trends_data'
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


def save_waves_data(wavedf, savename="", dirpath="data"):
    """
    save the trends data to a hd5 file, including an ihr column

    parameters
    ----------
    trenddf : pd.dataframes
    savename : str
        dirpath : path to save in (default='data')

    output
    ------
    hdf_file, key='waves_data'
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
