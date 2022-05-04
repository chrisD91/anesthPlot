#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:20:50 2022

@author: cdesbois

"""
import os
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
from config.load_recordrc import build_paths

paths = build_paths()

import loadrec.agg_load as loadagg
import plot.w_agg_plot as wagg
import plot.wave_plot as wplot
import treatrec
import treatrec.wave_func as wf
from base import _Waves
from loadrec import loadmonitor_waverecord as lmw
from loadrec import loadtelevet as ltv


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
                # trace = loadagg.select_type(question='choose wave', items=cols)
                for num in [1, 2]:
                    trace = wagg.select_wave_to_plot(waves=cols, num=num)
                    if trace is not None:
                        traces_list.append(trace)
            if traces_list:
                print("call wplot.plot_wave")
                fig, lines = wplot.plot_wave(
                    self.data, keys=traces_list, param=self.param
                )
                print("returned from wplot.plot_wave")
                self.trace_list = traces_list
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
        elif self.fig:
            # roidict = wplot.get_wave_roi(self)
            roidict = wplot.get_wave_roi(self.fig, self.data, self.param)
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

    def plot_sample_systolic_variation(
        self, lims: Tuple = None, teach: bool = False, annotations: bool = False
    ):
        "plot the systolic variation"
        if self.roi:
            treatrec.arterial_func.plot_sample_systolic_pressure_variation(
                self, lims, teach, annotations
            )
            # wplot.plot_systolic_pressure_variation(self)
        else:
            print("please define a ROI using mwave.save_a_roi")

    def plot_record_systolic_variation(self):
        "plot the systolic variation"
        treatrec.arterial_func.plot_record_systolic_variation(self)

    def plot_sample_ekgbeat_overlap(self, threshold=-1, lims=None):
        "overlap a sample ekg R centered traces"
        fig = treatrec.ekg_func.plot_sample_ekgbeat_overlap(
            self, lims=lims, threshold=threshold
        )
        return fig


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
            # filename = ltv.choosefile_gui(dir_path)
            filename = loadagg.choosefile_gui(dir_path)
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
            # filename = lmw.choosefile_gui(dir_path)
            filename = loadagg.choosefile_gui(dir_path)
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
