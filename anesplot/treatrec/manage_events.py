#!/usr/bin/env python3
"""
Created on Sat Dec 18 10:30:54 2021

@author: cdesbois

functions ued to extract the events from the taphonius files

"""
import logging
from datetime import datetime, timedelta
from math import ceil
from typing import Any, Optional, Tuple, Union

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", 50)
pd.set_option("display.max_columns", 500)
# %%


def convert_day(txt: str) -> str:
    """Convert YYYYmonthD to YYY-month-D."""
    previous = txt[0]
    new = txt[0]
    for car in txt[1:]:
        if car.isalpha() == previous.isalpha():
            new += car
        else:
            new += "-" + car
        previous = car
    return new


def extract_taphmessages(df: pd.DataFrame, display: bool = False) -> Tuple[Any, Any]:
    """
    Extract the messages.

    Parameters
    ----------
    df : pd.DataFrame
        dt_event_df.
    display : bool, optional (default is False)
        print the messages in the terminal

    Returns
    -------
    dict
        acts : dict of actions.
    dict
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
        logging.warning(f"{'-' * 10} extract_taphmessages")
        logging.warning(f"{'-' * 5} content : ")
        for item in content:
            logging.warning(item)

    return acts, content


def build_event_dataframe(datadf: pd.DataFrame) -> pd.DataFrame:
    """
    Build a pandas datafame with a countinuous datetime:event pairs.

    Parameters
    ----------
    datadf : pd.DataFrame
        the taphonius recording.

    Returns
    -------
    dteventsdf : pd.DataFrame
        dataframe with index=datetime.
    """
    dteventsdf = pd.DataFrame(columns=["events"])
    if datadf.empty:
        logging.warning("empty dataframe")
        return dteventsdf
    df = datadf[["events", "dtime"]].dropna().set_index("dtime")
    df.events = df.events.apply(
        lambda st: [_.strip("[").strip("]") for _ in st.splitlines()]
    )
    if df.events.dropna().empty:
        logging.warning("no events in the recording")
        return dteventsdf
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
        for time, event in t_event:
            if len(time) >= 16:
                event = time.split("]")[-1].strip()
                time = time.split("]")[0]
            if " am" in time:
                time = time.replace(" am", "") + " am"
            if " pm" in time:
                time = time.replace(" pm", "") + " pm"
            try:
                eventtime = pd.to_datetime(time).time()
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
        #        if batch.index.values in events_ser.index.values:
        if set(batch.index.values) & set(events_ser.index.values):
            # two events at the same index -> index has to be shifted
            newtimes = []
            for datet in batch.index:
                if datet in events_ser:
                    datet = datet + timedelta(milliseconds=1)
                newtimes.append(datet)
                logging.warning(f"{newtimes}")
            batch = batch.set_axis(newtimes)
        events_ser = pd.concat([events_ser, batch])
    dteventsdf = pd.DataFrame(events_ser)
    dteventsdf = dteventsdf.sort_index()
    dteventsdf.index = pd.to_datetime(dteventsdf.index)
    return dteventsdf


def extract_ventilation_drive(
    dteventsdf: pd.DataFrame, acts: Optional[set[Any]] = None
) -> pd.DataFrame:
    """Extract a dataframe containing the ventilatory management.

    Parameters
    ----------
    dteventsdf : pd.DataFrame
        a container for taph generated events (dtime as index, event as column).
    acts : set, optional (default is None)
        container for action messages.

    Returns
    -------
    pd.DataFrame with datetime index and one column per action (ex 'rr changed')
    """
    if dteventsdf.empty:
        logging.warning("extract_ventilation_drive: dt_event_df is empty")
        return pd.DataFrame()

    if acts is None:
        acts = {
            "cpap value changed",
            "mwpl value changed",
            "rr changed",
            "tidal volume changed",
            "buffer vol",
            "it",
            "ip",
        }
    # nb in the taphonius, the default setings are not included in the recorded data
    default_chris = {
        "tidal": 7,
        "rr": 8,
        "it": 2,
        "ip": 10,
        "mwpl": 55,
        "cpap": 5,
        "buffer": 10,
    }
    runs = {"ventilate": True, "standby": False}

    def end_of_line_to_float(line: str) -> Union[float, None]:
        """Return float value else none."""
        line = line.split(" ")[-1].replace("s", "")
        try:
            val = float(line)
        except ValueError:
            try:
                # old files
                val = float(line.replace(",", "."))
            except ValueError:
                # print(f"end_of_line_to_float: fix me for '{line}'")
                val = np.nan
        return val

    assert (
        dteventsdf.index.is_unique
    ), "extract_ventilation_drive: check unicity for dteventsdf.index"

    dteventsdf = dteventsdf.replace("NAN", np.nan)
    # extract the ventilation period -> ventilation True or False
    dteventsdf["ventil"] = np.nan
    dteventsdf.iloc[0, dteventsdf.columns.get_loc("ventil")] = False
    runs = {"ventilate": True, "standby": False}
    for k, bol in runs.items():
        for datet, event in dteventsdf.events.iteritems():
            if k in event:
                dteventsdf.loc[datet, ["ventil"]] = bol
    dteventsdf.ventil = dteventsdf.ventil.ffill()

    for act in acts:
        if len(act.split(" ")) > 1:
            # two words in act
            mask = dteventsdf.events.str.contains(act)
        else:
            mask = dteventsdf.events.str.contains(" " + act + " ")
        dteventsdf[act] = np.nan
        if len(mask.unique()) > 1:
            # fill with change messages
            dteventsdf.loc[mask, [act]] = dteventsdf.events
            # replace first line with the first 'changed from ...'
            first_message = dteventsdf.loc[mask, [act]].iloc[0][act]
            from_message = first_message.split("to")[0].strip(" ")
            if default_chris[act.split(" ")[0]] == end_of_line_to_float(from_message):
                dteventsdf.iloc[0, dteventsdf.columns.get_loc(act)] = from_message
            else:
                # replace the from extracted value by the defauls one
                # taph bug : first message ie cpap value changed from 0, not preset 5)
                logging.warning(
                    f"first value is differant from default_settings for '{act}'"
                )
                logging.warning(f"replaced '{from_message}'")
                logging.warning(
                    f"by '{default_chris[act.split(' ')[0]]}' (as initial '{act}' value)"
                )
                dteventsdf.iloc[0, dteventsdf.columns.get_loc(act)] = str(
                    default_chris[act.split(" ")[0]]
                )
            # to values extraction and fill
            dteventsdf[act] = dteventsdf[act].dropna().apply(end_of_line_to_float)
            dteventsdf[act] = dteventsdf[act].ffill()
        else:
            dteventsdf[act] = default_chris.get(act.split(" ")[0], np.nan)
        # remove non ventilate values
        dteventsdf.loc[~dteventsdf.ventil, [act]] = np.nan

    return dteventsdf.dropna(how="all", axis=1)


def plot_ventilation_drive(
    df: pd.DataFrame, param: dict[str, Any], all_traces: bool = False
) -> plt.Figure:
    """
    Plot the ventilatory drive ie the data that were changed.

    Parameters
    ----------
    df : pd.DataFrame
        ventildrive_df
    param : dict
        the recording parameters
    all: bool (default is False)
        to include {'buffer', 'ip', 'mwpl'}

    Returns
    -------
    fig : plt.Figure
    """
    df.columns = [_.split(" ")[0] for _ in df.columns]
    cols = df.columns[2:]

    if not all_traces:
        cols = [_ for _ in cols if _ not in {"buffer", "ip", "mwpl"}]
        # tops = {"it", "tidal", "rr", "cpap"}

    labels = {
        "ip": "inspiratoryPause",
        "it": "inspTime",
        "tidal": "tidalVol",
        "rr": "respRate",
        "buffer": "bufferVolume",
        "cpap": "peep",
        "mwpl": "pressureLimit",
    }
    # lack it -> to be checked
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
                logging.warning(
                    f"plot_ventilation_drive : please update the labels for {col}"
                )
            ax.step(
                df.index, df[col].fillna(0), linewidth=1.5, label=labels.get(col, col)
            )
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ylims = ax.get_ylim()
    ylims = (0, ceil(ylims[1] / 5) * 5)
    ax.set_ylim(ylims)
    ax.set_yticks(np.arange(ylims[0], ylims[1] + 0.1, 5))
    ax.grid()
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.text(0.99, 0.01, "anesthPlot", ha="right", va="bottom", alpha=0.4, size=12)
    fig.text(0.01, 0.01, param["file"], ha="left", va="bottom", alpha=0.4)

    fig.tight_layout()
    return fig


# %%

plt.close("all")


def plot_events(
    dteventsdf: pd.DataFrame,
    param: dict[str, Any],
    todrop: Optional[list[str]] = None,
    dtime: bool = False,
) -> plt.figure:
    """Plot all events.

    Parameters
    ----------
    dteventsdf : pd.DataFrame
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
        dteventsdf = dteventsdf.drop(
            dteventsdf.loc[dteventsdf.events.str.contains(item)].index
        )
    # copy to modifyonly inside the function
    event_df = dteventsdf.copy()
    # manage color
    event_df["color"] = "red"
    mask = event_df.events.str.contains("vacuum")
    event_df.loc[mask, ["color"]] = "blue"
    mask = event_df.events.str.contains("changed")
    event_df.loc[mask, ["color"]] = "green"
    mask = event_df.events.str.contains("ventilate")
    event_df.loc[mask, ["color"]] = "black"
    mask = event_df.events.str.contains("standby")
    event_df.loc[mask, ["color"]] = "black"

    # set index to num
    if not dtime:
        event_df = event_df.reset_index()
        event_df = event_df.rename(columns={"index": "dt"})
    fig = plt.figure(figsize=(15, 4))
    ax = fig.add_subplot(111)
    event_df["uni"] = 1
    # ax.plot(dteventsdf.uni)
    ax.scatter(event_df.index, event_df.uni, color=event_df.color, marker=".")
    # ax.scatter(dteventsdf.index, dteventsdf.uni, color="tab:green", marker=".")
    for datet, color in event_df.color.iteritems():
        ax.vlines(datet, 0, 1, color=color)
    # filter messages to remove the actions

    # plot the events - action
    for datet, (event, color) in event_df[["events", "color"]].iterrows():
        # pos = (mdates.date2num(dt), 1)
        pos = (datet, 1)
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

