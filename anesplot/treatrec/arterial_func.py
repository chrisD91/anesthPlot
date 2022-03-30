#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 13:00:08 2022

@author: cdesbois
"""


import os
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as sg

# %%
plt.close("all")


# def plot_systolic_pressure_variation(mwave, lims: Tuple = None):
#     """
#     extract and plot the systolic pressure variation"

#     Parameters
#     ----------
#     mwave : monitor trend object
#         the monitor recording
#     lims : tuple, (default is none)
#         the limits to use (in sec)
#         If none the mwave.roi will be used
#     Returns
#     -------
#     fig : plt.Figure
#         the matplotlib figure.

#     """

#     datadf = mwave.data[["sec", "wap"]].dropna().copy()
#     if lims is None:
#         lims = mwave.roi["sec"]
#         # lims = (df.iloc[0].sec, df.iloc[0].sec + 60)
#     datadf = datadf.set_index("sec").loc[lims[0] : lims[1]]

#     # plot the arterial pressure data
#     fig = plt.figure()
#     ax = fig.add_subplot(111)
#     ax.plot(datadf, "-r")
#     for spine in ["top", "right"]:
#         ax.spines[spine].set_visible(False)
#     # find the (up) peaks
#     threshold = datadf.wap.quantile(q=0.8)
#     # ax.axhline(q, color="tab:green", alpha=0.5)
#     peaks_up, properties = sg.find_peaks(datadf.wap, height=threshold)
#     ax.plot(datadf.iloc[peaks_up], "or", alpha=0.2)

#     peaks_vals = datadf.iloc[peaks_up].copy()  # to keep the index ('sec')
#     peaks_vals = peaks_vals.reset_index()
#     peaks_vals["local_max"] = False
#     peaks_vals["local_min"] = False

#     maxi, mini, mean = peaks_vals["wap"].agg(["max", "min", "mean"])
#     systolic_variation = (maxi - mini) / mean
#     mes = f"{systolic_variation = :.2f}"
#     print(mes)

#     # get local max
#     maxis_loc, _ = sg.find_peaks(properties["peak_heights"])
#     peaks_vals.loc[maxis_loc, "local_max"] = True
#     # ax.plot(peaks_vals.loc[peaks_vals.local_max, ["sec", "wap"]].set_index("sec"), "rD")

#     # get local min
#     minis_loc, _ = sg.find_peaks(-properties["peak_heights"])
#     peaks_vals.loc[minis_loc, "local_min"] = True
#     # ax.plot(peaks_vals.loc[peaks_vals.local_min, ["sec", "wap"]].set_index("sec"), "bD")
#     #    import pdb

#     #    pdb.set_trace()
#     inter_beat = round((peaks_vals.sec - peaks_vals.sec.shift(1)).mean())
#     beat_loc_df = peaks_vals.set_index("sec")
#     for i, loc in beat_loc_df.loc[
#         beat_loc_df.local_max + beat_loc_df.local_min, "wap"
#     ].iteritems():
#         ax.hlines(loc, i - inter_beat, i + inter_beat, color="tab:grey")

#     title = mes
#     fig.suptitle(title)
#     ax.set_ylabel("arterial pressure")
#     ax.set_xlabel("time(sec)")
#     # annotations
#     fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
#     fig.text(0.01, 0.01, mwave.param["file"], ha="left", va="bottom", alpha=0.4)

#     fig.tight_layout()

#     return fig


# %%

# if __name__ == "__main__":
#     import anesplot.record_main as rec
#     from anesplot.loadrec.export_reload import build_obj_from_hdf

#     DIRNAME = "/Users/cdesbois/enva/clinique/recordings/casClin/220315/data"
#     FILE = "qDonUnico.hdf"
#     filename = os.path.join(DIRNAME, FILE)
#     _, _, mwaves = build_obj_from_hdf(filename)
#     figure = plot_systolic_pressure_variation(mwaves, (4100, 4160))
