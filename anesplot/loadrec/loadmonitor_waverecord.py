#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:56:58 2019
@author: cdesbois

load a monitor wave recording:
    - choose a file
    - load the header to a pandas dataframe
    - load the date into a pandas dataframe

____
"""

import os
import sys

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog


#%%
def choosefile_gui(dir_path=None):
    """select a file using a dialog.

    :param str dir_path: optional location of the data (paths['data'])

    :returns: filename (full path)
    :rtype: str
    """
    if dir_path is None:
        dir_path = os.path.expanduser("~")
    caption = "choose a recording"
    options = QFileDialog.Options()
    # to be able to see the caption, but impose to work with the mouse
    # options |= QFileDialog.DontUseNativeDialog
    fname = QFileDialog.getOpenFileName(
        caption=caption, directory=dir_path, filter="*.csv", options=options
    )
    # fname = QFileDialog.getOpenfilename(caption=caption,
    # directory=direct, filter='*.csv')
    # TODO : be sure to be able to see the caption
    return fname[0]


#%%
def loadmonitor_waveheader(filename):
    """load the wave file header.

    :param str filename: full name of the file

    :returns: header
    :rtype: pandas.Dataframe
    """
    df = pd.read_csv(
        filename, sep=",", header=None, index_col=None, nrows=12, encoding="iso-8859-1"
    )
    return df


def loadmonitor_wavedata(filename):
    """load the monitor wave csvDataFile.

    :param str filename: full name of the file

    :returns: df = trends data
    :rtype: pandas.Dataframe
    """
    print("loading data", os.path.basename(filename))
    fs = 300  # sampling rate
    # header :
    header_df = pd.read_csv(
        filename, sep=",", header=None, index_col=None, nrows=12, encoding="iso-8859-1"
    )
    date = header_df.iloc[0][1]

    df = pd.read_csv(
        filename,
        sep=",",
        skiprows=[14],
        header=13,
        index_col=False,
        encoding="iso-8859-1",
        usecols=[0, 2, 3, 4, 5, 6],
        dtype={"Unnamed: 0": str},
    )  # , nrows=200000) #NB for development
    # columns names correction
    colnames = {
        "~ECG1": "wekg",
        "~INVP1": "wap",
        "~INVP2": "wvp",
        "~CO.2": "wco2",
        "~AWP": "wawp",
        "~Flow": "wflow",
        "~AirV": "wVol",
        "Unnamed: 0": "time",
    }
    df = df.rename(columns=colnames)

    # scaling correction
    if "wco2" in df.columns:
        df.wco2 = df.wco2.shift(-480)  # time lag correction
        df["wco2"] *= 7.6  # CO2 % -> mmHg
    df["wekg"] /= 100  # tranform EKG in mVolts
    df["wawp"] *= 10  # mmH2O -> cmH2O
    df.time = df.time.apply(
        lambda x: pd.to_datetime(date + "-" + x) if not pd.isna(x) else x
    )
    # interpolate time values (fill the gaps)
    dt_df = df.time[df.time.notnull()]
    time_delta = (dt_df.iloc[-1] - dt_df.iloc[0]) / (
        dt_df.index[-1] - dt_df.index[0] - 1
    )
    start_time = df.time.iloc[0]
    df["datetime"] = [start_time + i * time_delta for i in range(len(df))]
    df["point"] = df.index  # point location
    # add a 'sec'
    df["sec"] = df.index / fs

    # clean data
    # params = ['wekg', 'wap', 'wco2', 'wawp', 'wflow']

    # wData.wap.value_counts().sort_index()
    df.loc[df.wap < -100, "wap"] = np.nan
    df.loc[df.wap > 200, "wap"] = np.nan
    if "wco2" in df.columns:
        df.loc[df.wco2 < 0, "wco2"] = 0
    return df


#%%
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    file_name = choosefile_gui(os.path.expanduser("~"))
    file = os.path.basename(file_name)
    if file[0] == "M":
        if "Wave" in file:
            wheader_df = loadmonitor_waveheader(file_name)
            wdata_df = loadmonitor_wavedata(file_name)
