#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main script/module to load and display an anesthesia record

can be runned as a script::
    python record_main.py

or imported as a package::

    import anesplot.record_main as rec
    %gui qt5 (required only to use the dialogs if using spyder)

    # objects:
    mtrends = rec.MonitorTrend()
    waves = rec.MonitorWave(rec.trendname_to_wavename(mtrends.filename))
    ttrends = rec.TaphTtrend()

    # use methods and or attributes:
    mtrends.show_graphs() -> clinical debrief selection
    waves.plot_wave() -> select one or two waves to plot

    ...

----
nb to work within spyder : move inside anestplot (>> cd anesplot)

"""

import os
import sys
from importlib import reload
import faulthandler
from datetime import datetime

import numpy as np
import pandas as pd
import pyperclip

import matplotlib

matplotlib.use("Qt5Agg")  # NB use automatic for updating
import matplotlib.pyplot as plt
from matplotlib import rcParams
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QWidget

from config.load_recordrc import build_paths

paths = build_paths()


# requires to have '.../anesthPlot' in the path
import loadrec
from loadrec import loadmonitor_trendrecord as lmt
from loadrec import loadmonitor_waverecord as lmw
from loadrec import loadtaph_trendrecord as ltt
from loadrec import loadtelevet as ltv
import plot.trend_plot as tplot
import plot.wave_plot as wplot

from anesplot.guides.choose_guide import get_guide

import treatrec.clean_data as clean
import treatrec

import anesplot.treatrec.wave_func as wf

# import anesplot.treatrec as treat

# to have the display beginning from 0
rcParams["axes.xmargin"] = 0
rcParams["axes.ymargin"] = 0

faulthandler.enable()
APP = QApplication(sys.argv)


def get_basic_debrief_commands():
    """copy in clipboard the usual commands to build a debrief"""
    lines = [
        "mtrends = rec.MonitorTrend()",
        "mwaves = rec.MonitorWave(rec.trendname_to_wavename(mtrends.filename))",
        "ttrends = rec.TaphTrend(monitorname = mtrends.filename)",
    ]
    print("basic debrief commands are in the clipboard")
    return pyperclip.copy(" \n".join(lines))


def choosefile_gui(dirname: str = None) -> str:
    """Select a file via a dialog and return the (full) filename.

    Parameters
    ----------
    dirname : str, optional (default is None)
        DESCRIPTION. location to place the gui ('generally paths['data']) else home

    Returns
    -------
    fname[0] : str
        DESCRIPTION. : full name of the selected file

    """
    global APP

    if dirname is None:
        dirname = (
            "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onPanelPcRecorded"
        )
    ##########
    # print("define widget")
    # wid = QWidget()
    # print("show command")
    # wid.show()
    # print("define options")
    # options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    print("define QFiledialog")
    fname = QFileDialog.getOpenFileName(
        None, "Select a file...", dirname, filter="All files (*)"
    )
    print("return")
    if isinstance(fname, tuple):
        return fname[0]
    return str(fname)


def trendname_to_wavename(name: str) -> str:
    """just compute the supposed (full)name"""
    return name.split(".")[0] + "Wave.csv"


def select_type(question: str = None, items: list = None, num: int = 0) -> str:
    """
    display a pulldown menu to choose the kind of recording

    Parameters
    ----------
    question : str, optional
        The question that APPears in the dialog (default is None).
    items : list, optional
        the list of all items in the pulldown menu. (default is None).
    num : int, optional
        number in the list the pointer will be one. The default is 0.

    Returns
    -------
    str
        kind of recording in [monitorTrend, monitorWave, taphTrend, telvet].

    """

    if items is None:
        items = ["monitorTrend", "monitorWave", "taphTrend", "telVet"]
    if question is None:
        question = "choose kind of file"
    global APP
    #    APP = QApplication(sys.argv)
    widg = QWidget()
    kind, ok_pressed = QInputDialog.getItem(widg, "select", question, items, num, False)
    if ok_pressed and kind:
        selection = kind
    else:
        selection = None
    return selection


def select_wave_to_plot(waves: list, num=1) -> str:
    """
    select the wave trace to plot

    Parameters
    ----------
    waves : list
        list of available waves traces
    num : TYPE, optional
        index of the waves in the plot (1 or 2)
    Returns
    -------
    str
        wave name
    """

    global APP
    if num == 1:
        question = "choose first wave"
    if num == 2:
        question = "do you want a second one ?"
    #    APP = QApplication(sys.argv)
    widg = QWidget()
    wave, ok_pressed = QInputDialog.getItem(widg, "select", question, waves, 0, False)
    if ok_pressed and wave:
        selection = wave
    else:
        selection = None
    return selection


def plot_trenddata(datadf: pd.DataFrame, header: dict, param_dico: dict) -> dict:
    """
    generate a series of plots for anesthesia debriefing purposes

    Parameters
    ----------
    datadf : pd.DataFrame
        recorded data (MonitorTrend.data or TaphTrend.data).
    header : dict
        recording parameters (MonitorTrend.header or TaphTrend.header).
    param_dico : dict
        plotting parameters (MonitorTrend.param or TaphTrend.param).

    Returns
    -------
    dict
        afig_dico : {names:fig_obj} of displayed figures

    """

    # clean the data for taph monitoring
    if param_dico["source"] == "taphTrend":
        if "co2exp" in datadf.columns.values:
            datadf.loc[datadf["co2exp"] < 20, "co2exp"] = np.NaN
        # test ip1m
        if ("ip1m" in datadf.columns) and not datadf.ip1m.isnull().all():
            datadf.loc[datadf["ip1m"] < 20, "ip1m"] = np.NaN
        else:
            print("no pressure tdata recorded")
    afig_list = []
    print("building figures")
    # plotting
    plot_func_list = [
        tplot.ventil,
        tplot.co2o2,
        tplot.co2iso,
        tplot.cardiovasc,
        tplot.hist_co2_iso,
        tplot.hist_cardio,
    ]
    if param_dico["source"] == "taphTrend":
        plot_func_list.insert(0, tplot.sat_hr)
    for func in plot_func_list:
        afig_list.append(func(datadf, param_dico))

    if header:
        afig_list.append(tplot.plot_header(header, param_dico))
    print("plt.show")
    plt.show()
    names = [st.__name__ for st in plot_func_list]
    if header:
        names.append("header")
    fig_dico = dict(zip(names, afig_list))
    return fig_dico


class _Waves:
    """the base object to store the records."""

    def __init__(self):
        """
        :param filename: DESCRIPTION, defaults to None
        :type filename: str, optional
        :return: basic class for the records
        :rtype: wave object

        """
        self.data = None
        self.header = None
        self.param = dict(
            xmin=None,
            xmax=None,
            ymin=0,
            ymax=None,
            path=paths.get("sFig", "~"),
            unit="min",
            save=False,
            memo=False,
            file=None,
            source=None,
            sampling_freq=None,
            dtime=True,
        )


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
        fig_dico = plot_trenddata(self.data, self.header, self.param)
        return fig_dico


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
            filename = lmt.choosefile_gui(paths["mon_data"])
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

    def extract_events(self):
        """decode the taph messages, build events, actions and ventil_drive"""
        dt_events_df = treatrec.manage_events.build_event_dataframe(self.data)
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
        ltt.shift_datetime(self.data, minutes)

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


# ++++++++
class _FastWave(_Waves):
    """class for Fastwaves = continuous recordings."""

    # def __init__(self, filename=None):
    #     super().__init__(filename)
    def __init__(self):
        super().__init__()
        self.filename = None
        self.trace_list = None
        self.fig = None
        self.roi = None

    def filter_ekg(self):
        """filter the ekg trace -> build 'ekgMovAvg' & 'ekgLowPass'"""
        datadf = self.data
        samplingfreq = self.param["sampling_freq"]
        if "wekg" in datadf.columns:
            item = "wekg"
        elif "d2" in datadf.columns:
            item = "d2"
        else:
            print("no ekg trace in the data")
            return
        # print("-" * 10, "filtering : builded 'ekgMovAvg' ")
        # df["ekgMovAvg"] = wf.rol_mean(df[item], fs)
        print(f"{'-' * 10} filtering : builded 'ekgLowPass' ")
        datadf["ekgLowPass"] = wf.fix_baseline_wander(datadf[item], samplingfreq)

    def plot_wave(self, traces_list: list = None):
        """
        simple choose and plot for a wave

        Parameters
        ----------
        traces_list : list, optional (default is None)
            list of waves to plot (max=2)
            if none -> open a dialog to choose column names.

        Returns
        -------
            fig : pyplot.figure
            lines : [line2D object]
            traces_list : [name of the traces]

        """
        if self.data.empty:
            fig = None
            lines = None
            traces_list = None
            print("there are no data to plot")
        else:
            print(f"{'-' * 20} started FastWave plot_wave)")
            print(f"{'-' * 10}> choose the wave(s)")
            cols = [w for w in self.data.columns if w[0] in ["i", "r", "w"]]
            if traces_list is None:
                traces_list = []
                # trace = select_type(question='choose wave', items=cols)
                for num in [1, 2]:
                    trace = select_wave_to_plot(waves=cols, num=num)
                    if trace is not None:
                        traces_list.append(trace)
            if traces_list:
                print("call wplot.plot_wave")
                fig, lines = wplot.plot_wave(
                    self.data, keys=traces_list, param=self.param
                )
                print("returned from wplot.plot_wave")
                self.trace_list = traces_list
                # pyperclip.copy(str(traces_list))
                plt.show()  # required to display the plot before exiting
            else:
                self.trace_list = None
                fig = None
                lines = None
            self.fig = fig
            print(f"{'-' * 20} ended FastWave plot_wave")
        return fig, lines, traces_list

    def save_roi(self, erase: bool = False) -> dict:
        """
        define a Region Of Interest (roi).

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
        elif self.fig:
            # roidict = wplot.get_roi(self)
            roidict = wplot.get_roi(self.fig, self.data, self.param)
            roidict.update({"traces": self.trace_list, "fig": self.fig})
        else:
            print("no fig attribute, please use plot_wave() method to build one")
            roidict = {}

        self.roi = roidict
        return roidict

    def animate_fig(
        self,
        speed: int = 1,
        save: bool = False,
        savename: str = "video",
        savedir: str = "~",
    ):
        """
        build a video the previous builded figure
        NB requires :
            the .fig attribute (builded through .plot_wave())
            and the .roi attribute (builded through .define_a_roi())

        Parameters
        ----------
        speed : int, optional
            speed of the video (defaults is 1).
        save : bool, optional
            decide to save (default is False).
        savename : str, optional
            name of the video (default is "video").
        savedir : str, optional
            Path of the save folder (default is "~").

        Returns
        -------
        None.

        """

        if self.roi:
            wplot.create_video(
                self.data,
                self.param,
                self.roi,
                speed=speed,
                save=save,
                savename=savename,
                savedir="~",
            )
            # wplot.create_video(
            #     self, speed=speed, save=save, savename=savename, savedir="~"
            # )
        else:
            print("no roi attribute, please use record_roi() to build one")

    def plot_systolic_variation(self):
        "plot the systolic variation"
        if self.roi:
            wplot.plot_systolic_pressure_variation(self)
        else:
            print("please define a ROI using mwave.save_a_roi")


class TelevetWave(_FastWave):
    """
    class to organise teleVet recordings transformed to csv files.

    input:
        filename : str (fullpath, default:None)
    """

    # def __init__(self, filename=None):
    def __init__(self, filename=None):
        super().__init__()
        if filename is None:
            dir_path = paths.get("telv_data")
            filename = ltv.choosefile_gui(dir_path)
        self.filename = filename
        data = ltv.loadtelevet(filename)
        self.data = data
        # self.source = "teleVet"
        self.param["source"] = "televet"
        self.param["filename"] = filename
        self.param["file"] = os.path.basename(filename)
        sampling_freq = data.index.max() / data.sec.iloc[-1]
        self.param["sampling_freq"] = sampling_freq


class MonitorWave(_FastWave):
    """class to organise monitorWave recordings.

        input : filename = path to file
        load = boolean to load data (default is True)

    attibutes ... FILLME


    methods ... FILLME
    """

    def __init__(self, filename: str = None, load: bool = True):
        super().__init__()
        if filename is None:
            dir_path = paths.get("mon_data")
            filename = lmw.choosefile_gui(dir_path)
        self.filename = filename
        self.param["filename"] = filename
        self.param["file"] = os.path.basename(filename)
        header = lmw.loadmonitor_waveheader(filename)
        self.header = header
        if load and bool(header):
            self.data = lmw.loadmonitor_wavedata(filename)
        else:
            print(f"{'-'*5} MonitorWave: didn't load the data ({load=})")
            self.data = pd.DataFrame()
        self.param["source"] = "monitorWave"
        self.param["sampling_freq"] = float(header.get("Data Rate (ms)", 0)) * 60 / 1000
        # usually 300 Hz


def main(file_name: str = None):
    """
    main script called from command line
    call : "python record_main.py"
    call a GUI, load recording and display a series of plt.figure
    NB filename will be placed in the clipboard

    Parameters
    ----------
    file_name : str, optional
        recordfile fullname (default is None).

    Returns
    -------
    None.

    """
    # os.chdir(paths.get("recordMain", os.path.expanduser('~')))
    print(f"backEnd= {plt.get_backend()}")  # required ?
    print("start QtApp")
    global APP
    # APP = QApplication(sys.argv)
    APP.setQuitOnLastWindowClosed(True)

    # choose file and indicate the source
    print("select the file containing the data")
    print(f"file_name is {file_name}")
    if file_name is None:
        file_name = choosefile_gui(paths["data"])
    kinds = ["monitorTrend", "monitorWave", "taphTrend", "telVet"]
    # select base index in the scroll down
    num = 0
    if "Wave" in file_name:
        num = 1
    if not os.path.basename(file_name).startswith("M"):
        num = 2
    source = select_type(question="choose kind of file", items=kinds, num=num)

    if not os.path.isfile(file_name):
        print("this is not a file")
    elif source == "telVet":
        telvet = TelevetWave(file_name)
        telvet.plot_wave()
    elif source == "monitorTrend":
        monitor_trend = MonitorTrend(file_name)
        monitor_trend.show_graphs()
    elif source == "monitorWave":
        monitor_wave = MonitorWave(file_name)
        fig, *_ = monitor_wave.plot_wave()
    elif source == "taphTrend":
        taph_trend = TaphTrend(file_name)
        taph_trend.show_graphs()
    else:
        print("this is not a recognized recording")

    pyperclip.copy(file_name)
    plt.show()


# %%
if __name__ == "__main__":
    IN_NAME = None
    # check if a filename was provided from terminal call
    print(sys.argv)

    if len(sys.argv) > 1:
        provided_name = sys.argv[1]
        if os.path.isfile(provided_name):
            IN_NAME = provided_name
        else:
            print("the provided filename is not valid")
    main(IN_NAME)
