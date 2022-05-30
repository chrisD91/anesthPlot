# !/usr/bin/env python3

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

nb to work within spyder : move inside anestplot (>> cd anesplot)

"""

import faulthandler
import os
import sys
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import pyperclip
from matplotlib import rcParams
from PyQt5.QtWidgets import QApplication

import anesplot.loadrec.agg_load as loadagg
from anesplot.config.load_recordrc import build_paths
from anesplot.fast_waves import MonitorWave, TelevetWave
from anesplot.slow_waves import MonitorTrend, TaphTrend
from anesplot.guides.choose_guide import get_guide  # pylint: disable=unused-import

paths = build_paths()
matplotlib.use("Qt5Agg")  # NB required for the dialogs
# to have the display beginning from 0
rcParams["axes.xmargin"] = 0
rcParams["axes.ymargin"] = 0

faulthandler.enable()


def get_basic_debrief_commands() -> str:
    """Copy in clipboard the usual commands to build a debrief."""
    lines = [
        "mtrends = rec.MonitorTrend()",
        "mwaves = rec.MonitorWave(rec.trendname_to_wavename(mtrends.filename))",
        "ttrends = rec.TaphTrend(monitorname = mtrends.filename)",
    ]
    message = "basic debrief commands are in the clipboard"
    # print(message)
    splitlines = " \n".join(lines)
    pyperclip.copy(splitlines)
    return message


def trendname_to_wavename(name: str) -> str:
    """Compute the supposed (full)name."""
    return name.split(".")[0] + "Wave.csv"


def main(file_name: Optional[str] = None) -> None:
    """
    Script called from command line.

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
        monitor_wave.plot_wave()
    elif source == "taphTrend":
        taph_trend = TaphTrend(file_name)
        taph_trend.show_graphs()
    else:
        print("this is not a recognized recording")

    pyperclip.copy(file_name)
    plt.show()


# %%
if __name__ == "__main__":
    main()
