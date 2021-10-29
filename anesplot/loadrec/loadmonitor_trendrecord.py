#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
----

Created on Wed Jul 24 13:43:26 2019
@author: cdesbois

load a monitor trend recording:
    - choose a file
    - load the header to a dictionary
    - load the date into a pandas dataframe

____
"""

import os
import sys
from datetime import timedelta

import pandas as pd

# import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog


def choosefile_gui(dirname=None):
    """Select a file via a dialog and return the (full) filename.

    parameters
    ----
    dir_path : str
        location to place the gui ('generally paths['data']) else home

    return
    ----
    fname[0] : str
        filename
    """
    # nb these imports seems to be required to allow processing after importation
    # import sys
    # from PyQt5.QtWidgets import QApplication, QFileDialog

    if dirname is None:
        dirname = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
    global app
    # app = QApplication(sys.argv)
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirname, filter="All files (*)"
    )

    if isinstance(fname, tuple):
        return fname[0]
    return str(fname)


# Monitor trend
def loadmonitor_trendheader(filename):
    """load the file header.

    :param str filename: full name of the file

    :returns: header
    :rtype: dict
    """
    print("loadmonitor_trendrecord.loadmonitor_trendheader")
    print("loading header", os.path.basename(filename))
    try:
        headerdf = pd.read_csv(
            filename,
            sep=",",
            header=None,
            index_col=None,
            nrows=11,
            encoding="iso8859_1",
            on_bad_lines="skip",
        )
    # except UnicodeDecodeError as error:
    except pd.errors.EmptyDataError:
        print("{} as an empty header".format(os.path.basename(filename)))
        descr = {"empty": filename}
    except FileNotFoundError:
        print("cancelled")
        descr = {}
        # print(error)
    # NB encoding needed for accentuated letters
    else:
        headerdf = headerdf.set_index(0).T
        if "Sampling Rate" not in headerdf.columns:
            print(
                ">" * 10
                + " {} is not a trend record".format(os.path.basename(filename))
            )
            return {}
        for col in ["Weight", "Height", "Sampling Rate"]:
            headerdf[col] = headerdf[col].astype(float)
        # convert to a dictionary
        descr = headerdf.loc[1].to_dict()
    return descr


def loadmonitor_trenddata(filename, headerdico):
    """load the monitor trend data

    :param str filename: fullname
    :param dict headerdico: fileheader

    :returns: df = trends data
    :rtype: pandas.Dataframe
    """
    print("loadmonitor_trendrecord.loadmonitor_trenddata")
    print("loading data", os.path.basename(filename))
    try:
        datadf = pd.read_csv(filename, sep=",", skiprows=[13], header=12)
    except UnicodeDecodeError:
        datadf = pd.read_csv(
            filename, sep=",", skiprows=[13], header=12, encoding="ISO-8859-1"
        )
    except pd.errors.EmptyDataError:
        print("! " * 10 + " {} contains no data !".format(os.path.basename(filename)))
        emptydf = pd.DataFrame()
        return emptydf

    datadf = pd.DataFrame(datadf)
    # drop waves time indicators(column name beginning with a '~')
    for col in datadf.columns:
        if col[0] == "~":
            datadf.pop(col)
    # is empty (ie only a few lines of waves data)
    if datadf.set_index("Time").dropna(how="all").empty:
        print("! " * 10 + " {} contains no data !".format(os.path.basename(filename)))
        emptydf = pd.DataFrame(columns=datadf.columns)
        return emptydf
    # to float values
    to_fix = []
    for col in datadf.columns:
        if datadf[col].dtype != "float64":
            if col != "Time":
                to_fix.append(col)
    if to_fix:
        for col in to_fix:
            datadf[col] = pd.to_numeric(datadf[col], errors="coerce")

    # correct the titles
    corr_title = {
        "AA  LB": "aaLabel",
        "AA_Insp": "aaInsp",
        "AA_Exp": "aaExp",
        "CO2 RR": "co2RR",
        "CO2_Insp": "co2insp",
        "CO2_Exp": "co2exp",
        "ECG HR": "ekgHR",
        "IP1_M": "ip1m",
        "IP1_S": "ip1s",
        "IP1_D": "ip1d",
        "IP1PR": "hr",
        "IP2_M": "ip2m",
        "IP2_S": "ip2s",
        "IP2_D": "ip2d",
        "IP2PR": "ip2PR",
        "O2_Insp": "o2insp",
        "O2_Exp": "o2exp",
        "Time": "datetime",
        "Resp": "resp",
        "PPeak": "pPeak",
        "Peep": "peep",
        "PPlat": "pPlat",
        "pmean": "pmean",
        "ipeep": "ipeep",
        "TV_Insp": "tvInsp",
        "TV_Exp": "tvExp",
        "Compli": "compli",
        "raw": "raw",
        "MinV_Insp": "minVinsp",
        "MinV_Exp": "minVexp",
        "epeep": "epeep",
        "peepe": "peepe",
        "peepi": "peepi",
        "I:E": "ieRat",
        "Inp_T": "inspT",
        "Exp_T": "expT",
        "eTime": "eTime",
        "S_comp": "sCompl",
        "Spplat": "sPplat",
    }
    datadf.rename(columns=corr_title, inplace=True)
    # TODO fix the code for 1 and 2
    if "aaLabel" in datadf.columns:
        anesth_code = {0: "none", 1: "", 2: "", 4: "iso", 6: "sevo"}
        datadf.aaLabel = datadf.aaLabel.fillna(0)
        datadf.aaLabel = datadf.aaLabel.apply(lambda x: anesth_code.get(int(x), ""))

    # remove empty rows and columns
    datadf.dropna(axis=0, how="all", inplace=True)
    datadf.dropna(axis=1, how="all", inplace=True)

    # should be interesting to export the comment
    # for index, row in df.iterrows():
    #     if len(row) < 6:
    #         print(index, row)
    # remove comments present in colon 1(ie suppres if less than 5 item rows)
    datadf = datadf.dropna(thresh=6)

    # CO2: from % to mmHg
    try:
        datadf[["co2exp", "co2insp"]] *= 760 / 100
    except KeyError:
        print("no capnographic recording")

    # elapsed time(in seconds)
    datadf["eTime"] = datadf.index * headerdico["Sampling Rate"]
    datadf["eTimeMin"] = datadf["eTime"] / 60
    # convert time to dateTime
    min_time_iloc = datadf.loc[
        datadf["datetime"] == datadf["datetime"].min()
    ].index.values[0]
    datadf.datetime = datadf.datetime.apply(lambda x: headerdico["Date"] + "-" + x)
    datadf.datetime = pd.to_datetime(datadf.datetime, format="%d-%m-%Y-%H:%M:%S")
    # if overlap between two dates (ie over midnight): add one day
    if min_time_iloc > datadf.index.min():
        print("recording was performed during two days")
        datetime_series = datadf.datetime.copy()
        datetime_series.iloc[min_time_iloc:] += timedelta(days=1)
        datadf.datetime = datetime_series
    # remove irrelevant measures
    # df.co2exp.loc[data.co2exp < 30] = np.nan
    return datadf


#%%
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    dir_name = (
        "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
    )
    file_name = choosefile_gui(dir_name)
    file = os.path.basename(file_name)
    if not file:
        print("canceled by the user")
    elif file[0] == "M":
        if "Wave" not in file:
            header_dict = loadmonitor_trendheader(file_name)
            if header_dict:
                mdata_df = loadmonitor_trenddata(file_name, header_dict)
                print("{} loaded recording of {} in mdata_df".format(">" * 10, file))
                # mdata= cleanMonitorTrendData(mdata)
            else:
                mdata_df = None
                print("{}  {} file is empty  {}".format("!" * 5, file, "!" * 5))
        else:
            print(
                "{} {} is not a MonitorTrend recording {}".format(
                    "!" * 5, file, "!" * 5
                )
            )
    else:
        print(
            "{}  {} is not a MonitorTrend recording  {}".format("!" * 5, file, "!" * 5)
        )
