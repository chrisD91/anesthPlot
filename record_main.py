#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%reset -f      # NB if uncomented if prevent the use from the terminal !!
"""
main program to load and display an anesthesia record file

"""

import os
import sys
import pyperclip
import numpy as np
import pandas as pd
from importlib import reload
import matplotlib
matplotlib.use('Qt5Agg')  #NB use automatic for updating
import matplotlib.pyplot as plt
#from socket import gethostname
from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5.QtWidgets import QInputDialog, QWidget
# to have the display beginning from 0
from pylab import rcParams
rcParams['axes.xmargin'] = 0
rcParams['axes.ymargin'] = 0

#print(dir())
#TODO test to change all to absolute import
from anesthPlot.config import load_recordRc
paths = load_recordRc.paths
#import config.load_recordRc
#paths = config.load_recordRc.paths
#import utils
#import bloodGases2 as bg
from anesthPlot.plot import trend_plot as tplot
#from anesthPlot.plot import trend_plot as tplot
from anesthPlot.plot import wave_plot as wplot
from anesthPlot.treatrec import wave_func as wf
from anesthPlot.treatrec import clean_data as clean
# ##import bloodGases2 as bg

# from loadrec import loadmonitor_trendrecord, loadmonitor_waverecord
# from loadrec import loadtaph_trendrecord
#from loadrec import explore
# import plot
# import treatrec as treat

from anesthPlot.loadrec import loadmonitor_trendrecord as lmt
from anesthPlot.loadrec  import loadmonitor_waverecord as lmw
from anesthPlot.loadrec  import loadtaph_trendrecord as ltt
from anesthPlot.loadrec  import loadtelevet as ltv
from anesthPlot.loadrec  import explore as explore
#

def choosefile_gui(dir_path=None, caption='choose a recording'):
    """
    Select a file via a dialog and return the (full) filename.
    input : dir_path = location ('generally paths['data']) else home
    """
    if not dir_path:
        dir_path = os.path.expanduser('~')
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
    return name.split('.')[0] + 'Wave.csv'



def select_type(caption=None, items=None):
    """
    select the recording type:
       return : monitorTrend, monitorWave, taphTrend or telvet
       """
#    if kind=='record':
#        caption = "choose kind of file"
#        items = ("monitorTrend","monitorWave","taphTrend", "telVet")
#    elif kind
#    item, ok_pressed = QInputDialog.getItem(caption = \
# "choose kind of file","kind:", items, 1, False)
    qw = QWidget()
    item, ok_pressed = QInputDialog.getItem(qw, caption, "kind:", items, 0, False)
    if ok_pressed and item:
        return item

def build_param_dico(file='', source=''):
    """initialise a dict save parameters  ----> TODO see min vs sec
    """
    dico = {'item': 1,
            'xmin': None,
            'xmax': None,
            'ymin': 0,
            'ymax': None,
            'path': paths['sFig'],
            'unit': 'min',
            'save': False,
            'memo': False,
            'file': file,
            'source': source}
    return dico

import gc

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


def list_loaded():
    """
    list the loaded files
    return a dictionary recordObj : file
    """
    records = {}
    try:
        taphTrend
    except NameError:
        pass
    else:
        records['taphTrend'] = taphTrend
    try:
        monitorTrend
    except NameError:
        pass
    else:
        records['monitorTrend'] = monitorTrend
    try:
        monitorWave
    except NameError:
        pass
    else:
        records['monitorWave'] = monitorWave
    try:
        telvet
    except NameError:
        pass
    else:
        records['telvet'] = telvet
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('records loaded:')
    for key in records:
        print(key, records[key].file.split('.')[0])
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    return records

def plot_trenddata(file, df, header, param_dico):
    """
    plot the trend recordings
        input : file, df=pdDataframe, header=dictionary, params=dict,
            params=dictionary
        output : matplotlib plots
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
                      tplot.hist_co2_iso, tplot.hist_pam)
    for func in plot_func_list:
        afig_list.append(func(df.set_index('eTimeMin'), param_dico))
    afig_list.append(tplot.plot_header(header, param_dico))
    for fig in afig_list:
        if fig:                 # test if figure is present
            fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
            fig.text(0.01, 0.01, file, ha='left', va='bottom', alpha=0.4)
    print('plt.show')
    plt.show()
    return afig_list


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
        if not filename:
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
    """
    def __init__(self, filename):
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
        fig_list = plot_trenddata(self.file, self.data, self.header, self.param)
        return fig_list

