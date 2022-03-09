#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
anesthPlot is a package to plot/use clinical anesthesia records for teaching

three way to use it:
    1. run directly anesplot from a terminal
        -> PYTHONPATH=<pathToAnesthPlot> python -m anesplot
        -> generate a quick plotting of most interestings parts
        (e.g. to use during an anesthesia debriefing session)
    2. from an ipython terminal
        -> import anesthPlot.anesplot.recordmain as rec
        -> mtrends = rec.MonitorTrend()
        -> waves = rec.MonitorWave()
        -> ttrends = rec.TaphTrend()
        -> ... and use the objects trends and waves
    3. import the module in a python environment (see below)


(the presets are actually designed
     - for use with equine anesthesia
     - to load data from a Monitor generated datex AS3/5 monitoring machine)


typical use when importing the module
to build a clinical case

import os
import sys

import numpy as np
import pandas as pd

import anesplot.record_main as rec
sys.path.append(os.path.expanduser('~/pg/utils'))
from utils import saveGraph
import bloodGases.bgmain_manual as bgman

paths = rec.paths
paths['save'] = os.path.expanduser('~/toPlay/temp/')
os.chdir(paths['save'])

## globals
def save_plot(name):
    filename = os.path.join(paths['save'], 'fig', name)
    saveGraph(filename, ext='png', close=False, verbose=True)

def explore_hdf(filename):
    try:
        hdf = pd.HDFStore(filename)
        keys= [key.replace('/', '') for key in hdf.keys()]
        print(' found h5_file {}
              that contains {}'.format(filename, keys))
        hdf.close()
    except:
        print('{} is not an h5 file'.format(filename))


saveName = os.path.join(paths['save'], 'data', 'aname.h5')

explore_hdf(saveName)


## load and work
trendName = rec.choosefile_gui(paths['data'])
WaveName = rec.choosefile_gui(paths['data'])


# build objects with headers
trends = rec.MonitorTrend(trendName, load=True)
waves = rec.MonitorWave(waveName, load=True

# or append data (pretreated ones)
#trends.data = pd.read_hdf(saveName, 'trend_df')
#waves.data = pd.read_hdf(saveName, 'wave_df')

#remove  filenames
del waveName, trendName

# now you are ready to work with loaded trends and waves

"""


# For relative imports to work in Python 3.6
import os
import sys

# see https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
from pathlib import Path

# import pyperclip


# to be able to use imports in spyder
# from PyQt5.QtWidgets import QApplication, QFileDialog


print("Running" if __name__ == "__main__" else "Importing", Path(__file__).resolve())
if os.path.dirname(os.path.realpath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))


# build a QApplication to be able to use a Qt GUi to choose files or waves
# try:
#     isinstance(app, QApplication)
# except NameError:
#    app = QApplication(sys.argv)
#    app.setQuitOnLastWindowClosed(True)

# required when importing record_main from an external ipython terminal
# app = QApplication(sys.argv)
