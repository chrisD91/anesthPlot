
# -*- coding: utf-8 -*-
#%reset -f      # NB if uncomented if prevent the use from the terminal !!
"""
main program to load and display an anesthesia record file

"""

import os
import sys
import yaml
import matplotlib
matplotlib.use('Qt5Agg')  #NB use automatic for updating
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#from socket import gethostname
from PyQt5.QtWidgets import QFileDialog, QApplication

from importlib import reload
import pyperclip
# to have the display beginning from 0
from pylab import rcParams
rcParams['axes.xmargin'] = 0
rcParams['axes.ymargin'] = 0

#%%
def read_config():
    """
    read the yaml configuration file
    """
    #locate
    try:
        local_mod_path = os.path.dirname(__file__)
    except:
        # for inside spyder
        local_mod_path = '/Users/cdesbois/pg/chrisPg/anesthplot'
    filename = os.path.join(local_mod_path, 'recordRc.yaml')
    #load
    if os.path.isfile(filename):
        with open(filename, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
            return cfg
    else:
        print('no recordRc.yaml configFile present')
        print('please build one -> cf buildConfig.py')
        return None

def append_syspath(paths):
    """
    add the folder location to the system path
    """
    if paths['recordMain'] not in sys.path:
        sys.path.append(paths['recordMain'])
        print('added', paths['recordMain'], ' to the path')
        print('location=', paths['recordMain'])
#    if paths['utils'] not in sys.path:
#        sys.path.append(paths['utils'])
#        print('added', paths['utils'], ' to the path')

paths = read_config()
append_syspath(paths)

#import utils
#import bloodGases2 as bg
import trendPlot as plot
import waveFunc as wf
##import bloodGases2 as bg
import loadRec.loadMonitorTrendRecord as lmt
import loadRec.loadMonitorWaveRecord as lmw
import loadRec.loadTaphTrendRecord as ltt
import loadRec.loadTelevet as ltv
import treatRec.cleanData as clean
from PyQt5.QtWidgets import QInputDialog, QWidget

#%%

def gui_choose_file(paths, direct=None, caption='choose a recording'):
    """
    Select a file via a dialog and return the file name.
    """
    if not direct:
        direct = paths['data']
    options = QFileDialog.Options()
# to be able to see the caption, but impose to work with the mouse
#    options |= QFileDialog.DontUseNativeDialog
    fname = QFileDialog.getOpenFileName(caption=caption,
                                        directory=direct, filter='*.csv',
                                        options=options)
#    fname = QFileDialog.getOpenfilename(caption=caption,
#                                        directory=direct, filter='*.csv')
    #TODO : be sure to ba able to see the caption
    return fname[0]

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

def build_param_dico(paths, file='', source=''):
    """initialise a dict save parameters  ----> TODO see min vs sec
    """
    params = {'item': 1,
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
    return params

def list_loaded():
    """
    list the loaded files
    return a dictionary recordObj : file
    """
    records = {}
    try:
        taphTrend
        records['taphTrend'] = taphTrend
    except:
        pass
    try:
        monitorTrend
        records['monitorTrend'] = monitorTrend
    except:
        pass
    try:
        monitorWave
        records['monitorWave'] = monitorWave
    except:
        pass
    try:
        telvet
        records['telvet'] = telvet
    except:
        pass
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('records loaded:')
    for key in records:
        print(key, records[key].file.split('.')[0])
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    return records

def plot_trend_data(file, df, header, params):
    """
    plot the trend recordings
        input : file, df=pdDataframe, header=dictionary, params=dict,
            params=dictionary
        output : matplotlib plots
    """
    # clean the data for taph monitoring
    if params['source'] == 'taphTrend':
        if 'co2exp' in df.columns.values:
            df.loc[df['co2exp'] < 20, 'co2exp'] = np.NaN
        if ('ip1m' in df.columns.values) and not df.ip1m.isnull().all():
            df.loc[df['ip1m'] < 20, 'ip1m'] = np.NaN
        else:
            print('no pressure tdata recorded')
    fig_list = []
    print('build figs')
    #plotting
    plot_func_list = (plot.ventil, plot.co2o2, plot.co2iso, plot.cardiovasc,
                      plot.hist_co2_iso, plot.hist_pam)
    for func in plot_func_list:
        fig_list.append(func(df.set_index('eTimeMin'), params))
    fig_list.append(plot.plot_header(header, params))
    for fig in fig_list:
        if fig:                 # test if figure is present
            fig.text(0.99, 0.01, 'cDesbois', ha='right', va='bottom', alpha=0.4)
            fig.text(0.01, 0.01, file, ha='left', va='bottom', alpha=0.4)
    print('plt.show')
    plt.show()
    return fig_list


def plot_monitor_wave_data(headdf, wavedf):
    """
    not implemented for the moment
    """
#TODO : build a GUI to choose a trace to plot ? or implement that in the class ?
    for item in ['Date', 'Patient Name', 'Patient ID']:
        print(item, ' : ', headdf[item])


##### NB use fig = plot... to obtain a reference to the plot
    # and then axList = fig.axes
    # use axes in this list to change the scales
#%%
class Waves():
    """
    base class for the records
    """
    def __init__(self, filename=None):
        if not filename:
            filename = gui_choose_file(paths)
        self.filename = filename
        self.file = os.path.basename(filename)
        self.fs = None
        self.source = None
        self.data = None

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
        df = clean.clean_trendData(self.data)
        return df
    def show_graphs(self):
        """ basic clinical plots """
        fig_list = plot_trend_data(self.file, self.data, self.header, self.param)
        return fig_list

class MonitorTrend(SlowWave):
    """ monitor trends recordings"""
    def __init__(self, filename):
        super().__init__(filename)
        self.header = lmt.extract_monitor_trend_header(self.filename)
        self.data = lmt.load_monitor_trend_data(self.filename, self.header)
        self.source = 'monitor'
        self.fs = self.header['Sampling Rate']

class TaphTrend(SlowWave):
    """ taphonius trends recordings"""
    def __init__(self, filename):
        super().__init__(filename)
        self.data = ltt.load_taph_trend_data(self.filename)
        self.source = 'taphTrend'
        self.header = self.load_header()
    def load_header(self): 
        """ load the header -> pandas.dataframe """
        headername = gui_choose_file(paths, direct=os.path.dirname(filename),
                                     caption='choose Patient Data')
        if headername != '':
            header = ltt.extract_taph_patient_file(headername)
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
        simple choose and plot for a wave
        """
        cols = [w for w in self.data.columns if w[0] == 'w']
        trace = select_type(caption='choose wave', items=cols)
        if trace:
            fig, _ = wf.plot_wave(self.data, keys=[trace], mini=None, maxi=None)
            fig.text(0.99, 0.01, 'cDesbois', ha='right', va='bottom', alpha=0.4)
            fig.text(0.01, 0.01, self.file, ha='left', va='bottom', alpha=0.4)
            self.trace = trace
            self.fig = fig
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
        self.data = ltv.loadTeleVet(filename)
        self.source = 'teleVet'
        self.fs = self.data.index.max() / self.data.timeS.iloc[-1]

class MonitorWave(FastWave):
    """
    class to organise monitorWave recordings
    """
    def __init__(self, filename):
        super().__init__(filename)
        header = lmw.extract_monitor_wave_header(filename)
        self.header = dict(zip(header[0], header[1]))
        data = lmw.load_monitor_waves_data(filename)
        data = lmw.append_monitor_wave_datetime_data(data)
        self.data = data
        self.source = 'monitorWave'
        self.fs = 300


#%%
if __name__ == '__main__':
    os.chdir(paths['recordMain'])
    print('backEnd= ', plt.get_backend())   # required ?
    print('start QtApp')
    try:
        app
    except:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
#        app.quitOnLastWindowClosed() == True
    # list of loaded records
    try:
        records
    except:
        records = {}
    # choose file and indicate the source
    filename = gui_choose_file(paths)
    source = select_type(caption="choose kind of file",
                         items=("monitorTrend", "monitorWave",
                                "taphTrend", "telVet"))
    # general parameters
    params = build_param_dico(paths, file=os.path.basename(filename),
                              source=source)
# TODO check the validity of the file    email
    if source == 'telVet':
        telvet = TelevetWave(filename)
        telvet.param = params
        telvet.plot_wave()
    elif source == 'monitorTrend':
        monitorTrend = MonitorTrend(filename)
        monitorTrend.param = params
        fig_list = monitorTrend.show_graphs()
    elif source == 'monitorWave':
        monitorWave = MonitorWave(filename)
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
    except:
        app.exec_()
