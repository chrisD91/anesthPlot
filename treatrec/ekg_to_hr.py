#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 16:52:00 2020

function used to treat an EKG signal and extract the heart rate
typically
(
after
import anesthPlot.record_main as rec
from treatrec import ekg_to_hr as tohr
)

0- load the data in a pandas dataframe
    (through classes rec.MonitorTrend & rec.MonitorWave)
    trends = rec.MonitorTrend(trendname)
    waves = rec.MonitorWave(wavename)

1- treat the ekg wave :
    params = waves.param
    # build a dataframe to work with (waves)
    ekg_df = pd.DataFrame(waves.data.wekg)
    #low pass filtering
    ekg_df['wekg_lowpass'] = wf.fix_baseline_wander(ekg_df.wekg,
                                                waves.param['fs'])
    # build the beat locations (beat based dataFrame)
    beat_df = tohr.detect_beats(ekg_df.wekg_lowpass)

2- perform the manual adjustments required:
    # based on a graphical display of beat locations, an rr values
    figure = tohr.plot_beats(ekg_df.wekg_lowpass, beat_df)
    build a container for the manual corrections:
    to_change_df = pd.DataFrame(columns=beat_df.columns.insert(0, 'action'))

    # remove or add peaks : zoom on the figure to observe only one peak, then
    to_change_df = tohr.remove_beat(beat_df, ekg_df, to_change_df, figure)
    to_change_df = tohr.append_beat(beat_df, ekg_df, to_change_df, figure)

    #save the peak and to_change to csv
    see save_temp()

    # load and combine to update the beat_df
    beat_df = update_beat_df()

4- go from points values to continuous time
    beat_df = tohr.compute_rr(beat_df)
    ahr_df = tohr.interpolate_rr(beat_df)
    tohr.plot_rr(ahr_df, params)

5- append intantaneous heart rate to the initial data:
    ekg_df = tohr.append_rr_and_ihr_to_wave(ekg_df, ahr_df)
    waves.data = tohr.append_rr_and_ihr_to_wave(waves.data, ahr_df)
    trends.data = tohr.append_ihr_to_trend(trends.data, waves.data, ekg_df)



    figure = plot_beats(ekg_df.wekg_lowpass, beat_df)

    #fs=300
    beat_df = compute_rr(beat_df, monitorWave.param)
    hr_df = interpolate_rr(beat_df)
    figure = plot_rr(hr_df, params, HR=True)


@author: cdesbois
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.signal as sg
from scipy.interpolate import interp1d

import treatrec.wave_func as wf


#%%
def detect_beats(ser, fs=300, species='horse', mult=1):
    """
    detect the peak locations
    input:
        ser: pandas series,
        fs: sampling frequency
        species in [horse]
        mult: correction / 1 for qRs amplitude
    output:
        pandas dataframe
    """
    df = pd.DataFrame()
    # fs = param.get('fs', 300)
    if species == 'horse':
        height = 1      # mini
        hr_max = 120    # bpm
        distance = fs * 60 / hr_max    # sec
        prominence = 1  # mini/surrounding
        #    width=(2,15)
        #    plateau_size= 1
    else:
        print('no parametrisation performed ... to be done')
        return df
    #correcttion
    height *= mult
    prominence *= mult
    #detect
    pk, beats_params = sg.find_peaks(ser*-1, height=height, distance=distance,
                                     prominence=prominence)
    df['pLoc'] = pk
    for key in beats_params.keys():
        df[key] = beats_params[key]
    if 'peak_heights' in df.columns:
        df = df.rename(columns={'peak_heights': 'yLoc'})
        df.yLoc *= -1   # inverted trace <-> horse R wave
    return df