# %%


def extract_event(eventdf: pd.DataFrame) -> dict[str, pd.Timestamp]:
    """
    Extract timestamp of the messages.

    Parameters
    ----------
    eventdfdf : pd.DataFrame
        pandasDataFrame containing the taphonius events.

    Returns
    -------
    dict
        {message : [timestamp]}.
    """
    messages = ["Init Complete", "Ventilate", "standby", "data finalised"]
    messages = [_.lower() for _ in messages]

    ser = pd.Series(dtype=str)
    for index, event in eventdf.events.iteritems():
        for message in messages:
            if message in event:
                ser.loc[index] = event
    dico = ser.to_dict()
    return dict(dico)


# %%


# def build_dataframe(acts) -> pd.DataFrame:
#     """Build a dataframe containing all the actions, one per column."""
#     names = {
#         "Inspiratory pause value changed": "pause",
#         "CPAP value changed": "peep",
#         "Tidal Volume changed": "vol",
#         "RR changed": "rr",
#         "MWPL value changed": "mwpl",
#         "Buffer Vol changed": "bufferVol",
#         "O2 expired high alarm value changed": "highO2ExpAlarm",
#         "O2 inspired high alarm value changed": "highO2InspAlarm",
#         "O2 inspired low alarm value changed": "lowO2InspAlarm",
#         "IP changed": "IP",
#         "IT changed": "IT",
#     }
#     dflist = []
#     for act, event in acts.items():
#         colname = names.get(act, "notdefined")
#         actdf = pd.DataFrame(event, columns=["dt", colname]).set_index("dt")
#         dflist.append(actdf)
#         if colname == "notdefined":
#             logging.warning(f"manage_events.build_dataframe : names should be updated for {act}")
#     acts_df = pd.concat(dflist).sort_index()

#     return acts_df


# %%
if __name__ == "__main__":
    # import os
    # import anesplot.record_main as rec
    pass
    # import anesplot.slow_waves  # MonitorTrend, TaphTrend
    # from anesplot.config.load_recordrc import build_paths

    # AFILE = "before2020/ALEA_/Patients2016OCT06/Record22_31_18/\
    #     SD2016OCT6-22_31_19.csv"
    # AFILE = "Anonymous/Patients2021AUG10/Record13_36_34/\
    #     SD2021AUG10-13_36_34.csv"
    # AFILE = "before2020/Anonymous/Patients2014NOV07/Record19_34_48/S\
    #         D2014NOV7-19_34_49.csv"
    # AFILE = "before2020/BELAMIDUBOCAGE_A15-8244/Patients2015JUN25/\
    #     Record15_48_30/SD2015JUN25-15_48_30.csv"

    # paths = build_paths()
    # file_name = os.path.join(paths["taph_data"], AFILE)

    # # see the taphClass
    # ttrend = anesplot.slow_waves.TaphTrend(file_name)
    # ttrend.extract_events()
    # ttrend.show_graphs()
    # ttrend.plot_events()
    # ttrend.plot_ventil_drive()
