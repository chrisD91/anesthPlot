#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:56:58 2019

@author: cdesbois
"""

import os
import pandas as pd
import numpy as np
import time
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog


#%%
def guiChooseFile(paths, direct=None):
    """Select a file via a dialog and return the file name.
    """
    if not direct:
        direct = paths['data']
    fname = QFileDialog.getOpenFileName(caption='choose a file',
                                        directory=direct, filter='*.csv')   
    return fname[0]

#%%
def extractMonitorWaveHeader(fileName):
    df = pd.read_csv(fileName, sep=',', header=None, index_col=None, nrows=12,
                     encoding='iso-8859-1')
    return df

def loadMonitorWavesData(fileName):
    print('loading ', os.path.basename(fileName))
    fs = 300    # sampling rate
#    fileName = os.path.join(paths['data'], file)
    # bug in the header caused by an acentuated character in line 9 ('césarienne')
    # header and data to dataFrame

    df = pd.read_csv(fileName, sep = ',', skiprows=[14], header=13,
                    index_col=False, encoding='iso-8859-1',
                    usecols=[0,2,3,4,5,6])#, nrows=200000) #NB fro development
    # columns names correction
    colNames = {'~ECG1': 'wekg',
                 '~INVP1': 'wap',
                 '~CO.2': 'wco2',
                 '~AWP': 'wawp',
                 '~Flow' : 'wflow',
                 '~AirV': 'wVol',
                 'Unnamed: 0': 'time'}
    df = df.rename(columns= colNames)
    # NO MORE NEEDED
    #wData.reset_index(inplace=True)
    #build a time column
    #wData.rename(columns={'index':'time'}, inplace=True)
    #TODO = rebuilt a timeserie index
    #see pandas fill_method

    # scaling correction
    df.wco2 = df.wco2.shift(-480) # time lag correction
    df['wco2'] *= 7.6    # CO2 % -> mmHg
    df['wekg'] /= 100    # tranform EKG in mVolts
    df['wawp'] *= 10     # mmH2O -> cmH2O

    df.time = pd.to_datetime(df.time) # time column to dateTime format
    df['point'] = df.index         # point location

    # add a 'sec'
    df['sec'] = df.index/fs
#    wData.set_index('sec')
#   wData.set_index('sec', inplace=True)


    # build a column containing a calibrated time series
    #start = wData.time[0]
    #ptPerSec = 300   # see end of this file to verify
    #end = start + datetime.timedelta(0,(len(wData.time)/ptPerSec))
    #
    #rng = pd.date_range(start= start, end= end,  freq='ms')
    #df.set_index(rng[:-1], inplace=True)
    # bug : the index doen't correspond)
    # the data doesnt seem to be equally spaced (wData.time[wData.time.notnull()])

    # clean data
    #params = ['wekg', 'wap', 'wco2', 'wawp', 'wflow']

    #wData.wap.value_counts().sort_index()
    df.loc[df.wap < -100, 'wap'] = np.nan
    df.loc[df.wap > 200, 'wap'] = np.nan
    df.loc[df.wco2 < 0, 'wco2'] = 0

    return df

def appendMonitorWaveDatetimeData(df):
    df['seconds'] = [time.mktime(t.timetuple()) if t is not pd.NaT else float('nan') for t in df['time'] ]
    df['intepolated'] = df['seconds'].interpolate('values')
    df['datetime'] = [datetime.utcfromtimestamp(t) for t in df['intepolated']]
    #correction for localzone 
    lag = df.iloc[0].time - df.iloc[0].datetime
    df.datetime += lag
    del df['intepolated'], df['time'], df['seconds'], df['point']
    return df

#%%
if __name__ == '__main__':
    fileName = guiChooseFile(paths={'data':'~'})          
    file = os.path.basename(fileName)
    if file[0] == 'M':
        if 'Wave' in file:
            wheader = extractMonitorWaveHeader(fileName)
            wdata = loadMonitorWavesData(fileName)
            wdata = appendMonitorWaveDatetimeData(wdata)