def plot_beats(ecg, beats):
    """ plot ecg waveform + beat location """
    fig = plt.figure(figsize=(13, 5))
    fig.suptitle('verify the accuracy of the beat detection')
    ax0 = fig.add_subplot(211)
    ax0.plot(ecg.values, label='ekg')
    ax0.set_ylabel('ekg (mV)')
    ax0.set_xlabel('pt value')
    ax0.plot(beats.pLoc, beats.yLoc, 'o', color='orange', label='R')

    ax1 = fig.add_subplot(212, sharex=ax0)
    ax1.plot(beats.pLoc[:-1], np.diff(beats.pLoc), 'r-', label='rr')
    ax1.set_ylabel('rr (pt value)')
    ax1.set_xlabel('pt value')
    fig.legend()
    for ax in fig.get_axes():
        for loca in ['top', 'right']:
            ax.spines[loca].set_visible(False)
    fig.tight_layout()
    txt0 = 'locate the peak to add : zoom and use'
    txt1 = 'to_change_df = tohr.add_beat(beat_df, ekg_df, to_change_df, figure)'
    fig.text(0.99, 0.03, txt0, ha='right', va='bottom', alpha=0.5)
    fig.text(0.99, 0.00, txt1, ha='right', va='bottom', alpha=0.5, size='small')
    txt0 = 'locate the peak to remove : zoom and use'
    txt1 = 'to_change_df = tohr.remove_beat(beat_df, ekg_df, to_change_df, figure, scale=1)'
    fig.text(0.01, 0.03, txt0, ha='left', va='bottom', alpha=0.5)
    fig.text(0.01, 0.00, txt1, ha='left', va='bottom', alpha=0.5, size='small')
    return fig

def append_beat(beatdf, ekgdf, tochange_df, fig, lim=None, yscale=1):
    """
    locate the beat in the figure, append to a dataframe['toAppend']
    input:
        beatdf (pLocs), ekgdf (wekg_lowpass),
        fig:figure to fing limits
        lim: to give it manually
        tochange_df(toAppend, to Remove)
        mult = amplitude mutliplication factor for detection (default=1)
    output: incremented changedf (pt location)
    """
    """ locate the beat in the figure, append to a dataframe['toAppend']
       0: if not present : build a dataframe :
           to_change_df = pd.DataFrame(columns=['toAppend', 'toRemove'])
       1: locate the extra beat in the figure (cf plot_beats())
       and zoom to observe only a negative peak
       2- call the function:
           to_change_df = remove_beat(beatdf, ekgdf, tochange_df, fig)
    -> the beat parameters will be added the dataFrame
    (in the end of the manual check, update the beat_df
    first : save beat_df and to_change_df
    second : run beat_df = update_beat_df())
    """
    # find the limits of the figure
    if not lim:
        lims = fig.get_axes()[0].get_xlim()
        lim = (int(lims[0]), int(lims[1]))
    #restrict area around the undetected pic (based on pt x val)
    df = ekgdf.wekg_lowpass.loc[lim[0]:lim[1]]
    #locate the beat (external call)
    onepoint_beatdf = detect_beats(df, mult=yscale)
    onepoint_beatdf['action'] = 'append'
    if len(onepoint_beatdf) < 1:
        print('no beat founded')
        return tochange_df
    found_loc = onepoint_beatdf.pLoc.values[0]
    yloc = onepoint_beatdf.yLoc.values[0]
    # reassign the pt value
    ploc = ekgdf.wekg_lowpass.loc[lim[0]:lim[1]].index[found_loc]
    onepoint_beatdf['pLoc'] = ploc
    print('founded ', ploc)
    # append to figure
    fig.get_axes()[0].plot(ploc, yloc, 'og')
    onepoint_beatdf.pLoc = ploc
    onepoint_beatdf.left_bases += (ploc - found_loc)
    onepoint_beatdf.right_bases.values[0] += (ploc - found_loc)
    # insert in the tochange_df
    # beatdf = beatdf.drop_duplicates('pLoc')
    tochange_df = tochange_df.append(onepoint_beatdf)
    return tochange_df