class MonitorTrend(SlowWave):
    """ monitor trends recordings"""
    def __init__(self, filename):
        super().__init__(filename)
        self.header = lmt.loadmonitor_trendheader(self.filename)
        if self.header:
            self.data = lmt.loadmonitor_trenddata(self.filename, self.header)
            self.source = 'monitor'
            self.fs = self.header['Sampling Rate']
            self.param['source'] = 'monitorTrend'
            #self.param'file' : os.path.basename(filename)}

class TaphTrend(SlowWave):
    """ taphonius trends recordings"""
    def __init__(self, filename):
        super().__init__(filename)
        self.data = ltt.loadtaph_trenddata(self.filename)
        self.source = 'taphTrend'
        self.header = self.load_header()
    def load_header(self):
        """ load the header -> pandas.dataframe """
        headername = choosefile_gui(dir_path=os.path.dirname(filename),
                                    caption='choose Patient Data')
        if headername != '':
            header = ltt.loadtaph_patientfile(headername)
        else:
            header = ''
        return header
    def extract_taph_events(self):
        """
        extract Taph events
        input = tdata (record df form taphonius recording)
        output : dataFrame
        """
        eventdf = self.data[['events', 'datetime']].dropna()
        # remove time, keep event
        eventdf.events = eventdf.events.apply(lambda st: st.split('-')[1])
        return eventdf

#++++++++
class FastWave(Waves):
    """
    class for Fastwaves = continuous recordings
    """
    def __init__(self, filename):
        super().__init__(filename)
    def plot_wave(self):
        """
20        simple choose and plot for a wave
        """
        cols = [w for w in self.data.columns if w[0] == 'w']
        trace = select_type(caption='choose wave', items=cols)
        if trace:
#            fig, _ = wf.plot_wave(self.data, keys=[trace], mini=None, maxi=None)
            fig, _ = wplot.plot_wave(self.data, keys=[trace], mini=None, maxi=None)
            fig.text(0.99, 0.01, 'anesthPlot', ha='right', va='bottom', alpha=0.4)
            fig.text(0.01, 0.01, self.file, ha='left', va='bottom', alpha=0.4)
            self.trace = trace
            self.fig = fig
            plt.show()
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
    def __init__(self, filename):
        super().__init__(filename)
        self.data = ltv.loadtelevet(filename)
        self.source = 'teleVet'
        self.fs = self.data.index.max() / self.data.timeS.iloc[-1]

class MonitorWave(FastWave):
    """
    class to organise monitorWave recordings
    """
    def __init__(self, filename):
        super().__init__(filename)
        header = lmw.loadmonitor_waveheader(filename)
        self.header = dict(zip(header[0], header[1]))
        data = lmw.loadmonitor_wavedata(filename)
        data = lmw.append_monitorwave_datetime(data)
        self.data = data
        self.source = 'monitorWave'
        self.fs = 300
        self.param['fs'] = 300

#%%
if __name__ == '__main__':
    #paths = build_paths()
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
    filename = choosefile_gui(paths['data'])
    source = select_type(caption="choose kind of file",
                         items=("monitorTrend", "monitorWave",
                                "taphTrend", "telVet"))
    # general parameters
    params = build_param_dico(file=os.path.basename(filename),
                              source=source)
# TODO check the validity of the file    email
    if source == 'telVet':
        telvet = TelevetWave(filename)
        params['fs'] = 500
        params['kind'] = 'telVet'
        telvet.param = params
        telvet.plot_wave()
    elif source == 'monitorTrend':
        monitorTrend = MonitorTrend(filename)
        monitorTrend.param = params
        if monitorTrend.data is not None:
            fig_list = monitorTrend.show_graphs()
    elif source == 'monitorWave':
        monitorWave = MonitorWave(filename)
        params['fs'] = float(monitorWave.header['Data Rate (ms)'])*60/1000
        params['kind'] = 'as3'
        monitorWave.param = params
        monitorWave.plot_wave()
    elif source == 'taphTrend':
        taphTrend = TaphTrend(filename)
        taphTrend.param = params
#        tdata= clean.clean_trendData(tdata)
        fig_list = taphTrend.show_graphs()
    else:
        print('this is not recognized recording')
    records = list_loaded()
    plt.show()
    try:
        app
    except NameError:
        app.exec_()
