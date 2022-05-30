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
    5 	 samplePaVariation.txt
    -------------------------

 .. code-block:: python

     > enter 0
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
in csv2hdf.py execute :

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

    > 1
    the content of 'csv2hdf.txt' is in your clipboard

paste in csv2hdf -> the resulting file:

.. code-block:: python

    import os

    import anesplot.record_main as rec
    from anesplot.loadrec.export_reload import export_data_to_hdf

    paths = rec.paths
    paths["save"] = "~"

    # %% load and save to hdf
    m_name = None
    mtrends = rec.MonitorTrend(m_name)
    mwaves = rec.MonitorWave(rec.trendname_to_wavename(mtrends.filename))
    ttrends = rec.TaphTrend(monitorname=mtrends.filename)
    t_name = None
    ttrends = rec.TaphTrend(t_name)

    name = mtrends.header["Patient Name"].title().replace(" ", "")
    name = name[0].lower() + name[1:]


    mtrends.show_graphs()
    ttrends.show_graphs()
    ## correction for machine time (in minutes)
    # ttrends.shift_datetime(60)

    ## correction for etime (minutes and sec) based on the start of the monitor recording
    # mstart = mtrends.data.datetime.iloc[0]
    # ttrends.sync_etime(mstart)


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
