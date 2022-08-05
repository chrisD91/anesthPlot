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
from anesplot.loadrec import dialogs

# import get_file, get_directory

paths = rec.paths


def get_directory() -> str:
    """Choose the directory to scan."""
    dirname = dialogs.get_directory(
        "choose the folder to scan", dirname=paths["mon_data"]
    )
    return dirname


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
    name = dialogs.choose_in_alist(names, message=question)
    func = [_ for _ in func_list if _.__name__ == name][0]
    return func


def scandir(dirname: str, func: Any) -> list[str]:
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
    for file in os.scandir(dirname):
        if "Wave" not in file.name and file.is_file():
            filename = os.path.join(paths["mon_data"], "2021", file)
            files.append(file.name)
            # files.append(os.path.join(paths['mon_data'], file))
            mtrend = rec.MonitorTrend(filename)
            func(mtrend.data, mtrend.param)
    return files


# %%
if __name__ == "__main__":
    DIR_NAME = get_directory()
    funct = get_plot_function()
    file_list = scandir(DIR_NAME, funct)
    print("'file_list' contains a list of all plotted record names")
