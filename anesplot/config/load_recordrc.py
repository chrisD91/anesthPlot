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

# TODO : move the configuration file to the home dir as .anesplotrc

def build_paths():
    """read the yaml configuration file."""
    # import package -> absolute location
    # run record main -> absolute path
    # as a script -> doesnt work
    # nb from command line -> __file__ = absolute path 
    # from python -> relative path
    
    print("in build_path, __file__ is {}".format(__file__))
    print("in build_path,argv= {}".format(sys.argv))
   
    # rc_file -> dico
    rc_filename = os.path.expanduser('~/.anesplotrc')
    if os.path.isfile(rc_filename):
        with open(rc_filename, "r") as ymlfile:
            rcdico = yaml.safe_load(ymlfile)
    else:
        # absent -> default
        print("didn't find -> {}, using default values".format(rc_filename))
        print("consider running buildConfig.py to build one")# default config
        try:
            # print(__file__)
            loc = os.path.dirname(__file__)
            # print("loc = {}".format(loc))
            sep = os.path.sep
            examples = os.path.join(
                sep.join(loc.split(sep)[:-2]), 'example_files')
            print("examples = {}".format(examples))
            dirname = examples
        except NameError:
            print('exception !!!')
            dirname = os.path.expanduser('~')
        rcdico = dict.fromkeys(['data'], dirname)
    print("data location is {}".format(rcdico['data']))
    return rcdico
        
    # try:
    #     local_mod_path = os.path.dirname(__file__)
    #     # local_mod_path = main_loc
    #     print("__file__= {}".format(__file__))
    #     print("argv= {}".format(sys.argv))
    # except NameError:
    #     # for inside spyder
    #     local_mod_path = "/Users/cdesbois/pg/chrisPg/anesthplot/anesplot/config"
    #     print('no local directory')
    # rc_file = os.path.join(local_mod_path, "recordRc.yaml")
    # # load
    # if os.path.isfile(rc_file):
    #     with open(rc_file, "r") as ymlfile:
    #         cfg = yaml.safe_load(ymlfile)
    #         return cfg
    # else:
    #     print("didn't find {}".format(rc_file))
    #     # print("no recordRc.yaml configFile present")
    #     print("please build one -> cf buildConfig.py")
    #     return None


def adapt_with_syspath(path_dico):
    """add the folder location to the system path."""
    if path_dico["recordMain"] not in sys.path:
        sys.path.append(path_dico["recordMain"])
        print("added", path_dico["recordMain"], " to the path")
        print("location=", path_dico["recordMain"])


#    if paths['utils'] not in sys.path:
#        sys.path.append(paths['utils'])
#        print('added', paths['utils'], ' to the path')

#    adapt_with_syspath(paths)
# trying to avoid to have a python package in the path

#%%
if __name__ == '__main__':
    paths = build_paths()
    if paths:
        pass

