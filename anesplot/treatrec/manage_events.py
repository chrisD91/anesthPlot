#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 10:30:54 2021

@author: cdesbois

to extract the events from the taphonius files

"""
import os

import anesplot.record_main as rec

file_name = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/ALEA_/Patients2016OCT06/Record22_31_18/SD2016OCT6-22_31_19.csv"
file = os.path.basename(file_name)

# see the taphClass
ttrend = rec.TaphTrend(file_name)
self = ttrend
eventdf = self.data[["events", "datetime"]].dropna()
eventdf = eventdf.set_index("datetime")
eventdf.events = eventdf.events.apply(
    lambda st: [_.strip("[").strip("]") for _ in st.split("\r\n")]
)

#%%
def extract_taphmessages(df):
    """extract the messages that contain the kw"""
    content = set()
    for cell in df.events:
        for event in cell:
            content.add(event.split("-")[-1])
    content = {_.split(":")[0].strip() for _ in content}
    content = {_.split("from")[0].strip() for _ in content}

    actions = {_ for _ in content if "changed" in _ or "Ventilate" in _}
    actions = {
        _ for _ in actions if not _.startswith("Power") and not _.startswith("Primary")
    }
    errors = content - actions

    return errors, actions


error_messages, action_messages = extract_taphmessages(eventdf)

#%% initial values


def convert_day(st):
    """get a day YYYYmonthD an convert it to YYY-month-D"""
    previous = st[0]
    new = st[0]
    for i, x in enumerate(st[1:]):
        if x.isalpha() == previous.isalpha():
            new += x
        else:
            new += "-" + x
        previous = x
    return new


# '2016OCT6'
day = file.split("-")[0].strip("SD")
day = convert_day(day)


message = ""  # ?? presetq
message = "Init Complete"  # i = 24
message = "Ventilate"  # i=32


# to be continued -> extract settings (respiratory rates, tidal volume, ..) and clinical alarms
# get times of events
for cell in df.events:
    for event in cell:
        if mes in event:
            print(event)

event = "11:22:40 PM.375 - Ventilate"
event.split(".")[0]

os.path.basename(file_name)
file = os.path.basename(file_name)
file.split("-")
file.split("-")[0].strip("SD")
day = file.split("-")[0].strip("SD")
