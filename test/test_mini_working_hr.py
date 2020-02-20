#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:15:27 2020

@author: cdesbois
"""

import os
import record_main as recmain
import pandas as pd

#%%

def load():
    #files:
    tfile = 'M2020_2_4-9_49_5.csv'
    wfile = 'M2020_2_4-9_49_5Wave.csv'
    dir_loc = '~/enva/clinique/recordings/anesthRecords/onPanelPcRecorded'
    trend_filename = os.path.join(dir_loc, tfile)
    wave_filename = os.path.join(dir_loc, wfile)  
  
    #load
    #trends
    monitorTrend = recmain.MonitorTrend(trend_filename)
    params = recmain.build_param_dico(file=tfile, source='monitorTrend')
    #waves
    monitorWave = recmain.MonitorWave(wave_filename)
    params = recmain.build_param_dico(file=wfile, source='monitorWave')
    params['fs'] = float(monitorWave.header['Data Rate (ms)'])*60/1000
    params['kind'] = 'as3'
    monitorWave.param = params
    #remove unnecessary waves
    for item in ['wflow', 'wawp', 'wvp']:
        del monitorWave.data[item]
    return monitorTrend, monitorWave

monitorTrend, monitorWave = load()    
#%% extract heart rate from wave
import treatrec as treat
#to force to load ekg_to_hr (why is it necessary ?)
from treatrec import ekg_to_hr

#%detect beats after record_main for monitorWave
params = monitorWave.param

#NB data = monitorWave.data
# build a dataframe to work with (waves)
ekg_df = pd.DataFrame(monitorWave.data.wekg)*(-1)

#low pass filtering
ekg_df['wekg_lowpass'] = recmain.wf.fix_baseline_wander(ekg_df.wekg,
                                                monitorWave.param['fs'])
# beats locations (beat based dataFrame)
beat_df = treat.ekg_to_hr.detect_beats(ekg_df.wekg_lowpass, params)
#plot
figure = treat.ekg_to_hr.plot_beats(ekg_df.wekg_lowpass, beat_df)

#fs=300
beat_df = treat.ekg_to_hr.compute_rr(beat_df, monitorWave.param)
hr_df = treat.ekg_to_hr.interpolate_rr(beat_df)
figure = treat.ekg_to_hr.plot_rr(hr_df, params, HR=True)
