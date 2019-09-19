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
def guiChooseFile(paths, direct=None):
    """Select a file via a dialog and return the file name.
    """
    if not direct:
        direct = paths['data']
    fname = QFileDialog.getOpenFileName(caption='choose a file',
                                        directory=direct, filter='*.csv')   
    return fname[0]


def loadTeleVet(file=None, allTraces=False):
    filePath = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTelVetRecorded'
    if not file:
        file = 'STEF_0031_00114_20171205_121305.csv'
    fileName = os.path.join(filePath, file)
    if not os.path.isfile(fileName):
        print('no file for ', fileName)
        return

    if allTraces:
        df = pd.read_csv(fileName, sep=';')
    else:
        df = pd.read_csv(fileName, sep=';', usecols=[2])  # only d2 loaded

    df.rename(columns={'Channel1': 'd1', 'Channel2' : 'd2', 'Channel3': 'd3'},
          inplace=True)
    df /= 100       # to mV
    df['timeS'] = df.index / 500
    df['timeM'] = df.timeS / 60

    return(df)


if __name__ == '__main__':
    fileName = guiChooseFile(paths)          
    file = os.path.basename(fileName)
    ekgData = loadTeleVet(fileName, allTraces=False)
