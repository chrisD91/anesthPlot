script or package
=================

use anesplot as a script from a terminal
-----------------------------------------

- you can **load** recordings from a trend or a wave file

   - from command line ('script mode'):
      .. code-block:: bash

         python anesthPlot/anesplot/__main__.py
         or
         python -m anesplot
         -> this will open an GUI choose menu to choose the recording 
         (MonitorTrend, TaphoniusTrend, MonitorWave, TelevetWave)


      - this script approach will build a **standard plot series** for debriefing purposes:
         
         - global histograms (cardiovascular and anesthesia summary)
         - cardiovascular time based trends plots
         - respiratory time based trends plots
         - anesthesia time based trends plots

      - or will build a user selected **plot for wave** recording 
  
         - one or two waves on the same plot (script usage, pop_up menu to choose)

   .. note::
      after the plots have been displayed, you can use the graphical interface to scale and save the plots


import anesplot in a python environment
----------------------------------------

   - you can use this code as a **python package** ('import mode'):
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

      .. hint::   
         after **'import anesplot.record_main as rec'**

         **'rec.get_basic_debrief_commands()**' will prefill the clipboard with this standard code

   - additional functions are available to extract instaneous heart rate

      - see anesplot/treatrec/ekg_to_hr.py

.. hint:: 
   **'rec.get_guide()'** allow the filling of the clipboard with standard approaches
