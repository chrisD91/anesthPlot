#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:15:27 2020

@author: cdesbois
"""

import os, sys
import pandas as pd

try:
    from .context import record_main as recmain
except ModuleNotFoundError:
    from context import record_main as recmain
    
#%%
def load(tfile = 'M2020_2_4-9_49_5.csv',
         wfile = 'M2020_2_4-9_49_5Wave.csv',
         dir_loc = '~/enva/clinique/recordings/anesthRecords/onPanelPcRecorded'):
    
    #files:
    if os.path.isfile(tfile):
        trend_filename = tfile
    else:
        trend_filename = os.path.join(dir_loc, tfile)
        
    if os.path.isfile(wfile):
        wave_filename = wfile
    else:
        wave_filename = os.path.join(dir_loc, wfile)  
        
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


if len(sys.argv)<2:
    print('/!\ NEED TO PROVIDE TREND AND WAVE FILE AS ARGUMENTS')
else:
    Trend_File = sys.argv[1]
    Wave_File = sys.argv[2]



monitorTrend, monitorWave = load(tfile=Trend_File, wfile=Wave_File)

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
beat_df= treat.ekg_to_hr.compute_rr(beat_df, monitorWave.param)
print(beat_df)
hr_df = treat.ekg_to_hr.interpolate_rr(beat_df)
figure = treat.ekg_to_hr.plot_rr(hr_df, params, HR=True)

figure.savefig('fig.png')

