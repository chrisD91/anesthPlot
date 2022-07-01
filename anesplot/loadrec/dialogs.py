#!/usr/bin/env python3
"""
Created on Thu Jun  2 15:26:56 2022

@author: cdesbois
"""
import sys
from typing import Optional

from PyQt5.QtWidgets import QFileDialog, QApplication


def get_file(
    title: str = "", dirname: Optional[str] = None, filtre: Optional[str] = None
) -> str:
    """
    Choose a file, return the filename.

    Parameters
    ----------
    title :  str (default is ""
        the title to use
    dirname : Optional[str], default is None -> ~
        the directory name to begin selection
    filtre : Optional[str] (default is None ->  CSV Files (*.csv);;All Files (*)")

    Returns
    -------
    str
        fullname.

    """
    if dirname is None:
        dirname = "~"
    if filtre is None:
        filtre = "CSV Files (*.csv);;All Files (*)"
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(
        None,
        title,
        dirname,
        filtre,
        options=options,
    )
    if filename:
        return str(filename)
    return ""


app = QApplication(sys.argv)
