#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 16:22:06 2019

@author: cdesbois
"""
import os
import pandas as pd
from PyQt5.QtWidgets import QFileDialog

#%%
def gui_choosefile(paths, direct=None):
    """ Select a file via a QtDialog, return the filename (str). """
    if not direct:
        assert paths['data']
        direct = paths['data']
    fname = QFileDialog.getOpenfilename(caption='choose a file',
                                        directory=direct, filter='*.csv')
    name = fname[0]
    return name


def loadtelevet(file=None, all_traces=False):
    """ load the televetCsvExportedFile, return a pandasDataframe """
    filepath = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTelVetRecorded'
    if not file:
        file = 'STEF_0031_00114_20171205_121305.csv'
    filename = os.path.join(filepath, file)
    if not os.path.isfile(filename):
        print('no file for ', filename)
        return

    if all_traces:
        df = pd.read_csv(filename, sep=';')
    else:
        df = pd.read_csv(filename, sep=';', usecols=[2])  # only d2 loaded

    df.rename(columns={'Channel1': 'd1', 'Channel2' : 'd2', 'Channel3': 'd3'},
              inplace=True)
    df /= 100       # to mV
    df['timeS'] = df.index / 500
    df['timeM'] = df.timeS / 60

    return df

try:
    paths
except:
    paths = {}

if __name__ == '__main__':
    filename = gui_choosefile(paths)
    file = os.path.basename(filename)
    ekg_data = loadtelevet(filename, all_traces=False)
