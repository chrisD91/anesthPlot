#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 10:30:54 2021

@author: cdesbois

to extract the events from the taphonius files

"""
import os
from datetime import datetime, timedelta
from typing import Tuple, Dict

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", 50)
pd.set_option("display.max_columns", 500)
#%%


def convert_day(st: str) -> str:
    """get a day YYYYmonthD an convert it to YYY-month-D"""
    previous = st[0]
    new = st[0]
    for x in st[1:]:
        if x.isalpha() == previous.isalpha():
            new += x
        else:
            new += "-" + x
        previous = x
    return new


def extract_taphmessages(df: pd.DataFrame, display: bool = False):
    """extract the messages
    input:
        df : pd.DataFrame of dt_event_df
    return:
        acts : dict of actions
        content: dict of taph messages
    """
    if df.empty:
        return {}, {}
    content = set(df.events)
    content = {_.split(":")[0].strip() for _ in content}
    content = {_.split("from")[0].strip() for _ in content}
    content = {_.split("(")[0] for _ in content}

    acts = {_ for _ in content if "changed" in _}
    not_acts = {"power", "primary", "preset", "scales", "buffer", "trace"}
    acts = {_ for _ in acts if not any(_.startswith(w) for w in not_acts)}

    if display:
        print(f"{'-' * 10} extract_taphmessages")
        print(f"{'-' * 5} content : ")
        for item in content:
            print(item)

    return acts, content


def build_event_dataframe(datadf: pd.DataFrame) -> pd.DataFrame:
    """build a pandas datafame with a countinuous datetime:event pairs
    input:
    ------
    datadf : pd.DataFrame taphonius recording
    ouput:
    ------
        dteventdf: pd.DataFrame index=datetime,
    """
    dteventdf = pd.DataFrame(columns=["events"])
    if datadf.empty:
        print("empty dataframe")
        return dteventdf
    df = datadf[["events", "datetime"]].dropna().set_index("datetime")
    df.events = df.events.apply(
        lambda st: [_.strip("[").strip("]") for _ in st.splitlines()]
    )
    if df.events.dropna().empty:
        print("no events in the recording")
        return dteventdf
    # linearize the events
    events_ser = pd.Series(name="events", dtype=str)
    events_ser.flags.allows_duplicate_labels = False
    for index, line in df.events.iteritems():
        # break if injection event eg
        # SD2015MAR1-5_58_19.csv
        t_event = {
            (_.split("-")[0].strip().lower(), _.split("-")[-1].strip().lower())
            for _ in line
            if _
        }
        dico = {}
        indexdate = index.date()
        indextime = index.time()
        for t, event in t_event:
            if len(t) >= 16:
                event = t.split("]")[-1].strip()
                t = t.split("]")[0]
            if " am" in t:
                t = t.replace(" am", "") + " am"
            if " pm" in t:
                t = t.replace(" pm", "") + " pm"
            try:
                eventtime = pd.to_datetime(t).time()
            except pd.errors.OutOfBoundsDatetime:
                eventtime = index.time()
            except pd.errors.ParserError:
                eventtime = index.time()
            except ValueError:
                eventtime = index.time()
            # TODO - to be improved for speed
            themoment = datetime.combine(indexdate, eventtime)
            # check overlap minutes/day around midnight
            moment_minus_index = themoment - datetime.combine(indexdate, indextime)
            if moment_minus_index.total_seconds() / 60 > 60:
                themoment = themoment - timedelta(days=1)
            dico[themoment] = event

        batch = pd.Series(dico, dtype="object", name="events")
        try:
            events_ser = events_ser.append(batch)
        except pd.errors.DuplicateLabelError:
            # two events at the same index
            for dt in batch.index:
                if dt in events_ser:
                    batch = batch.drop(index=dt)
            events_ser = events_ser.append(batch)
    dteventdf = pd.DataFrame(events_ser)
    dteventdf = dteventdf.sort_index()
    return dteventdf


def extract_ventilation_drive(
    dteventdf: pd.DataFrame, acts: set = None
) -> pd.DataFrame:
    """extract a dataframe containing the ventilatory management

    Parameters
    ----------
    dteventdf : pd.DataFrame
        a container for taph generated events (dtime as index, event as column).
    acts : set, optional (default is None)
        container for action messages.

    Returns
    -------
    pd.DataFrame with datetime index and one column per action (ex 'rr changed')

    """
    if dteventdf.empty:
        print("extract_ventilation_drive: dt_event_df is empty")
        return pd.DataFrame()

    if acts is None:
        acts = {
            "cpap value changed",
            "mwpl value changed",
            "rr changed",
            "tidal volume changed",
            "buffer vol",
        }

    runs = {"ventilate": True, "standby": False}

    def end_of_line_to_float(line: str):
        """return float value else none"""
        line = line.split(" ")[-1].replace("s", "")
        try:
            val = float(line)
        except ValueError:
            try:
                # old files
                val = float(line.replace(",", "."))
            except ValueError:
                print(f"end_of_line_to_float: fix me for '{line}'")
                val = np.nan
        return val

    assert (
        dteventdf.index.is_unique
    ), "extract_ventilation_drive: check unicity for dteventdf.index"

    dteventdf = dteventdf.replace("NAN", np.nan)
    # ventilation True or False
    dteventdf["ventil"] = np.nan
    dteventdf.iloc[0, dteventdf.columns.get_loc("ventil")] = False
    runs = {"ventilate": True, "standby": False}
    for k, bol in runs.items():
        for dt, event in dteventdf.events.iteritems():
            if k in event:
                dteventdf.loc[dt, ["ventil"]] = bol
    dteventdf.ventil = dteventdf.ventil.ffill()

    for act in acts:
        mask = dteventdf.events.str.contains(act)
        if len(mask.unique()) > 1:
            # fill with change messages
            dteventdf[act] = np.nan
            dteventdf.loc[mask, [act]] = dteventdf.events
            # fill first line with 'from'
            first_message = dteventdf.loc[mask, [act]].iloc[0][act]
            from_message = first_message.split("to")[0].strip(" ")
            dteventdf.iloc[0, dteventdf.columns.get_loc(act)] = from_message
            # to values and fill
            dteventdf[act] = dteventdf[act].dropna().apply(end_of_line_to_float)
            dteventdf[act] = dteventdf[act].ffill()
            # remove non ventilate values
            dteventdf.loc[~dteventdf.ventil, [act]] = np.nan

    return dteventdf.dropna(how="all", axis=1)


def plot_ventilation_drive(df: pd.DataFrame, param: dict) -> plt.Figure:
    """plot the ventilatory drive ie the data that were changed
    input:
        df : pd.DataFrame = ventildrive_df
        param : dict

    return
        plt.figure
    """
    df.columns = [_.split(" ")[0] for _ in df.columns]
    cols = df.columns[2:]

    labels = {
        "it": "inspTime",
        "tidal": "tidalVol",
        "rr": "respRate",
        "buffer": "bufferVolume",
        "cpap": "peep",
        "mwpl": "pressureLimit",
    }

    fig = plt.figure()
    fig.suptitle("respiratory drive")
    ax = fig.add_subplot(111)
    for col in cols:
        if col == "rr":
            ax.step(
                df.index,
                df[col].fillna(0),
                linewidth=2.5,
                linestyle=":",
                color="k",
                label=labels[col],
            )
        else:
            if col not in labels:
                print(f"plot_ventilation_drive : please update the labels for {col}")
            ax.step(
                df.index, df[col].fillna(0), linewidth=1.5, label=labels.get(col, col)
            )
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ymax = ax.get_ylim()[1]
    ax.set_ylim(0, round(ymax / 5) * 5)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()
    return fig


#%%

plt.close("all")


def plot_events(
    dteventdf: pd.DataFrame, param: dict, todrop: list = None, dtime: bool = False
) -> plt.figure:
    """plot all events

    Parameters
    ----------
    dteventdf : pd.DataFrame
        the data with a datetime index, and an event column
    param : dict
        data recording parameters (just to get the filename)
    todrop : list, optional (default is None)
        str in the columns to drop the column
    dtime : boolean (default is False)
        to use dtime as the xscale.

    Returns
    -------
    fig : plt.Figure

    """

    if todrop is None:
        todrop = []
    # drop events
    for item in todrop:
        dteventdf = dteventdf.drop(
            dteventdf.loc[dteventdf.events.str.contains(item)].index
        )

    # manage color
    dteventdf["color"] = "red"
    mask = dteventdf.events.str.contains("vacuum")
    dteventdf.loc[mask, ["color"]] = "blue"
    mask = dteventdf.events.str.contains("changed")
    dteventdf.loc[mask, ["color"]] = "green"
    mask = dteventdf.events.str.contains("ventilate")
    dteventdf.loc[mask, ["color"]] = "black"
    mask = dteventdf.events.str.contains("standby")
    dteventdf.loc[mask, ["color"]] = "black"

    # set index to num
    if not dtime:
        dteventdf.reset_index(inplace=True)
        dteventdf.rename(columns={"index": "dt"}, inplace=True)
    fig = plt.figure(figsize=(15, 4))
    ax = fig.add_subplot(111)
    dteventdf["uni"] = 1
    # ax.plot(dteventdf.uni)
    ax.scatter(dteventdf.index, dteventdf.uni, color=dteventdf.color, marker=".")
    # ax.scatter(dteventdf.index, dteventdf.uni, color="tab:green", marker=".")
    for dt, color in dteventdf.color.iteritems():
        ax.vlines(dt, 0, 1, color=color)
    # filter messages to remove the actions

    # plot the events - action
    for dt, (event, color) in dteventdf[["events", "color"]].iterrows():
        # pos = (mdates.date2num(dt), 1)
        pos = (dt, 1)
        ax.annotate(
            event,
            pos,
            rotation=45,
            va="bottom",
            ha="left",
            color=color,
        )
    if dtime:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_ylim(0, 25)
    for spine in ["left", "top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.yaxis.set_ticks([])

    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()
    plt.show()
    return fig


# fig = plot_events(ttrend.dt_events_df)

#%%
# TODO find preset values
# message = ""  # ?? presetq


def extract_event(df: pd.DataFrame) -> dict:
    """extract timestamp of the messages
    input:
        df: pandasDataFrame containing the taphonius events
    output:
        marks: dictionary {message : [timestamp]}
    """
    messages = ["Init Complete", "Ventilate", "standby", "data finalised"]
    messages = [_.lower() for _ in messages]

    ser = pd.Series(dtype=str)
    for index, event in df.events.iteritems():
        for message in messages:
            if message in event:
                ser.loc[index] = event
    return ser.to_dict()


#%%


def build_dataframe(acts) -> pd.DataFrame:
    """build a dataframe containing all the actions, one per column"""

    names = {
        "Inspiratory pause value changed": "pause",
        "CPAP value changed": "peep",
        "Tidal Volume changed": "vol",
        "RR changed": "rr",
        "MWPL value changed": "mwpl",
        "Buffer Vol changed": "bufferVol",
        "O2 expired high alarm value changed": "highO2ExpAlarm",
        "O2 inspired high alarm value changed": "highO2InspAlarm",
        "O2 inspired low alarm value changed": "lowO2InspAlarm",
        "IP changed": "IP",
        "IT changed": "IT",
    }
    dflist = []
    for act, event in acts.items():
        colname = names.get(act, "notdefined")
        df = pd.DataFrame(event, columns=["dt", colname]).set_index("dt")
        dflist.append(df)
        if colname == "notdefined":
            print(f"manage_events.build_dataframe : names should be updated for {act}")
    df = pd.concat(dflist).sort_index()

    return df


#%%
if __name__ == "__main__":
    import anesplot.record_main as rec

    afile = "before2020/ALEA_/Patients2016OCT06/Record22_31_18/SD2016OCT6-22_31_19.csv"
    afile = "Anonymous/Patients2021AUG10/Record13_36_34/SD2021AUG10-13_36_34.csv"
    afile = (
        "before2020/Anonymous/Patients2014NOV07/Record19_34_48/SD2014NOV7-19_34_49.csv"
    )
    afile = "before2020/BELAMIDUBOCAGE_A15-8244/Patients2015JUN25/Record15_48_30/SD2015JUN25-15_48_30.csv"

    file_name = os.path.join(rec.paths["taph_data"], afile)
    # see the taphClass
    ttrend = rec.TaphTrend(file_name)
    ttrend.extract_events()
    ttrend.show_graphs()
    ttrend.plot_events()
    ttrend.plot_ventil_drive()
