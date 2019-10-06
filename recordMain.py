
# -*- coding: utf-8 -*-
#%reset -f      # NB if uncomented if prevent the use from the terminal !!

import os, sys
import yaml
import matplotlib
matplotlib.use('Qt5Agg')  #NB use automatic for updating
import numpy as np
import matplotlib.pyplot as plt
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
def readConfig():
    #locate
    try:
        localModPath = os.path.dirname(__file__)
    except:
        # for inside spyder
        localModPath = '/Users/cdesbois/pg/chrisPg/anesthplot'
    filename = os.path.join(localModPath, 'recordRc.yaml')
    #load
    if os.path.isfile(filename):
        with open(filename, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
            return(cfg)
    else:
        print ('no recordRc.yaml configFile present')
        print ('please build one -> cf buildConfig.py')
        return(None)

def appendSyspath(paths):
    if paths['recordMain'] not in sys.path:
        sys.path.append(paths['recordMain'])
        print('added', paths['recordMain'], ' to the path')
        print('location=', paths['recordMain'])
#    if paths['utils'] not in sys.path:
#        sys.path.append(paths['utils'])
#        print('added', paths['utils'], ' to the path')
    
paths = readConfig()       
appendSyspath(paths)

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

#%%
from PyQt5.QtWidgets import QInputDialog, QWidget

def guiChooseFile(paths, direct=None, caption= 'choose a recording'):
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
                                        options = options)   
#    fname = QFileDialog.getOpenFileName(caption=caption,
#                                        directory=direct, filter='*.csv')  
    #TODO : be sure to ba able to see the caption 
    return fname[0]

def selectType(caption=None, items=None):
    """
    select the recording type:
       return : monitorTrend, monitorWave, taphTrend or telvet
       """
#    if kind=='record':
#        caption = "choose kind of file"
#        items = ("monitorTrend","monitorWave","taphTrend", "telVet")
#    elif kind 
        
#    item, okPressed = QInputDialog.getItem(caption = "choose kind of file","kind:", items, 1, False)
    qw = QWidget()
    item, okPressed = QInputDialog.getItem(qw, caption,"kind:", items, 0, False)
    if okPressed and item:
        return item
    else:
        return None

def buildParamDico(paths, file='', source=''):
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

def listLoaded():
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
    for key in records.keys():
        print (key, records[key].file.split('.')[0])
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    return records
    

def plotTrendData(file, df, header, params):
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
        if ('ip1m' in df.columns.values) and not (df.ip1m.isnull().all()):
            df.loc[df['ip1m'] < 20, 'ip1m'] = np.NaN
        else:
            print ('no pressure tdata recorded')
    figList=[]
    print('build figs')
    #plotting
    plotFuncList=(plot.ventil, plot.co2o2, plot.co2iso, plot.cardiovasc,
                  plot.histCO2iso, plot.histPaM)
    for plotFunc in plotFuncList:
        figList.append(plotFunc(df.set_index('eTimeMin'), params))
    figList.append(plot.plotHeader(header, params))
    for fig in figList:
        if fig:                 # test if figure is present
            fig.text(0.99,0.01, 'cDesbois', ha='right', va='bottom', alpha=0.4)
            fig.text(0.01,0.01, file, ha='left', va='bottom', alpha=0.4)
    print('plt.show')
    plt.show()
    return figList


def plotMonitorWaveData(headdf, wavedf):
    """
    not implemented for the moment
    """
#TODO : build a GUI to choose a trace to plot ? or implement that in the class ?
    for item in ['Date', 'Patient Name', 'Patient ID']:
        print(item, ' : ',  headdf[item])


##### NB use fig = plot... to obtain a reference to the plot
    # and then axList = fig.axes
    # use axes in this list to change the scales
#%%
class Waves():
    """
    base class for the records
    """
    def __init__(self, fileName=None):
        if not fileName:
            fileName = guiChooseFile(paths)
        self.fileName = fileName
        self.file = os.path.basename(fileName)        
        self.fs = None
        self.source = None
        self.data = None

#+++++++            
class SlowWave(Waves):
    """
    class for slowWaves = trends
    """
    def __init__(self, fileName):
        super().__init__(fileName)
    def cleanTrend(self):
        """
        clean the data, remove irrelevant, 
        input = self.data, 
        output = pandas dataFrame
        nb doesnt change the obj.data in place
        """
        df = clean.cleanTrendData(self.data)
        return df
    def showGraphs(self):
        """ basic clinical plots """
        figList = plotTrendData(self.file, self.data, self.header, self.param)
        return figList
    
