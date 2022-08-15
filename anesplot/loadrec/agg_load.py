# !/usr/bin/env python3
"""
Created on Thu Apr 28 15:50:27 2022

@author: cdesbois
"""
import logging
import os
import sys
from typing import Optional, Union

from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QWidget

app = QApplication.instance()
logging.info(f"agg_load.py : {__name__=}")
if app is None:
    logging.info("N0 QApplication instance - - - - - - - - - - - - - > creating one")
    app = QApplication([])
else:
    logging.warning(f"QApplication instance already exists: {QApplication.instance()}")


def choosefile_gui(dirname: Optional[str] = None) -> str:
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
    if dirname is None:
        dirname = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
    # bug un macos : necessity to add a fakename
    dirname = os.path.join(dirname, "fakename.csv")
    if "app" not in dir():
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirname, filter="All files (*)"
    )
    logging.warning("return")

    if isinstance(fname, tuple):
        fullname = fname[0]
    else:
        fullname = fname
    return str(fullname)


def select_type(
    question: Optional[str] = None, items: Optional[list[str]] = None, num: int = 0
) -> Union[str, None]:
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
    if "app" not in dir():
        app = QApplication([])
        app.setQuitOnLastWindowClosed(True)
    widg = QWidget()
    kind, ok_pressed = QInputDialog.getItem(widg, "select", question, items, num, False)
    if ok_pressed and kind:
        selection = str(kind)
    else:
        selection = None
    return selection


# %%
if __name__ == "__main__":
    import anesplot.config.load_recordrc

    paths = anesplot.config.load_recordrc.paths
    FILENAME = choosefile_gui(paths["data"])
    logging.warning(os.path.basename(FILENAME))
