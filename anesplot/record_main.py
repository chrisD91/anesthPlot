#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main script/module to load and display an anesthesia record

can be runned as a script::
    "python record_main.py" or "python -m anesplot"

or imported as a package::

    import anesplot.record_main as rec
    %gui qt5 (required only to use the dialogs if using spyder)

    # objects:
    mtrends = rec.MonitorTrend()
    waves = rec.MonitorWave(rec.trendname_to_wavename(mtrends.filename))
    ttrends = rec.TaphTtrend()

    # use methods and or attributes:
    mtrends.show_graphs() -> clinical debrief selection
    waves.plot_wave() -> select one or two waves to plot

    ...

----
nb to work within spyder : move inside anestplot (>> cd anesplot)

"""

import faulthandler
import os
import sys
import pyperclip

import matplotlib
from matplotlib import rcParams
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg")  # NB required for the dialogs
import pandas as pd

from anesplot.config.load_recordrc import build_paths
from PyQt5.QtWidgets import QApplication

paths = build_paths()

import anesplot.loadrec.agg_load as loadagg

# import plot.t_agg_plot as tagg
# import plot.w_agg_plot as wagg

# import plot.trend_plot as tplot
# import plot.wave_plot as wplot
# import treatrec
# import treatrec.clean_data as clean
# import treatrec.wave_func as wf
# from guides.choose_guide import get_guide

# requires to have '.../anesthPlot' in the path
# import loadrec
# from loadrec import loadmonitor_trendrecord as lmt
# from loadrec import loadmonitor_waverecord as lmw
# from loadrec import loadtaph_trendrecord as ltt
# from loadrec import loadtelevet as ltv

# import anesplot.treatrec as treat

# to have the display beginning from 0
rcParams["axes.xmargin"] = 0
rcParams["axes.ymargin"] = 0

faulthandler.enable()
# APP = QApplication(sys.argv)


from anesplot.slow_waves import MonitorTrend, TaphTrend
from anesplot.fast_waves import MonitorWave, TelevetWave


def get_basic_debrief_commands():
    """copy in clipboard the usual commands to build a debrief"""
    lines = [
        "mtrends = rec.MonitorTrend()",
        "mwaves = rec.MonitorWave(rec.trendname_to_wavename(mtrends.filename))",
        "ttrends = rec.TaphTrend(monitorname = mtrends.filename)",
    ]
    print("basic debrief commands are in the clipboard")
    return pyperclip.copy(" \n".join(lines))


def trendname_to_wavename(name: str) -> str:
    """just compute the supposed (full)name"""
    return name.split(".")[0] + "Wave.csv"


def main(file_name: str = None):
    """
    main script called from command line
    call : "python record_main.py"
    call a GUI, load recording and display a series of plt.figure
    NB filename will be placed in the clipboard

    Parameters
    ----------
    file_name : str, optional
        recordfile fullname (default is None).

    Returns
    -------
    None.

    """
    # os.chdir(paths.get("recordMain", os.path.expanduser('~')))
    print(f"backEnd= {plt.get_backend()}")  # required ?
    print("start QtApp")
    # global APP
    if "app" not in dir():
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)

    # choose file and indicate the source
    print("select the file containing the data")
    print(f"file_name is {file_name}")
    if file_name is None:
        file_name = loadagg.choosefile_gui(paths["data"])
    kinds = ["monitorTrend", "monitorWave", "taphTrend", "telVet"]
    # select base index in the scroll down
    num = 0
    if "Wave" in file_name:
        num = 1
    if not os.path.basename(file_name).startswith("M"):
        num = 2
    source = loadagg.select_type(question="choose kind of file", items=kinds, num=num)

    if not os.path.isfile(file_name):
        print("this is not a file")
    elif source == "telVet":
        telvet = TelevetWave(file_name)
        telvet.plot_wave()
    elif source == "monitorTrend":
        monitor_trend = MonitorTrend(file_name)
        monitor_trend.show_graphs()
    elif source == "monitorWave":
        monitor_wave = MonitorWave(file_name)
        fig, *_ = monitor_wave.plot_wave()
    elif source == "taphTrend":
        taph_trend = TaphTrend(file_name)
        taph_trend.show_graphs()
    else:
        print("this is not a recognized recording")

    pyperclip.copy(file_name)
    plt.show()
    # app.quit()


# %%
# if __name__ == "__main__":
#     IN_NAME = None
#     # check if a filename was provided from terminal call
#     print(sys.argv)

#     if len(sys.argv) > 1:
#         provided_name = sys.argv[1]
#         if os.path.isfile(provided_name):
#             IN_NAME = provided_name
#         else:
#             print("the provided filename is not valid")
#     main(IN_NAME)
