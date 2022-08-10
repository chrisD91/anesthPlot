# !/usr/bin/env python3
"""
Created on Wed Jul 31 16:22:06 2019
@author: cdesbois

load televet exported (csv) data:
to be developped

____
"""

import logging
import os

# import sys
from typing import Optional

import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog

# %%
app = QApplication.instance()
logging.warning(f"load_televet.py : {__name__=}")
if app is None:
    app = QApplication([])
    logging.warning("create QApplication instance")
else:
    logging.warning(f"QApplication instance already exists: {QApplication.instance()}")


def choosefile_gui(dirpath: Optional[str] = None) -> str:
    """
    Select a file using a dialog.

    Parameters
    ----------
    dirpath : str, optional (The default is None -> '~')
       location of the data, ex : paths['data']. .

    Returns
    -------
    str
        full name of the selected file.
    """
    if dirpath is None:
        dirpath = os.path.expanduser("~")
    # bug in macos  necessity to add a filename
    dirpath = os.path.join(dirpath, "fakename.csv")
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirpath, filter="csv (*.csv)"
    )

    if isinstance(fname, tuple):
        filename = fname[0]
    else:
        filename = fname
    return str(filename)


def loadtelevet(fname: Optional[str] = None, all_traces: bool = False) -> pd.DataFrame:
    """
    Load the televetCsvExportedFile.

    Parameters
    ----------
    fname : str, optional (default is None)
        (full) name of the file.
    all_traces : bool, optional (default is False)
        load all the derivations.

    Returns
    -------
    pandas.DataFrame
        the recorded traces.
    """
    filepath = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTelVetRecorded"
    if fname is None:
        fname = "STEF_0031_00114_20171205_121305.csv"
    filename = os.path.join(filepath, fname)

    logging.warning(f"{'-' * 20} > loadtelevet datafile")
    if not os.path.isfile(filename):
        logging.warning(f"{'!' * 10} televet datafile not found")
        logging.warning(f"{filename}")
        logging.warning(f"{'!' * 10} televet datafile not found")
        return pd.DataFrame()
    logging.warning(f"{'-' * 10} loading televet {os.path.basename(filename)}")

    if all_traces:
        datadf = pd.read_csv(filename, sep=";")
    else:
        datadf = pd.read_csv(filename, sep=";", usecols=[2])  # only d2 loaded

    datadf.rename(
        columns={"Channel1": "d1", "Channel2": "wekg", "Channel3": "d3"}, inplace=True
    )
    datadf /= 100  # to mV
    # implement time values
    datadf["point"] = datadf.index
    datadf["etimesec"] = datadf.index / 500
    datadf["etimemin"] = datadf.sec / 60

    logging.warning(f"{'-' * 20} < loaded televet datafile")
    return datadf


# %%
if __name__ == "__main__":
    import anesplot.config.load_recordrc

    paths = anesplot.config.load_recordrc.build_paths()

    FILE_NAME = choosefile_gui(paths.get("telv_data"))
    ekg_data = loadtelevet(FILE_NAME, all_traces=False)
