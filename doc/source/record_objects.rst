record_objects
---------------


record_objects
--------------

the recorded data and associated methods are loaded in "wave classes".

four classes are builded to store and display the data and manipulate them, two for slowWaves ('trends'), two for fastWaves:

  - MonitorTrend
  - MonitorWave 
  - TaphTrend
  - TelevetWave

loading is possible from an ipython terminal: 

   .. code-block:: python

      mtrends = rec.MonitorTrend()
      mwaves = rec.MonitorWave()
      ttrends = rec.TaphTrend()
      telwaves = rec.TelevetWave()  <- this has to be improved quite a lot 

the methods provided allows to choose plotting and treatment actions
for example ::

   mtrends, ttrends:      
      # attributes =  'data', 'fig', 'filename', 'header', 'param', ...
      # methods = 'show_graphs', 'clean_trend', 'plot_trend', 'save_roi', ...

   mwaves:
      # attributes = 'data', 'fig', 'filename', 'header', 'param' ... 
      # methods : 'animate_fig', 'filter_ekg', 'plot_sample_ekgbeat_overlap', 'plot_sample_systolic_variation', 'plot_wave', ...


MonitorTrend object
....................
   
   .. automodule:: anesplot.slow_waves.MonitorTrend


TaphTrend object
....................

   .. automodule:: anesplot.slow_waves.TaphTrend


MonitorWave object
....................

   .. automodule:: anesplot.fast_waves.MonitorWave


TelevetWave object
....................

   .. automodule:: anesplot.fast_waves.TelevetWave