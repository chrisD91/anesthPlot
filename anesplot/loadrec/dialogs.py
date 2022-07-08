#!/usr/bin/env python3
"""
Created on Thu Jun  2 15:26:56 2022

@author: cdesbois
"""
import os
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
        dirname = os.path.join("os.path.expanduser(~)")
        # NB  a fake name has to bee added for the procedure to work on macos
    dirname = os.path.join(dirname, "fakename.csv")
    if filtre is None:
        filtre = "CSV Files (*.csv);;All Files (*)"
        # filtre = ''
    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
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


def get_name() -> str:
    """Test."""
    return str(QFileDialog.getOpenFileName())


app = QApplication(sys.argv)


# %%
if __name__ == "__main__":
    #    file_name = get_name()
    FILE_NAME = get_file()
    #    file_name = str(QFileDialog.getOpenFileName())
    #    file_name = get_file()
    #    syt.exit(app.exec_())
    print(f"{FILE_NAME}")
