#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 08:37:18 2022

@author: cdesbois
"""
import os
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as sg

from anesplot.treatrec.ekg_to_hr import detect_beats
from anesplot.treatrec.wave_func import fix_baseline_wander


# %%


def plot_sample_ekgbeat_overlap(mwave, lims: Tuple = None, threshold=-1) -> plt.Figure:
    """
    extract and plot an overlap of ekg beats"

    Parameters
    ----------
    mwave : monitor trend object
        the monitor recording
    lims : tuple, (default is None)
        the limits to use (in sec)
        If none the mwave.roi will be used
    Returns
    -------
    fig : plt.Figure
        the matplotlib figure.

    """
    datadf = mwave.data[["sec", "wekg"]].dropna().copy()
    if lims is None:
        lims = mwave.roi["sec"]
        # lims = (df.iloc[0].sec, df.iloc[0].sec + 60)
    datadf = datadf.set_index("sec").loc[lims[0] : lims[1]]

    # find the R peaks
    ser = fix_baseline_wander(datadf.wekg, mwave.param["sampling_freq"])

    beatloc_df = detect_beats(ser.dropna(), threshold=threshold)
    beatloc_df["x_loc"] = datadf.index[beatloc_df.p_loc]

    interbeat_sec = (beatloc_df.x_loc.shift(-1) - beatloc_df.x_loc).dropna().median()
    # interbeat *= .5

    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i, x_loc in enumerate(beatloc_df.x_loc):
        x_loc = beatloc_df.x_loc[i]
        beat = datadf.loc[x_loc - 0.3 * interbeat_sec : x_loc + 0.4 * interbeat_sec]
        beat.index = beat.index - x_loc
        ax.plot(beat)
    ax.set_ymargin(0.1)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.axhline(y=0, color="k")
    ax.set_ylabel("ekg (mv)")
    ax.set_xlabel("time (sec)")

    # annotations
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4)
    fig.text(0.01, 0.01, mwave.param["file"], ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()
    plt.show()

    return fig


# %%
if __name__ == "__main__":
    import anesplot.record_main as rec
    from anesplot.loadrec.export_reload import build_obj_from_hdf

    paths = rec.paths
    paths["save"] = "/Users/cdesbois/enva/clinique/recordings/casClin/220419"
    name = "unknown_220419"
    save_name = os.path.join(paths["save"], "data", name + ".hdf")
    if not os.path.isfile(save_name):
        print(f"the file '{os.path.basename(save_name)}' doesn't exists")
        print(f"check the folder '{os.path.dirname(save_name)}'")
    mtrends, ttrends, mwaves = build_obj_from_hdf(save_name)

    mtrends.data.hr = mtrends.data.ihr

    fig, *_ = mwaves.plot_wave(["wekg"])
    lims = (19101.08725772946, 19101.087809159864)
    ax = fig.get_axes()[0]
    ax.set_xlim(lims)
    ax.set_ylim(-2, 1)
    # adjust the scale
    mwaves.save_roi()

    plot_sample_ekgbeat_overlap(mwaves)
