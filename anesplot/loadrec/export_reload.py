#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:09:29 2022

@author: cdesbois
"""


# import os

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

    def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """fix the dtype of a dataframe"""
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
                # df[col] = df[col].astype('int64')
            except ValueError:
                df[col] = df[col].astype(str)
        return df

    # monitor trends
    if mtrend:
        mtrend.data.to_hdf(savename, key="mtrends_data")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in mtrend.header.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="mtrends_header")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in mtrend.param.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="mtrends_param")
    # taph trends
    if ttrend:
        ttrend.data.to_hdf(savename, key="ttrends_data")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in ttrend.header.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="ttrends_header")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in ttrend.param.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="ttrends_param")
    # waves
    if mwave:
        mwave.data.to_hdf(savename, key="mwaves_data")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in mwave.header.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="mwaves_header")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in mwave.param.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="mwaves_param")


# %%


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

    def df_to_dico_with_none(df):
        """df to dico, and replace nan with none"""
        return df.mask(df.isna(), other=None).to_dict()[0]

    messages = []
    with pd.HDFStore(savename) as store:
        keys = store.keys(include="pandas")
        new_mtrends = rec.MonitorTrend(filename="", load=False)
        if "/" + "mtrends_data" in keys:
            new_mtrends.data = store.get("mtrends_data")
            new_mtrends.header = df_to_dico_with_none(store.get("mtrends_header").T)
            new_mtrends.param = df_to_dico_with_none(store.get("mtrends_param").T)
            new_mtrends.filename = new_mtrends.param["filename"]
            messages.append(f"{'-'*10} loaded mtrends {'-'*10}")

        new_ttrends = rec.TaphTrend(filename="", load=False)
        if "/" + "ttrends_data" in keys:
            new_ttrends.data = store.get("ttrends_data")
            new_ttrends.header = df_to_dico_with_none(store.get("ttrends_header").T)
            new_ttrends.param = df_to_dico_with_none(store.get("ttrends_param").T)
            new_ttrends.filename = new_ttrends.param["filename"]
            new_ttrends.extract_events()
            messages.append(f"{'-'*10} loaded ttrends {'-'*10}")

        new_mwaves = rec.MonitorWave(filename="", load=False)
        if "/" + "mwaves_data" in keys:
            new_mwaves.data = store.get("mwaves_data")
            new_mwaves.header = df_to_dico_with_none(store.get("mwaves_header").T)
            new_mwaves.param = df_to_dico_with_none(store.get("mwaves_param").T)
            new_mwaves.filename = new_mwaves.param["filename"]
            messages.append(f"{'-'*10} loaded mwaves {'-'*10}")
    print()
    for message in messages:
        print(message)
    return new_mtrends, new_ttrends, new_mwaves


# if __name__ == '__main__':
# save_name = os.path.join(os.path.expanduser("~"), "toPlay", "test_export.hdf")
# export_to_hdf(save_name, mtrend=mtrends, ttrend=ttrends, mwave=mwaves)
# n_mtrends, n_ttrends, n_mwaves = load_from_hdf(save_name)

# duplicates = {_ for _ in cols if cols.count(_) > 1}
# print(f"{duplicates=}")


# %%
