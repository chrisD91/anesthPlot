#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""load an already generated 'recordRc.yaml' configuration file

- input <-> 'data' : to load the records
- output <-> 'save' : to save the plots

----
"""
import os
import sys

import yaml


def build_paths():
    """read the yaml configuration file."""
    # locate
    try:
        # local_mod_path = os.path.dirname(__file__)
        local_mod_path = main_loc
        print("__file__", __file__)
        print("argv", sys.argv)
    except NameError:
        # for inside spyder
        local_mod_path = "/Users/cdesbois/pg/chrisPg/anesthplot/anesplot/config"
    rc_file = os.path.join(local_mod_path, "recordRc.yaml")
    # load
    if os.path.isfile(rc_file):
        with open(rc_file, "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
            return cfg
    else:
        print("rc_file should be ", rc_file)
        print("no recordRc.yaml configFile present")
        print("please build one -> cf buildConfig.py")
        return None


def adapt_with_syspath(path_dico):
    """add the folder location to the system path."""
    if path_dico["recordMain"] not in sys.path:
        sys.path.append(path_dico["recordMain"])
        print("added", path_dico["recordMain"], " to the path")
        print("location=", path_dico["recordMain"])


#    if paths['utils'] not in sys.path:
#        sys.path.append(paths['utils'])
#        print('added', paths['utils'], ' to the path')

paths = build_paths()
if paths:
    pass
#    adapt_with_syspath(paths)
# trying to avoid to have a python package in the path
