# see https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
from pathlib import Path

print("Running" if __name__ == "__main__" else "Importing", Path(__file__).resolve())


# For relative imports to work in Python 3.6
import os, sys

if os.path.dirname(os.path.realpath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# __name__ = "__main__"
# from anesplot import record_main
# from anesplot import treatrec

from . import record_main

# from . import treatrec

print("-" * 10)
# print('"anesthPloT.anesthplot.__main__ file"')
# print('this is {} file and __name__ is {}'.format('__main__', __name__))
# print('this is {} file and __package__ is {}'.format('__main__', __package__))
# for _ in dir():
#     print(_)
print("-" * 10)


if __name__ == "__main__":
    record_main.main()

# ie import the module from the top level package
