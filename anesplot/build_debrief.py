#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 09:07:52 2022

@author: cdesbois
"""

import os
import logging
from typing import Optional
from datetime import datetime

import anesplot.loadrec.dialogs as dlg
from anesplot.config.load_recordrc import build_paths

paths = build_paths()


def locate_debriefs_directory(basedir: Optional[str] = None) -> str:
    """
    Choose the location of the debrief folders.

    Parameters
    ----------
    basedir : Optional[str], optional (default is None.)
        the debrief folder to build into

    Returns
    -------
    str
        the debriefs folder.

    """
    if basedir is None:
        basedir = os.path.expanduser("~")
    dirname = dlg.choose_directory(
        basedir, "choose the parent directory", see_question=True
    )
    return dirname


def select_atrend_record(basedir: Optional[str] = None) -> str:
    """
    Select a record file to base the folde construction.

    Parameters
    ----------
    basedir : Optional[str], optional (default is None)
        path to the data

    Returns
    -------
    str
        filename (fullname)

    """
    if basedir is None:
        basedir = os.path.expanduser("~")
    filename = dlg.choose_file(basedir)
    return filename


def build_thedebrieffolder(filename: str, basedir: str) -> str:
    """
    Build and move to debrieffolder ('yymmdd').

    Parameters
    ----------
    filename : str
        a filename to decode the date.
    basedir : str
        the location of the 'debriefs' directory.

    Returns
    -------
    dirname
        fullname of the folder.

    """
    if not os.path.isdir(basedir):
        print("please provide a basedirectory to build in")
        return ""
    adate = os.path.basename(filename).strip(".csv").strip("M")
    dtime = datetime.strptime(adate, "%Y_%m_%d-%H_%M_%S")
    newfoldername = dtime.strftime("%y%m%d_%H")
    dirname = os.path.join(basedir, newfoldername)
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    else:
        print(f"folder already exists {dirname}")
    os.chdir(dirname)
    return dirname


def organize_debrief_folder(dirname: str) -> None:
    """
    Build file and sub_folders for debrief process inside the current directory.

    Returns
    -------
    None.

    """
    if not os.path.isdir(dirname):
        logging.warning(f"{dirname=} is not a folder")
        print("please provide a valid dirname")

    now = datetime.now()
    date = now.strftime("%Y_%m_%d-%H:%m:%S")
    # os.chdir("/Users/cdesbois/toPlay/dir_test")
    os.chdir(dirname)

    shebang = ["#!/usr/bin/env python3", "# -*- coding: utf-8 -*-", ""]
    build = [
        '"""',
        f"Created on {date}",
        "",
        f"@author: {os.path.basename(os.path.expanduser('~'))}",
        '"""',
    ]

    for directory in ["data", "fig", "doc", "bib"]:
        try:
            os.mkdir(directory)
            logging.debug(f"builded {directory}")
        except FileExistsError:
            logging.debug(f"directory {directory} already exist")

    for file in ["csv2hdf.py", "ekg2hr.py", "work_on.py", "todo.md"]:
        if os.path.exists(file):
            logging.debug(f"{file} already exists")
        else:
            with open(file, "w", encoding="utf-8") as openf:
                if file.rsplit(".", maxsplit=1)[-1] == "py":
                    openf.writelines(line + "\n" for line in shebang)
                openf.writelines(line + "\n" for line in build)


# %%

if __name__ == "__main__":
    location = os.path.join(
        os.path.expanduser("~"), "enva", "clinique", "recordings", "debriefs"
    )
    paths["debriefs"] = locate_debriefs_directory(location)
    file_name = select_atrend_record(paths["mon_data"])
    dir_name = build_thedebrieffolder(file_name, paths["debriefs"])
