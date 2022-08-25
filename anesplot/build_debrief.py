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

import pyperclip

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
            directories.append(directory)
            logging.debug(f"builded {directory}")
        except FileExistsError:
            logging.debug(f"directory {directory} already exist")
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
        "from anesplot.config.load_recordrc import build_paths",
        "",
        "paths = build_paths()",
        f"paths['debriefs'] = '{paths['debriefs']}'",
        f"dir_name = '{debrief_dirname}'",
        "os.chdir(dir_name)",
        "",
        f"file_name = '{record_name}'",
        "mtrends = MonitorTrend(file_name)",
        "mwaves = MonitorWave((mtrends.wavename()))",
        "ttrends = TaphTrend(monitorname = mtrends.filename)",
        "",
        "save_name = os.path.join(dir_name, 'data', os.path.basename(dir_name)+'.hd5')",
        "io.export_data_to_hdf(save_name, mtrend=mtrends, mwave=mwaves, ttrend=ttrends)"
        "",
    ]
    with open("csv2hdf.py", "r", encoding="utf8") as openf:
        if lines[-2] in openf.read():
            print("csv2hdf has already be filled")
            return
    with open("csv2hdf.py", "a", encoding="utf8") as openf:
        for line in lines:
            openf.write(line + "\n")
        print("prefilled csv2hdf.py")


def fill_work_on(record_name: str, debrief_dirname: str) -> None:
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
        "from anesplot.config.load_recordrc import build_paths",
        "",
        "paths = build_paths()",
        f"paths['debriefs'] = '{paths['debriefs']}'",
        f"dir_name = '{debrief_dirname}'",
        "os.chdir(dir_name)",
        "",
        f"file_name = '{record_name}'",
        "",
        "save_name = os.path.join(dir_name, 'data', os.path.basename(dir_name)+'.hd5')",
        "mtrends, ttrends, mwaves = io.build_obj_from_hdf(savedname = save_name)",
        "",
    ]
    with open("work_on.py", "r", encoding="utf8") as openf:
        if lines[-2] in openf.read():
            print("work_on has already be filled")
            return
    with open("work_on.py", "a", encoding="utf8") as openf:
        for line in lines:
            openf.write(line + "\n")
        print("prefilled work_on.py")


def fill_ekg2hr(record_name: str, debrief_dirname: str) -> None:
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
        "import pandas as pd",
        "",
        "import anesplot.loadrec.export_reload as io",
        "import anesplot.treatrec.ekg_to_hr as tohr",
        "from anesplot.slow_waves import MonitorTrend, TaphTrend",
        "from anesplot.fast_waves import MonitorWave",
        "from anesplot.config.load_recordrc import build_paths",
        "from anesplot.treatrec.wave_func import fix_baseline_wander",
        "",
        "paths = build_paths()",
        f"paths['debriefs'] = '{paths['debriefs']}'",
        f"dir_name = '{debrief_dirname}'",
        "os.chdir(dir_name)",
        "",
        f"file_name = '{record_name}'",
        "",
        "# %% 1.load",
        "save_name = os.path.join(dir_name, 'data', os.path.basename(dir_name)+'.hd5')",
        "mtrends, ttrends, mwaves = io.build_obj_from_hdf(savedname=save_name)",
        "# format the name",
        "name = mtrends.header['Patient Name'].title().replace(' ', '')",
        "name = name[0].lower() + name[1:]",
        "",
        "# %% 2. treat the ekg wave:",
        "params = mwaves.param",
        "ekg_df = pd.DataFrame(mwaves.data.wekg)",
        "ekg_df['wekg_lowpass'] = fix_baseline_wander(ekg_df.wekg, mwaves.param['sampling_freq'])",
        "beatloc_df = tohr.detect_beats(ekg_df.wekg_lowpass, threshold=-1)",
        "",
        "# %% 3. perform the manual adjustments required:",
        "figure = tohr.plot_beats(ekg_df.wekg_lowpass, beatloc_df)",
        "beats_tochange_df = pd.DataFrame(columns=beatloc_df.columns.insert(0, 'action'))"
        "",
        "# - remove or add peaks : zoom on the figure to observe only one peak, then::",
        "beats_tochange_df = tohr.remove_a_beat(beatloc_df, beats_tochange_df, figure)",
        "# or",
        "beats_tochange_df = tohr.remove_allbeats(beatloc_df, beats_tochange_df, figure)",
        "# or",
        "beats_tochange_df = tohr.append_a_beat(ekg_df, beats_tochange_df, figure, yscale=-1)",
        "",
        "# - combine to update the beatloc_df with the manual changes::",
        "beatloc_df = tohr.update_beatloc_df(beatloc_df, beats_tochange_df, path_to_file="
        ", from_file=False)",
        "",
        "# %% - save the peaks locations::",
        "save = False",
        "if save:",
        "   tohr.save_beats(beatloc_df, beats_tochange_df, savename='', dirpath=None)",
        "# (# or reload",
        "# beatloc_df = pd.read_hdf('beatDf.hdf', key='beatDf') )",
        "",
        "# %% 4. go from points values to continuous time:",
        "beatloc_df = tohr.point_to_time_rr(beatloc_df)",
        "ahr_df = tohr.interpolate_rr(beatloc_df)",
        "tohr.plot_rr(ahr_df, params)",
        "",
        "# %% 5. append intantaneous heart rate to the initial data:",
        "ekg_df = tohr.append_rr_and_ihr_to_wave(ekg_df, ahr_df)",
        "mwaves.data = tohr.append_rr_and_ihr_to_wave(mwaves.data, ahr_df)",
        "",
        "TODO: implement the save process in build_debrief",
    ]

    with open("ekg2hr.py", "r", encoding="utf8") as openf:
        if lines[-2] in openf.read():
            print("ekg2hr.py has already be filled")
            return
    with open("ekg2hr.py", "a", encoding="utf8") as openf:
        for line in lines:
            openf.write(line + "\n")
        print("prefilled ekg2hr.py")


def main() -> None:
    """Build process."""
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
    fill_work_on(file_name, dir_name)
    pyperclip.copy(dir_name)
    print("the debriefing path in is the clipboard")
    print("move to that folder and execute 'python csv2hdf.py' to load and save to hd5")
    print("then 'work_on.py' will be ready to be used")


# %%

if __name__ == "__main__":
    main()
