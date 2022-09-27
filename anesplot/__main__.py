#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 22/04/04 14:47:37

entry point from command line: use  'python -m anesplot'

@author: cdesbois
"""


import os
import sys

import anesplot.record_main

if __name__ == "__main__":
    IN_NAME = None
    # check if a filename was provided from terminal call
    print(f"{sys.argv=}")

    if len(sys.argv) > 1:
        provided_name = sys.argv[1]
        if os.path.isfile(provided_name):
            IN_NAME = provided_name
        else:
            print("the provided filename is not valid")
    anesplot.record_main.main(IN_NAME)