def remove_beat(beatdf, ekgdf, tochange_df, fig, lim=None):
    """ locate the beat in the figure, append to a dataframe['toRemove']
       0: if not present build a dataframe :
           to_change_df = pd.DataFrame(columns=['toAppend', 'toRemove'])
       1: locate the extra beat in the figure (cf plot_beats())
       and zoom to observe only a negative peak
       2- call the function:
           to_change_df = remove_beat(beatdf, ekgdf, tochange_df, fig)
    -> the beat parameters will be added the dataFrame
    (in the end of the manual check, update the beat_df
    first : save beat_df and to_change_df
    second : run beat_df = update_beat_df())
    """
    # find the limits of the figure
    if not lim:
        lims = fig.get_axes()[0].get_xlim()
        lim = (int(lims[0]), int(lims[1]))
    position = beatdf.pLoc[(lim[0] < beatdf.pLoc) & (beatdf.pLoc < lim[1])]
    iloc = position.index.values[0]
    ptloc = position.values      #pt values of the peak
    if len(ptloc) > 1:
        print('several beats detected')
        return tochange_df
    pos = int(ptloc[0])               # array -> value
    # mark on the graph
    pLoc, yLoc = beatdf.loc[iloc, ['pLoc', 'yLoc']]
    pLoc = int(pLoc)
    ax = fig.get_axes()[0]
    ax.plot(pLoc, yLoc, 'Xr')
    # mark to remove
    onepoint_beatdf = beatdf.loc[iloc].copy()
    onepoint_beatdf['action'] = 'remove'
    tochange_df = tochange_df.append(onepoint_beatdf, ignore_index=True)
    # beatdf.loc[pos, ['yLoc']] = np.NaN
    print("position is ", pos)
    return tochange_df

#TODO append the missing R in case of BAV2

def save_temp():
    name = os.path.join(paths['save'], 'beatDf.csv')
    beat_df.to_csv(name)
    name = os.path.join(paths['save'], 'toChange.csv')
    to_change_df.to_csv(name)

#%% apply changes to the beatdf

def update_beat_df(beat_df, to_change_df, path_to_file='', from_file=False):
    """ implement in the beat location the manual corrections
        fromFile = True force the disk loading of the dataframes
    """
    if from_file:
        name = os.path.join(path_to_file, 'beatDf.csv')
        beat_df = pd.read_csv(name, index_col=0)
        name = os.path.join(path_to_file, 'toChange.csv')
        to_change_df = pd.read_csv(name, index_col=0)
    for col in ['pLoc', 'left_bases', 'right_bases']:
        to_change_df[col] = to_change_df[col].astype(int)
    # remove
    to_remove = to_change_df.loc[
        to_change_df['action'] == 'remove', ['pLoc']]
    to_remove = to_remove.values.flatten().tolist()
    beat_df = beat_df.set_index('pLoc').drop(to_remove, errors='ignore')
    beat_df.reset_index(inplace=True)
    #append
    temp_df = to_change_df.loc[to_change_df['action'] == 'append'].set_index('action')
    beat_df = beat_df.append(temp_df, ignore_index=True)
    #rebuild
    beat_df.drop_duplicates(keep=False, inplace=True)
    beat_df = beat_df.sort_values(by='pLoc').reset_index(drop=True)
    return beat_df

# beat_df = update_beat_df(beat_df, to_change_df)

#%% =========================================
def compute_rr(abeat_df, fs=None):
    """
    compute rr intervals (from pt to time)
    intput : pd.DataFrame with 'pLoc', and fs=sampling frequency
    output : pd.DataFrame appendend with:
        'rr' =  rr duration
        'rrDiff' = rrVariation
        'rrSqDiff' = rrVariation^2
    """
    if not fs:
        fs = 300
    # compute rr intervals
#    beat_df['rr'] = np.diff(beat_df.pLoc)
    abeat_df['rr'] = abeat_df.pLoc.shift(-1) - abeat_df.pLoc # pt duration
    abeat_df.rr = abeat_df.rr / fs*1_000     # time duration
    #remove outliers (HR < 20)
    abeat_df = abeat_df.replace(abeat_df.loc[abeat_df.rr > 20_000], np.nan)
    abeat_df = abeat_df.interpolate()
    abeat_df = abeat_df.dropna(how='all')
    abeat_df = abeat_df.dropna(axis=1, how='all')
    # compute variation
    abeat_df['rrDiff'] = abs(abeat_df.rr.shift(-1) - abeat_df.rr)
    abeat_df['rrSqDiff'] = (abeat_df.rr.shift(-1) - abeat_df.rr)**2
    return abeat_df

