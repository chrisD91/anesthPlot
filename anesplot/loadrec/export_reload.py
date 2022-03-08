#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:09:29 2022

@author: cdesbois
"""


import os

import pandas as pd


def export_records(savename, mtrend=None, ttrend=None, mwave=None):
    """
    export the recordings in an hdf file
    keys are
        mtrends_data, mtrends_header, mtrends_param
        ttrends_data, ttrends_header, ttrends_param
        mwaves_data, mwaves_header, mwaves_param

    Parameters
    ----------
    savename : str
        the savename to use.
    mtrend : MonitorTrend object, optional (default is None)
        The Monitor recording
    ttrend : TaphoniusTrend, optional (default is None)
        the taphonius recording
    mwave : MonitorWave, optional (default is None)
        the wave recording

    Returns
    -------
    None.

    """

    # monitor trends
    if mtrend:
        mtrend.data.to_hdf(savename, key="mtrends_data")
        pd.DataFrame.from_dict(
            {k: [str(v)] for k, v in mtrend.header.items()}
        ).T.to_hdf(savename, key="mtrends_header")
        pd.DataFrame.from_dict({k: [str(v)] for k, v in mtrend.param.items()}).T.to_hdf(
            savename, key="mtrends_param"
        )
    # filename

    # taph trends
    if ttrend:
        ttrend.data.to_hdf(savename, key="ttrends_data")
        pd.DataFrame.from_dict(
            {k: [str(v)] for k, v in ttrend.header.items()}
        ).T.to_hdf(savename, key="ttrends_header")
        pd.DataFrame.from_dict({k: [str(v)] for k, v in ttrend.param.items()}).T.to_hdf(
            savename, key="ttrends_param"
        )

    # waves
    if mwave:
        mwave.data.to_hdf(savename, key="mwaves_data")
        pd.DataFrame.from_dict({k: [str(v)] for k, v in mwave.header.items()}).T.to_hdf(
            savename, key="mwaves_header"
        )
        pd.DataFrame.from_dict({k: [str(v)] for k, v in mwave.param.items()}).T.to_hdf(
            savename, key="mwaves_param"
        )


save_name = os.path.join(os.path.expanduser("~"), "toPlay", "export.hdf")
export_records(save_name, mtrend=mtrends, ttrend=ttrends, mwave=mwaves)


# duplicates = {_ for _ in cols if cols.count(_) > 1}
# print(f"{duplicates=}")
