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

# import sys
from datetime import datetime
from types import SimpleNamespace
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import pyperclip
from matplotlib import rcParams
from PyQt5.QtWidgets import QApplication

# from PyQt5.QtWidgets import QApplication
import anesplot.loadrec.agg_load as loadagg
from anesplot.config.load_recordrc import build_paths
from anesplot.fast_waves import MonitorWave, TelevetWave
from anesplot.slow_waves import MonitorTrend, TaphTrend
from anesplot.guides.choose_guide import get_guide  # pylint: disable=unused-import
import anesplot.loadrec.dialogs as dlgs

paths = build_paths()
matplotlib.use("Qt5Agg")  # NB required for the dialogs
# to have the display beginning from 0
rcParams["axes.xmargin"] = 0
rcParams["axes.ymargin"] = 0

faulthandler.enable()

# if "app" not in dir():
#    app = QApplication(sys.argv)
#    app.setQuitOnLastWindowClosed(False)
fig_group = SimpleNamespace()


def append_to_figures(
    figs: SimpleNamespace, figdico: dict[str, plt.Figure], key: str = "t"
) -> None:
    """
    Link figures to a simpleNameSpace variables.

    Parameters
    ----------
    figures : SimpleNamespace
        group the figures names for easy access.
    figdico : dict[str, plt.Figure]
        list of builded figures.
    add_key : str, optional (default is "t")
        key to add to the figure name

    Returns
    -------
    None.

    """
    for name, fig in figdico.items():
        setattr(figs, name + "_".join([name, key]), fig)


def organize_debrief_folder() -> None:
    """
    Build file and sub_folders for debrief process inside the current directory.

    Returns
    -------
    None.

    """
    now = datetime.now()
    date = now.strftime("%Y_%m_%d-%H:%m:%S")
    os.chdir("/Users/cdesbois/toPlay/dir_test")

    shebang = ["#!/usr/bin/env python3", "# -*- coding: utf-8 -*-", ""]
    build = [
        '"""',
        f"Created on {date}",
        "",
        f"@author: {os.path.basename(os.path.expanduser('~'))}",
        '"""',
    ]

    for directory in ["data", "fig", "doc", "bib"]:
        try:
            os.mkdir(directory)
            print(f"builded {directory}")
        except FileExistsError:
            print(f"directory {directory} already exist")

    for file in ["csv2hdf.py", "ekg2hr.py", "work_on.py", "todo.md"]:
        if os.path.exists(file):
            print(f"{file} already exists")
        else:
            with open(file, "w", encoding="utf-8") as openf:
                if file.rsplit(".", maxsplit=1)[-1] == "py":
                    openf.writelines(line + "\n" for line in shebang)
                openf.writelines(line + "\n" for line in build)


def get_basic_debrief_commands() -> str:
    """Copy in clipboard the usual commands to build a debrief."""
    lines = [
        "mtrends = rec.MonitorTrend()  #<- add filename here (if you know it)",
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


def main(file_name: Optional[str] = None) -> str:
    """
    Script called from command line.

    call : "python record_main.py"
    call a GUI, load recording and display a series of plt.figure
    NB filename will be placed in the clipboard

    Parameters
    ----------
    file_name : str, optional (default is None)
        recordfile fullname .

    Returns
    -------
    None.
    """
    # faulthandler.enable()
    # os.chdir(paths.get("recordMain", os.path.expanduser('~')))
    print(f"backEnd= {plt.get_backend()}")  # required ?
    print("start QtApp")
    # global APP
    # if "app" not in dir():
    # 1 print ("app not in dir()")
    # app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(True)
    # app = QApplication.instance()
    # if app is None:
    # app = QApplication([])
    # choose file and indicate the source
    print("select the file containing the data")
    print(f"file_name is {file_name}")
    if file_name is None:
        # file_name = loadagg.choosefile_gui(paths["data"])
        file_name = dlgs.choose_file("", paths["data"], "*.csv")
    if not file_name:
        return ""
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
    return file_name


# %%
if __name__ == "__main__":
    # app = QApplication.instance()
    if QApplication.instance() is None:
        app = QApplication([])
    else:
        print(f"QApplication instance already exists: {QApplication.instance()}")
    main()
