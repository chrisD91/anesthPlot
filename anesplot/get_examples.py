#!/usr/bin/env python3
"""
Created on Wed Jun 29 16:53:25 2022

@author: cdesbois

load the examples files provided

usage:

import get_examples
mtrends, mwaves, ttrends = get_examples.load_example_records()
"""


import os
from typing import Any

import anesplot.config.load_recordrc
from anesplot.fast_waves import MonitorWave
from anesplot.slow_waves import MonitorTrend, TaphTrend


def load_example_records() -> tuple[Any, Any, Any]:
    """
    Load the example files as record objects.

    Returns
    -------
    mtrends : rec.MonitorTrend
        an example of monitor trends recording
    mwaves : rec.MonitorWave
        an example of monitor waves recording
    ttrends : rec.TaphTrend
        an example of taphonius trends recording

    """
    paths = anesplot.config.load_recordrc.paths
    dirname = os.path.join(paths["cwd"], "example_files")

    mont = "M2021_4_16-8_44_38.csv"
    monw = "M2021_4_16-8_44_38Wave.csv"
    tapht = "SD2021APR16-7_19_4.csv"

    filename = os.path.join(dirname, mont)
    monitor_trends = MonitorTrend(filename)

    filename = os.path.join(dirname, tapht)
    taphonius_trends = TaphTrend(filename)

    filename = os.path.join(dirname, monw)
    monitor_waves = MonitorWave(filename)

    return monitor_trends, monitor_waves, taphonius_trends


# %%
if __name__ == "__main__":
    mtrends, mwaves, ttrends = load_example_records()
    print(f"{'=' * 40}")
    print(
        "builded record examples: \n \
          'mtrends' : a MonitorTrend \n \
          'mwaves'  : a MonitorWave \n \
          'ttrends' : a TaphoniusTrend "
    )
    print("go-on : explore attributes and methods !")
    print(f"{'-' * 40}")
