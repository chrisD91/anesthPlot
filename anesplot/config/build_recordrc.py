# !/usr/bin/env python3

"""
build a 'recordRc.yaml' configuration file at the root of anesplot

- input <-> 'data' : to load the records
- output <-> 'save' : to save the plots

----
"""


import os

# import sys
from typing import Any

import yaml  # type: ignore

# from PyQt5 import QtCore
# from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

import anesplot.loadrec.dialogs as dlg

# %%


# def filedialog(
#     kind: str = "",
#     directory: Optional[str] = None,
#     for_open: bool = True,
#     fmt: str = "",
#     is_folder: bool = False,
# ) -> Union[str, list[str]]:
#     """
#     General dialog function.

#     Parameters
#     ----------
#     kind : str, optional (default is "")
#         displayed in the dialog title
#     directory : str, optional (default is os.path.dirname(__file__))
#         the directory to start with
#     for_open : bool, optional (default is True)
#     fmt : str, optional (default is "")
#     is_folder : bool, optional (default is False)

#     Returns
#     -------
#     str
#         the selected path.
#     """
#     label = "select the folder for " + kind
#     options = QFileDialog.Options()
#     #    options |= QFileDialog.DontUseNativeDialog
#     #    options |= QFileDialog.DontUseCustomDirectoryIcons
#     dialog = QFileDialog(caption=label)
#     dialog.setOptions(options)

#     dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)

#     # ARE WE TALKING ABOUT FILES OR FOLDERS
#     if is_folder:
#         dialog.setFileMode(QFileDialog.DirectoryOnly)
#     else:
#         dialog.setFileMode(QFileDialog.AnyFile)
#     # OPENING OR SAVING
#     dialog.setAcceptMode(QFileDialog.AcceptOpen) if for_open else dialog.setAcceptMode(
#         QFileDialog.AcceptSave
#     )

#     # SET FORMAT, IF SPECIFIED
#     if fmt != "" and is_folder is False:
#         dialog.setDefaultSuffix(fmt)
#         dialog.setNameFilters([f"{fmt} (*.{fmt})"])

#     # SET THE STARTING DIRECTORY
#     if directory != "":
#         dialog.setDirectory(str(directory))
#     else:
#         try:
#             __file__
#             dialog.setDirectory(os.path.dirname(__file__))
#         except NameError:
#             dialog.setDirectory(os.getcwd())

#     if dialog.exec_() == QDialog.Accepted:
#         path = dialog.selectedFiles()[0]  # returns a list
#     else:
#         path = ""
#     return str(path)


def read_config(cfg_filename: str) -> dict[str, Any]:
    """
    Load the config yaml file.

    Parameters
    ----------
    cfg_filename : str
        the config filename.

    Returns
    -------
    dict[str, Any]
        a dictionary to the defined paths.

    """
    # locate
    # try:
    #     # for external call
    #     # NB __file__ is supposed to
    #     # "always give you the path to the current file",
    #     # and sys.argv[0] is supposed to
    #     # "always give the path of the script that initiated the process"
    #     local_mod_path = os.path.dirname(__file__)
    # except NameError:
    #     # for inside spyder
    #     local_mod_path = "/Users/cdesbois/pg/chrisPg/anesthPlot/anesplot/config"
    # filename = os.path.join(local_mod_path, "recordRc.yaml")
    # # load onfiguration dico
    # print(filename)
    if os.path.isfile(cfg_filename):
        with open(cfg_filename, encoding="utf-8") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        ymlfile.close()
    else:
        cfg = {}
        print("no config file founded")
        print("please build one -> cf build_recordrc.py")
    return dict(cfg)


def build_new_paths(record_main_dir: str) -> dict[str, str]:
    """
    Build the paths dictionary.

    Parameters
    ----------
    record_main_dir : str
        the root of the package.

    Returns
    -------
    paths: dict[str:str]
        a dictionary containing the directory locations

    """
    newpaths = {}
    newpaths["recordMain"] = record_main_dir
    newpaths["cwd"] = os.getcwd()
    # manual define/confirm the paths
    for key in ["root", "data", "save"]:
        txt = f"choose directory for {key}"
        folder = newpaths.get(key, os.path.expanduser("~"))
        newpaths[key] = dlg.choose_directory(
            dirname=folder, title=txt, see_question=True
        )
    for key in ["mon_data", "taph_data", "telv_data"]:
        txt = f"choose directory for {key}"
        folder = newpaths.get(key, newpaths["data"])
        newpaths[key] = dlg.choose_directory(
            dirname=folder, title=txt, see_question=True
        )
    for key in ["sFig", "sBg"]:
        txt = f"choose directory for {key}"
        folder = newpaths.get(key, newpaths["save"])
        newpaths[key] = dlg.choose_directory(
            dirname=folder, title=txt, see_question=True
        )
    newpaths["utils"] = "~"
    return newpaths


def write_configfile(path: dict[str, Any]) -> None:
    """Record the yaml file."""
    config_loc = os.path.join(path["recordMain"], "config")
    os.chdir(path[config_loc])
    with open("recordRc.yaml", "w", encoding="utf-8") as ymlfile:
        yaml.dump(path, ymlfile, default_flow_style=False)


def main() -> None:
    """Script execution entry point."""
    # test if paths exists (ie config present)
    if "paths" not in dir():
        # get package directory
        key = "record_main.py"
        record_main_dir = dlg.choose_file(
            dirname=os.getcwd(), title=f"select the file '{key}'", filtre="*.py"
        )
        if os.path.isfile(record_main_dir):
            record_main_dir = os.path.dirname(record_main_dir)
        config_filename = os.path.join(record_main_dir, "config", "recordRc.yaml")
        paths = read_config(config_filename)
    # paths empty <-> no config_file
    if not paths:
        paths = build_new_paths(record_main_dir)
    # write config
    write_configfile(paths)


# %%


if __name__ == "__main__":
    main()
