#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 12:36:35 2022

@author: cdesbois
"""
import os
from datetime import datetime

import pandas as pd


# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.plot(df.reset_index()["tv"])

# bug taphonius connection avec le microcontrôleur


file_name = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/Anonymous/Patients2022JAN21/Record22_52_07/SD2022JAN21-22_52_7.csv"
filename = file_name

with open(filename) as f:
    lines = f.read().splitlines()

for i, line in enumerate(lines[3:10], start=3):
    print(i, line)


to_skip = [
    2,
]
for i, line in enumerate(lines):
    if str(line).startswith("["):
        to_skip.append(i)

pd.read_csv(
    filename,
    sep=",",
    header=1,
    skiprows=sorted(to_skip),
    on_bad_lines="skip",
    engine="python",
    index_col=False,
)

# the change in date
for i, line in enumerate(lines):
    t = line.split(",")[0]
    if not line.startswith("["):
        try:
            theyear = datetime.strptime(t, "%d/%M/%Y").year
            if theyear != 2022:
                print(i, line)
                break
        except:
            pass

# look at the lines
for i in range(2610, 2613):
    print(lines[i])

#
def extract_journal(tfilename):

    # load lines
    with open(filename) as f:
        lines = f.read().splitlines()

    # build df
    df = pd.DataFrame(columns=["key", "dt", "line"]).T
    dt = ""
    for i, line in enumerate(lines):
        for key in ["ventilate", "standby"]:
            if key in line.casefold():
                try:
                    # dt = pd.to_datetime(
                    #     line.split(",")[0] + ", " + line.split(",")[1], errors="coerce"
                    # )
                    dt = pd.to_datetime(line.split(",")[0] + ", " + line.split(",")[1])
                except Exception:
                    print(line)
                    try:
                        dt = pd.to_datetime(
                            line.split("-")[0].strip("[").strip(" ")
                        ).time()
                    except Exception:
                        dt = ""

                print(f"{'-'*10}")
                print(i, dt, key)
                df[i] = [key, dt, line]

    # append date drop
    for i, line in enumerate(lines):
        if "PM." in line:
            print(f"{'-'*10}")
            print(i, line)
            try:
                dt = pd.to_datetime(
                    " ".join(line.split('"')[0].strip(",").split(",15,"))
                )
            except Exception:
                try:
                    dt = line.replace('"', "").split(",")[0].strip("[]").split(" - ")[0]
                    hms = dt.split(" ")[0]
                    ampm, ms = dt.split(" ")[1].split(".")
                    dt = hms + "." + ms + " " + ampm
                    dt = pd.to_datetime(dt).time()
                except Exception:
                    dt = " ".join(
                        line.split("[")[0].replace('"', "").strip(",").split(",")
                    )
                    dt = pd.to_datetime(dt)
            df[i] = [key, dt, line]

            return df.T.sort_index()

    return df.T.sort_index()


journal = extract_journal(filename)

for i in [2610, 2611]:
    print(lines[i])
