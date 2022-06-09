test with the example files
===========================

1. load the data
----------------

.. code-block:: python3

    import os
    import anesplot.record_main as rec
    paths = rec.path()
    monitorname = os.path.join(paths['cwd'], 'example_files', 'M2021_4_16-8_44_38.csv')
    mtrends = rec.MonitorTrend(monitorname)
    mwaves = rec.MonitorWave(rec.trendname_to_wavename(mtrends.filename))
    taphname = os.path.join(paths['cwd'], 'example_files', 'SD2021APR16-7_19_4.csv')
    ttrends = rec.TaphTrend(taphname)
    # perform a correction for the time shift between the two computers
    ttrends.shift_datetime(60)

2. play with the monitor_trend_object
--------------------------------------

.. code-block:: python3

    mtrends.show_graphs()        # -> 'clinical debrief'

    # close the plots one by one

    trends.plot_trend()          # -> choose a time based plot (for example cardiovascular)
    # use the loop to zoom on an ineresting part
    mtrends.save_roi()           # save the plot information
    mtrends.build_half_white(lang='en')   # build debrief slides


1. play with the taph_trend_object
--------------------------------------

.. code-block:: python3

    ttrends.show_graphs()        # -> 'clinical debrief'
    ttrends.plot_ventil_drive()   # -> plot the ventilation management


4. play with the monitor_wave_object
--------------------------------------

.. code-block:: python3

    mwaves.plot_wave()   # choose the wave(s) to plot
    # zoom and select an interesting part of the recording
    mwaves.save_roi()
    # if ekg you can try
    mwaves.plot_roi_ekgbeat_overlap()
    # if arterial pressure you can try
    mwave.plot_roi_systolic_variation()
    # or to build a video
    mwave.animate_fig()


cookbook
========

1. initialize the working directory
-----------------------------------

build from a terminal:

.. code-block:: bash

    $ mkdir anInterestingCase
    $ cd anInterestingCase
    $ touch example_file.py
    $ open example_file.py

in example_file.py

.. code-block:: python

    import os
    import anesplot.record_main as rec
    # move to the working directory
    os.chdir('path_to_anInterestingCase')
    # get terminal template
    rec.get_guide()

.. line-block:: the output:

        type the index of the file
    -------------------------
    0 	 buildPyFiles.txt
    1 	 csv2hdf.txt
    2 	 ekg2hr.txt
    3 	 guide_ekg_to_hr.txt
    4 	 hdf2work.txt
    5 	 roiPaVariation.txt
    -------------------------

.. code-block:: python

     > type 0 & enter
     the content of 'buildPyFiles.txt' is in your clipboard

 paste and execute in terminal:

.. code-block:: bash

    $ mkdir data
    $ touch csv2hdf.py ekg2hr.py work_on.py todo.md

.. line-block:: the initialized working directory

    anInterestingCase
    ├── example_file.py
    ├── csv2hdf.py
    ├── ekg2hr.py
    ├── work_on.py
    ├── todo.md
    └── data/

1. load the data and save to hdf
--------------------------------
execute in an ipython terminal:

.. code-block:: python

    rec.get_guide()

.. line-block::

    type the index of the file
    -------------------------
    0 	 buildPyFiles.txt
    1 	 csv2hdf.txt
    2 	 ekg2hr.txt
    3 	 guide_ekg_to_hr.txt
    4 	 hdf2work.txt
    5 	 samplePaVariation.txt
    -------------------------

.. code-block:: python

    > type 1 & enter
    the content of 'csv2hdf.txt' is in your clipboard

open csv2hdf.py and paste the content of you clipboard
-> the resulting file:

.. code-block:: python

    import os

    import anesplot.record_main as rec
    from anesplot.loadrec.export_reload import export_data_to_hdf

    paths = rec.paths
    paths["save"] = "~"     # <--- the directory to save-in (FILL ME)

    ############################################# load
    m_name = None           # <--- the monitor filename (FILL ME)
    mtrends = rec.MonitorTrend(m_name)
    mwaves = rec.MonitorWave(rec.trendname_to_wavename(mtrends.filename))

    ttrends = rec.TaphTrend(monitorname=mtrends.filename)   # comment when t_name is defined
    # --> a dialog will appear to choose the right file according to the monitor filename

    t_name = ''             # <--- FILL ME (use the value of ttends.filename)
    ttrends = rec.TaphTrend(filename = t_name)  # --> will load without the dialog

    ############################################# look at the data
    mtrends.show_graphs()
    ttrends.show_graphs()

    ############################################# adapt
    # ttrends.shift_datetime(60)  # ---> correction? between monitor and taph file (in minutes)
    # ---> check the result

    ## correction for etime (minutes and sec) based on the start of the monitor recording
    # mstart = mtrends.data.datetime.iloc[0]
    # ttrends.sync_etime(mstart)

    ############################################# export to hdf
    name = mtrends.header["Patient Name"].title().replace(" ", "")
    name = name[0].lower() + name[1:]

    save_name = os.path.join(paths["save"], 'data', name + ".hdf")
    save = False
    if save:
        export_data_to_hdf(save_name, mtrend=mtrends, mwave=mwaves, ttrend=ttrends)




  execute it line by line
  and field the missing fields:

    - path["save"]  # the path_to_anInterestingCase  + folder 'data'
    -  m_name =       # the monitor filename
        - NB running rec.MonitorTrend() without argument will allow
            - to choose a file
            - to get the filename (fullname) available in the clipboard
            - assign the filename to m_name to fix the value in the code
    -  t_name =     # the taphonius filename
        - NB using monitorname as an argument allow to get the closest recording date in the choosefile menu
        - ie check the date and time
        - assign the value of ttrends.filename to t_name to fix the value in the code
