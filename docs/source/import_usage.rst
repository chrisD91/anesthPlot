use anesplot as a package : import anesplot in a python environment
-------------------------------------------------------------------

- you can use this code as a **python package** ('import mode'):
      
   here is an example python code

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

      **'rec.get_basic_debrief_commands()**' will prefill the clipboard with 'a standard' code template

   - additional functions are available to extract instaneous heart rate, overlap ekg beats, extract blood pressure systolic variation, ...

      - see for example anesplot/treatrec/ekg_to_hr.py

.. hint:: 
   **'rec.get_guide()'** will fill the clipboard with code templates of standard approaches

