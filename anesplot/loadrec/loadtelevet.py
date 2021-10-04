#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 16:22:06 2019
@author: cdesbois

load televet exported (csv) data:
to be developped

____
"""

import os
import sys

import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog


#%%
# def choosefile_gui(dir_path=None):
#     """select a file using a dialog.

#     :param str dir_path: optional location of the data (paths['data'])

#     :returns: filename (full path)
#     :rtype: str
#     """

#     if dir_path is None:
#         dir_path = os.path.expanduser("~")
#     options = QFileDialog.Options()
#     caption = "choose a recording"
#     # to be able to see the caption, but impose to work with the mouse
#     #    options |= QFileDialog.DontUseNativeDialog
#     fname = QFileDialog.getOpenFileName(
#         caption=caption, directory=dir_path, filter="*.csv", options=options
#     )
#     #    fname = QFileDialog.getOpenfilename(caption=caption,
#     #                                        directory=direct, filter='*.csv')
#     # TODO : be sure to be able to see the caption
#     return fname[0]


def choosefile_gui(dir_path=None):
    """select a file using a dialog.

    :param str dir_path: optional location of the data (paths['data'])

    :returns: filename (full path)
    :rtype: str
    """

    if dir_path is None:
        dir_path = os.path.expanduser("~")

    apps = QApplication([dir_path])
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dir_path, filter="csv (*.csv)"
    )

    if isinstance(fname, tuple):
        filename = fname[0]
    else:
        filename = str(fname)
    return filename


def loadtelevet(fname=None, all_traces=False):
    """ load the televetCsvExportedFile.

    :param str file: name of the file
    :param bool all_traces: load all the derivations

    :returns: df = recorded traces
    :rtype: pandas.Dataframe
    """

    filepath = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTelVetRecorded"
    if fname is None:
        fname = "STEF_0031_00114_20171205_121305.csv"
    filename = os.path.join(filepath, fname)
    if not os.path.isfile(filename):
        print("no file for ", filename)
        return

    if all_traces:
        df = pd.read_csv(filename, sep=";")
    else:
        df = pd.read_csv(filename, sep=";", usecols=[2])  # only d2 loaded

    df.rename(
        columns={"Channel1": "d1", "Channel2": "d2", "Channel3": "d3"}, inplace=True
    )
    df /= 100  # to mV
    df["timeS"] = df.index / 500
    df["timeM"] = df.timeS / 60

    return df


if not "paths" in dir():
    paths: dict = {"data": "~"}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    file_name = choosefile_gui(paths.get("data"))
    file = os.path.basename(file_name)
    ekg_data = loadtelevet(file_name, all_traces=False)
