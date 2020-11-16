#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 16:22:06 2019

@author: cdesbois
"""
import os
import sys

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
#    options |= QFileDialog.DontUseNativeDialog
    fname = QFileDialog.getOpenFileName(caption=caption,
                                        directory=dir_path, filter='*.csv',
                                        options=options)
#    fname = QFileDialog.getOpenfilename(caption=caption,
#                                        directory=direct, filter='*.csv')
    #TODO : be sure to be able to see the caption
    return fname[0]


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
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    filename = choosefile_gui(paths)
    file = os.path.basename(filename)
    ekg_data = loadtelevet(filename, all_traces=False)
