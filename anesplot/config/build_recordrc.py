#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
build a 'recordRc.yaml' configuration file to adapt to a specific computer
location at the root of anesplot

- input <-> 'data' : to load the records
- output <-> 'save' : to save the plots

----
"""

import os
import sys

import yaml
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

# TODO add to path: mon_data, taph_data, telv_data

# %%


def filedialog(
    kind="", directory=os.path.dirname(__file__), for_open=True, fmt="", is_folder=False
):
    """general dialog function."""
    label = "select the folder for " + kind
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    options |= QFileDialog.DontUseCustomDirectoryIcons
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
        dialog.setDirectory(os.getcwd())

    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()[0]  # returns a list
    else:
        path = ""
    return path


def read_config():
    """locate & load the yaml file."""
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
        with open(filename, "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        ymlfile.close()
        return cfg
    print("no config file founded")
    print("please build one -> cf buildConfig.py")
    return {}


def write_configfile(path):
    """record the yaml file."""
    config_loc = os.path.join(path["recordMain"], "config")
    os.chdir(path[config_loc])
    with open("recordRc.yaml", "w") as ymlfile:
        yaml.dump(path, ymlfile, default_flow_style=False)


def main():
    """main function for script execution."""
    try:
        app
    except NameError:
        app = QApplication(sys.argv)
    # test if paths exists (ie config present)
    try:
        paths
    except NameError:
        # print('no paths dico defined')
        # package location
        key = "record_main.py"
        # record_main_path = filedialog(kind=key, directory= os.getcwd(), is_folder=True)
        record_main_path = filedialog(kind=key, directory=os.getcwd())
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
