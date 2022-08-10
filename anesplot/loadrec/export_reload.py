#!/usr/bin/env python3
"""
Created on Tue Mar  8 11:09:29 2022

@author: cdesbois

export locally the record objects to hdf,
and load them back

"""


# import os
import logging
from typing import Any

import pandas as pd

from anesplot.fast_waves import MonitorWave

# import anesplot.record_main as rec
from anesplot.slow_waves import MonitorTrend, TaphTrend


# def export_to_hdf(savename, mtrend=None, ttrend=None, mwave=None):
def export_data_to_hdf(
    savename: str, mtrend: Any = None, ttrend: Any = None, mwave: Any = None
) -> None:
    """
    Export the recordings in an hdf file.

    keys are
    - mtrends_data, mtrends_header, mtrends_param
    - ttrends_data, ttrends_header, ttrends_param
    - mwaves_data, mwaves_header, mwaves_param

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

    def fix_dtypes(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Fix the dtype of a dataframe."""
        for col in dataframe.columns:
            try:
                dataframe[col] = pd.to_numeric(dataframe[col])
                # df[col] = df[col].astype('int64')
            except ValueError:
                dataframe[col] = dataframe[col].astype(str)
        return dataframe

    # monitor trends
    if mtrend:
        mtrend.data.to_hdf(savename, key="mtrends_data")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in mtrend.header.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="mtrends_header")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in mtrend.param.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="mtrends_param")
        logging.warning("monitorTrend to %s", savename)
        logging.warning("keys= 'mtrends_data, mtrends_header, mtrends_param'")
    # taph trends
    if ttrend:
        ttrend.data.to_hdf(savename, key="ttrends_data")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in ttrend.header.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="ttrends_header")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in ttrend.param.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="ttrends_param")
        logging.warning("taphTrend to %s", savename)
        logging.warning("keys= 'ttrends_data, ttrends_header, ttrends_param'")
    # waves
    if mwave:
        mwave.data.to_hdf(savename, key="mwaves_data")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in mwave.header.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="mwaves_header")
        dicodf = pd.DataFrame.from_dict({k: [v] for k, v in mwave.param.items()})
        fix_dtypes(dicodf).to_hdf(savename, key="mwaves_param")
        logging.warning("monitorTrend to %s", savename)
        logging.warning("keys= 'mwaves_data, mwaves_header, mtrends_param'")


# %%


# def load_from_hdf(savename: str):
def build_obj_from_hdf(savename: str) -> tuple[Any, Any, Any]:
    """
    Build MonitorTrend, TaphTrenbd and MonitorWave objects.

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

    def change_sec_to_etimesec(datadf: pd.DataFrame) -> pd.DataFrame:
        """Change column name."""
        cols = datadf.columns.to_list()
        cols = [_.replace("sec", "etimesec") for _ in cols if _ == "sec"]
        datadf.columns = cols
        return datadf

    def df_to_dico_with_none(itemdf: pd.DataFrame) -> dict[str, Any]:
        """Df to dico, and replace nan with none."""
        if itemdf.empty:
            dico = {}
        else:
            dico = itemdf.mask(itemdf.isna(), other=None).to_dict()[0]
        return dict(dico)

    messages = []
    with pd.HDFStore(savename) as store:
        keys = store.keys(include="pandas")
        new_mtrends = MonitorTrend(filename="", load=False)
        if "/" + "mtrends_data" in keys:
            new_mtrends.data = store.get("mtrends_data")
            new_mtrends.data = change_sec_to_etimesec(new_mtrends.data)
            new_mtrends.header = df_to_dico_with_none(store.get("mtrends_header").T)
            new_mtrends.param = df_to_dico_with_none(store.get("mtrends_param").T)
            new_mtrends.filename = new_mtrends.param["filename"]
            messages.append(f"{'-'*10} loaded mtrends from hdf {'-'*10}")

        new_ttrends = TaphTrend(filename="", load=False)
        if "/" + "ttrends_data" in keys:
            new_ttrends.data = store.get("ttrends_data")
            new_ttrends.data = change_sec_to_etimesec(new_ttrends.data)
            new_ttrends.header = df_to_dico_with_none(store.get("ttrends_header").T)
            new_ttrends.param = df_to_dico_with_none(store.get("ttrends_param").T)
            new_ttrends.filename = new_ttrends.param["filename"]
            new_ttrends.extract_events()
            messages.append(f"{'-'*10} loaded ttrends from hdf {'-'*10}")

        new_mwaves = MonitorWave(filename="", load=False)
        if "/" + "mwaves_data" in keys:
            new_mwaves.data = store.get("mwaves_data")
            new_mwaves.data = change_sec_to_etimesec(new_mwaves.data)
            new_mwaves.header = df_to_dico_with_none(store.get("mwaves_header").T)
            new_mwaves.param = df_to_dico_with_none(store.get("mwaves_param").T)
            new_mwaves.filename = new_mwaves.param["filename"]
            messages.append(f"{'-'*10} loaded mwaves from hdf {'-'*10}")
    for message in messages:
        logging.warning(message)
    return new_mtrends, new_ttrends, new_mwaves


# if __name__ == '__main__':
# save_name = os.path.join(os.path.expanduser("~"), "toPlay", "test_export.hdf")
# export_to_hdf(save_name, mtrend=mtrends, ttrend=ttrends, mwave=mwaves)
# n_mtrends, n_ttrends, n_mwaves = load_from_hdf(save_name)

# duplicates = {_ for _ in cols if cols.count(_) > 1}
# logging.warning(f"{duplicates=}")


# %%
