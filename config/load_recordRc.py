# -*- coding: utf-8 -*-


import os
import sys
import yaml

def build_paths():
    """
    read the yaml configuration file
    """
    #locate
    try:
        local_mod_path = os.path.dirname(__file__)
        print(__file__)
    except NameError:
        # for inside spyder
        local_mod_path = '/Users/cdesbois/pg/chrisPg/anesthplot'
    rc_file = os.path.join(local_mod_path, 'recordRc.yaml')
    #load
    if os.path.isfile(rc_file):
        with open(rc_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
            return cfg
    else:
        print('no recordRc.yaml configFile present')
        print('please build one -> cf buildConfig.py')
        return None

def adapt_with_syspath(path_dico):
    """
    add the folder location to the system path
    """
    if path_dico['recordMain'] not in sys.path:
        sys.path.append(path_dico['recordMain'])
        print('added', path_dico['recordMain'], ' to the path')
        print('location=', path_dico['recordMain'])
#    if paths['utils'] not in sys.path:
#        sys.path.append(paths['utils'])
#        print('added', paths['utils'], ' to the path')

paths = build_paths()
if paths:
    adapt_with_syspath(paths)
