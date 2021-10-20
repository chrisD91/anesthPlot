#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from random import choices

import pytest
import pandas as pd

import anesplot.record_main as rec

paths = rec.paths


def test_loadtrends():
    """testing trends loading"""
    records = [_ for _ in os.listdir(paths["data"]) if _.startswith("M")]
    files = [_ for _ in records if "Wave" not in _]

    for file in choices(files, k=5):
        trend_name = os.path.join(paths["data"], file)
        trends = rec.MonitorTrend(trend_name)

        assert isinstance(trends.header, dict)
        assert isinstance(trends.data, pd.DataFrame)


def test_loadwaves():
    """testing waves loading"""
    records = [_ for _ in os.listdir(paths["data"]) if _.startswith("M")]
    files = [_ for _ in records if "Wave" in _]

    for file in choices(files, k=3):
        wave_name = os.path.join(paths["data"], file)
        waves = rec.MonitorWave(wave_name)

        assert isinstance(waves.header, dict)
        assert isinstance(waves.data, pd.DataFrame)
