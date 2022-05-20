# !/usr/bin/env python3
"""
Created on Wed Jul 24 13:43:26 2019
@author: cdesbois

load a monitor trend recording:
    - choose a file GUI -> filename
    - load the header -> dictionary
    - load the data -> pandas.DataFrame
"""

import os
import sys
from datetime import timedelta
from typing import Optional, Any

import pandas as pd

# import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog


def choosefile_gui(dirname: Optional[str] = None) -> str:
    """
    Select a file via a dialog and return the (full) filename.

    Parameters
    ----------
    dirname : str, optional
        location to place the gui ('generally paths['data']) else home
                                   (default is None).

    Returns
    -------
    str
        the choosed file fullname.

    """
    if dirname is None:
        dirname = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
    app = QApplication([dirname])
    app.setQuitOnLastWindowClosed(True)
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirname, filter="All files (*)"
    )

    if isinstance(fname, tuple):
        name = fname[0]
    else:
        name = fname
    return str(name)


# Monitor trend
def loadmonitor_trendheader(filename: str) -> dict["str", Any]:
    """
    Load the file header.

    Parameters
    ----------
    filename : str
        full name of the file.

    Returns
    -------
    dict
        the content of the header.

    """
    descr = {}  # type: dict[str, Any]
    if filename == "":
        # to build and empty header
        # return {}
        return descr

    print(f"{'-' * 20} < loadmonitor_trendheader")
    if not os.path.isfile(filename):
        print(f"{'!'* 10} file not found")
        print(f"{filename}")
        print(f"{'!'* 10} file not found")
        print()
        return descr
    print(f"{'.' * 10} loading header {os.path.basename(filename)}")

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
        print(f"{os.path.basename(filename)} as an empty header")
        # descr = {"empty": filename}
        # descr = {}  # type: dict[str, Any]
    except FileNotFoundError:
        print("header not found")
        # descr = {}  # type: dict[str, Any]
        # print(error)
    # NB encoding needed for accentuated letters
    else:
        headerdf = headerdf.set_index(0).T
        if "Sampling Rate" not in headerdf.columns:
            print(f"{'>'* 10} {os.path.basename(filename)} is not a trend record")
            return {}
        for col in ["Weight", "Height", "Sampling Rate"]:
            headerdf[col] = headerdf[col].astype(float)
        # convert to a dictionary
        descr = headerdf.loc[1].to_dict()
    print(f"{'-' * 20} loaded trendheader >")
    return descr


def loadmonitor_trenddata(filename: str, headerdico: dict[str, Any]) -> pd.DataFrame:
    """
    Load the monitor trend data.

    Parameters
    ----------
    filename : str
        full name of the datafile.
    headerdico : dict
        fileheader content.

    Returns
    -------
    pd.DataFrame
        the recorded data.

    """
    print(f"{'-' * 20} < loadmonitor_trenddata")
    if not os.path.isfile(filename):
        print(f"{'!' * 10} datafile not found")
        print("{filename}")
        print(f"{'!' * 10} datafile not found")
        print()
        return pd.DataFrame()

    print(f"{'.' * 10} loading trenddata {os.path.basename(filename)}")
    try:
        datadf = pd.read_csv(filename, sep=",", skiprows=[13], header=12)
    except UnicodeDecodeError:
        datadf = pd.read_csv(
            filename, sep=",", skiprows=[13], header=12, encoding="ISO-8859-1"
        )
    except pd.errors.EmptyDataError:
        print(f"{'!' * 10}  {os.path.basename(filename)} contains no data !")
        return pd.DataFrame()

    datadf = pd.DataFrame(datadf)
    # drop waves time indicators(column name beginning with a '~')
    datadf = datadf.drop([_ for _ in datadf.columns if _.startswith("~")], axis=1)
    # is empty (ie only a few lines of waves data)
    if datadf.set_index("Time").dropna(how="all").empty:
        print(f"{'!' * 10}  {os.path.basename(filename)} contains no data !")
        return pd.DataFrame(columns=datadf.columns)
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
    print(f"{'-' * 20} loaded trenddata >")
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
    elif file[0] == "M":
        if "Wave" not in file:
            header_dict = loadmonitor_trendheader(FILE_NAME)
            if header_dict:
                MDATA_DF = loadmonitor_trenddata(FILE_NAME, header_dict)
                print(f"{'>' * 10} loaded recording of {file} in mdata_df")
                # mdata= cleanMonitorTrendData(mdata)
            else:
                MDATA_DF = None
                print(f"{'!' * 5}  {file} file is empty  {'!' * 5}")
        else:
            print(f"{'!' * 5} {file} is not a MonitorTrend recording {'!' * 5}")
    else:
        print(f"{'!' * 5}  {file} is not a MonitorTrend recording  {'!' * 5}")
