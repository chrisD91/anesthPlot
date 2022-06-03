# !/usr/bin/env python3

"""load an already generated 'recordRc.yaml' configuration file

- input <-> 'data' : to load the records
- output <-> 'save' : to save the plots

----
"""
import os
import sys

import yaml  # type: ignore

# TODO : move the configuration file to the home dir as .anesplotrc


def build_paths() -> dict[str, str]:
    """Read the yaml configuration file."""
    rc_filename = os.path.expanduser("~/.anesplotrc")
    if os.path.isfile(os.path.join(os.path.dirname(__file__), ".anesplotrc")):
        with open(rc_filename, encoding="utf-8") as ymlfile:
            rcdico = dict(yaml.safe_load(ymlfile))
    elif os.path.isfile(os.path.join(os.path.dirname(__file__), "recordRc.yaml")):
        rc_filename = os.path.join(os.path.dirname(__file__), "recordRc.yaml")
        # print("configuration file will be moved the the home folder in future versions")
        with open(rc_filename, encoding="utf-8") as ymlfile:
            rcdico = dict(yaml.safe_load(ymlfile))
    else:
        # absent -> default
        print(f"didn't find -> {rc_filename}, using default values")
        print("consider running buildConfig.py to build one")  # default config
        try:
            # print(__file__)
            loc = os.path.dirname(__file__)
            # print("loc = {}".format(loc))
            sep = os.path.sep
            examples = os.path.join(sep.join(loc.split(sep)[:-2]), "example_files")
            print(f"examples = {examples}")
            dirname = examples
        except NameError:
            print("exception !!!")
            dirname = os.path.expanduser("~")
        rcdico = dict.fromkeys(["data"], dirname)
    # print("data location is {}".format(rcdico["data"]))
    return rcdico


def adapt_with_syspath(path_dico: dict[str, str]) -> None:
    """Add the folder location to the system path."""
    if path_dico["recordMain"] not in sys.path:
        sys.path.append(path_dico["recordMain"])
        print("added", path_dico["recordMain"], " to the path")
        print("location=", path_dico["recordMain"])


#    if paths['utils'] not in sys.path:
#        sys.path.append(paths['utils'])
#        print('added', paths['utils'], ' to the path')

#    adapt_with_syspath(paths)
# trying to avoid to have a python package in the path

paths = build_paths()
# %%
if __name__ == "__main__":
    paths = build_paths()
    print(paths)
