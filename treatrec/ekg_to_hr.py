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
    beat_df = detect_beats(ekg_df.wekg_lowpass, params)

2- perform the manual adjustments required:
    (based on a graphical display of beat locations, an rr values)
    figure = tohr.plot_beats(ekg_df.wekg_lowpass, beat_df)
    # remove the first bas detections:
    beat_df = beat_df.loc[beat_df.pLoc > <ptValues>]
    # add missed peaks (using the figure limits or lims=(xmin, xmax)):
    beat_df = tohr.append_a_peak(beat_df, ekg_df, figure, lims)
    # remove extra peaks:
    tohr.locate_beat(beat_df, figure, lim=lims) -> locate a peak index val
    beat_df.drop("peak index val", inplace=True)

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

#import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.signal as sg
from scipy.interpolate import interp1d
import treatrec.wave_func as wf

#%%
def detect_beats(ser, fs=300, species='horse'):
    """ detect the peak locations """
    df = pd.DataFrame()
#    fs = param.get('fs', 300)
    if species == 'horse':
        height = 0.5      # min, max
        distance = 0.7*fs    # sec
        prominence = 1
        #    width=(2,15)
        #    plateau_size= 1
    else:
        print('no parametrisation performed ... to be done')
        return df
    pk, beats_params = sg.find_peaks(ser*-1, height=height, distance=distance,
                                     prominence=prominence)
    df['pLoc'] = pk
    for key in beats_params.keys():
        df[key] = beats_params[key]
    if 'peak_heights' in df.columns:
        df = df.rename(columns={'peak_heights': 'yLoc'})
        df.yLoc *= -1
    return df

def plot_beats(ecg, beats):
    """ plot ecg waveform + beat location """
    fig = plt.figure(figsize=(12, 8))
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
    txt0 = 'locate the peak to remove : zoom and use'
    txt1 = 'tohr.locate_beat(beat_df, figure)'
    fig.text(0.99, 0.03, txt0, ha='right', va='bottom', alpha=0.5)
    fig.text(0.99, 0.01, txt1, ha='right', va='bottom', alpha=0.5)
    txt0 = 'add peak : zoom and use'
    txt1 = "beat_df = tohr.append_a_peak(beat_df, ekg_df, figure)'"
    fig.text(0.01, 0.03, txt0, ha='left', va='bottom', alpha=0.5)
    fig.text(0.01, 0.01, txt1, ha='left', va='bottom', alpha=0.5)
    return fig

def locate_beat(df, fig, lim=None):
    """ locate the beat location identified in the figure """
    # find irrelevant beat location
    # see https://stackoverflow.com/questions/21415661/
    #logical-operators-for-boolean-indexing-in-pandas
    # find the limits of the figure
    if not lim:
        lim = fig.get_axes()[0].get_xlim()
    position = df.pLoc[(lim[0] < df.pLoc) & (df.pLoc < lim[1])].index
    iloc = position.values
    if len(iloc) > 1:
        print('several beats detected')
        return
    pos = iloc[0]
    print("position is ", pos)
    print('to remove a peak use df.drop(<position>, inplace=True)')
    print("don't forget to rebuild the index")
    print("df.sort_value(by=['pLoc']).reset_index(drop=True)")
    return pos

def append_a_beat(beatdf, ekgdf, fig, lim=None):
    """ append the beat location in the fig to the beat_df
        input : beat_df,
                figure scaled to see one peak,
                lim = tuple(xmin, xmax), default=None
        output : df sorted and reindexed
    """
    # find the limits of the figure
    if not lim:
        lim = fig.get_axes()[0].get_xlim()
    #restrict area around the undetected pic
    df = ekgdf.wekg_lowpass.loc[lim[0]:lim[1]]
    #locate the beat (external call)
    local_df = detect_beats(df)
    locpic = local_df.pLoc.values[0]
    # reassign the pt value
    pt_pic = ekgdf.wekg_lowpass.loc[lim[0]:lim[1]].index[locpic]
    print('founded ', pt_pic)
    local_df.pLoc.values[0] = pt_pic
    local_df.left_bases.values[0] += (pt_pic - locpic)
    local_df.right_bases.values[0] += (pt_pic - locpic)
    # reinsert in the beat_df
    beatdf = pd.concat([beatdf, local_df])
    beatdf = beatdf.drop_duplicates('pLoc')
    beatdf = beatdf.sort_values(by=['pLoc']).reset_index(drop=True)
    return beatdf


#TODO append the missing R in case of BAV2

#% =========================================
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
    abeat_df.rr = abeat_df.rr / fs*1000     # time duration
    #remove outliers
    abeat_df = abeat_df.replace(abeat_df.loc[abeat_df.rr > 2000], np.nan)
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
ekg_df = append_rr_and_ihr_to_wave(ekg_df, ahr_df)
waves.data = append_rr_and_ihr_to_wave(waves.data, ahr_df)
trends.data = append_ihr_to_trend(trends.data, waves.data, ekg_df)


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

