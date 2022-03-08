#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:09:29 2022

@author: cdesbois
"""


import os

import pandas as pd

import anesplot.record_main as rec


def export_to_hdf(savename, mtrend=None, ttrend=None, mwave=None):
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


save_name = os.path.join(os.path.expanduser("~"), "toPlay", "test_export.hdf")
export_to_hdf(save_name, mtrend=mtrends, ttrend=ttrends, mwave=mwaves)

# %%
# TODO save / recover filename


def load_from_hdf(savename):
    """
    build MonitorTrend, TaphTrenbd and MonitorWave objects
    fill them from hdf file

    Parameters
    ----------
    savename : str
        the path to the saved hdf file.

    Returns
    -------
    MonitorTrend, TaphTrend and MonitorWave
    (empty objects if the corresponding keys are not present in the file)
    """

    def convert_to_float(dico):
        """convert the str values of the dictionary"""
        for k, v in dico.items():
            if v.isdigit():
                dico[k] = float(v)
            if v == "None":
                dico[k] = None
            if v == "False":
                dico[k] = False
            if v == "True":
                dico[k] = True
        return dico

    with pd.HDFStore(savename) as store:
        keys = store.keys(include="pandas")
        new_mtrends = rec.MonitorTrend(filename="", load=False)
        if "/" + "mtrends_data" in keys:
            new_mtrends.data = store.get("mtrends_data")
            header = store.get("mtrends_header").to_dict()[0]
            new_mtrends.header = convert_to_float(header)
            param = store.get("mtrends_param").to_dict()[0]
            new_mtrends.param = convert_to_float(param)
            print(f"{'>'*10} loaded mtrends {'<'*10}")

        new_ttrends = rec.TaphTrend(filename="", load=False)
        if "/" + "ttrends_data" in keys:
            new_ttrends.data = store.get("ttrends_data")
            header = store.get("ttrends_header").to_dict()[0]
            new_ttrends.header = convert_to_float(header)
            param = store.get("ttrends_param").to_dict()[0]
            new_ttrends.param = convert_to_float(param)
            new_ttrends.extract_events()
            print(f"{'>'*10} loaded ttrends {'<'*10}")

        new_mwaves = rec.MonitorWave(filename="", load=False)
        if "/" + "mwaves_data" in keys:
            new_mwaves.data = store.get("mwaves_data")
            header = store.get("mwaves_header").to_dict()[0]
            new_mwaves.header = convert_to_float(header)
            param = store.get("mwaves_param").to_dict()[0]
            new_mwaves.param = convert_to_float(param)
            print(f"{'>'*10} loaded mwaves {'<'*10}")

    return new_mtrends, new_ttrends, new_mwaves


n_mtrends, n_ttrends, n_mwaves = load_from_hdf(save_name)

# duplicates = {_ for _ in cols if cols.count(_) > 1}
# print(f"{duplicates=}")
