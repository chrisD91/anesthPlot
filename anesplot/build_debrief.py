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
import anesplot.loadrec.export_reload as io  # noqa: F401
from anesplot.slow_waves import MonitorTrend, TaphTrend  # noqa: F401
from anesplot.fast_waves import MonitorWave  # noqa: F401
from anesplot.config.load_recordrc import build_paths
from anesplot.guides.choose_guide import (  # noqa: F401
    get_basic_debrief_commands,
)

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
        basedir, "choose the debriefs parent directory", see_question=True
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
    txt = "choose the record to build from"
    filename = dlg.choose_file(basedir, title=txt)
    return filename


def build_debrief_name(filename: str) -> str:
    """
    Decode the date and build a string from it.

    Parameters
    ----------
    filename : str
        a trends recording name (taphonius or monitor record name).

    Returns
    -------
    str
        directory name : 'YYmmdd-H' + 'h'

    """
    if os.path.basename(filename).startswith("SD"):
        # taph record
        months = {
            "jan": "_01_",
            "feb": "_02_",
            "mar": "_03_",
            "apr": "_04_",
            "may": "_05_",
            "jun": "_06_",
            "jul": "_07_",
            "aug": "_08_",
            "sep": "_09_",
            "oct": "_10_",
            "nov": "_11_",
            "dec": "_12_",
        }

        recorddate = os.path.basename(filename).strip("SD").strip(".csv").lower()
        for abbr, num in months.items():
            recorddate = recorddate.replace(abbr, num)
        dtime = datetime.strptime(recorddate, "%Y_%m_%d-%H_%M_%S")
    elif os.path.basename(filename).startswith("M"):
        adate = os.path.basename(filename).strip(".csv").strip("M").strip("Wave")
        dtime = datetime.strptime(adate, "%Y_%m_%d-%H_%M_%S")
    else:
        print(f"unable to decode the date from {filename}")
        print("please provide a trend file name")
        print("should be 'SDYYYYMMMD-h_m_s.csv' or 'MYYmmdd.csv'")
        logging.warning(f"unable to decode date from {filename=}")
        return ""
    newfoldername = dtime.strftime("%y%m%d_%H") + "h"
    return newfoldername


def build_thedebrieffolder(newfoldername: str, basedir: str) -> str:
    """
    Build and move to debrieffolder ('yymmdd').

    Parameters
    ----------
    newfoldername : str
        a the folder to create.
    basedir : str
        the location of the container ('debriefs' directory).

    Returns
    -------
    dirname
        fullname of the newfolder.

    """
    if not os.path.isdir(basedir):
        print("please provide a basedirectory to build in")
        return ""
    dirname = os.path.join(basedir, newfoldername)
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    else:
        print(f"folder already exists {dirname}")
    return dirname


def fill_debrief_folder(dirname: str) -> None:
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

    shebang = ["#!/usr/bin/env python3", "# -*- coding: utf-8 -*-", ""]
    build = [
        '"""',
        f"Created on {date}",
        "",
        f"@author: {os.path.basename(os.path.expanduser('~'))}",
        '"""',
    ]

    directories = []
    for directory in ["data", "fig", "doc", "bib"]:
        try:
            os.mkdir(directory)
            logging.debug(f"builded {directory}")
        except FileExistsError:
            logging.debug(f"directory {directory} already exist")
        finally:
            directories.append(directory)
    print(f"created directories : {directories}")

    files = []
    for file in ["csv2hdf.py", "ekg2hr.py", "work_on.py", "todo.md"]:
        if os.path.exists(file):
            logging.debug(f"{file} already exists")
        else:
            with open(file, "w", encoding="utf-8") as openf:
                if file.rsplit(".", maxsplit=1)[-1] == "py":
                    openf.writelines(line + "\n" for line in shebang)
                openf.writelines(line + "\n" for line in build)
            logging.debug(f"{file} created")
            files.append(file)
    print(f"created files : {files}")


def fill_csv2hdf(record_name: str, debrief_dirname: str) -> None:
    """
    Fill the file with standard process and adequate variables.

    Parameters
    ----------
    record_name : str
        the monitorRecord filename.
    debrief_dirname : str
        the destination dirname.

    Returns
    -------
    None.

    """

    lines = [
        "import os",
        "",
        "import anesplot.loadrec.export_reload as io",
        "from anesplot.slow_waves import MonitorTrend, TaphTrend",
        "from anesplot.fast_waves import MonitorWave",
        "from anesplot.load_recordrc import build_paths",
        "",
        "paths = build_paths()",
        f"paths['debriefs' = {paths['debriefs']}",
        f"dir_name = {debrief_dirname}",
        "os.chdir(dir_name)",
        "",
        f"file_name = '{record_name}'",
        "mtrends = rec.MonitorTrend(file_name)",
        "mwaves = rec.MonitorWave((mtrends.wavename()))",
        "ttrends = rec.TaphTrend(monitorname = mtrends.filename)",
        "",
        "save_name = os.path.join(dir_name, 'data', os.path.basename(dir_name)+'.hd5')",
        "mtrends.data.aaLabel = mtrends.data.aaLabel.astype(str)",
        "io.export_data_to_hdf(save_name, mtrend=mtrends, mwave=mwaves, ttrend=ttrends)"
        "",
    ]

    with open("csv2hdf.py", "a", encoding="utf8") as openf:
        # openf.write(f"file_name = '{filename}'" + "\n")
        for line in lines:
            openf.write(line + "\n")


def main() -> None:
    """Building process."""
    location = os.path.join(
        os.path.expanduser("~"), "enva", "clinique", "recordings", "debriefs"
    )
    paths["debriefs"] = locate_debriefs_directory(location)
    file_name = select_atrend_record(paths["mon_data"])
    newfolder_name = build_debrief_name(file_name)
    dir_name = build_thedebrieffolder(newfolder_name, paths["debriefs"])
    os.chdir(dir_name)
    fill_debrief_folder(dir_name)
    fill_csv2hdf(file_name, dir_name)


# %%

if __name__ == "__main__":
    main()
