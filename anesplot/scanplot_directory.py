#!/usr/bin/env python3
"""
Created on Fri Aug  5 14:41:23 2022

select a directory containing monitor trends
select a trend plot function
scan all the files using this function

@author: cdesbois
"""

import os
from typing import Any


import anesplot.record_main as rec
import anesplot.plot.trend_plot as tplot
import anesplot.loadrec.dialogs as dlg
from anesplot.loadrec.loadmonitor_trendrecord import loadmonitor_trenddata
from anesplot.loadrec.loadtaph_trendrecord import list_taph_recordings
from anesplot.slow_waves import TaphTrend

# import get_file, get_directory

paths = rec.paths


def get_directory() -> str:
    """Choose the directory to scan."""
    dirname = dlg.choose_directory(
        "choose the folder to scan", dirname=paths["mon_data"]
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
        tplot.plot_co2o2,
        tplot.plot_co2aa,
        tplot.plot_cardiovasc,
        tplot.hist_co2aa,
        tplot.hist_cardio,
    ]
    if taph:
        func_list.insert(0, tplot.plot_sathr)
    question = "choose the function to use"
    names = [st.__name__ for st in func_list[::-1]]
    name = dlg.choose_in_alist(names, message=question)
    func = [_ for _ in func_list if _.__name__ == name][0]
    return func


def scandir(dirname: str, func: Any, taph: bool) -> list[str]:
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
    files = []
    if taph:
        filesdico = list_taph_recordings(paths["taph_data"])
        for file, filelist in filesdico.items():
            files.append(file)
            ttrend = TaphTrend(filelist[0])
            func(ttrend.data, ttrend.param)
            # TODO add a filter (eg by year) -> too many recordings
    else:
        for entry in os.scandir(dirname):
            if "Wave" not in entry.name and entry.is_file():
                files.append(entry.path)
                # files.append(os.path.join(paths['mon_data'], file))
                # mtrend = MonitorTrend(entry.path)
                data_df, _ = loadmonitor_trenddata(entry.path)
                func(data_df, {"dtime": False})
    return files


# %%
if __name__ == "__main__":
    DIR_NAME = dlg.choose_directory()
    IS_TAPHREC = is_taph(DIR_NAME)
    funct = get_plot_function(IS_TAPHREC)
    file_list = scandir(DIR_NAME, funct, IS_TAPHREC)
    print("'file_list' contains a list of all plotted record names")
