#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:15:27 2020

@author: cdesbois
"""

import os
import sys

import matplotlib.pylab as plt
import numpy as np
import pandas as pd

try:
    from .context import recmain, wavelet
except ModuleNotFoundError:
    from context import recmain, wavelet

import treatrec as treat
from treatrec import ekg_to_hr


#%%
def load(
    tfile="M2020_2_4-9_49_5.csv",
    wfile="M2020_2_4-9_49_5Wave.csv",
    dir_loc="~/enva/clinique/recordings/anesthRecords/onPanelPcRecorded",
):

    # files:
    if os.path.isfile(tfile):
        trend_filename = tfile
    else:
        trend_filename = os.path.join(dir_loc, tfile)

    if os.path.isfile(wfile):
        wave_filename = wfile
    else:
        wave_filename = os.path.join(dir_loc, wfile)

    # trends
    monitorTrend = recmain.MonitorTrend(trend_filename)
    params = recmain.build_param_dico(file=tfile, source="monitorTrend")
    # waves
    monitorWave = recmain.MonitorWave(wave_filename)
    params = recmain.build_param_dico(file=wfile, source="monitorWave")
    params["fs"] = float(monitorWave.header["Data Rate (ms)"]) * 60 / 1000
    params["kind"] = "as3"
    monitorWave.param = params
    # remove unnecessary waves
    for item in ["wflow", "wawp", "wvp"]:
        del monitorWave.data[item]
    return monitorTrend, monitorWave


def time_freq_plot(t, freqs, data, coefs, time_label="time (ms)"):
    """
    a plot to illustrate the output of the wavelet analysis
    """
    dt = t[1] - t[0]

    fig = plt.figure(figsize=(8, 5))
    plt.subplots_adjust(wspace=0.8, hspace=0.5, bottom=0.2)
    # signal plot
    plt.subplot2grid((3, 8), (0, 0), colspan=6)
    plt.plot(t, data, "k-", lw=2)
    plt.ylabel("signal")
    plt.xlim([t[0], t[-1]])
    # time frequency power plot
    ax1 = plt.subplot2grid((3, 8), (1, 0), rowspan=2, colspan=6)
    c = plt.contourf(t, freqs, np.real(coefs), cmap="PRGn", aspect="auto")
    plt.xlabel(time_label)
    plt.ylabel("frequency (Hz)")
    plt.yscale("log")
    # inset with legend
    acb = plt.axes([0.8, 0.7, 0.02, 0.2])
    plt.colorbar(c, cax=acb, label="coeffs (a.u.)", ticks=[-1, 0, 1])
    # mean power plot over intervals
    plt.subplot2grid((3, 8), (1, 6), rowspan=2)
    plt.barh(freqs, np.power(coefs, 2).mean(axis=1) * dt)
    plt.xticks([])
    plt.xlabel(" mean \n power \n (a.u.)")
    # max of power over intervals
    plt.subplot2grid((3, 8), (1, 7), rowspan=2)
    plt.barh(freqs, np.power(coefs, 2).max(axis=1) * dt)
    plt.xticks([])
    plt.xlabel(" max. \n power \n (a.u.)")
    return fig


if len(sys.argv) < 2:
    print("/!\ NEED TO PROVIDE TREND AND WAVE FILE AS ARGUMENTS")
else:
    Trend_File = sys.argv[1]
    Wave_File = sys.argv[2]


#%% extract heart rate from wave
# to force to load ekg_to_hr (why is it necessary ?)

if os.path.isfile("data/hr_df.npy"):
    hr_df = np.load("data/hr_df.npy")

else:
    monitorTrend, monitorWave = load(tfile=Trend_File, wfile=Wave_File)

    #%detect beats after record_main for monitorWave
    params = monitorWave.param

    # NB data = monitorWave.data
    # build a dataframe to work with (waves)
    ekg_df = pd.DataFrame(monitorWave.data.wekg) * (-1)

    # low pass filtering
    ekg_df["wekg_lowpass"] = recmain.wf.fix_baseline_wander(
        ekg_df.wekg, monitorWave.param["fs"]
    )
    # beats locations (beat based dataFrame)
    beat_df = treat.ekg_to_hr.detect_beats(ekg_df.wekg_lowpass, params)
    # plot
    figure = treat.ekg_to_hr.plot_beats(ekg_df.wekg_lowpass, beat_df)

    # fs=300
    beat_df = treat.ekg_to_hr.compute_rr(beat_df, monitorWave.param)

    hr_df = treat.ekg_to_hr.interpolate_rr(beat_df)

    np.save("data/hr_df.npy", np.array(hr_df.rrInterpol))
    hr_df = np.array(hr_df.rrInterpol)


dt = 1.0 / 300.0
t, data = np.arange(len(hr_df)) * dt, (hr_df - hr_df.mean()) / hr_df.std()
freqs = np.logspace(-3, 0, 20)
coefs = wavelet.my_cwt(data, freqs, dt)

figure = time_freq_plot(t[::10] / 60.0, freqs, data[::10], coefs[:, ::10])

plt.show()
