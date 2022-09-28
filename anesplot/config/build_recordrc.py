# !/usr/bin/env python3

"""
build a 'recordRc.yaml' configuration file at the root of anesplot

- input <-> 'data' : to load the records
- output <-> 'save' : to save the plots

----
"""


import os
from typing import Any
import yaml  # type: ignore

import anesplot.loadrec.dialogs as dlg

# %%


def get_config_files() -> tuple[str, str]:
    """
    Find the path for config files.

    Returns
    -------
    main_dir : TYPE
        base directory for the package 'ie contains record_main.py.
    cfg_filename : TYPE
        fullname of the configuration file.

    """

    def find_file(name: str, path: str) -> str:
        """Find file."""
        filename = ""
        for root, dirs, files in os.walk(path):
            if name in files:
                filename = os.path.join(root, name)
        return filename

    main_file = find_file(name="record_main.py", path=os.getcwd())
    main_dir = os.path.dirname(main_file)
    cfg_filename = find_file(name="recordRc.yaml", path=os.getcwd())
    return main_dir, cfg_filename


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
    os.chdir(config_loc)
    with open("recordRc.yaml", "w", encoding="utf-8") as ymlfile:
        yaml.dump(path, ymlfile, default_flow_style=False)
    print("builded config/recordRc.yaml that contains:")
    print(f"{'-'*20}")
    for key, loc in path.items():
        print(key, loc)
    print(f"{'-'*20}")


def main() -> None:
    """Script execution entry point."""
    # test if paths exists (ie config present)
    record_main_dir, config_filename = get_config_files()
    paths = read_config(config_filename)
    print("config file contains:")
    for key, path in paths.items():
        print(key, path)
    # paths empty <-> no config_file
    if not paths:
        paths = build_new_paths(record_main_dir)
        # write config
        write_configfile(paths)


# %%
if __name__ == "__main__":
    main()
