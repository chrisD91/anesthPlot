#!/usr/bin/env python3
"""
Created on Fri Aug  5 14:41:23 2022

select a directory containing monitor trends
select a trend plot function
scan all the files using this function

@author: cdesbois
"""

import logging
import os
from typing import Any, Optional

from PyQt5.QtWidgets import QApplication

import anesplot.loadrec.dialogs as dlg
import anesplot.plot.trend_plot as tplot
import anesplot.record_main as rec
from anesplot.loadrec.loadmonitor_trendrecord import loadmonitor_trenddata
from anesplot.loadrec.loadtaph_trendrecord import (
    list_taph_recordings,
    loadtaph_trenddata,
)

# from anesplot.slow_waves import TaphTrend

# import get_file, get_directory

paths = rec.paths

app = QApplication.instance()
logging.info(f"scanplot_directory.py : {__name__=}")
if app is None:
    logging.info("N0 QApplication instance -> creating one")
    app = QApplication([])
else:
    logging.warning(f"QApplication instance already exists: {QApplication.instance()}")


def get_directory() -> str:
    """Choose the directory to scan."""
    dirname = dlg.choose_directory(
        dirname=paths["mon_data"],
        title="choose the folder to scan",
    )
    return dirname


def is_taph(dirname: str) -> Any:
    """Return True if dirname contains taph recordings."""
    return "taph" in dirname.lower()


def get_plot_function(taph: bool = False) -> Any:
    """
    Choose the plot_function to use.

    Parameters
    ----------
    taph : boolean, optional (default is False)
        taph recording or not

    Returns
    -------
    func :
        the trend plot_function to use.

    """
    func_list = [
        tplot.plot_ventil,
        tplot.plot_ventilcardio,
        tplot.plot_co2o2,
        tplot.plot_co2aa,
        tplot.plot_cardiovasc,
        tplot.hist_co2aa,
        tplot.hist_cardio,
    ]
    if taph:
        func_list.insert(0, tplot.plot_sathr)
    else:
        func_list.insert(5, tplot.plot_cardiovasc_p1p2)
    question = "choose the function to use"
    names = [st.__name__ for st in func_list[::-1]]
    name = dlg.choose_in_alist(names, message=question)
    func = [_ for _ in func_list if _.__name__ == name][0]
    return func


def list_taphtrendfiles(dirname: str) -> dict[str, list[str]]:
    """
    Return taph trendfiles as a dictionary (year:fullname).

    Parameters
    ----------
    dirname : str
        the directory to scan.

    Returns
    -------
    dict[str, str]
        taphtrends names {year:[fullnames]}.

    """
    filesdico = list_taph_recordings(dirname)
    years = {_.split("_")[0].strip("SD") for _ in filesdico.keys()}
    files_byyear = dict()
    for year in years:
        files_byyear[year] = [v[0] for k, v in filesdico.items() if year in k]
    return files_byyear


def list_montrendfiles(dirname: str) -> list[str]:
    """
    Scan the directory and plot every monitor trend record using the func.

    Parameters
    ----------
    dirname : str
        the directory to scan.
    func : Any
        the plot function to use.

    Returns
    -------
    files : list
        the list of all record name.

    """
    files: list[str] = []
    for entry in os.scandir(dirname):
        if "Wave" in entry.name:
            continue
        if entry.name.startswith("."):
            continue
        if not entry.name.endswith("csv"):
            continue
        if entry.is_file():
            files.append(entry.path)
    return files


def loadplot_mondata(files: list[str], func: Any) -> None:
    """
    Load and plot the monitor record.

    Parameters
    ----------
    files : list[str]
        file list.
    func : plot function
        the plot function to use.

    Returns
    -------
    None.

    """
    for file in files:
        data_df, _ = loadmonitor_trenddata(file)
        if data_df.empty:
            continue
        fig = func(data_df, {"dtime": False, "file": os.path.basename(file)})
        fig.show()
    return


def loadplot_taphdata(files: list[str], func: Any) -> None:
    """
    Load and plot the taph record.

    Parameters
    ----------
    files : list[str]
        record list (fullname).
    func : Any
        the plot function to use.

    Returns
    -------
    None

    """
    for file in files:
        data_df = loadtaph_trenddata(file)
        if data_df.empty:
            continue
        fig = func(data_df, {"dtime": False, "file": os.path.basename(file)})
        fig.show()
    return


def main(apath: Optional[str] = None) -> list[str]:
    """Scan directory and plot the choosed plots."""
    if apath is None:
        apath = os.path.expanduser("~")
    dir_name = dlg.choose_directory(apath, title="choose a folder", see_question=True)
    is_taphrec = is_taph(dir_name)
    if is_taphrec:
        yearfiles = list_taphtrendfiles(dir_name)
        years = sorted(list(yearfiles.keys()), reverse=True)
        year = dlg.choose_in_alist(years, message="choose the year")
        file_list = yearfiles[year]
    else:
        file_list = list_montrendfiles(dir_name)

    funct = get_plot_function(is_taphrec)

    if is_taphrec:
        loadplot_taphdata(file_list, funct)
    else:
        loadplot_mondata(file_list, funct)

    logging.warning("'file_list' contains a list of all plotted record names")
    return file_list


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    main(paths["mon_data"])
    plt.show()
    # plt.draw()
    # plt.pause(0.001)
