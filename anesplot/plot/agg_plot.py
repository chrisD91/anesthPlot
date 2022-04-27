#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 15:46:14 2022

@author: cdesbois

list of function to choose, manipulate and combine the plot functions
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

import anesplot.plot.trend_plot as tplot
import anesplot.plot.wave_plot as wplot


# test how to plot half of the plot
# TODO build a model to predict evolution

# tplot.cardiovasc(datadf: pandas.core.frame.DataFrame, param: dict = None) -> matplotlib.figure.Figure
def retrieve_function(name):
    """ get the function from it's name """
    func_list = [
            tplot.ventil,
            tplot.co2o2,
            tplot.co2iso,
            tplot.cardiovasc,
            tplot.hist_co2_iso,
            tplot.hist_cardio,
            tplot.sat_hr]
    return [_ for _ in func_list if _.__name__ == name][0]


def build_half_white(fig, name, trends):
    axes = fig.get_axes()
    ax = axes[0]
    lims = ax.get_xlim()
    if ax.lines[0].get_xdata().dtype == '<M8[ns]':
        # datetime scale
        t_loc0 = mdates.num2date(lims[0]).replace(tzinfo=None)
        t_loc1 = mdates.num2date(lims[1]).replace(tzinfo=None)
        df = trends.data.set_index('datetime').loc[t_loc0: t_loc1].reset_index().copy()
    else:
        # etime scale
        df = trends.data.set_index('eTimeMin').loc[lims[0]: lims[1]].reset_index().copy()

    func = retrieve_function(name)
    nfig = func(df, trends.param)
    nax = nfig.get_axes()[0]
    nlims = (lims[0], lims[1] + lims[1] - lims[0])
    nax.set_xlim(nlims)
    nax.axvline(lims[1], color='tab:grey')
    txt1 = '1: que se passe-t-il ?'
    txt2 = '2: que va-t-il se passer ?'
    txt3 = "3: c'est grave docteur ?"
    txt4 = '4: vous faites quoi ?'
    nax.text(0.25, 0.9, txt1, horizontalalignment='center', fontsize=18,
             verticalalignment='center', transform=ax.transAxes)
    nax.text(0.6, 0.9, txt2, horizontalalignment='left', fontsize=18,
             verticalalignment='center', transform=ax.transAxes)
    nax.text(0.6, 0.7, txt3, horizontalalignment='left', fontsize=18,
             verticalalignment='center', transform=ax.transAxes)
    nax.text(0.6, 0.5, txt4, horizontalalignment='left', fontsize=18,
             verticalalignment='center', transform=ax.transAxes)
    return fig, nlims


# %%

if __name__ == '__main__':
    # import anesplot.record_main as rec
    # mtrends = rec.MonitorTrend()
    fig, name = mtrends.plot_trend()
    print('now scale the figure please')
    # scale the figure
    n_fig, n_lims = build_half_white(fig, name, mtrends)
    # change the scale for third
    fig.get_axes()[0].set_xlim(n_lims)
