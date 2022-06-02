#!/usr/bin/env python3
"""
Created on Thu Jun  2 15:26:56 2022

@author: cdesbois
"""
from typing import Optional

from PyQt5.QtWidgets import QFileDialog


def get_file(dirname: Optional[str] = None) -> str:
    """
    Choose a file, return the filename.

    Parameters
    ----------
    dirname : Optional[str], default is None -> ~
        the directory name to begin selection

    Returns
    -------
    str
        fullname.

    """
    if dirname is None:
        dirname = "~"
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(
        None,
        "QFileDialog.getOpenFileName()",
        dirname,
        "CSV Files (*.csv);;All Files (*)",
        options=options,
    )
    if filename:
        return str(filename)
    return ""
