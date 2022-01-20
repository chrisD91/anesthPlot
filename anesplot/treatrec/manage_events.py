#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 10:30:54 2021

@author: cdesbois

to extract the events from the taphonius files

"""
import os
from datetime import datetime
from typing import Tuple, Dict

import numpy as np
import pandas as pd

pd.set_option("display.max_rows", 500)
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

    return:
        acts : dict of actions
        content: dict of taph messages
    """
    content = set(df.events)
    content = {_.split(":")[0].strip() for _ in content}
    content = {_.split("from")[0].strip() for _ in content}
    content = {_.split("(")[0] for _ in content}

    acts = {_ for _ in content if "changed" in _}
    acts = {
        _ for _ in acts if not _.startswith("power") and not _.startswith("primary")
    }
    if display:
        print(f"{'-' * 10} extract_taphmessages")
        print(f"{'-' * 5} content : ")
        for item in content:
            print(item)

    acts = {_ for _ in content if "changed" in _}
    acts = {
        _ for _ in acts if not _.startswith("power") and not _.startswith("primary")
    }

    return acts, content


def build_event_dataframe(datadf: pd.DataFrame) -> pd.DataFrame:
    """build a pandas datafame with a countinuous datetime:event pairs
    input:
    ------
    datadf : pd.DataFrame taphonius recording
    ouput:
        dteventdf: pd.DataFrame index=datetime,
    """
    dteventdf = pd.DataFrame(columns=["events"])
    if datadf.empty:
        print("empty dataframe")
        return dteventdf
    df = datadf[["events", "datetime"]].dropna().set_index("datetime")
    df.events = df.events.apply(
        lambda st: [_.strip("[").strip("]") for _ in st.split("\r\n")]
    )
    if df.events.dropna().empty:
        print("no events in the recording")
        return dteventdf
    # linearize the events
    events_ser = pd.Series(name="events", dtype=str)
    for index, line in df.events.iteritems():
        t_event = [
            (_.split("-")[0].strip().lower(), _.split("-")[1].strip().lower())
            for _ in line
            if _
        ]
        dico = {}
        thedate = index.date()
        for t, event in t_event:
            if len(t) >= 16:
                event = t.split("]")[1].strip()
                t = t.split("]")[0]
            try:
                thetime = pd.to_datetime(t).time()
            except pd.errors.OutOfBoundsDatetime:
                thetime = index.time()
            except ValueError:
                # am/pm coding for old files
                H = t.split(" ")[0]
                am, ms = t.split(" ")[1].split(".")
                thetime = pd.to_datetime(H + "." + ms + " " + am).time()
            themoment = datetime.combine(thedate, thetime)
            dico[themoment] = event

        batch = pd.Series(dico, dtype="object", name="events")
        events_ser = events_ser.append(batch)
    dteventdf = pd.DataFrame(events_ser)
    return dteventdf


def extract_ventilation_drive(
    dteventdf: pd.DataFrame, actions: set = None
) -> pd.DataFrame:
    """extract a dataframe containing the ventilatory management"""
    # TODO extract the beginning (ventilate -> to first change)
    if actions is None:
        actions = {
            "cpap value changed",
            "mwpl value changed",
            "rr changed",
            "tidal volume changed",
        }

    # dteventdf = self.dt_events_df
    dteventdf = dteventdf.replace("NAN", np.nan)
    for action in actions:
        mask = dteventdf.events.str.contains(action)
        dteventdf[action] = np.nan
        dteventdf.loc[mask, [action]] = dteventdf.events
        dteventdf[action] = (
            dteventdf[action]
            .dropna()
            .apply(lambda st: float(st.split(" ")[-1].replace("s", "")))
        )
        dteventdf[action] = dteventdf[action].ffill()
    return dteventdf


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


actions = [
    "cpap value changed",
    "mwpl value changed",
    "rr changed",
    "tidal volume changed",
]


def extract_actions(df: pd.DataFrame, messages) -> Dict:
    """extract actions dtime and changes from taph recording:
    input:
        df: pandasDataFrame of taph events
        actions : action messages
    output
        marks: dictionary {action : [[timestamp, (valueBefore, valueAfter)], ...]}
    """
    marks: Dict[str, list] = {}
    for mes in messages:
        matching = []
        for i, cell in enumerate(df.events):
            for event in cell:
                if mes in event:
                    matching.append((i, event))
                    # print(event)
        # action : [[dtime, before, after], ...]
        marks[mes] = []
        for match in matching:
            i = match[0]
            values = list(match[1].split("from")[-1].strip().split(" to "))

            values = [_.replace("s", "") for _ in values]
            try:
                values = [float(_) for _ in values]
            except:
                print("exception... to be documented")
                values = values
            time_stp = df.index[i]
            marks[mes].append([time_stp, values])
    return marks


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
            print(
                "manage_events.build_dataframe : names should be updated for {}".format(
                    act
                )
            )
    df = pd.concat(dflist).sort_index()

    return df


#%%
if __name__ == "__main__":
    import anesplot.record_main as rec

    file_name = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/ALEA_/Patients2016OCT06/Record22_31_18/SD2016OCT6-22_31_19.csv"
    file_name = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/Anonymous/Patients2021AUG10/Record13_36_34/SD2021AUG10-13_36_34.csv"
    file_name = os.path.expanduser(
        "~/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/Anonymous/Patients2014NOV07/Record19_34_48/SD2014NOV7-19_34_49.csv"
    )
    file = os.path.basename(file_name)

    # see the taphClass
    ttrend = rec.TaphTrend(file_name)
