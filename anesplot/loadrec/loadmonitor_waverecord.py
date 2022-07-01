#!/usr/bin/env python3
"""
Created on Wed Jul 24 14:56:58 2019
@author: cdesbois

load a monitor wave recording:
    - choose a file GUI -> filename
    - load the header -> pandas.DataFrame
    - load the data i-> pandasDataFrame

"""

import os
import sys
from datetime import timedelta
from typing import Optional, Any

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog


def choosefile_gui(dirname: Optional[str] = None) -> str:
    """
    Select a file via a dialog and return the (full) filename.

    Parameters
    ----------
    dirname : str, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    str : the choosed file full name

    """
    if dirname is None:
        dirname = os.path.expanduser("~")
    # app = QApplication([dirname])
    # app.setQuitOnLastWindowClosed(True)

    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirname, filter="All files (*)"
    )

    if isinstance(fname, tuple):
        name = fname[0]
    else:
        name = fname
    return str(name)


def loadmonitor_waveheader(filename: Optional[str] = None) -> dict[str, Any]:
    """
    Load the wave file header.

    Parameters
    ----------
    filename : str, optional
        full name of the file (default is None).

    Returns
    -------
    dict
        content of the header.

    """
    if filename is None:
        filename = choosefile_gui()
        print(f"called returned= {filename}")

    else:
        if filename == "":
            # to build and empty header
            return {}
        print(f"{'-' * 20} < loadmonitor_waveheader")
        if not os.path.isfile(filename):
            # wrong name
            print(f"{'!' * 10} file not found)")
            print(f"{filename}")
            print(f"{'!' * 10} file not found)")
            print()
            return {}

    print(f"{'.' * 10} loading header {os.path.basename(filename)}")

    try:
        headerdf = pd.read_csv(
            filename,
            sep=",",
            header=None,
            index_col=None,
            nrows=12,
            encoding="iso-8859-1",
        )
        header = dict(headerdf.values)
    except FileNotFoundError:
        print("canceled by the user")
        header = {}
    print(f"{'-' * 20} loaded waveheader >")
    return header


def loadmonitor_wavedata(filename: str) -> pd.DataFrame:
    """
    Load the monitor wave csvDataFile.

    Parameters
    ----------
    filename : str, optional
        full name of the file (default is None).

    Returns
    -------
    pandas.Dataframe
        the recorded wave data
    """
    print(f"{'-' * 20} < loadmonitor_wavedata")
    if not os.path.isfile(filename):
        print(f"{'!' * 10} file not found")
        print("f{filename}")
        print(f"{'!' * 10} file not found")
        print()
        return pd.DataFrame()
    if filename:
        print(f"{'.' * 10} loading wavedata {os.path.basename(filename)}")
    sampling_fr = 300  # sampling rate
    try:
        date = pd.read_csv(filename, nrows=1, header=None).iloc[0][1]
    except UnicodeDecodeError:
        date = pd.read_csv(filename, nrows=1, header=None, encoding="iso-8859-1").iloc[
            0
        ][1]
    datadf = pd.read_csv(
        filename,
        sep=",",
        skiprows=[14],
        header=13,
        index_col=False,
        encoding="iso-8859-1",
        usecols=[0, 2, 3, 4, 5, 6],
        dtype={"Unnamed: 0": str},
    )  # , nrows=200000) #NB for development
    datadf = pd.DataFrame(datadf)
    if datadf.empty:
        print(
            f"{'!' * 10} there are no data in this file : {os.path.basename(filename)} !"
        )
        return datadf
    # columns names correction
    colnames = {
        "~ECG1": "wekg",
        "~INVP1": "wap",
        "~INVP2": "wvp",
        "~CO.2": "wco2",
        "~AWP": "wawp",
        "~Flow": "wflow",
        "~AirV": "wVol",
        "Unnamed: 0": "dtime",
    }
    datadf = datadf.rename(columns=colnames)

    # scaling correction
    if "wco2" in datadf.columns:
        datadf.wco2 = datadf.wco2.shift(-480)  # time lag correction
        datadf["wco2"] *= 7.6  # CO2 % -> mmHg
    datadf["wekg"] /= 100  # tranform EKG in mVolts
    datadf["wawp"] *= 10  # mmH2O -> cmH2O

    datadf.dtime = datadf.dtime.apply(
        lambda x: pd.to_datetime(date + "-" + x) if not pd.isna(x) else x
    )
    # correct date time if over midnight
    min_time_iloc = datadf.loc[datadf.dtime == datadf.dtime.min()].index.values[0]
    if min_time_iloc > datadf.index.min():
        print("recording was performed during two days")
        datetime_series = datadf.dtime.copy()
        datetime_series.iloc[min_time_iloc:] = datetime_series.iloc[
            min_time_iloc:
        ].apply(lambda x: x + timedelta(days=1) if not pd.isna(x) else x)
        datadf.dtime = datetime_series
    # interpolate time values (fill the gaps)
    dt_df = datadf.dtime[datadf.dtime.notnull()]
    time_delta = (dt_df.iloc[-1] - dt_df.iloc[0]) / (
        dt_df.index[-1] - dt_df.index[0] - 1
    )
    start_time = datadf.dtime.iloc[0]
    datadf["dtime"] = [start_time + i * time_delta for i in range(len(datadf))]
    datadf["point"] = datadf.index  # point location
    # add a 'sec'
    datadf["etimesec"] = datadf.index / sampling_fr

    # clean data
    # params = ['wekg', 'wap', 'wco2', 'wawp', 'wflow']

    # wData.wap.value_counts().sort_index()
    datadf.loc[datadf.wap < -100, "wap"] = np.nan
    datadf.loc[datadf.wap > 200, "wap"] = np.nan
    if "wco2" in datadf.columns:
        datadf.loc[datadf.wco2 < 0, "wco2"] = 0

    print(f"{'-' * 20} loaded wavedata >")
    return datadf


# %%
if __name__ == "__main__":
    APP = QApplication(sys.argv)
    APP.setQuitOnLastWindowClosed(True)
    DIR_NAME = (
        "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
    )
    FILE_NAME = choosefile_gui(DIR_NAME)
    file = os.path.basename(FILE_NAME)
    if not file:
        print("canceled by the user")
    else:
        if file[0] == "M":
            if "Wave" in file:
                wheader_df = loadmonitor_waveheader(FILE_NAME)
                wdata_df = loadmonitor_wavedata(FILE_NAME)
                print(f"loaded {file} in wheader_df & wdata_df")
            else:
                print(f"{'!' * 5} {file} is not a MonitorWave recording {'!' * 5}")
        else:
            print(f"{'!' * 5} {file} is not a Monitor record {'!' * 5}")
