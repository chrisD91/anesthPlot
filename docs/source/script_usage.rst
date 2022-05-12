use anesplot as a script : call from a terminal 
-----------------------------------------------

- you can **choose** a recordings, **load** it and **plot** the data from a terminal:
   

   .. code-block:: bash

      python anesthPlot/anesplot/__main__.py
      or
      python -m anesplot

- the command  will open an GUI choose menu to choose the recording 
      (MonitorTrend, TaphoniusTrend, MonitorWave, TelevetWave)

- this script approach will build a **standard plot series** for debriefing purposes:
         
   - global histograms (cardiovascular and anesthesia summary)
   - cardiovascular time based trends plots
   - respiratory time based trends plots
   - anesthesia time based trends plots

- or will build a **plot for wave** recording 
  (the user will be asked to choose the wave to be displayed) 
  
   - one or two waves on the same plot (script usage, pop_up menu to choose)

.. note::
   after the plots have been displayed, you can use the graphical interface to scale and save the plots
