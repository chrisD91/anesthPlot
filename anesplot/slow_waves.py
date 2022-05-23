# !/usr/bin/env python3
"""
Created on Thu Apr 28 16:20:28 2022

@author: cdesbois

build the objects for the slow_waves ('trends'):
    -> MonitorTrend
    -> TaphTrend

"""
import os
from datetime import datetime, timedelta
from typing import Any, Optional

import matplotlib.pyplot as plt
import pandas as pd

# import anesplot
import anesplot.loadrec.loadtaph_trendrecord as ltt
import anesplot.plot.t_agg_plot as tagg
from anesplot.base import _Waves
from anesplot.config.load_recordrc import build_paths
from anesplot.loadrec.agg_load import choosefile_gui
from anesplot.loadrec.loadmonitor_trendrecord import (
    loadmonitor_trenddata,
    loadmonitor_trendheader,
)
from anesplot.treatrec import manage_events
from anesplot.treatrec.clean_data import clean_trenddata

paths = build_paths()


# +++++++
class _SlowWave(_Waves):
    """
    Class for slow_waves = trends.

    Attributes
    ----------
    file : str
        shortname
    filename : str
        longname

    Methods
    -------
    clean_trend : external
        clean the data
    show_graphs : external
        plot clinical main plots
    """

    def __init__(self) -> None:
        super().__init__()
        self.name: str

    def clean_trend(self) -> pd.DataFrame:
        """
        Clean the data, remove irrelevant.

        input = self.data,
        output = pandas dataFrame
        nb doesnt change the obj.data in place
        """
        datadf = clean_trenddata(self.data)
        return datadf

    def show_graphs(self) -> dict[str, Any]:
        """Build and display classical clinical plots."""
        if self.data.empty:
            print("recording is empty : no data to plot")
            fig_dico = {}
        else:
            fig_dico = tagg.plot_trenddata(self.data, self.header, self.param)
        return fig_dico

    def plot_trend(self) -> tuple[plt.Figure, str]:
        """Choose the graph to use from a pulldown menu."""
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

    def save_roi(self, erase: bool = False) -> dict[str, Any]:
        """
        Memorize a Region Of Interest (roi).

        Parameters
        ----------
        erase : bool, optional (default is False)
            use the figure attribute

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

    def build_half_white(self) -> tuple[plt.Figure, plt.Figure]:
        """
        Take self.fig and build a figure with a, empty 50% time expansion.

        Return
        ------
        halffig: plt.Figure
            the builded (half) plot
        fullfig: plt.Figure
            a fullscale plot
        """
        if self.fig is None or self.name is None:
            print("please build a figure to start with -> .plot_trend()")
            return plt.Figure(), plt.Figure()
        if self.roi is None:
            print("please define a roi -> .save_roi()")
            return plt.Figure(), plt.Figure()
        halffig, _, fullfig = tagg.build_half_white(
            self.fig, self.name, self.data, self.param, self.roi
        )
        halffig.show()
        fullfig.show()
        return halffig, fullfig


class MonitorTrend(_SlowWave):
    """
    Monitor trends recordings class.

    Attributes
    ----------
    filename : str
        the fullname of the file
    header : dict
        the header data
    data : pd.DataFrame
        the recorded data
    param : dict
        description of data loaded and manipulated
    fig : plt.Figure
        the current fig
    roi : dict
        the memorized RegionOfInterest (related to the actual figure)

    Methods
    -------
    show_graphs
        plot debriefing plots
    plot_trend
        plot after a selection dialog
    save_roi
        update the roi from the current plot
    build_half_white
        build and helf_right empty plot (teaching purposes)
    clean_trend
        (to be improved)
    """

    def __init__(self, filename: Optional[str] = None, load: bool = True):
        """
        Initilisation routine.

        Parameters
        ----------
        filename : str, optional (default is None)
            the fullname to the file.
        load : bool, optional (default is True)
            indication to load the data (the header is always loaded)
        """
        super().__init__()
        if filename is None:
            filename = choosefile_gui(paths["mon_data"])
        self.filename = filename
        self.param["filename"] = filename
        self.param["file"] = os.path.basename(filename)

        header = loadmonitor_trendheader(filename)
        self.header = header
        if header and load:
            data = loadmonitor_trenddata(filename, header)
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
    taphonius trends recordings.

    Attributes
    ----------
        filename : str
            the fullname
        header : dictionary
            the recorded info (patient, ...)
        data : pd.DataFrame
            the recorded data
        param : dictionary
            the informations about the record (file, scales, ...)
        actions : dictionary
            a summary of the operator actions
        events : set
            the detected events
        dt_events_df : pd.DataFrame
            the detected events over time
        ventil_drive_df : pd.DataFrame
            a summary of the user interaction with the ventilator
        fig : plt.Figure
            the current figure
        roi : dict
            the RegionOfInterest parameters for the current fig

    Methods
    -------
        show_graphs
            plot debriefing plots
        plot_trend
            plot after a selection dialog
        save_roi
            update the roi from the current plot
        build_half_white
            build and helf_right empty plot (teaching purposes)
        clean_trend
            (to be improved)
    """

    def __init__(
        self,
        filename: str,
        monitorname: Optional[str] = None,
        load: Optional[bool] = True,
    ):
        """
        Initilisation routine.

        Parameters
        ----------
        filename : str, optional (default is None)
            the fullname to the file.
        monitorname : str, optional (default is None)
            the fullname of the monitor file to get a matching based on recorded date
        load : bool, optional (default is True)
            indication to load the data
        """
        super().__init__()
        if filename is None:
            filename = ltt.choose_taph_record(monitorname)
        self.filename = filename
        if filename:
            self.param["filename"] = filename
            self.param["file"] = os.path.basename(filename)
        if load:
            data = ltt.loadtaph_trenddata(filename)
            data = pd.DataFrame(data)
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

    def extract_events(self, shift_min: Optional[int] = None) -> None:
        """
        Decode the taph messages, build events, actions and ventil_drive.

        Attributes
        ----------
        shift_min : int
            the minute to shift the record to fit with monitor dates
        """
        dt_events_df = manage_events.build_event_dataframe(self.data)
        if shift_min is not None:
            shift = timedelta(minutes=shift_min)
            dt_events_df.index = dt_events_df.index + shift

        self.dt_events_df = dt_events_df

        actions, events = manage_events.extract_taphmessages(self.dt_events_df)
        self.actions = actions
        self.events = events
        # removed actions to be able to plot everything that arrives
        # (not only actions ie include the preset values)
        ventil_drive_df = manage_events.extract_ventilation_drive(dt_events_df)
        self.ventil_drive_df = ventil_drive_df

    def plot_ventil_drive(self, all_traces: bool = False) -> plt.Figure:
        """Plot the ventilation commands that have been used.

        Attributes
        ----------
        all_traces : bool
            plot all actions
        """
        fig = manage_events.plot_ventilation_drive(
            self.ventil_drive_df, self.param, all_traces
        )
        fig.show()
        return fig

    def plot_events(
        self, todrop: Optional[list[str]] = None, dtime: bool = False
    ) -> plt.Figure:
        """
        Plot the events as a time display, dtime allow dtime use.

        Parameters
        ----------
        todrop : list, optional (default is None)
            a list of events to drop
        dtime : bool, optional (default is False)
            plot using datetime (instead of elapsed time)

        Returns
        -------
        plt.Figure

        """
        # TODO : add exclusion list
        fig = manage_events.plot_events(self.dt_events_df, self.param, todrop, dtime)
        return fig

    def export_taph_events(self, save_to_file: bool = False) -> None:
        """
        Export in a txt files all the events (paths:~/temp/events.txt).

        Parameters
        ----------
        save_to_file : bool, optional (default is False)
            save the txt file

        Returns
        -------
        None
        """
        if save_to_file:
            filename = os.path.expanduser(os.path.join("~", "temp", "events.txt"))
            with open(filename, "w", encoding="utf-8") as file:
                for i, line in enumerate(self.data.events.dropna()):
                    file.write(f"{'-'*10} \n")
                    for item in line.split("\r\n"):
                        file.write(f"{i} {item}, \n")
            print(f"saved taph events to {filename}")
        else:
            for i, line in enumerate(self.data.events.dropna()):
                print("-" * 10)
                for item in line.split("\r\n"):
                    print(i, item)

    def shift_datetime(self, minutes: int) -> None:
        """
        Shift the recording datetime.

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

    def shift_etime(self, minutes: int) -> None:
        """
        Shift the elapsed time.

        Parameters
        ----------
        minutes : int
            the minutes to add to the elapsed time.

        Returns
        -------
        None.

        """
        ltt.shift_elapsed_time(self.data, minutes)

    def sync_etime(self, datetime0: datetime) -> None:
        """
        Shift the elapsed time based a 'zero' datetime.datetime.

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
