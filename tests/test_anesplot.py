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

    for file in choices(files, k=num):
        trend_name = os.path.join(paths["data"], file)
        trends = rec.MonitorTrend(trend_name)

        assert isinstance(trends.header, dict)
        assert isinstance(trends.data, pd.DataFrame)


def test_loadwaves(num=5):
    """testing waves loading
    input:
        num : (int) number of iterations
    """
    records = [_ for _ in os.listdir(paths["data"]) if _.startswith("M")]
    files = [_ for _ in records if "Wave" in _]

    for file in choices(files, k=num):
        wave_name = os.path.join(paths["data"], file)
        waves = rec.MonitorWave(wave_name)

        assert isinstance(waves.header, dict)
        assert isinstance(waves.data, pd.DataFrame)


def test_loadtaph(num=15):
    """testing taph loading
    input:
        num : (int) number of iterations
    """
    apath = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"
    records = []
    for root, dirs, files in os.walk(apath):
        found = [_ for _ in files if _.startswith("SD") and _.endswith(".csv")]
        if found:
            record = found[0]
            record_name = os.path.join(root, record)
            records.append(record_name)
    for trend_name in choices(records, k=num):
        pyperclip.copy(trend_name)
        trends = rec.TaphTrend(trend_name)
        assert isinstance(trends.data, pd.DataFrame)
        trends.show_graphs()
        plt.close("all")
