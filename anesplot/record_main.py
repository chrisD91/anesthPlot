#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main script/module to load and display an anesthesia record

can be runned as a script::
    python record_main.py

or imported as a package::
    import anesplot.record_main as rec
    %gui qt5 (required only to use the dialogs if using spyder)
    trends = rec.MonitorTrend()
    waves = rec.MonitorWave(rec.trendname_to_wavename(trends.filename))
----
nb to work within spyder : move inside anestplot (>> cd anesplot)

"""

import os
import sys
from importlib import reload
import faulthandler

import numpy as np
import pandas as pd
import pyperclip

import matplotlib

matplotlib.use("Qt5Agg")  # NB use automatic for updating
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QWidget

# to have the display beginning from 0
from matplotlib import rcParams

rcParams["axes.xmargin"] = 0
rcParams["axes.ymargin"] = 0

# from anesplot.config.load_recordrc import build_paths
from config.load_recordrc import build_paths

paths = build_paths()

# requires to have '.../anesthPlot' in the path
# import anesplot.loadrec.loadmonitor_trendrecord as lmt

import loadrec.loadmonitor_trendrecord as lmt
import loadrec.loadmonitor_waverecord as lmw
import loadrec.loadtaph_trendrecord as ltt
import loadrec.loadtelevet as ltv
import plot.trend_plot as tplot
import plot.wave_plot as wplot

# import treatrec.clean_data as clean
import treatrec as treat

# import anesplot.treatrec.wave_func as wf
# import anesplot.treatrec as treat

faulthandler.enable()
app = QApplication(sys.argv)


def choosefile_gui(dirname=None):
    """Select a file via a dialog and return the (full) filename.

    parameters
    ----
    dir_path : str
        location to place the gui ('generally paths['data']) else home

    return
    ----
    fname[0] : str
        filename
    """
    global app

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


def trendname_to_wavename(name):
    """just compute the supposed name"""
    return name.split(".")[0] + "Wave.csv"


def select_type(question=None, items=None, num=0):
    """select the recording type:

    parameters
    ----

    return
    ----
    kind : str
        kind of recording in [monitorTrend, monitorWave, taphTrend, telvet]
    """
    if items is None:
        items = ("monitorTrend", "monitorWave", "taphTrend", "telVet")
    if question is None:
        question = "choose kind of file"
    global app
    #    app = QApplication(sys.argv)
    widg = QWidget()
    kind, ok_pressed = QInputDialog.getItem(widg, "select", question, items, num, False)
    if ok_pressed and kind:
        selection = kind
    else:
        selection = None
    return selection


def select_wave(waves, num=1):
    """select the recording type:

    parameters
    ----

    return
    ----
    kind : str
        kind of recording in [monitorTrend, monitorWave, taphTrend, telvet]
    """
    global app
    if num == 1:
        question = "choose first wave"
    if num == 2:
        question = "do you want a second one ?"
    #    app = QApplication(sys.argv)
    widg = QWidget()
    wave, ok_pressed = QInputDialog.getItem(widg, "select", question, waves, 0, False)
    if ok_pressed and wave:
        selection = wave
    else:
        selection = None
    return selection


def build_param_dico(file=None, asource=None, pathdico=paths):
    """initialise a dict save parameters  ----> TODO see min vs sec

    parameters
    ----
    file : str
        the recording filename
    source : str
        the origin of the recording
    return
    ----
    dico : dict
        a dictionary describing the situation
            [item, xmin, xmax, ymin, ymax, path, unit, save, memo, file, source]
    """
    dico = dict(
        item=1,
        xmin=None,
        xmax=None,
        ymin=0,
        ymax=None,
        path=pathdico.get("sFig", "~"),
        unit="min",
        save=False,
        memo=False,
        file=file,
        source=asource,
        dtime=True,
    )
    return dico


def plot_trenddata(datadf, header, param_dico):
    """clinical main plots of a trend recordings

    parameters
    df : pdDataframe
        recorded data (MonitorTrend.data)
    header : dict
        recording parameters (MonitorTrend.header)
    param_dico : dict
        plotting parameters (MonitorTrend.param)

    return
    ----
    afig_dico : dict of name:fig
    """
    # clean the data for taph monitoring
    if param_dico["source"] == "taphTrend":
        if "co2exp" in datadf.columns.values:
            datadf.loc[datadf["co2exp"] < 20, "co2exp"] = np.NaN
        if ("ip1m" in datadf.columns.values) and not datadf.ip1m.isnull().all():
            datadf.loc[datadf["ip1m"] < 20, "ip1m"] = np.NaN
        else:
            print("no pressure tdata recorded")
    afig_list = []
    print("building figures")
    # plotting
    plot_func_list = (
        tplot.ventil,
        tplot.co2o2,
        tplot.co2iso,
        tplot.cardiovasc,
        tplot.hist_co2_iso,
        tplot.hist_cardio,
    )
    for func in plot_func_list:
        # afig_list.append(func(df.set_index("eTimeMin"), param_dico))
        afig_list.append(func(datadf, param_dico))

    if header:
        afig_list.append(tplot.plot_header(header, param_dico))
    # for fig in afig_list:
    #     if fig:                 # test if figure is present
    #         fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
    #         fig.text(0.01, 0.01, file, ha='left', va='bottom', alpha=0.4)
    print("plt.show")
    plt.show()
    names = [st.__name__ for st in plot_func_list]
    if header:
        names.append("header")
    fig_dico = dict(zip(names, afig_list))
    return fig_dico


class _Waves:
    """the base object to store the records."""

    def __init__(self, filename=None):
        """
        :param filename: DESCRIPTION, defaults to None
        :type filename: str, optional
        :return: basic class for the records
        :rtype: wave object

        """
        if filename is None:
            filename = choosefile_gui(paths["data"])
        self.filename = filename
        self.file = os.path.basename(filename)
        self.sampling_freq = None
        self.source = None
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
            file=os.path.basename(filename),
            source=None,
            fs=None,
            dtime=True,
        )


# +++++++
class _SlowWave(_Waves):
    """class for slowWaves = trends

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

    def __init__(self, filename=None):
        super().__init__(filename)

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
    """monitor trends recordings:

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
        source : str
            recording apparatus (default = 'monitor')
        sampling_freq : float
            sampling frequency
        param : dict
            display parameters

    methods (inherited)
    -------------------
        clean_trend : external
            clean the data
        show_graphs : external
            plot clinical main plots
    """

    def __init__(self, filename=None, load=True):
        super().__init__(filename)
        self.header = lmt.loadmonitor_trendheader(self.filename)
        self.load = load
        # load if header is present & not data
        if self.header and self.load:
            if self.load:
                self.data = lmt.loadmonitor_trenddata(self.filename, self.header)
            self.source = "monitor"
            self.sampling_freq = self.header.get("Sampling Rate", None)
            self.param["source"] = "monitorTrend"
            # self.param'file' : os.path.basename(filename)}


class TaphTrend(_SlowWave):
    """taphonius trends recordings

    input  ... FILLME

    attributes ... FILLME


    """

    def __init__(self, filename=None):
        super().__init__(filename)
        self.data = ltt.loadtaph_trenddata(self.filename)
        self.source = "taphTrend"
        self.header = self.load_header(self.filename)
        self.actions = self.extract_taph_actions(self.data)

    def load_header(self, filename):
        """load the header
        input :
            use the filename to list the directory content
            and load the Patient.csv file
        output :
            header : pandas dataframe
        """
        dirname = os.path.dirname(filename)
        files = os.listdir(dirname)
        print("{} > taphTrend load header".format("-" * 20))
        print("{} files are present".format(len(files)))
        for file in files:
            print(file)
        try:
            file = [_ for _ in files if "Patient" in _][0]
            headername = os.path.join(dirname, file)
        except IndexError:
            headername = None
        # headername = choosefile_gui(dirname=os.path.dirname(self.filename))
        if headername:
            header = ltt.loadtaph_patientfile(headername)
            print("{} < loaded header ({})".format("-" * 20, file))
        else:
            header = None
        return header

    def extract_taph_actions(self, data):
        """extract Taph actions

        parameters
        ----------
        data : pandas dataframe
            record df form taphonius recording)

        return
        ------
        actiondf pandas dataframe
        """
        eventdf = data[["events", "datetime"]].dropna()
        eventdf = eventdf.set_index("datetime")
        eventdf.events = eventdf.events.apply(
            lambda st: [_.strip("[").strip("]") for _ in st.split("\r\n")]
        )
        error_messages, action_messages = treat.manage_events.extract_taphmessages(
            eventdf
        )
        events = treat.manage_events.extract_event(eventdf)
        actions = treat.manage_events.extract_actions(eventdf, action_messages)
        if actions:
            actiondf = treat.manage_events.build_dataframe(actions)
        else:
            actiondf = None
        # remove time, keep event
        #        eventdf.events = eventdf.events.apply(lambda st: st.split("-")[1])
        # TODO extract all the event in a column

        return actiondf


# ++++++++
class _FastWave(_Waves):
    """class for Fastwaves = continuous recordings."""

    def __init__(self, filename=None):
        super().__init__(filename)
        self.trace_list = None
        self.fig = None
        self.roi = None

    def plot_wave(self, traces_list=None, dtime=None):
        """
        simple choose and plot for a wave
        input = none -> GUI, or list of waves to plot (max=2)

        """
        if self.data.empty:
            fig = None
            lines = None
            traces_list = None
            print("there are no data to plot")
        else:
            print("*" * 20, "started FastWave plot_wave")
            cols = [w for w in self.data.columns if w[0] in ["i", "r", "w"]]
            if traces_list is None:
                traces_list = []
                # trace = select_type(question='choose wave', items=cols)
                for num in [1, 2]:
                    trace = select_wave(waves=cols, num=num)
                    if trace is not None:
                        traces_list.append(trace)
            if traces_list:
                fig, lines = wplot.plot_wave(
                    self.data, keys=traces_list, param=self.param
                )
                self.trace_list = traces_list
                pyperclip.copy(str(traces_list))
                plt.show()
            else:
                self.trace_list = None
                fig = None
                lines = None
            self.fig = fig
            print("*" * 20, "ended FastWave plot_wave")
        return fig, lines, traces_list

    def record_roi(self, erase=False):
        """define a Region Of Interest (roi).

        input : erase (boolean) default=False
        takes the figure attribute
        return a dictionary containing:
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
            roidict = wplot.get_roi(self)
            roidict.update({"traces": self.trace_list, "fig": self.fig})
        else:
            print("no fig attribute, please use plot_wave() method to build one")
            roidict = {}

        self.roi = roidict
        return roidict

    def animate_fig(self, speed=1, save=False, savedir="~"):
        """build a video the previous builded figure

        use .fig attribute (builded through .plot_wave())
        and .roi attribute (builded thourhg .define_a_roi())

        :param speed: speed of the video, defaults to 1
        :type speed: int, optional
        :param save: save or just display, defaults to False
        :type save: boolean, optional
        :param savedir: directory to save the animation, defaults to "~"
        :type savedir: str, optional
        :return: video file
        :rtype: mp4

        """
        if self.roi:
            wplot.create_video(self, speed=speed, save=save, savedir="~")
        else:
            print("no roi attribute, please use record_roi() to build one")


class TelevetWave(_FastWave):
    """class to organise teleVet recordings transformed to csv files."""

    def __init__(self, filename=None):
        super().__init__(filename)
        self.data = ltv.loadtelevet(filename)
        self.source = "teleVet"
        self.sampling_freq = self.data.index.max() / self.data.timeS.iloc[-1]


class MonitorWave(_FastWave):
    """class to organise monitorWave recordings.
        input : filename = path to file
        load = boolean to load data (default is True)

    attibutes ... FILLME


    methods ... FILLME
    """

    def __init__(self, filename=None, load=True):
        print("*" * 20, "started MonitorWave init process")
        # define filename -> self.filenamewa
        super().__init__(filename)
        # load header
        header_df = lmw.loadmonitor_waveheader(self.filename)
        header_df = pd.DataFrame(header_df)
        if not header_df.empty:
            self.header = dict(header_df.values)
        # load data
        self.load = load
        if load and not header_df.empty:
            data = lmw.loadmonitor_wavedata(filename=self.filename)
            self.data = data
        self.source = "monitorWave"
        self.sampling_freq = 300
        self.param["fs"] = 300
        print("*" * 20, "ended MonitorWave init process")


def main(file_name=None):
    """main script called from command line
    call : "python anesthPlot/anesplot/__main__.py"
    args : optional filename (fullname)

    return: set of plots for either monitorTrend, monitorWave oe televet recording
    """
    # os.chdir(paths.get("recordMain", os.path.expanduser('~')))
    print("backEnd= ", plt.get_backend())  # required ?
    print("start QtApp")
    global app
    # app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    fig_list = []
    # choose file and indicate the source
    print("select the file containing the data")
    print("file_name is {}".format(file_name))
    if file_name is None:
        file_name = choosefile_gui(paths["data"])
    pyperclip.copy(file_name)
    kinds = ["monitorTrend", "monitorWave", "taphTrend", "telVet"]
    # select base index in the scoll down
    num = 0
    if "Wave" in file_name:
        num = 1
    if not os.path.basename(file_name).startswith("M"):
        num = 2
    source = select_type(question="choose kind of file", items=kinds, num=num)
    # general parameters
    params = build_param_dico(file=os.path.basename(file_name), asource=source)
    if not os.path.isfile(file_name):
        print("this is not a file")
        return fig_list
    if source == "telVet":
        telvet = TelevetWave(file_name)
        params["fs"] = 500
        params["kind"] = "telVet"
        telvet.param = params
        telvet.plot_wave()
    elif source == "monitorTrend":
        monitor_trend = MonitorTrend(file_name)
        if monitor_trend.data.empty:
            print("empty recording")
            return fig_list
        if monitor_trend.header is None:
            print("empty header")
            return fig_list
        params["t_fs"] = monitor_trend.header.get("Sampling Rate") / 60
        monitor_trend.param = params
        if monitor_trend.data is not None:
            fig_list = monitor_trend.show_graphs()
    elif source == "monitorWave":
        monitor_wave = MonitorWave(file_name)
        params["fs"] = float(monitor_wave.header["Data Rate (ms)"]) * 60 / 1000
        params["kind"] = "as3"
        monitor_wave.param = params
        monitor_wave.plot_wave()
    elif source == "taphTrend":
        taph_trend = TaphTrend(file_name)
        taph_trend.param = params
        # tdata= clean.clean_trendData(tdata)
        fig_list = taph_trend.show_graphs()
    else:
        print("this is not recognized recording")
    plt.show()
    return fig_list


#%%
if __name__ == "__main__":
    # to work (on taphonius class)
    # >>
    file_name = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/ALEA_/Patients2016OCT06/Record22_31_18/SD2016OCT6-22_31_19.csv"
    file_name = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/Anonymous/Patients2021AUG10/Record13_36_34/SD2021AUG10-13_36_34.csv"
    in_name = file_name
    # <<
    in_name = None
    # check if a filename was provided from terminal call
    print(sys.argv)

    if len(sys.argv) > 1:
        provided_name = sys.argv[1]
        if os.path.isfile(provided_name):
            in_name = provided_name
        else:
            print("the provided filename is not valid")
    main(in_name)
