# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 15:50:27 2022

@author: cdesbois
"""

import sys

from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QWidget


def choosefile_gui(dirname: str = None) -> str:
    """Select a file via a dialog and return the (full) filename.

    Parameters
    ----------
    dirname : str, optional (default is None)
        DESCRIPTION. location to place the gui ('generally paths['data']) else home

    Returns
    -------
    fname[0] : str
        DESCRIPTION. : full name of the selected file

    """
    # global APP
    # if 'app' not in dir():
    if dirname is None:
        dirname = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
    # from PyQt5.QtGui import QGuiApplication
    # app = QGuiApplication([dirname])
    if "app" not in dir():
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
    # print("define QFiledialog")
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirname, filter="All files (*)"
    )
    print("return")
    # app.quit()
    if isinstance(fname, tuple):
        return fname[0]
    return str(fname)


def select_type(question: str = None, items: list = None, num: int = 0) -> str:
    """
    Display a pulldown menu to choose the kind of recording.

    Parameters
    ----------
    question : str, optional
        The question that APPears in the dialog (default is None).
    items : list, optional
        the list of all items in the pulldown menu. (default is None).
    num : int, optional
        number in the list the pointer will be one. The default is 0.

    Returns
    -------
    str
        kind of recording in [monitorTrend, monitorWave, taphTrend, telvet].
    """
    if items is None:
        items = ["monitorTrend", "monitorWave", "taphTrend", "telVet"]
    if question is None:
        question = "choose kind of file"
    # if 'app' not in dir():
    app = QApplication([])
    app.setQuitOnLastWindowClosed(True)
    # global APP
    widg = QWidget()
    kind, ok_pressed = QInputDialog.getItem(widg, "select", question, items, num, False)
    if ok_pressed and kind:
        selection = kind
    else:
        selection = None
    return selection
