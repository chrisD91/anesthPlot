#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 10:30:54 2021

@author: cdesbois

to extract the events from the taphonius files

"""

import anesplot.record_main as rec

file_name = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/ALEA_/Patients2016OCT06/Record22_31_18/SD2016OCT6-22_31_19.csv"


# see the taphClass
ttrend = rec.TaphTrend(file_name)
self = ttrend
eventdf = self.data[["events", "datetime"]].dropna()
eventdf = eventdf.set_index("datetime")
df = eventdf.copy()
df.head()
df.iloc[0]
df.iloc[0, ["events"]]
df.iloc[0].events
cell = df.iloc[0].events
cell.split("\r\n")


# explore keys
all_keys = {}
content = []
for i in range(len(df)):
    cell_content = df.iloc[i].events.split("\r\n")
    [content.append(_) for _ in cell_content]
    if len(cell_content) > 1:
        print("{}{}".format(i, "_" * 5))
        print(cell_content)
# messages
# remove date
messages = {_.split("-")[1].strip() for _ in content}

messages = {_.split(":")[0].strip() for _ in messages}
messages = {_.split("from")[0].strip() for _ in messages}
to_remove = ["Delivered Breath", "Vacuum Pump", "Auxiliary Controller", "EDump"]
for st in to_remove:
    messages = {_ for _ in messages if st not in _}

# to be continued -> extract settings (respiratory rates, tidal volume, ..) and clinical alarms
