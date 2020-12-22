#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main program to load and display an anesthesia record file

"""
# print('-'*10)
# print('this is {} file and __name__ is {}'.format('record_main', __name__))
# print('this is {} file and __package__ is {}'.format('record_main', __package__))
# print('-'*10)


import gc
import os
import sys
from importlib import reload

import numpy as np
import pandas as pd
import pyperclip

import matplotlib
matplotlib.use('Qt5Agg')  #NB use automatic for updating
import matplotlib.pyplot as plt
#from socket import gethostname
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QWidget

# to have the display beginning from 0
from pylab import rcParams
rcParams['axes.xmargin'] = 0
rcParams['axes.ymargin'] = 0

from anesplot.config.load_recordRc import build_paths
paths = build_paths()
#paths = load_recordRc.paths

from anesplot.loadrec import explore
from anesplot.loadrec import loadmonitor_trendrecord as lmt
from anesplot.loadrec import loadmonitor_waverecord as lmw
from anesplot.loadrec import loadtaph_trendrecord as ltt
from anesplot.loadrec import loadtelevet as ltv
from anesplot.plot import trend_plot as tplot
from anesplot.plot import wave_plot as wplot
from anesplot.treatrec import clean_data as clean
from anesplot.treatrec import wave_func as wf

#

def choosefile_gui(dir_path=None):
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
    if dir_path is None:
        dir_path = os.path.expanduser('~')
    caption='choose a recording'
    options = QFileDialog.Options()
# to be able to see the caption, but impose to work with the mouse
#    options |= QFileDialog.DontUseNativeDialog
    fname = QFileDialog.getOpenFileName(caption=caption,
                                        directory=dir_path, filter='*.csv',
                                        options=options)
#    fname = QFileDialog.getOpenfilename(caption=caption,
#                                        directory=direct, filter='*.csv')
    #TODO : be sure to be able to see the caption
    return fname[0]

def trendname_to_wavename(name):
    """ just compute the supposed name """
    return name.split('.')[0] + 'Wave.csv'


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
        question = 'choose kind of file'
    qw = QWidget()
    kind, ok_pressed = QInputDialog.getItem(qw, 'select',
                                            question, items, num, False)
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
    if num == 1:
        question = 'choose first wave'
    if num == 2: 
        question = 'do you want a second one ?'
    qw = QWidget()
    wave, ok_pressed = QInputDialog.getItem(qw, 'select',
                                            question, waves, 0, False)
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
    dico = dict(item = 1,
                xmin = None,
                xmax = None,
                ymin = 0,
                ymax = None,
                path = pathdico.get('sFig', '~'),
                unit = 'min',
                save = False,
                memo = False,
                file = file,
                source = asource)
    return dico

#%
def check():
    """ print the loaded recordings """
    #TODO : doesn't work ?? to be adjusted
    imported = {}
    for item in gc.get_objects():
        if isinstance(item, MonitorTrend):
            alist = [k for k, v in locals().items() if v is item]
            imported[alist[0]] = item.file
            print(alist)
        elif isinstance(item, MonitorWave):
            alist = [k for k, v in locals().items() if v is item]
            imported[alist[0]] = item.file
            print(alist)
    for key, val in imported.items():
        print(key, '<->', val)


# def list_loaded():
#     """
#     list the loaded files
#     return a dictionary recordObj : file
#     """
#     recorded = {}
#     try:
#         taphTrend
#     except NameError:
#         pass
#     else:
#         recorded['taphTrend'] = taphTrend
#     try:
#         monitorTrend
#     except NameError:
#         pass
#     else:
#         recorded['monitorTrend'] = monitorTrend
#     try:
#         monitorWave
#     except NameError:
#         pass
#     else:
#         recorded['monitorWave'] = monitorWave
#     try:
#         telvet
#     except NameError:
#         pass
#     else:
#         recorded['telvet'] = telvet
#     print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
#     print('records loaded:')
#     for key in records:
#         print(key, records[key].file.split('.')[0])
#     print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
#     return recorded


