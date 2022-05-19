#!/usr/bin/env python3
"""
Created on Wed Jul 31 16:05:29 2019

@author: cdesbois

filtering process ot the traces : actually not used, to be improved

"""
import numpy as np
import pandas as pd


def clean_trenddata(datadf: pd.DataFrame) -> pd.DataFrame:
    """Remove artifacts in the recorded trends."""
    param_list = [
        "ip1s",
        "ip1d",
        "ip1m",
        "hr",
        "co2insp",
        "co2exp",
        "co2RR",
        "o2insp",
        "o2exp",
        "aaInsp",
        "aaExp",
        "pPeak",
        "peep",
        "pPlat",
        "tvInsp",
        "tvExp",
        "compli",
        "ipeep",
        "pmean",
        "raw",
        "minVinsp",
        "minVexp",
        "epeep",
        "ieRat",
        "inspT",
        "expT",
        "peepe",
        "peepi",
    ]
    range_dict = {
        "ip1s": (30, None),
        "ip1d": (10, None),
        "ip1m": (20, None),
        "hr": (20, 80),
        "co2insp": (None, None),
        "co2exp": (20, None),
        "co2RR": (None, None),
        "o2insp": (None, None),
        "o2exp": (None, None),
        "aaInsp": (None, None),
        "aaExp": (None, None),
        "pPeak": (None, None),
        "peep": (None, None),
        "pPlat": (None, None),
        "tvInsp": (None, None),
        "tvExp": (None, None),
        "compli": (None, None),
        "ipeep": (None, None),
        "pmean": (None, None),
        "raw": (None, None),
        "minVinsp": (None, None),
        "minVexp": (None, None),
        "epeep": (None, None),
        "ieRat": (None, None),
        "inspT": (None, None),
        "expT": (None, None),
        "peepe": (None, None),
        "peepi": (None, None),
    }
    # irrelevant
    for item, lims in range_dict.items():
        if item in datadf.columns:
            datadf.loc[datadf[item] < lims[0], item] = np.NaN
            datadf.loc[datadf[item] > lims[1], item] = np.NaN
    # outliers
    for item in param_list:
        if item in datadf.columns:
            mini, maxi = datadf[item].quantile([0.01, 0.99])
            datadf.loc[datadf[item] < mini, item] = np.NaN
            datadf.loc[datadf[item] > maxi, item] = np.NaN

    # fill with interpolation
    # df = df.interpolate(method='linear')
    # TODO = pb when the animal is disconnected :
    # the linear interpolation is not relevant
    return datadf
