#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
anesthPlot is a package to plot/use clinical anesthesia records for teaching

three way to use it:
    1. run directly anesplot from a terminal
        -> PYTHONPATH=<pathToAnesthPlot> python -m anesplot
        -> generate a quick plotting of most interestings parts
    2. from an ipython terminal
        -> import anesplot as aplot
        -> trends = aplot.rec.MonitorTrend()
        -> ...
    3. import the module to in a python environment (see below)


(the presets are actually designed 
     - for use with equine anesthesia
     - to load data from a Monitor generated datex AS3/5 monitoring machine)


typical use when importing the module 
to build a clinical case 

import os
import sys

import numpy as np
import pandas as pd

import anesthPlot.anesplot.record_main as rec
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
# print('-'*10)
# print('this is {} file and __name__ is {}'.format('__init__', __name__))
# print('this is {} file and __package__ is {}'.format('__init__', __package__))
# print('-'*10)

# import anesplot.config
# import anesplotloadrec
# import anesplot.treatrec
# import  anesPlot.record_main


from anesplot import record_main as rec
from anesplot import treatrec