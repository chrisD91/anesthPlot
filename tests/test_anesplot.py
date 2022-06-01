#!/usr/bin/env python3
"""
module to use using pytest
Created on Wed Jun  1 10:32:17 2022

@author: cdesbois
"""

import os
from random import choices
from typing import Any, Callable, Optional

import matplotlib.pyplot as plt
import pandas as pd
import pyperclip

# import pytest


# import anesplot.record_main
import anesplot.slow_waves
import anesplot.fast_waves
import anesplot.plot.trend_plot
from anesplot.config.load_recordrc import build_paths

paths = build_paths()


def test_loadtrends(num: int = 5) -> None:
    """testing trends loading
    input:
        num : (int) number of iterations
    """
    records = [_ for _ in os.listdir(paths["data"]) if _.startswith("M")]
    files = [_ for _ in records if "Wave" not in _]

    if files:  # there are files in the folder
        for file in choices(files, k=num):
            trend_name = os.path.join(paths["data"], file)
            # trends = rec.MonitorTrend(trend_name)
            trends = anesplot.slow_waves.MonitorTrend(trend_name)

            assert isinstance(trends.header, dict)
            assert isinstance(trends.data, pd.DataFrame)
    else:
        print(f"{'!' * 10} there are no trendfiles in paths['data']")
        print(paths["data"])
        print(f"{'!' * 10} there are no trendfiles in paths['data']")
        print()


def test_loadwaves(num: int = 2) -> None:
    """testing waves loading
    input:
        num : (int) number of iterations
    """
    records = [_ for _ in os.listdir(paths["data"]) if _.startswith("M")]
    files = [_ for _ in records if "Wave" in _]

    if files:  # there are files in the folder
        for file in choices(files, k=num):
            wave_name = os.path.join(paths["data"], file)
            # waves = rec.MonitorWave(wave_name)
            # waves = rec.MonitorWave(wave_name)
            waves = anesplot.fast_waves.MonitorWave(wave_name)

            assert isinstance(waves.header, dict)
            assert isinstance(waves.data, pd.DataFrame)
    else:
        print(f"{'!' * 10} there are no wavefiles in paths['data']")
        print(paths["data"])
        print(f"{'!' * 10} there are no wavefiles in paths['data']")
        print()


def test_loadtaph(num: int = 5) -> None:
    """testing taph loading
    input:
        num : (int) number of iterations
    """
    apath = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"
    # tested = []
    records = []
    for root, _, files in os.walk(apath):
        found = [_ for _ in files if _.startswith("SD") and _.endswith(".csv")]
        if found:
            record = found[0]
            record_name = os.path.join(root, record)
            records.append(record_name)
    if records:
        for trend_name in choices(records, k=num):
            pyperclip.copy(trend_name)
            print(f"testing {trend_name}")
            # trends = rec.TaphTrend(trend_name)
            trends = anesplot.slow_waves.TaphTrend(trend_name)
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
        print(f"{'!' * 10} there are no taphfiles in the selected folder")
        print(apath)
        print("{'!' * 10} there are no wavefiles in the selected folder")
        print()


def test_trend_plot() -> None:
    """test the trend plotting"""

    def t_header_plot(header: pd.DataFrame, param: dict[str, Any]) -> None:
        """Test the plotting for header."""
        headerfunc_list: list[
            Callable[[dict[str, Any], Optional[dict[str, Any]]], plt.Figure]
        ] = [
            anesplot.plot.trend_plot.plot_header,
        ]

        # print(f"{'...'*5} test_header_plot < ")
        for func in headerfunc_list:
            # plt.close('all')
            fig = func(header, param)
            fig.show()
            print(func.__name__)
            plt.close(fig)
        plt.close("all")
        # print(f"{'...'*5} > test_header_plot")

    def t_data_plot(data: pd.DataFrame, param: dict[str, Any]) -> None:
        """Test the plotting for data."""
        # print(f"{'...'*5} test_data_plot < ")
        datafunc_list: list[
            Callable[[pd.DataFrame, Optional[dict[str, Any]]], plt.Figure]
        ] = [
            anesplot.plot.trend_plot.cardiovasc,
            anesplot.plot.trend_plot.cardiovasc_p1p2,
            anesplot.plot.trend_plot.co2iso,
            anesplot.plot.trend_plot.co2o2,
            anesplot.plot.trend_plot.hist_cardio,
            anesplot.plot.trend_plot.hist_co2_iso,
            anesplot.plot.trend_plot.recrut,
            anesplot.plot.trend_plot.sat_hr,
            anesplot.plot.trend_plot.ventil,
            anesplot.plot.trend_plot.ventil_cardio,
        ]
        for func in datafunc_list:
            # plt.close('all')
            print(func.__name__)
            fig = func(data, param)
            fig.show()
            plt.close(fig)
        plt.close("all")
        print(f"{'...'*5} > test_data_plot")

    print(f"{'='* 20} ")
    file = "example_files/MonitorTrend.csv"
    filename = os.path.join(paths["cwd"], file)
    mtrends = anesplot.slow_waves.MonitorTrend(filename)
    print(f"{'='* 20} ")
    t_header_plot(mtrends.header, mtrends.param)
    t_data_plot(mtrends.data, mtrends.param)
    print(f"{'='* 20} ")
