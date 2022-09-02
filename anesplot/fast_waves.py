# !/usr/bin/env python3
"""
Created on Thu Apr 28 16:20:50 2022

@author: cdesbois

build the objects or the fast_waves ('waves'):
    -> MonitorWave
    -> TeleVet (basic)

"""
import logging
import os
from typing import Any, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
from PyQt5.QtWidgets import QApplication

import anesplot.loadrec.dialogs as dlgs
import anesplot.plot.t_agg_plot as tagg
import anesplot.plot.wave2video as w2vid
import anesplot.plot.wave_plot as wplot
import anesplot.treatrec.arterial_func
import anesplot.treatrec.ekg_func
from anesplot.base import Waves
from anesplot.config.load_recordrc import build_paths

# from anesplot.loadrec.agg_load import choosefile_gui
from anesplot.loadrec.loadmonitor_waverecord import (
    loadmonitor_wavedata,
    loadmonitor_waveheader,
)
from anesplot.loadrec.loadtelevet import loadtelevet

# from anesplot.plot.w_agg_plot import select_wave_to_plot
from anesplot.treatrec.wave_func import fix_baseline_wander

paths = build_paths()

app = QApplication.instance()
logging.info(f"dialogs.py : {__name__=}")
if app is None:
    logging.info("N0 QApplication instance - - - - - - - - - - - - - > creating one")
    app = QApplication([])
else:
    logging.warning(f"QApplication instance already exists: {QApplication.instance()}")


