#!/usr/bin/env python3
"""
Created on Thu Jun  2 15:26:56 2022

@author: cdesbois
"""
import logging
import os

# import sys
from typing import Any, Optional

from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog  # , QWidget

app = QApplication.instance()
logging.info(f"dialogs.py : {__name__=}")
if app is None:
    logging.info("N0 QApplication instance - - - - - - - - - - - - - > creating one")
    app = QApplication([])
else:
    logging.warning(f"QApplication instance already exists: {QApplication.instance()}")


def choose_file(
    dirname: Optional[str] = None, title: str = "", filtre: Optional[str] = None
) -> str:
    """
    Choose a file, return the filename.

    Parameters
    ----------
    dirname : Optional[str], default is None -> ~
        the directory name to begin selection
    title :  str (default is ""
        the title to use
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
    if len(title) > 0:
        options |= QFileDialog.DontUseNativeDialog
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


def choose_directory(
    dirname: Optional[str] = None, title: str = "", see_question: bool = False
) -> str:
    """
    Choose a file, return the filename.

    Parameters
    ----------
    dirname : Optional[str], default is None -> ~
        the directory name to begin selection
    title :  str (default is ""
        the title to use
    see_question : bool (default is False)
        use non native dialog .. to see the question

    Returns
    -------
    str
        fullname.

    """
    if dirname is None:
        dirname = os.path.join(os.path.expanduser("~"))
        # NB  a fake name has to bee added for the procedure to work on macos
    # dirname = os.path.join(dirname, "fakename.csv")
    options = QFileDialog.Options()
    if see_question:
        options |= QFileDialog.DontUseNativeDialog
    dirname = QFileDialog.getExistingDirectory(
        None,
        caption=title,
        directory=dirname,
        options=options,
    )
    if dirname:
        return str(dirname)
    return ""


def choose_in_alist(
    thelist: list[Any], message: Optional[str] = None, index: Optional[int] = 0
) -> Any:
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
        message = "select the item to use"
    # widg = QWidget()
    name, ok_pressed = QInputDialog.getItem(
        None, "select", message, thelist, index, False
    )
    if not ok_pressed and name:
        return ""
    return name


def get_name() -> str:
    """Test."""
    return str(QFileDialog.getOpenFileName())


# %%
if __name__ == "__main__":
    #    file_name = get_name()
    FILE_NAME = choose_file()
    #    file_name = str(QFileDialog.getOpenFileName())
    #    file_name = get_file()
    #    syt.exit(app.exec_())
    logging.warning(f"{FILE_NAME}")
