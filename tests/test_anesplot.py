#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from random import choices

import matplotlib.pyplot as plt
import pandas as pd
import pyperclip
import pytest

import anesplot.record_main as rec

paths = rec.paths


def test_loadtrends(num=15):
    """testing trends loading
    input:
        num : (int) number of iterations
    """
    records = [_ for _ in os.listdir(paths["data"]) if _.startswith("M")]
    files = [_ for _ in records if "Wave" not in _]

    if files:  # there are files in the folder
        for file in choices(files, k=num):
            trend_name = os.path.join(paths["data"], file)
            trends = rec.MonitorTrend(trend_name)

            assert isinstance(trends.header, dict)
            assert isinstance(trends.data, pd.DataFrame)
    else:
        print("{} there are no trendfiles in paths['data']".format("!" * 10))
        print(paths["data"])
        print("{} there are no trendfiles in paths['data']".format("!" * 10))
        print()


def test_loadwaves(num=5):
    """testing waves loading
    input:
        num : (int) number of iterations
    """
    records = [_ for _ in os.listdir(paths["data"]) if _.startswith("M")]
    files = [_ for _ in records if "Wave" in _]

    if files:  # there are files in the folder
        for file in choices(files, k=num):
            wave_name = os.path.join(paths["data"], file)
            waves = rec.MonitorWave(wave_name)

            assert isinstance(waves.header, dict)
            assert isinstance(waves.data, pd.DataFrame)
    else:
        print("{} there are no wavefiles in paths['data']".format("!" * 10))
        print(paths["data"])
        print("{} there are no wavefiles in paths['data']".format("!" * 10))
        print()


def test_loadtaph(num=15):
    """testing taph loading
    input:
        num : (int) number of iterations
    """
    apath = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"
    tested = []
    records = []
    for root, dirs, files in os.walk(apath):
        found = [_ for _ in files if _.startswith("SD") and _.endswith(".csv")]
        if found:
            record = found[0]
            record_name = os.path.join(root, record)
            records.append(record_name)
    if records:
        for trend_name in choices(records, k=num):
            pyperclip.copy(trend_name)
            print(f"testing {trend_name}")
            trends = rec.TaphTrend(trend_name)
            assert isinstance(trends.data, pd.DataFrame)
            # trends.show_graphs()
            # plt.close("all")
            trends.extract_events()
            # TODO -> implement the plotting testing
            # trends.plot_ventil_drive()
            # trends.plot_events()
            # figs = list(map(plt.figure, plt.get_fignums()))
            # for fig in figs:
            # plt.close(fig)
            # plt.close("all")

    else:
        print("{} there are no taphfiles in the selected folder".format("!" * 10))
        print(apath)
        print("{} there are no wavefiles in the selected folder".format("!" * 10))
        print()
