#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
file used to run the package as a script from terminal:
> python anesplot/__main__.py
"""
import os
import sys

from pathlib import Path

print("Running" if __name__ == "__main__" else "Importing", Path(__file__).resolve())

# For relative imports to work in Python 3.6
if os.path.dirname(os.path.realpath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from . import record_main

# import record_main

print("-" * 10)
print('"anesthPloT.anesthplot.__main__ file"')
# print('this is {} file and __name__ is {}'.format('__main__', __name__))
# print('this is {} file and __package__ is {}'.format('__main__', __package__))
# for _ in dir():
#     print(_)
# print(s ys.argv)
print("-" * 10)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        provided_name = sys.argv[1]
        if os.path.isfile(provided_name):
            record_main.main(provided_name)
        else:
            print("the provided filename is not valid")
    else:
        record_main.main()

# ie import the module from the top level package
