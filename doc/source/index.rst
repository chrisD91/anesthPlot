.. anesplot documentation master file, created by
   sphinx-quickstart on Wed Sep  8 17:19:08 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to anesplot's documentation!
====================================
Welcome to anesthPlot's documentation!
======================================

anesthPlot is a python package developped to extract, manipulate and plots anesthesia data 
recorded from the Monitor Software to be used mostly in a teaching environment.
 
.. warning::

   This project is:
   
      - a work in process
      - the processes are mainly focused on horses anesthesia
      - in our environment the data recorded came from an as3 or as5 anesthesia machine

Features
---------

- **load** recordings from a trend or a wave recordings
- build a **standard debriefing** (trends) **plot series** (script usage)

   - global histograms (cardiovascular and anesthesia summary)
   - cardiovascular trends time based plots
   - respiratory trends time based plots
   - anesthesia trends time based plots

- build a **plot for wave** recording (one or two waves (script usage)

- can be used as a **python package**

   - usage :
      .. code-block::  python
 
         import anesplot.record_main as rec
         trendname = 'a_full_path_to_csv_file'
         trends = rec.MonitorTrend(trendname)
         wavename = rec.trendname_to_wavename(trendname)
         waves = rec.MonitorWave(trends)
         trends.show_graphs()

main script
==================

.. toctree::
   :maxdepth: 1
   :caption: main_script:

   anesplot.record_main

modules
==================
.. toctree::
   :maxdepth: 4
   :caption: Contents:

   anesplot


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