# ++++++++
class _FastWave(Waves):
    """Class for Fastwaves = continuous recordings."""

    def __init__(self) -> None:
        super().__init__()
        self.trace_list: list[plt.Line2D]

    def filter_ekg(self) -> None:
        """Filter the ekg trace -> build 'ekgMovAvg' & 'ekgLowPass'."""
        datadf = self.data
        samplingfreq = self.param["sampling_freq"]
        if "wekg" in datadf.columns:
            item = "wekg"
        elif "d2" in datadf.columns:
            item = "d2"
        else:
            logging.warning("no ekg trace in the data")
            return
        logging.info(f"{'-' * 10} filtering : builded 'ekgLowPass' ")
        datadf["ekgLowPass"] = fix_baseline_wander(datadf[item], samplingfreq)

    def plot_wave(
        self, traces_list: Union[list[str], None] = None
    ) -> tuple[plt.Figure, list[plt.Line2D], Optional[list[str]]]:
        """
        Choose and plot for a wave.

        Parameters
        ----------
        traces_list : list, optional (default is None)
            list of waves to plot (max=2)
            if None -> open a dialog to choose column names.

        Returns
        -------
            fig : pyplot.figure
            lines : [line2D object]
            traces_list : [name of the traces]
        """
        if self.data.empty:
            fig = plt.Figure()
            lines: list[plt.Line2D] = []
            traces_list = []
            logging.warning("there are no data to plot")
        else:
            logging.info(f"{'-' * 20} started FastWave plot_wave)")
            logging.info(f"{'-' * 10}> choose the wave(s)")
            cols: list[str] = [w for w in self.data.columns if w[0] in ["i", "r", "w"]]
            if traces_list is None and cols:
                traces_list = []
                atrace = dlgs.choose_in_alist(cols, message="choose the wave to plot")
                if atrace:
                    traces_list.append(atrace)
                    cols.remove(atrace)
                    atrace = dlgs.choose_in_alist(cols, message="a second one ?")
                    if atrace:
                        traces_list.append(atrace)
                # traces_list = select_wave_to_plot(waves=cols)
            if traces_list:
                logging.info("call wplot.plot_wave")
                # get segmentation fault if called after a trend.showplots()
                fig, lines = wplot.plot_wave(
                    self.data, keys=traces_list, param=self.param
                )
                logging.info("returned from wplot.plot_wave")
                self.trace_list = traces_list
                self.fig = fig
            else:
                self.trace_list = []
                fig = plt.figure()
                lines = [plt.Line2D]
            self.append_to_figures({"waveplot": fig})
            logging.info(f"{'-' * 20} ended FastWave plot_wave")
            plt.show()  # required to display the plot before exiting
        return fig, lines, traces_list

    def save_roi(self, erase: bool = False) -> dict[str, Any]:
        """
        Memorize a Region Of Interest (roi).

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
            # roidict = wplot.get_wave_roi(self.fig, self.data, self.param)
            roidict = tagg.get_roi(self.fig, self.data, self.param)
            roidict.update({"traces": self.trace_list, "fig": self.fig})
        else:
            logging.warning(
                "no fig attribute, please use plot_wave() method to build one"
            )
            roidict = {}

        self.roi = roidict
        return roidict

    def animate_fig(
        self,
        speed: int = 1,
        save: bool = False,
        savename: str = "video",
        # savedir: str = "~",
    ) -> Optional[Any]:
        """
        Build a video the previous builded figure.

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
        plt.Animation.

        """
        if self.roi:
            anim = w2vid.create_video(
                self.data,
                self.param,
                self.roi,
                speed=speed,
                save=save,
                savename=savename,
                savedir="~",
            )
            plt.show()
            return anim
        mes = "no roi attribute, please use record_roi() to build one"
        logging.warning(mes)
        return mes

    def plot_roi_systolic_variation(
        self,
        lims: Optional[Tuple[int, int]] = None,
        teach: bool = False,
        annotations: bool = False,
    ) -> None:
        """Plot the systolic variations (sample of a record based on ROI)."""
        if self.roi:
            (
                fig,
                _,
            ) = anesplot.treatrec.arterial_func.plot_roi_systolic_pressure_variation(
                self,
                teach=teach,
                annotations=annotations,
                lims=lims,
            )
            self.append_to_figures({"systolic_variation": fig})
            # wplot.plot_systolic_pressure_variation(self)
        else:
            logging.warning("please define a ROI using mwave.save_a_roi")

    def plot_record_systolic_variation(self) -> None:
        """Plot the systolic variation (whole record)."""
        fig, _ = anesplot.treatrec.arterial_func.plot_record_systolic_variation(self)
        self.append_to_figures({"systolic_variation": fig})

    def plot_roi_ekgbeat_overlap(
        self, lims: Optional[Tuple[float, float]] = None, threshold: float = -1
    ) -> plt.Figure:
        """Overlap a sample ekg R centered traces."""
        fig = anesplot.treatrec.ekg_func.plot_roi_ekgbeat_overlap(
            self, lims=lims, threshold=threshold
        )
        self.append_to_figures({"ekgbeat_overlap": fig})
        return fig


class TelevetWave(_FastWave):
    """
    Class to organise teleVet recordings transformed to csv files.

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
    """

    # def __init__(self, filename=None):
    def __init__(self, filename: str):
        super().__init__()
        if filename:
            dir_path = paths.get("telv_data")
            filename = dlgs.choose_file(
                dirname=dir_path, title="choose televet recording"
            )
            # filename = choosefile_gui(dir_path)
        self.filename = filename
        data = loadtelevet(filename)
        self.data = data
        # self.source = "teleVet"
        self.param["source"] = "televet"
        # self.param["source_abbr"] = "tw"
        self.param["filename"] = filename
        self.param["file"] = os.path.basename(filename)
        sampling_freq = data.index.max() / data.sec.iloc[-1]
        self.param["sampling_freq"] = sampling_freq


class MonitorWave(_FastWave):
    """Class to organise monitorWave recordings, gather data, provide methods.

    input : filename = path to file
    load = boolean to load data (default is True)

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
    trace_list :  list
        all tracenames in the fig
    roi : dict
        the memorized RegionOfInterest (related to the actual figure)

    Methods
    -------
    plot_wave
        choose trace(s) and plot
    save_roi
        update fig, trace_list and roi
    animate_fig
        build an animation
    filter_ekg
        filter the ekg
    plot_roi_ekgbeat_overlap
        overlap detected ekg beats
    plot_record_systolic_variation
        blood pressure variation
    plot_roi_systolic_variation
        blood pressure variation
    """

    def __init__(self, filename: Optional[str] = None, load: bool = True):
        super().__init__()
        if filename is None:
            dir_path = paths.get("mon_data")
            filename = dlgs.choose_file(
                dirname=dir_path, title="choose monitor wave recording"
            )
            # filename = choosefile_gui(dir_path)
        if filename and "Wave" not in os.path.basename(filename):
            raise ValueError("this is not a wave record")
            load = False
        self.filename = filename
        self.param["filename"] = filename
        self.param["file"] = os.path.basename(filename)
        header = loadmonitor_waveheader(filename)
        self.header = header
        if load and bool(header):
            self.data = loadmonitor_wavedata(filename)
        else:
            logging.warning(f"{'-'*5} MonitorWave: didn't load the data ({load=})")
            self.data = pd.DataFrame()
        self.param["source"] = "monitorWave"
        # self.param["source_abbr"] = "mw"
        self.param["sampling_freq"] = float(header.get("Data Rate (ms)", 0)) * 60 / 1000
        # usually 300 Hz
