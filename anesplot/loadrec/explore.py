#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu Mar 12 16:52:13 2020

@author: cdesbois
"""

import matplotlib.pyplot as plt

# import os
# from glob import glob
from PyQt5.QtWidgets import QApplication, QFileDialog

# %%


def gui_choosefile(paths=None):
    """select a file via a dialog and return the file name."""
    if not paths:
        paths = {}
    apath = paths.get("data", "~")
    app = QApplication([apath])
    app.setQuitOnLastWindowClosed(True)
    fname = QFileDialog.getOpenFileName(
        caption="choose a file", directory=apath, filter="*.csv"
    )
    return fname[0]


# %% list a folder
plt.close("all")

# =============================================================================
# def plotAllRecords(kind= 'cardio', xlims=None):
#     """
#     plot all records in a folder
#     kind = cardio, respi, co2o2 or ventil
#     xlims = None 'default, or a tupple
#     """
#     dir = os.path.join(paths['data'], 'onPanelPcRecorded', '2019')
#     # fileList
#     files = []
#     for item in glob(os.path.join(dir, '*.csv')):
#         file = os.path.basename(item)
#         if 'Wave' not in file:
#             files.append(file)
#     # plot
#     fig = None
#     for file in files:
#         fileName = os.path.join(dir, file)
#         data = MonitorTrend(fileName).data
#         plotsF = {'cardio': tplot.cardiovasc, 'respi': tplot.co2iso,
#                    'co2o2': tplot.co2o2, 'ventil': tplot.ventil}
#         fig = plotsF[kind](data.set_index('eTimeMin'), params)
#         if fig:
#             fig.text(0.99,0.01, 'cDesbois', ha='right', va='bottom', alpha=0.4)
#             fig.text(0.01,0.01, file, ha='left', va='bottom', alpha=0.4)
#             if xlims:
#                 fig.get_axes()[0].set_xlim(xlims)
#
# plotAllRecords(kind='cardio')
#
# =============================================================================


# %%
# if __name__ == '__main__':
#    pass