def plot_trenddata(file, df, header, param_dico):
    """clinical main plots of a trend recordings

    parameters
    ----
    file : str
        the filename
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
    if param_dico['source'] == 'taphTrend':
        if 'co2exp' in df.columns.values:
            df.loc[df['co2exp'] < 20, 'co2exp'] = np.NaN
        if ('ip1m' in df.columns.values) and not df.ip1m.isnull().all():
            df.loc[df['ip1m'] < 20, 'ip1m'] = np.NaN
        else:
            print('no pressure tdata recorded')
    afig_list = []
    print('build figs')
    #plotting
    plot_func_list = (tplot.ventil, tplot.co2o2, tplot.co2iso, tplot.cardiovasc,
                      tplot.hist_co2_iso, tplot.hist_cardio)
    for func in plot_func_list:
        afig_list.append(func(df.set_index('eTimeMin'), param_dico))
    afig_list.append(tplot.plot_header(header, param_dico))
    # for fig in afig_list:
    #     if fig:                 # test if figure is present
    #         fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
    #         fig.text(0.01, 0.01, file, ha='left', va='bottom', alpha=0.4)
    print('plt.show')
    plt.show()
    names = [st.__name__ for st in plot_func_list]
    names.append('header')
    fig_dico = dict(zip(names, afig_list))
    return fig_dico


def plot_monitorwave_data(headdf, wavedf):
    """
    not implemented for the moment
    """
#TODO : build a GUI to choose a trace to plot ? or implement that in the class ?
    for item in ['Date', 'Patient Name', 'Patient ID']:
        print(item, ' : ', headdf[item])


##### NB use fig = plot... to obtain a reference to the plot
    # and then axList = fig.axes
    # use axes in this list to change the scales
#

class Waves():
    """
    base class for the records

    """
    def __init__(self, filename=None):
        if filename is None:
            filename = choosefile_gui(paths['data'])
        self.filename = filename
        self.file = os.path.basename(filename)
        self.fs = None
        self.source = None
        self.data = None
        self.header = None
        self.param = dict(xmin=None, xmax=None,
                          ymin=0, ymax=None,
                          path=paths['sFig'], unit='min',
                          save=False, memo=False,
                          file=os.path.basename(filename),
                          source=None, fs=None)

#+++++++
class SlowWave(Waves):
    """
    class for slowWaves = trends

    attributes:
    ----
        file : str
            short name
        filename : str
            long name

    methods
    ----
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
        df = clean.clean_trenddata(self.data)
        return df
    def show_graphs(self):
        """ basic clinical plots """
        fig_dico = plot_trenddata(self.file, self.data, self.header, self.param)
        return fig_dico


class MonitorTrend(SlowWave):
    """ monitor trends recordings:

        input = filename : path to file
        load = boolean to load data (default is True)

    attibutes:
    ----
        file : str
            short name
        filename : str
            long name
        header : dict
            record parameters
        source : str
            recording apparatus (default = 'monitor')
        fs : float
            sampling rate
        param : dict
            display parameters

    methods (inherited)
    ----
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
        if self.header:
            if self.load:
                self.data = lmt.loadmonitor_trenddata(self.filename, self.header)
            self.source = 'monitor'
            self.fs = self.header.get('Sampling Rate', None)
            self.param['source'] = 'monitorTrend'
            #self.param'file' : os.path.basename(filename)}

class TaphTrend(SlowWave):
    """ taphonius trends recordings

    input  ... FILLME

    attributes ... FILLME


    """
    def __init__(self, filename=None):
        super().__init__(filename)
        self.data = ltt.loadtaph_trenddata(self.filename)
        self.source = 'taphTrend'
        self.header = self.load_header()
    def load_header(self):
        """ load the header -> pandas.dataframe """
        headername = choosefile_gui(dir_path=os.path.dirname(self.filename))
        if headername:
            header = ltt.loadtaph_patientfile(headername)
        else:
            header = None
        return header
    def extract_taph_events(self):
        """ extract Taph events

        parameters
        ----
        data : pandas dataframe
            record df form taphonius recording)

        return
        ----
        eventdf pandas dataframe
            events dataframe
        """
        eventdf = self.data[['events', 'datetime']].dropna()
        # remove time, keep event
        eventdf.events = eventdf.events.apply(lambda st: st.split('-')[1])
        return eventdf

#++++++++
class FastWave(Waves):
    """ class for Fastwaves = continuous recordings



    """
    def __init__(self, filename=None):
        super().__init__(filename)
    def plot_wave(self):
        """