class MonitorTrend(SlowWave):
    """ monitor trends recordings"""
    def __init__(self, fileName):
        super().__init__(fileName)
        self.header= lmt.extractMonitorTrendHeader(self.fileName)
        self.data= lmt.loadMonitorTrendData(self.fileName, self.header)
        self.source = 'monitor'
        self.fs = self.header['Sampling Rate']
    
class TaphTrend(SlowWave):
    """ taphonius trends recordings"""
    def __init__(self, fileName):
        super().__init__(fileName)
        self.data= ltt.loadTaphTrendData(self.fileName)
        self.source = 'taphTrend'
        self.header = self.loadHeader()
    def loadHeader(self):
        headerName = guiChooseFile(paths, direct=os.path.dirname(fileName),
                                   caption = 'choose Patient Data')
        if headerName != '':
            header = ltt.extractTaphPatientFile(headerName)
            return(header)
        else:
            return(None)
    def extractTaphEvents(self):
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
    def __init__(self, fileName):
        super().__init__(fileName)
    def plotWave(self):
        """
        simple choose and plot for a wave
        """
        cols = [w for w in self.data.columns if w[0]=='w']
        trace = selectType(caption= 'choose wave',
                   items= cols)
        if trace:
            fig, _ = wf.plotWave(self.data, keys=[trace], mini=None, maxi=None)
            self.trace = trace
            self.fig=fig
        else:
            self.trace = None
            self.fig= None
            
    def defineARoi(self):
        """
        define a ROI
        """
        df = self.data
        if self.fig:
            ax= self.fig.get_axes()[0]
            #point Value
            lims = ax.get_xlim() # pt values
            limpt= (int(lims[0]), int(lims[1]))
            #sec value
            limsec= (df.sec.loc[limpt[0]],  df.sec.loc[limpt[1]] )
            limdatetime = (df.datetime.loc[limpt[0]],  df.datetime.loc[limpt[1]] )        
            roidict = {
           'sec': limsec,
           'pt': limpt,
           'dt': limdatetime
           }
            self.roi = roidict
    
    
class TelevetWave(FastWave):
    """
    class to organise teleVet recordings transformed to csv files
    """
    def __init__(self, fileName):
        super().__init__(fileName)
        self.data = ltv.loadTeleVet(fileName)
        self.source = 'teleVet'
        self.fs = self.data.index.max() / self.data.timeS.iloc[-1]
         
class MonitorWave(FastWave):
    """
    class to organise monitorWave recordings
    """
    def __init__(self, fileName):
        super().__init__(fileName)
        header = lmw.extractMonitorWaveHeader(fileName)
        self.header = dict(zip(header[0], header[1]))
        data = lmw.loadMonitorWavesData(fileName)
        data = lmw.appendMonitorWaveDatetimeData(data)
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
        app.quitOnLastWindowClosed() == True
    # list of loaded records
    try:
        records
    except:
        records = {}
    # choose file and indicate the source
    fileName = guiChooseFile(paths)
    source = selectType(caption = "choose kind of file", 
                                 items = ("monitorTrend","monitorWave","taphTrend", "telVet"))
    # general parameters
    params = buildParamDico(paths, file=os.path.basename(fileName), 
                            source=source)
# TODO check the validity of the file    email
    if source == 'telVet':
        telvet = TelevetWave(fileName)
        telvet.param = params
        telvet.plotWave()
    elif source == 'monitorTrend':
        monitorTrend = MonitorTrend(fileName)
        monitorTrend.param = params
        figList = monitorTrend.showGraphs()
    elif source =='monitorWave':
            monitorWave = MonitorWave(fileName)    
            monitorWave.param = params
            monitorWave.plotWave()
    elif source == 'taphTrend':
        taphTrend = TaphTrend(fileName)
        taphTrend.param = params
#        tdata= clean.cleanTrendData(tdata)
        figList = taphTrend.showGraphs()
    else:
        print('this is not recognized recording')
    records = listLoaded()
    plt.show()
    try:
        app
    except:
        app.exec_()

