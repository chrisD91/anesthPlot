#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
anesthPlot is a package to plot/use clinical anesthesia records for teaching


two way to use it:

1. run directly anesplot from a terminal -> script mode

  .. code-block:: bash

   PYTHONPATH=<pathToAnesthPlot> python -m anesplot

   -> generate a quick plotting of most interestings parts
   (e.g. to use during an anesthesia debriefing session)

2. import in an ipython terminal or python environment -> module mode

   .. code-block:: python

       import anesthPlot.anesplot.recordmain as rec
       mtrends = rec.MonitorTrend()
       waves = rec.MonitorWave()
       ttrends = rec.TaphTrend()

   ​... and use the objects trends and waves


(the presets are actually designed
     - for use with equine anesthesia
     - to load data from a Monitor generated datex AS3/5 monitoring machine)


typical use when importing the module
to build a clinical case

.. code-block python

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

    # globals
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
    waves = rec.MonitorWave(waveName, load=True)

    # or append data (pretreated ones)
    #trends.data = pd.read_hdf(saveName, 'trend_df')
    #waves.data = pd.read_hdf(saveName, 'wave_df')

    #remove  filenames
    del waveName, trendName

    # now you are ready to work with loaded trends and waves


"""
import os
import logging

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication

plt.ion()

# activate the log file to ~/anesplot_log.log
logfile = os.path.expanduser(os.path.join("~", "anesplot_log.log"))
logging.basicConfig(
    level=logging.INFO,
    force=True,
    format="%(levelname)s:%(funcName)s:%(message)s",
    filename=logfile,
    filemode="w+",
    # handlers=[logging.FileHandler(logfile)],
)
logging.getLogger(name="matplotlib").setLevel(logging.WARNING)

app = QApplication.instance()
logging.info(f"anesplot.__init__.py : {__name__=}")
if app is None:
    # app = QApplication([])
    logging.warning("NO QApplication instance")
else:
    logging.warning(f"QApplication instance already exists: {QApplication.instance()}")