20        simple choose and plot for a wave
        """
        cols = [w for w in self.data.columns if w[0] == 'w']
        traces = []
        # trace = select_type(question='choose wave', items=cols)
        trace = select_wave(waves=cols, num=1)
        traces.append(trace)
        trace = select_wave(waves=cols, num=2)
        traces.append(trace)
        if traces:
            # fig, _ = wf.plot_wave(self.data, keys=[trace], mini=None, maxi=None)
            fig, _ = wplot.plot_wave(self.data, keys=traces, param=self.param)
            fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
            fig.text(0.01, 0.01, self.file, ha='left', va='bottom', alpha=0.4)
            self.trace = trace
            self.fig = fig
            plt.show()
            return fig
        else:
            self.trace = None
            self.fig = None

    def define_a_roi(self):
        """
        define a ROI
        """
        df = self.data
        if self.fig:
            ax = self.fig.get_axes()[0]
            #point Value
            lims = ax.get_xlim() # pt values
            limpt = (int(lims[0]), int(lims[1]))
            #sec value
            limsec = (df.sec.loc[limpt[0]], df.sec.loc[limpt[1]])
            limdatetime = (df.datetime.loc[limpt[0]], df.datetime.loc[limpt[1]])
            roidict = {'sec': limsec,
                       'pt': limpt,
                       'dt': limdatetime
                      }
            self.roi = roidict

class TelevetWave(FastWave):
    """
    class to organise teleVet recordings transformed to csv files
    """
    def __init__(self, filename=None):
        super().__init__(filename)
        self.data = ltv.loadtelevet(filename)
        self.source = 'teleVet'
        self.fs = self.data.index.max() / self.data.timeS.iloc[-1]

class MonitorWave(FastWave):
    """
    class to organise monitorWave recordings
        input : filename = path to file
        load = boolean to load data (default is True)

    attibutes ... FILLME


    methods ... FILLME
    """
    def __init__(self, filename=None, load=True):
        super().__init__(filename)
        header = lmw.loadmonitor_waveheader(filename)
        self.header = dict(zip(header[0], header[1]))
        self.load = load
        if self.load:
            data = lmw.loadmonitor_wavedata(filename)
            self.data = data
        self.source = 'monitorWave'
        self.fs = 300
        self.param['fs'] = 300


def main():
    os.chdir(paths['recordMain'])
    print('backEnd= ', plt.get_backend())   # required ?
    print('start QtApp')
    try:
        app
    except NameError:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
    # list of loaded records
    try:
        records
    except NameError:
        records = {}
    # choose file and indicate the source
    print('select the file containing the data')
    file_name = choosefile_gui(paths['data'])
    kinds = ["monitorTrend", "monitorWave", "taphTrend", "telVet"]
    # select base index in the scoll down
    num = 0
    if "Wave" in file_name:
        num = 1
    if not os.path.basename(file_name).startswith('M'):
        num = 2
    source = select_type(question="choose kind of file",
                         items=kinds, num=num)
    # general parameters
    params = build_param_dico(file=os.path.basename(file_name),
                          asource=source)
    if not os.path.isfile(file_name):
        print('this is not a file')
        return
    if source == 'telVet':
        telvet = TelevetWave(file_name)
        params['fs'] = 500
        params['kind'] = 'telVet'
        telvet.param = params
        telvet.plot_wave()
    elif source == 'monitorTrend':
        monitorTrend = MonitorTrend(file_name)
        params['t_fs'] = monitorTrend.header.get('Sampling Rate')/60
        monitorTrend.param = params
        if monitorTrend.data is not None:
            fig_list = monitorTrend.show_graphs()
    elif source == 'monitorWave':
        monitorWave = MonitorWave(file_name)
        params['fs'] = float(monitorWave.header['Data Rate (ms)'])*60/1000
        params['kind'] = 'as3'
        monitorWave.param = params
        monitorWave.plot_wave()
    elif source == 'taphTrend':
        taphTrend = TaphTrend(file_name)
        taphTrend.param = params
        # tdata= clean.clean_trendData(tdata)
        fig_list = taphTrend.show_graphs()
    else:
        print('this is not recognized recording')
    # records = list_loaded()
    plt.show()
    try:
        app
    except NameError:
        app.exec_()


#%%
if __name__ == '__main__':
    main()
