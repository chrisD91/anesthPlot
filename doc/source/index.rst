.. anesplot documentation master file, created by
   sphinx-quickstart on Wed Sep  8 17:19:08 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to anesplot's documentation!
====================================

anesthPlot is a python package developped to extract, manipulate and plots anesthesia data 
recorded from the Monitor Software to be used mostly in a teaching environment.
 
.. warning::

   This project is:
   
      - a work in progres
      - the processes are mainly focused on horses anesthesia (default values)
      - in our environment the data recorded came from either
       
        - an as3 or as5 anesthesia monitor (ekg, invasive pressure, etCO2, halogenate, spirometry)
        - a Taphonius equine ventilator
        - (some ekg data extracted using a Televet holter system)


Features
---------

- you can **load** recordings from a trend or a wave file

   - from command line:
      .. code-block:: bash

         python anesthPlot/anesplot/__main__.py
         or
         python -m anesplot
         -> will open an GUI choose menu to choose the recording 
         (MonitorTrend, TaphoniusTrend, MonitorWave, TelevetWave(from a .csv export))


      - will build a **standard debriefing** (trends) **plot series** (script usage)
         
         - global histograms (cardiovascular and anesthesia summary)
         - cardiovascular trends time based plots
         - respiratory trends time based plots
         - anesthesia trends time based plots

      - or will build a **plot for wave** recording 
  
         - one or two waves on the same plot (script usage)

- you can also use this code as a **python package**

   - usage :
      .. code-block::  python
 
         import anesplot.record_main as rec
         trendname = 'a_full_path_to_csv_file'
         # nb if no filename is provided, a chooseFile Gui will be called to choose the file
         trends = rec.MonitorTrend(trendname)
         #(you can also use trends = rec.taphTrend()
         wavename = rec.trendname_to_wavename(trendname)
         waves = rec.MonitorWave(wavename)
        
         trends.show_graphs() # -> set of plots for 'clinical' debriefing purposes

         waves.plot_waves() # -> one or two traces
         # ... adjust manually the scales of the display
         waves.define_a_roi() # -> to register the plotting scales
         waves.animate_fig() #-> to build an animation using these parameters

   - additional functions are available to extract instaneous heart rate

      - see anesplot/treatrec/ekg_to_hr.py




main script
=============

.. note::

   - anesplot/__main__.py:
     - can be called directly from a terminal :
  
     "python -m anesplot" or "python anesplot/__main__.py"
    
     - is the entry point to the program ('record_main.py')


.. toctree::
   :maxdepth: 1
   :caption: main_script:

   anesplot.record_main


modules
==================
.. toctree::
   :maxdepth: 4
   :caption: Contents:

   anesplot.guides
   anesplot.loadrec
   anesplot.plot
   anesplot.treatrec
   anesplot.config


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
