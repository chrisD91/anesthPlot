#!/usr/bin/env python3
"""
Created on Fri Dec  8 12:46:41 2017

@author: cdesbois

functions to be used with the waves recording

"""
from typing import Any, Union, Optional

import matplotlib.pyplot as plt

# import os
import numpy as np
import pandas as pd
from scipy.signal import medfilt


# //////////////////////////////////////////////// cardio
def fix_baseline_wander(ekg_ser: pd.Series, fs: int = 300) -> pd.Series:
    """
    BaselineWanderRemovalMedian from ecg-kit.

    Given a list of amplitude values
    (ekg_ser) and sample rate (sr), it applies two median filters to data to
    compute the baseline.  The returned result is the original data minus this
    computed baseline.

    Parameters
    ----------
    ekg_ser : pd.DataFrame
        the wave recording.
    fs : int, optional (default is 300)
        The sampling frequency.

    Returns
    -------
    pd.Series
        the ekg filtered series
    """
    # source : https://pypi.python.org/pypi/BaselineWanderRemoval/2017.10.25
    print("\n fix baseline_wander")
    print("source = Python port of BaselineWanderRemovalMedian.m from ECG-kit")
    print()
    # print("Alex Page, alex.page@rochester.edu")
    # print("https://bitbucket.org/atpage/baselinewanderremoval/src/master/")

    ekg_array = ekg_ser.values
    winsize = int(round(0.2 * fs))
    # delayBLR = round((winsize-1)/2)
    if winsize % 2 == 0:
        winsize += 1
    baseline_array = medfilt(ekg_array, kernel_size=winsize)
    winsize = int(round(0.6 * fs))
    # delayBLR = delayBLR + round((winsize-1)/2)
    if winsize % 2 == 0:
        winsize += 1
    baseline_array = medfilt(baseline_array, kernel_size=winsize)
    ekg_filtered = ekg_array - baseline_array
    # return ecg_blr.tolist()
    return pd.Series(data=ekg_filtered, index=ekg_ser.index)


def rol_mean(ser: pd.Series, win_lengh: int = 1, fs: int = 500) -> pd.Series:
    """
    Return a rolling mean of a RR serie.

    Parameters
    ----------
    ser= pd.Serie
    win_lengh: integer
        window lenght for averaging (in sec),
    fs: int
        sampling frequency
    """
    # moving average
    mov_avg = ser.rolling(window=int(win_lengh * fs), center=False).mean()
    # replace the initial values by the mean
    avg_hr = np.mean(ser)
    mov_avg = [avg_hr if np.isnan(x) else x for x in mov_avg]
    mov_avg = pd.Series(mov_avg)
    return mov_avg


def return_points(wavedf: pd.DataFrame, fig: plt.Figure) -> dict[str, Any]:
    """
    Return a tupple containing the point values of ROI.

    Parameters
    ----------
    wavedf : pd.DataFrame
        teh wave recording.
    fig : plt.Figure
        the plot to extract the xscale from.

    Returns
    -------
    dict
        the Region Of Interest.
    """
    ax = fig.get_axes()[0]
    # point Value
    lims = ax.get_xlim()
    limpt = (int(lims[0]), int(lims[1]))
    # sec value
    limsec = (wavedf.sec.loc[limpt[0]], wavedf.sec.loc[limpt[1]])
    limdatetime = (wavedf.datetime.loc[limpt[0]], wavedf.datetime.loc[limpt[1]])
    #    mini = wData.sec.get_loc(mini, method='nearest')
    #    mini = (df.sec - lims[0]).abs().argsort()[:1][0]
    #    maxi = (df.sec - lims[1]).abs().argsort()[:1][0]
    print()
    print("duration =", limsec[1] - limsec[0], "sec")
    print("time = ", limdatetime)
    print("limsec= (", limsec[0], ",", limsec[1], ")")
    print("limpt= (", limpt[0], ",", limpt[1], ")")
    print("mini:", int(limsec[0] / 60), "min :", limsec[0] % 60, "sec")
    print("maxi:", int(limsec[1] / 60), "min :", limsec[1] % 60, "sec")
    roidict = {"sec": limsec, "pt": limpt, "dt": limdatetime}
    return roidict


def restrict_time_area(
    df1: pd.DataFrame, mini: Optional[int] = None, maxi: Optional[int] = None
) -> pd.DataFrame:
    """
    Return a new dataframe with reindexation.

    Parameters
    ----------
    df1: pandas.DataFrame
    mini: integer
        miniPointValue
    maxi: integer
        maxiPointValue

    Returns
    -------
    pandas.DataFrame
    """
    try:
        "sec" in df1.columns
    except KeyError:
        print("'sec' should be in the dataframe columns")
        return pd.DataFrame
    df2 = df1.iloc[np.arange(mini, maxi)].reset_index()
    df2.sec = df2.sec - df2.iloc[0].sec
    return df2
