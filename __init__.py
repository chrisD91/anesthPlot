


"""
typîca use when importing the module 
to build a clinical case 

import os
import sys

import numpy as np
import pandas as pd

import anesthPlot.record_main as rec
sys.path.append(os.path.expanduser('~/pg/utils'))
from utils import saveGraph
import anesthPlot.plot.trend_plot as tplot
import anesthPlot.plot.wave_plot as wplot
import bloodGases.bgmain_manual as bgman

paths = rec.paths
paths['save'] = '/Users/cdesbois/enva/clinique/recordings/casClin/poney'
os.chdir(paths['save'])
"""