# !/usr/bin/env python3

"""
build a 'recordRc.yaml' configuration file to adapt to a specific computer
location at the root of anesplot

- input <-> 'data' : to load the records
- output <-> 'save' : to save the plots

----
"""


import os
import sys
from typing import Union, Any, Optional

import yaml  # type: ignore
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

# %%


def filedialog(
    kind: str = "",
    directory: Optional[str] = None,
    for_open: bool = True,
    fmt: str = "",
    is_folder: bool = False,
) -> Union[str, list[str]]:
    """
    General dialog function.

    Parameters
    ----------
    kind : str, optional (default is "")
        displayed in the dialog title
    directory : str, optional (default is os.path.dirname(__file__))
        the directory to start with
    for_open : bool, optional (default is True)
    fmt : str, optional (default is "")
    is_folder : bool, optional (default is False)

    Returns
    -------
    str
        the selected path.
    """
    label = "select the folder for " + kind
    options = QFileDialog.Options()
    #    options |= QFileDialog.DontUseNativeDialog
    #    options |= QFileDialog.DontUseCustomDirectoryIcons
    dialog = QFileDialog(caption=label)
    dialog.setOptions(options)

    dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)

    # ARE WE TALKING ABOUT FILES OR FOLDERS
    if is_folder:
        dialog.setFileMode(QFileDialog.DirectoryOnly)
    else:
        dialog.setFileMode(QFileDialog.AnyFile)
    # OPENING OR SAVING
    dialog.setAcceptMode(QFileDialog.AcceptOpen) if for_open else dialog.setAcceptMode(
        QFileDialog.AcceptSave
    )

    # SET FORMAT, IF SPECIFIED
    if fmt != "" and is_folder is False:
        dialog.setDefaultSuffix(fmt)
        dialog.setNameFilters([f"{fmt} (*.{fmt})"])

    # SET THE STARTING DIRECTORY
    if directory != "":
        dialog.setDirectory(str(directory))
    else:
        try:
            __file__
            dialog.setDirectory(os.path.dirname(__file__))
        except NameError:
            dialog.setDirectory(os.getcwd())

    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()[0]  # returns a list
    else:
        path = ""
    return str(path)


def read_config() -> dict[str, Any]:
    """Locate & load the yaml file."""
    # locate
    try:
        # for external call
        # NB __file__ is supposed to
        # "always give you the path to the current file",
        # and sys.argv[0] is supposed to
        # "always give the path of the script that initiated the process"
        local_mod_path = os.path.dirname(__file__)
    except NameError:
        # for inside spyder
        local_mod_path = "/Users/cdesbois/pg/chrisPg/anesthPlot/anesplot/config"
    filename = os.path.join(local_mod_path, "recordRc.yaml")
    # load onfiguration dico
    print(filename)
    if os.path.isfile(filename):
        with open(filename, encoding="utf-8") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        ymlfile.close()
    else:
        cfg = {}
        print("no config file founded")
        print("please build one -> cf buildConfig.py")
    return dict(cfg)


def write_configfile(path: dict[str, Any]) -> None:
    """Record the yaml file."""
    config_loc = os.path.join(path["recordMain"], "config")
    os.chdir(path[config_loc])
    with open("recordRc.yaml", "w", encoding="utf-8") as ymlfile:
        yaml.dump(path, ymlfile, default_flow_style=False)


def main() -> None:
    """Script execution entry point."""
    # try:
    #     app
    # except NameError:
    #     app = QApplication(sys.argv)
    if not "app" in dir():
        app = QApplication(sys.argv)

    # test if paths exists (ie config present)
    if not "paths" in dir():
        # print('no paths dico defined')
        # package location
        key = "record_main.py"
        # record_main_path = filedialog(kind=key, directory= os.getcwd(), is_folder=True)
        record_main_path = filedialog(kind=key, directory=os.getcwd())
        record_main_path = str(record_main_path)
        if os.path.isfile(record_main_path):
            record_main_path = os.path.dirname(record_main_path)
        config_name = os.path.join(record_main_path, "config", "recordRc.yaml")
        # yaml file location
        # print('yaml location shoud be {}'.format(config_name))
        if os.path.isfile(config_name):
            # read config file
            paths = read_config()
            # print('readconfig result')
            # print(paths)
        else:
            # build config file
            paths = {}
            paths["recordMain"] = record_main_path
            paths["cwd"] = os.getcwd()
    home = os.path.expanduser("~")
    # manual define/confirm the paths
    for key in ["root", "data", "save"]:
        if key in paths.keys():
            paths[key] = filedialog(kind=key, directory=paths[key], is_folder=True)
        else:
            paths[key] = filedialog(kind=key, directory=home, is_folder=True)
    # TODO implement a dialog for monitor, taphonius and televet data
    paths["mon_data"] = paths["data"]
    paths["taph_data"] = paths["data"]
    paths["telv_data"] = paths["data"]

    paths["sFig"] = paths["save"]
    paths["sBg"] = paths["save"]
    paths["utils"] = "~"
    # write config
    write_configfile(paths)
    try:
        app
    except NameError:
        app.exec_()


# %%


if __name__ == "__main__":
    main()
