# !/usr/bin/env python3
"""
Created on Wed Jul 24 13:43:26 2019
@author: cdesbois

load a monitor trend recording:
    - choose a file GUI -> filename
    - load the header -> dictionary
    - load the data -> pandas.DataFrame
"""

import logging
import os

# import sys
from datetime import timedelta
from typing import Any, Optional

import numpy as np
import pandas as pd

# import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog

from anesplot.loadrec import ctes_load

app = QApplication.instance()
logging.warning(f"loadmonitor_trendrecord.py : {__name__=}")
if app is None:
    app = QApplication([])
    logging.warning("create QApplication instance")
else:
    logging.warning(f"QApplication instance already exists: {QApplication.instance()}")


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
    # bug in macos : add fake name
    # dirname = os.path.join(dirname, "fakename.csv")
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
        return descr

    logging.info("%s < loadmonitor_trendheader", "-" * 20)
    if not os.path.isfile(filename):
        logging.warning(f"{'!' * 10} file not found")
        logging.warning(f"{filename=}")
        logging.warning(f"{'!' * 10} file not found")
        return descr
    logging.info(f"{'.' * 10} loading header {os.path.basename(filename)}")

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
        logging.warning(f"{os.path.basename(filename)} as an empty header")
        # descr = {"empty": filename}
        # descr = {}  # type: dict[str, Any]
    except FileNotFoundError:
        logging.warning("header not found")
        # descr = {}  # type: dict[str, Any]
        # logging.warning(error)
    # NB encoding needed for accentuated letters
    else:
        headerdf = headerdf.set_index(0).T
        if "Sampling Rate" not in headerdf.columns:
            logging.error(
                f"{'>' * 10} {os.path.basename(filename)} is not a trend record"
            )
            return {}
        for col in ["Weight", "Height", "Sampling Rate"]:
            headerdf[col] = headerdf[col].astype(float)
        # convert to a dictionary
        descr = headerdf.loc[1].to_dict()
    logging.info(f"{'-' * 20} loaded trendheader >")
    return descr


