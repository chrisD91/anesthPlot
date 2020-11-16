#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:56:58 2019

@author: cdesbois
"""

import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog


#%%
def choosefile_gui(dir_path=None, caption='choose a recording'):
    """
    Select a file via a dialog and return the (full) filename.
    input : dir_path = location ('generally paths['data']) else home
    """
    if not dir_path:
        dir_path = os.path.expanduser('~')
    options = QFileDialog.Options()
    # to be able to see the caption, but impose to work with the mouse
    # options |= QFileDialog.DontUseNativeDialog
    fname = QFileDialog.getOpenFileName(caption=caption,
                                        directory=dir_path, filter='*.csv',
                                        options=options)
    # fname = QFileDialog.getOpenfilename(caption=caption,
                                        # directory=direct, filter='*.csv')
    # TODO : be sure to be able to see the caption
    return fname[0]

#%%
def loadmonitor_waveheader(filename):
    """ load a monitor wave header, return a pandasDataframe """
    df = pd.read_csv(filename, sep=',', header=None, index_col=None, nrows=12,
                     encoding='iso-8859-1')
    return df

def loadmonitor_wavedata(filename):
    """ load a monitor csvDataFile, return a pandasDataframe """
    print('loading ', os.path.basename(filename))
    fs = 300    # sampling rate
    #header :
    header_df = pd.read_csv(filename, sep=',', header=None, index_col=None, nrows=12,
                            encoding='iso-8859-1')
    date = header_df.iloc[0][1]

    df = pd.read_csv(filename, sep=',', skiprows=[14], header=13,
                     index_col=False, encoding='iso-8859-1',
                     usecols=[0, 2, 3, 4, 5, 6])#, nrows=200000) #NB for development
    # columns names correction
    colnames = {'~ECG1': 'wekg',
                '~INVP1': 'wap',
                '~INVP2': 'wvp',
                '~CO.2': 'wco2',
                '~AWP': 'wawp',
                '~Flow' : 'wflow',
                '~AirV': 'wVol',
                'Unnamed: 0': 'time'}
    df = df.rename(columns=colnames)

    # scaling correction
    if 'wco2' in df.columns:
        df.wco2 = df.wco2.shift(-480) # time lag correction
        df['wco2'] *= 7.6    # CO2 % -> mmHg
    df['wekg'] /= 100    # tranform EKG in mVolts
    df['wawp'] *= 10     # mmH2O -> cmH2O
    df.time = df.time.apply(lambda x: pd.to_datetime(date + '-' + x) 
                            if not pd.isna(x) else x)
    ser = pd.Series(df.time.values.astype('int64'))
    ser[ser < 0] = np.nan
    df['datetime'] = pd.to_datetime(ser.interpolate(), unit='ns')
    df['point'] = df.index         # point location

    # add a 'sec'
    df['sec'] = df.index/fs

    # clean data
    #params = ['wekg', 'wap', 'wco2', 'wawp', 'wflow']

    #wData.wap.value_counts().sort_index()
    df.loc[df.wap < -100, 'wap'] = np.nan
    df.loc[df.wap > 200, 'wap'] = np.nan
    if 'wco2' in df.columns:
        df.loc[df.wco2 < 0, 'wco2'] = 0
    return df


#%%
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    filename = choosefile_gui(os.path.expanduser('~'))
    file = os.path.basename(filename)
    if file[0] == 'M':
        if 'Wave' in file:
            wheader = loadmonitor_waveheader(filename)
            wdata = loadmonitor_wavedata(filename)