def interpolate_rr(abeat_df, kind=None):
    """
    interpolate the beat_df (pt -> time values)
    input : beat Df, kind='linear' or 'cubic'(default)
    output : pdDatatrame with evenly spaced data
        'espts' = evenly spaced points
        'rrInterpol' = interpolated rr
    """
    if not kind:
        kind = 'cubic'
    ahr_df = pd.DataFrame()
    #prepare = sorting and removing possible duplicates
    abeat_df = abeat_df.sort_values(by='pLoc')
    abeat_df = abeat_df.drop_duplicates('pLoc')

    first_beat_pt = int(abeat_df.iloc[0].pLoc)
    last_beat_pt = int(abeat_df.iloc[-2].pLoc) # last interval
    newx = np.arange(first_beat_pt, last_beat_pt)
    # interpolate rr
    rrx = abeat_df.pLoc[:-1].values        # rr locations
    rry = abeat_df.rr[:-1].values         # rr values
    f = interp1d(rrx, rry, kind=kind)
    newy = f(newx)
    ahr_df['espts'] = newx
    ahr_df['rrInterpol'] = newy
    # interpolate rrDiff
    rry = abeat_df.rrDiff[:-1].values
    f = interp1d(rrx, rry, kind=kind)
    newy = f(newx)
    ahr_df['rrInterpolDiff'] = newy
    # interpolate rrSqrDiff
    rry = abeat_df.rrSqDiff[:-1].values
    f = interp1d(rrx, rry, kind=kind)
    newy = f(newx)
    ahr_df['rrInterpolSqDiff'] = newy
    return ahr_df

def plot_rr(ahr_df, param, HR=False):
    """
    plot RR vs pt values + rrSqDiff
    input :
        hr_df = pdDataFrame
        params : dict containing 'fs' as key
    """
    fs = param['fs']

    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(211)
    ax.set_title('RR duration')
    xvals = ahr_df.espts.values/fs/60
    ax.plot(xvals, ahr_df.rrInterpol.values)
    ax.set_ylabel('RR (msec)')
    ax.set_xlabel('min (fs  ' + str(fs) + ')')
    ax.grid()
    lims = ahr_df.rrInterpol.quantile([0.01, 0.99])
    ax.set_ylim(lims)
    ax2 = fig.add_subplot(212, sharex=ax)
    if HR:
        ax2.set_title('heart rate')
        yvals = 1/ahr_df.rrInterpol.values*60*1000
        ax2.plot(xvals, yvals, '-g')
        lims = (np.quantile(1/ahr_df.rrInterpol.values*60*1000, q=0.01),
                np.quantile(1/ahr_df.rrInterpol.values*60*1000, q=0.99))
        ax2.set_ylim(lims)
    else:
        ax2.set_title('RR sqVariation')
        ax2.plot(xvals, ahr_df.rrInterpolSqDiff.values, '-g')
        lims = (0, ahr_df.rrInterpolSqDiff.quantile(0.98))
        ax2.set_ylim(lims)
    for loca in ['top', 'right']:
        ax.spines[loca].set_visible(False)
        ax2.spines[loca].set_visible(False)
#    file = os.path.basename(filename)
    fig.text(0.99, 0.01, param['file'], ha='right', va='bottom', alpha=0.4)
    fig.text(0.01, 0.01, 'anesthPlot', ha='left', va='bottom', alpha=0.4)
    fig.tight_layout()
    return fig

#%% heart rate

#TOTO = correct wave.datetime (multiple repetitions of the same value)

def append_rr_and_ihr_to_wave(wave, ahrdf):
    """ append rr and ihr to the waves based on pt value (ie index) """
    df = pd.concat([wave, ahrdf.set_index('espts')], axis=1)
    df['ihr'] = 1/df.rrInterpol*60*1000
    return df

def plot_agreement(trend, ekgdf):
    """ plot ip1HR & hr to check agreement """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(trend.hr)
    axt = ax.twiny()
    axt.plot(1/ekgdf.rrInterpol*60*1000, 'r-')
    return fig

def append_ihr_to_trend(trend, wave, ekgdf):
    """ append 'ihr' (instataneous heart rate) to the trends """
    #build a new index
    ratio = len(wave)/len(trend)
    ser = (wave.index.to_series() / ratio).astype(int)
    # fill the data
    df = pd.DataFrame()
    df['ihr'] = 1/ekgdf.rrInterpol*60*1000
    # downsample
    df = df['ihr'].groupby(ser).median()
    # concatenate
    trend = pd.concat([trend, df], axis=1)
    return trend

#%%
#ekg_df = append_rr_and_ihr_to_wave(ekg_df, ahr_df)
#waves.data = append_rr_and_ihr_to_wave(waves.data, ahr_df)
#trends.data = append_ihr_to_trend(trends.data, waves.data, ekg_df)


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

