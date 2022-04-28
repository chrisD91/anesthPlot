#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 15:50:27 2022

@author: cdesbois
"""

from PyQt5.QtWidgets import QInputDialog, QWidget, QFileDialog


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
    global APP

    if dirname is None:
        dirname = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
    print("define QFiledialog")
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirname, filter="All files (*)"
    )
    print("return")
    if isinstance(fname, tuple):
        return fname[0]
    return str(fname)


def select_type(question: str = None, items: list = None, num: int = 0) -> str:
    """
    display a pulldown menu to choose the kind of recording

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
    global APP
    #    APP = QApplication(sys.argv)
    widg = QWidget()
    kind, ok_pressed = QInputDialog.getItem(widg, "select", question, items, num, False)
    if ok_pressed and kind:
        selection = kind
    else:
        selection = None
    return selection
