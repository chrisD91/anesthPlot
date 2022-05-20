#!/usr/bin/env python3
"""
Created on Thu Mar 10 08:37:18 2022

@author: cdesbois

functions to deal with ekg traces

"""
import os
from typing import Optional, Any

import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as sg

from anesplot.treatrec.ekg_to_hr import detect_beats
from anesplot.treatrec.wave_func import fix_baseline_wander

# %%


def plot_sample_ekgbeat_overlap(
    mwave: Any, lims: Optional[tuple[float, float]]=None, threshold: float = -1
) -> plt.Figure:
    """
    Extract and plot an overlap of ekg beats.

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
    ekgdf = mwave.data[["sec", "wekg"]].dropna().copy()  # pd.DataFrame
    if lims is None:
        lims = mwave.roi["sec"]
        # lims = (df.iloc[0].sec, df.iloc[0].sec + 60)
    ekgdf = ekgdf.set_index("sec").loc[lims[0] : lims[1]]  # type: ignore

    # find the R peaks
    ekgser = fix_baseline_wander(ekgdf.wekg, mwave.param["sampling_freq"])

    beatloc_df = detect_beats(ekgser.dropna(), threshold=threshold)
    # beatloc_df["x_loc"] = ekgdf.index[beatloc_df.p_loc]
    if beatloc_df.empty:
        print("no beat detected, change threshold?")
        fig = plt.figure(figsize=(5, 5))
        title = "no beat detected"
        fig.suptitle(title)
        ax = fig.add_subplot(111)
        ax.hist(ekgser, bins=30, log=True, orientation="horizontal")
        ax.set_ylabel("mv")
        ax.set_ymargin(0.1)
        ax.axhline(threshold, linewidth=3, color="r")
        txt = f"actual {threshold=}"
        ax.text(
            1,
            0.5,
            txt,
            horizontalalignment="right",
            verticalalignment="center",
            transform=ax.transAxes,
            color="r",
        )
        txt = "? change threshold value in the function call ?"
        ax.text(
            1,
            0.3,
            txt,
            horizontalalignment="right",
            verticalalignment="center",
            transform=ax.transAxes,
        )
        ax.axhline(threshold, linewidth=3, color="r")
        for spine in ["top", "right", "bottom"]:
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        plt.show()
        return fig

    # interbeat_sec = (beatloc_df.x_loc.shift(-1) - beatloc_df.x_loc).dropna().median()

    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    for i, x_loc in enumerate(beatloc_df.x_loc):
        x_loc = beatloc_df.x_loc[i]
        # beat = ekgdf.loc[x_loc - 0.3 * interbeat_sec : x_loc + 0.5 * interbeat_sec]
        beat = ekgdf.loc[x_loc - 0.5 : x_loc + 0.7]
        beat.index = beat.index - x_loc
        ax.plot(beat, label=i, alpha=0.8)
    ax.grid()
    ax.set_ymargin(0.1)
    # ax.legend()
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.axhline(y=0, color="tab:grey")
    ax.axvline(x=0, color="tab:grey")
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

    figure, *_ = mwaves.plot_wave(["wekg"])
    limits = (19101.08725772946, 19101.087809159864)
    ax = figure.get_axes()[0]
    ax.set_xlim(limits)
    ax.set_ylim(-2, 1)
    # adjust the scale
    mwaves.save_roi()

    plot_sample_ekgbeat_overlap(mwaves)
