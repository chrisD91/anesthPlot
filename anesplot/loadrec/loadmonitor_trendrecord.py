#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 13:43:26 2019

@author: cdesbois
"""

import os
import sys

import pandas as pd
#import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog


#%%
def choosefile_gui(dir_path=None):
    """
    Select a file using a dialog and return the filename.

    input : dir_path = location ('generally paths['data']) else home
    output : filename (full path)
    """
    if dir_path is None:
        dir_path = os.path.expanduser('~')
    caption = 'choose a recording'
    options = QFileDialog.Options()
    # to be able to see the caption, but impose to work with the mouse
    # options |= QFileDialog.DontUseNativeDialog
    fname = QFileDialog.getOpenFileName(caption=caption,
                                        directory=dir_path, filter='*.csv',
                                        options=options)
#    fname = QFileDialog.getOpenfilename(caption=caption,
#                                        directory=direct, filter='*.csv')
    #TODO : be sure to be able to see the caption
    return fname[0]

#%% Monitor trend
def loadmonitor_trendheader(filename):
    """ read filename (fullname) and return a dictionary """
    print('loading header', os.path.basename(filename))
    try:
        df = pd.read_csv(filename, sep=',', header=None, index_col=None,
                         nrows=11, encoding='iso8859_15')
    except Exception as e:
        print(e)
        return
    #NB encoding needed for accentuated letters
    df = df.set_index(0).T
    if 'Sampling Rate' not in df.columns:
        print('>>> this is not a trend record')
        return
    for col in ['Weight', 'Height', 'Sampling Rate']:
        df[col] = df[col].astype(float)
    # convert to a dictionary
    descr = df.loc[1].to_dict()
    return descr

def loadmonitor_trenddata(filename, header):
    """
    load the monitor trend data, return a pandasDataframe
    input :
        filename <-> fullname
        header <-> dictionary
    output :
        pandas dataframe
    """
    print('loading data', os.path.basename(filename))
    try:
        df = pd.read_csv(filename, sep=',', skiprows=[13], header=12)
    except:
        df = pd.read_csv(filename, sep=',', skiprows=[13], header=12,
                         encoding="ISO-8859-1")
    if len(df) == 0:
        print('no recorded values in this file', filename.split('/')[-1])
        return df
    #remove waves time indicators(column name beginning with a '~')
    for col in df.columns:
        if col[0] == '~':
            del df[col]
    to_fix = []
    for col in df.columns:
        if df[col].dtype != 'float64':
            if col != 'Time':
                to_fix.append(col)
    for col in to_fix:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    #elapsed time(in seconds)
    df['eTime'] = df.index * header['Sampling Rate']
    df['eTimeMin'] = df.eTime/60

    # correct the titles
    corr_title = {'AA  LB': 'aaLabel', 'AA_Insp':'aaInsp', 'AA_Exp':'aaExp',
                  'CO2 RR': 'co2RR', 'CO2_Insp': 'co2insp', 'CO2_Exp' : 'co2exp',
                  'ECG HR': 'ekgHR',
                  'IP1_M' : 'ip1m', 'IP1_S' : 'ip1s', 'IP1_D' : 'ip1d',
                  'IP1PR' : 'hr',
                  'IP2_M' : 'ip2m', 'IP2_S' : 'ip2s', 'IP2_D' : 'ip2d',
                  'IP2PR' : 'ip2PR',
                  'O2_Insp' : 'o2insp', 'O2_Exp' : 'o2exp',
                  'Time'   : 'datetime',
                  'Resp': 'resp',
                  'PPeak': 'pPeak', 'Peep' : 'peep', 'PPlat': 'pPlat', 'pmean':'pmean',
                  'ipeep':'ipeep',
                  'TV_Insp': 'tvInsp', 'TV_Exp' : 'tvExp',
                  'Compli': 'compli',
                  'raw': 'raw',
                  'MinV_Insp': 'minVinsp', 'MinV_Exp': 'minVexp',
                  'epeep': 'epeep', 'peepe': 'peepe', 'peepi': 'peepi',
                  'I:E': 'ieRat', 'Inp_T': 'inspT', 'Exp_T': 'expT', 'eTime': 'eTime',
                  'S_comp': 'sCompl', 'Spplat': 'sPplat'}
    df.rename(columns=corr_title, inplace=True)
#TODO fix the code for 1 and 2
    if 'aaLabel' in df.columns:
        anesth_code = {0 : 'none',
                       1 : '',
                       2 : '',
                       4 : 'iso',
                       6 : 'sevo'}
        df.aaLabel = df.aaLabel.fillna(0)
        df.aaLabel.apply(lambda x: anesth_code.get(int(x), ''))

    # remove empty rows and columns
    df.dropna(axis=0, how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    # should be interesting to export the comment
    # for index, row in df.iterrows():
    #     if len(row) < 6:
    #         print(index, row)
    # remove comments present in colon 1(ie suppres if less than 5 item rows)
    df = df.dropna(thresh=6)

    # CO2: from % to mmHg
    try:
        df[['co2exp', 'co2insp']] *= 760/100
    except:
        print('no capnographic recording')

    # convert time to dateTime
    df.datetime = df.datetime.apply(lambda x: header['Date'] + '-' + x)
    df.datetime = pd.to_datetime(df.datetime, format='%d-%m-%Y-%H:%M:%S')

    # remove irrelevant measures
    #df.co2exp.loc[data.co2exp < 30] = np.nan
    #TODO : find a way to proceed without the error pandas displays

    return df


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    file_name = choosefile_gui()
    file = os.path.basename(file_name)
    if file[0] == 'M':
        if 'Wave' not in file:
            header_dict = loadmonitor_trendheader(file_name)
            if header_dict is not None:
                mdata_df = loadmonitor_trenddata(file_name, header_dict)
                #mdata= cleanMonitorTrendData(mdata)
            else:
                mdata_df = None
