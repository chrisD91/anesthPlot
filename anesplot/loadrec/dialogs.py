#!/usr/bin/env python3
"""
Created on Thu Jun  2 15:26:56 2022

@author: cdesbois
"""
import os
import sys
from typing import Optional, Any

from PyQt5.QtWidgets import QFileDialog, QApplication, QInputDialog


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
        dirname = os.path.join(os.path.expanduser("~"))
        # NB  a fake name has to bee added for the procedure to work on macos
    # dirname = os.path.join(dirname, "fakename.csv")
    if filtre is None:
        filtre = "CSV Files (*.csv);;All Files (*)"
        # filtre = ''
    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(
        None,
        caption=title,
        directory=dirname,
        filter=filtre,
        options=options,
    )
    if filename:
        return str(filename)
    return ""


def get_directory(
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
        dirname = os.path.join(os.path.expanduser("~"))
        # NB  a fake name has to bee added for the procedure to work on macos
    # dirname = os.path.join(dirname, "fakename.csv")
    if filtre is None:
        filtre = "CSV Files (*.csv);;All Files (*)"
        # filtre = ''
    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    dirname = QFileDialog.getExistingDirectory(
        None,
        caption=title,
        directory=dirname,
        options=options,
    )
    if dirname:
        return str(dirname)
    return ""


def choose_in_alist(thelist: list[Any], message: Optional[str] = None) -> Any:
    """
    Choose an item in the list.

    Parameters
    ----------
    thelist : list
        the items to choose among.
    message : str, Optional (default is None)
        message to display.

    Returns
    -------
    Any
        the selected item.

    """
    if message is None:
        message = "choose the function to use"
    #    widg = QWidget()
    name, ok_pressed = QInputDialog.getItem(None, "select", message, thelist, 0, False)
    if not ok_pressed and name:
        return ""
    return name


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
