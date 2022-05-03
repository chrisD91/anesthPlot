#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:20:28 2022

@author: cdesbois
"""
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from anesplot.config.load_recordrc import build_paths

import anesplot.treatrec.clean_data as clean
from anesplot.base import _Waves
import loadrec.agg_load as loadagg
from anesplot.loadrec import loadmonitor_trendrecord as lmt
import anesplot.plot.t_agg_plot as tagg
from anesplot.loadrec import loadtaph_trendrecord as ltt
from anesplot import treatrec


paths = build_paths()


# +++++++
class _SlowWave(_Waves):

    """
    class for slowWaves = trends

    attributes:
    -----------
        file : str
            short name
        filename : str
            long name

    methods
    -------
        clean_trend : external
            clean the data
        show_graphs : external
            plot clinical main plots
    """

    def __init__(self):
        super().__init__()

    def clean_trend(self):
        """
        clean the data, remove irrelevant,
        input = self.data,
        output = pandas dataFrame
        nb doesnt change the obj.data in place
        """
        datadf = clean.clean_trenddata(self.data)
        return datadf

    def show_graphs(self):
        """basic clinical plots"""
        if self.data.empty:
            print("recording is empty : no data to plot")
            fig_dico = {}
        else:
            fig_dico = tagg.plot_trenddata(self.data, self.header, self.param)
        return fig_dico

    def plot_trend(self):
        """choose the graph to use from a pulldown menu"""
        # TODO add a preset if self.name is defined
        if self.data.empty:
            print("recording is empty : no data to plot")
            fig = plt.figure
            name = ""
        else:
            print(f"{'-' * 20} started trends plot_trend)")
            print(f"{'-' * 10}> choose the trace")
            fig, name = tagg.plot_a_trend(self.data, self.header, self.param)
            print(f"{'-' * 20} ended trends plot_trend")
            self.fig = fig
            self.name = name
        return fig, name

    def save_roi(self, erase: bool = False) -> dict:
        """
        memorize a Region Of Interest (roi).

        Parameters
        ----------
        erase : bool, optional (default is False)
            takes the figure attribute

        Returns
        -------
        dict that contains
            dt : xscale datetime location
            pt: xscale point location
            sec: xscale seconde location
            ylims: ylimits
            traces: waves used to draw the figure
            fig : the related figure

        """
        if erase:
            roidict = {}
        if self.fig:
            roidict = tagg.get_trend_roi(self.fig, self.data, self.param)
            roidict.update({"name": self.name, "fig": self.fig})
        else:
            print("no fig attribute, please use plot_trend() method to build one")
            roidict = {}
        self.roi = roidict
        return roidict

    def build_half_white(self):
        if self.fig is None or self.name is None:
            print("please build a figure to start with -> .plot_trend()")
            return
        if self.roi is None:
            print("please define a roi -> .save_roi()")
            return
        tagg.build_half_white(self.fig, self.name, self.data, self.param, self.roi)


class MonitorTrend(_SlowWave):
    """
    monitor trends recordings:

        input = filename : path to file
        load = boolean to load data (default is True)

    attibutes:
    ----------
        file : str
            short name
        filename : str
            long name
        header : dict
            record parameters
        param : dict
            parameters

    methods (inherited)
    -------------------
        clean_trend : external
            clean the data
        show_graphs : external
            plot clinical main plots
    """

    def __init__(self, filename: str = None, load: bool = True):
        super().__init__()
        if filename is None:
            # filename = lmt.choosefile_gui(paths["mon_data"])
            filename = loadagg.choosefile_gui(paths["mon_data"])
        self.filename = filename
        self.param["filename"] = filename
        self.param["file"] = os.path.basename(filename)

        header = lmt.loadmonitor_trendheader(filename)
        self.header = header
        if header and load:
            data = lmt.loadmonitor_trenddata(filename, header)
            self.data = data
            self.param["sampling_freq"] = header.get("60/Sampling Rate", None)
            self.param["source"] = "monitorTrend"
            name = str(header["Patient Name"]).title().replace(" ", "")
            # name = name.title().replace(" ", "")
            self.param["name"] = name[0].lower() + name[1:]

        else:
            print(f"{'-'*5} MonitorTrend: didn't load the data ({load=})")
            self.data = pd.DataFrame()


class TaphTrend(_SlowWave):
    """
    taphonius trends recordings

    attibutes:
    ----------
        data : pd.DataFrame = recorded data
        header : dictionary = recorded info (patient, ...)
        param : dictionary  = usage information (file, scales, ...)
        actions : pd.DataFrame

    methods:
    --------
        show_graphs (inherited) : plot the clinical debrief 'suite'
        extract_events : decode the taph messages, build events, actions and ventil_drive
        plot_ventil_drive : plot the ventilation commands that have been used"
        plot_events : plot the events as a time display, dtime allow dtime use
        export_taph_events : build a .txt containing all the events (paths:~/temp/events.txt)
    """

    def __init__(
        self, filename: str = None, monitorname: str = None, load: bool = True
    ):
        super().__init__()
        if filename is None:
            filename = ltt.choose_taph_record(monitorname)
        self.filename = filename
        if filename:
            self.param["filename"] = filename
            self.param["file"] = os.path.basename(filename)
        if load:
            data = ltt.loadtaph_trenddata(filename)
            header = ltt.loadtaph_patientfile(filename)
        else:
            print(f"{'-'*5} TaphTrend: didn't load the data ({load=})")
            data = pd.DataFrame()
            header = {}
        self.data = data
        self.header = header

        self.param["source"] = "taphTrend"
        self.param["sampling_freq"] = None
        self.extract_events()

    def extract_events(self, shift_min=None):
        """decode the taph messages, build events, actions and ventil_drive"""
        dt_events_df = treatrec.manage_events.build_event_dataframe(self.data)
        if shift_min is not None:
            shift = timedelta(minutes=shift_min)
            dt_events_df.index = dt_events_df.index + shift

        self.dt_events_df = dt_events_df

        actions, events = treatrec.manage_events.extract_taphmessages(self.dt_events_df)
        self.actions = actions
        self.events = events
        # removed actions to be able to plot everything that arrives
        # (not only actions ie include the preset values)
        ventil_drive_df = treatrec.manage_events.extract_ventilation_drive(dt_events_df)
        self.ventil_drive_df = ventil_drive_df

    def plot_ventil_drive(self, all_traces: bool = False):
        """plot the ventilation commands that have been used"""
        fig = treatrec.manage_events.plot_ventilation_drive(
            self.ventil_drive_df, self.param, all_traces
        )
        fig.show()

    def plot_events(self, todrop: list = None, dtime: bool = False):
        """plot the events as a time display, dtime allow dtime use"""
        treatrec.manage_events.plot_events(self.dt_events_df, self.param, todrop, dtime)

    # TODO : add exclusion list

    def export_taph_events(self, save_to_file=False):
        "export in a txt files all the events (paths:~/temp/events.txt)"
        if save_to_file:
            filename = os.path.expanduser(os.path.join("~", "temp", "events.txt"))
            with open(filename, "w", encoding="utf-8") as file:
                for i, line in enumerate(self.data.events.dropna()):
                    file.write("-" * 10, "\n")
                    for item in line.split("\r\n"):
                        file.write(f"{i} {item}, \n")
            print(f"saved taph events to {filename}")
        else:
            for i, line in enumerate(self.data.events.dropna()):
                print("-" * 10)
                for item in line.split("\r\n"):
                    print(i, item)

    def shift_datetime(self, minutes: int):
        """
        shift the recording datetime

        Parameters
        ----------
        minutes : int
            minutes to add to the datetime.

        Returns
        -------
        None.

        """
        self.data = ltt.shift_datetime(self.data, minutes)
        # recompute events extractions, ventildrive, ...
        self.extract_events(minutes)

    def shift_etime(self, minutes: int):
        """
        shift the elapsed time

        Parameters
        ----------
        minutes : int
            the minutes to add to the elapsed time.

        Returns
        -------
        None.

        """
        ltt.shift_elapsed_time(self.data, minutes)

    def sync_etime(self, datetime0: datetime):
        """
        shift the elapsed time based a 'zero' datetime.datetime

        Parameters
        ----------
        datetime0 : datetime.datetime
            the datetime considered to be zero.
            typically mtrends.data.datetime.iloc[0]

        Returns
        -------
        None.

        """
        ltt.sync_elapsed_time(datetime0, self.data)