def remove_txt_messages(recorddf: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract and remove the annotion in a monitor record.

    Parameters
    ----------
    recorddf : pd.DataFrame
        the recorded data.

    Returns
    -------
    recorddf : pd.DataFrame
        same data but with anoration replace by np.Nan.

    """
    to_fix = []
    messagesdf = pd.DataFrame()
    for col in recorddf.columns:
        if recorddf[col].dtype != "float64":
            if col != "Time":
                to_fix.append(col)
    if to_fix:
        logging.warning("there are non numericals values:")
        for line, ser in recorddf[to_fix].iterrows():
            try:
                pd.to_numeric(ser)
            except ValueError:
                message = recorddf.loc[line].dropna()
                txt = " ".join([str(_) for _ in message.to_list()])
                logging.warning(f"(replaced by NaN) -> {txt}")
                messagesdf[line] = message
                recorddf.loc[line] = np.nan
        for col in to_fix:
            recorddf[col] = pd.to_numeric(recorddf[col])
    return recorddf, messagesdf


def loadmonitor_trenddata(filename: str) -> pd.DataFrame:
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
    logging.info(f"{'-' * 20} < loadmonitor_trenddata")
    if not os.path.isfile(filename):
        logging.warning(f"{'!' * 10} datafile not found")
        logging.warning("{filename}")
        logging.warning(f"{'!' * 10} datafile not found")
        return pd.DataFrame()

    logging.info(f"{'.' * 10} loading trenddata {os.path.basename(filename)}")
    try:
        datadf = pd.read_csv(filename, sep=",", skiprows=[13], header=12)
    except UnicodeDecodeError:
        datadf = pd.read_csv(
            filename, sep=",", skiprows=[13], header=12, encoding="ISO-8859-1"
        )
    except pd.errors.EmptyDataError:
        logging.warning(f"{'!' * 10}  {os.path.basename(filename)} contains no data !")
        return pd.DataFrame()

    datadf = pd.DataFrame(datadf)
    # drop waves time indicators(column name beginning with a '~')
    datadf = datadf.drop([_ for _ in datadf.columns if _.startswith("~")], axis=1)
    # is empty (ie only a few lines of trend data)
    if datadf.set_index("Time").dropna(how="all").empty:
        logging.warning(f"{'!' * 10}  {os.path.basename(filename)} contains no data !")
        return pd.DataFrame(columns=datadf.columns), pd.DataFrame()

    datadf, anotdf = remove_txt_messages(datadf)
    datadf.rename(columns=ctes_load.mon_corr_title, inplace=True)

    # remove empty rows and columns
    datadf.dropna(axis=0, how="all", inplace=True)
    datadf.dropna(axis=1, how="all", inplace=True)

    # TODO fix the code for 1 and 2
    if "aaLabel" in datadf.columns:
        anesth_code = {0: "none", 1: "", 2: "", 4: "iso", 6: "sevo"}
        datadf.aaLabel = datadf.aaLabel.fillna(method="ffill")
        datadf.aaLabel = datadf.aaLabel.fillna(0)
        datadf.aaLabel = datadf.aaLabel.apply(lambda x: anesth_code.get(int(x), ""))
        datadf.aaLabel = datadf.aaLabel.astype("category")
        # aa = datadf.aaLabel.value_counts().index[0]

    # CO2: from % to mmHg
    try:
        datadf[["co2exp", "co2insp"]] *= 760 / 100
    except KeyError:
        logging.warning("no capnographic recording")

    day = os.path.basename(filename).strip("M").split("-")[0]
    datadf.dtime = datadf.dtime.astype(str)
    datadf.dtime = datadf.dtime.apply(lambda st: day + "-" + st)
    datadf.dtime = pd.to_datetime(datadf.dtime, format="%Y_%m_%d-%H:%M:%S")
    # overmidnight ? -> append a day after midnight
    overmidnight = (datadf.dtime.iloc[-1] - datadf.dtime.iloc[0]).days
    if overmidnight:
        last_index = datadf.dtime[datadf.dtime == datadf.dtime.max()].index[-1]
        dtime_ser = datadf.dtime.copy()
        dtime_ser.loc[dtime_ser.index > last_index] = dtime_ser.loc[
            dtime_ser.index > last_index
        ].apply(lambda dt: dt + timedelta(days=1))
        datadf.dtime = dtime_ser
    # elapsed time(in seconds)
    datadf["etimesec"] = datadf.dtime - datadf.dtime.iloc[0]
    datadf.etimesec = datadf.etimesec.apply(lambda dt: dt.total_seconds())
    datadf["etimemin"] = datadf.etimesec / 60
    # remove irrelevant measures
    # df.co2exp.loc[data.co2exp < 30] = np.nan

    # check sampling_freq:
    # sampling = round(
    #     (datadf.dtime.iloc[-1] - datadf.dtime.iloc[0]).total_seconds() / len(datadf)
    # )
    # logging.info(f"{sampling=}, header_sampling={headerdico['Sampling Rate']}")

    logging.info(f"{'-' * 20} loaded trenddata >")
    return datadf, anotdf


# %% merge consecutive recordings


def concat_param(param1: dict[str, Any], param2: dict[str, Any]) -> dict[str, Any]:
    """
    Concatenate the two param dictionary for a merge of two recordings.

    Parameters
    ----------
    param1 : dict[str, Any]
        mtrend.param.
    param2 : dict[str, Any]
        mtrend.param.

    Returns
    -------
    dict[str, Any]
        DESCRIPTION.

    """
    param = param1.copy()
    param["file"] = "_+_".join([param1["file"], param2["file"]])
    param["filename"] = "_+_".join([param1["filename"], param2["file"]])
    return param


def concat_data(
    datadf1: pd.DataFrame, datadf2: pd.DataFrame, sampling_freq: float = 0.2
) -> pd.DataFrame:
    """
    Concatenate the dataframe of two consecutive recording.

    Parameters
    ----------
    datadf1 : pd.DataFrame
        mtrends.data.
    datadf2 : pd.DataFrame
        mtrends.data.
    sampling_frequency: float (default = 0.2)
        mtrends.param["sampling_freq"]

    Returns
    -------
    df : pd.DataFrame
        the merged result.

    """
    # get delta time between the two reconrdings
    df1 = datadf1.copy()
    df2 = datadf2.copy()

    delta_sec = (df2.iloc[0].dtime - df1.iloc[-1].dtime).total_seconds()
    df2.etimesec += df1.iloc[-1].etimesec + delta_sec
    df2.etimemin += df1.iloc[-1].etimemin + delta_sec / 60

    # fill last line with nan (to avoid a continuous line in the plotting process)
    df1_newline = df1.iloc[-1].copy()
    delta_break = timedelta(seconds=1 / sampling_freq)
    df1_newline.dtime += delta_break
    cols = df1.columns.tolist()
    cols.remove("dtime")
    df1_newline[cols] = np.nan
    df1 = pd.concat([df1, df1_newline], ignore_index=True)

    datadf = pd.concat([df1, df2], ignore_index=True)

    return datadf


def main_chooseload_monitortrend(
    dir_name: Optional[str] = None,
) -> tuple[dict["str", Any], pd.DataFrame, pd.DataFrame]:
    """
    Load a monitortrend data (whith choose GUI).

    Parameters
    ----------
    dir_name : Optional[str] (default is None)
        The directory to search in.

    Returns
    -------
    header_dict: dict
        the header content
    mdata_df : pd.DataFrame
        the record data.
    anot_df : TYPE
        the annotations present in the file.

    """
    # app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(True)
    header_dict = {}
    mdata_df = pd.DataFrame()
    anot_df = pd.DataFrame()
    if dir_name is None:
        dir_name = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
    file_name = choosefile_gui(dir_name)
    file = os.path.basename(file_name)
    if not file:
        logging.warning("canceled by the user")

    elif file[0] == "M":
        if "Wave" not in file:
            header_dict = loadmonitor_trendheader(file_name)
            if header_dict:
                mdata_df, anot_df = loadmonitor_trenddata(file_name)
                logging.info(f"{'>' * 10} loaded recording of {file} in mdata_df")
                # mdata= cleanMonitorTrendData(mdata)
            else:
                logging.warning(f"{'!' * 5}  {file} file is empty  {'!' * 5}")
        else:
            logging.warning(
                f"{'!' * 5} {file} is not a MonitorTrend recording {'!' * 5}"
            )
    else:
        logging.warning(f"{'!' * 5}  {file} is not a MonitorTrend recording  {'!' * 5}")
    return header_dict, mdata_df, anot_df


# %%
if __name__ == "__main__":
    main_chooseload_monitortrend()
