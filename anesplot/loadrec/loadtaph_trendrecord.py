#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 15:30:07 2019
@author: cdesbois

load a taphonius data recording:
    - choose a file
    - load the patient datafile to a dictionary
    - load the physiological date into a pandas dataframe

nb = 4 files per recording :
    - .pdf -> anesthesia record 'manual style'
    - .xml -> taphonius technical record -> to be extracted
    - Patient.csv -> patient id and specifications
    - SD...csv -> anesthesia record
____
"""

import os
import sys
from collections import defaultdict
import time

import pandas as pd

# import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog


if not "paths" in dir():
    paths = {}
paths["taph"] = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"


# list taph recordings
def build_taph_decodedate_dico(pathdict=None):
    """list all the taph recordings and the paths to the record:
    input:
        paths: dictionary containing {'taph': pathToTheData}
    output:
        dictionary: {date : filename}
    """
    if pathdict is None:
        pathdict = paths
    months = {
        "jan": "_01_",
        "feb": "_02_",
        "mar": "_03_",
        "apr": "_04_",
        "may": "_05_",
        "jun": "_06_",
        "jul": "_07_",
        "aug": "_08_",
        "sep": "_09_",
        "oct": "_10_",
        "nov": "_11_",
        "dec": "_12_",
    }
    taphdata = "/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded"
    apath = pathdict.get("taph_data", taphdata)

    dct = defaultdict(list)
    # records = []
    for root, _, files in os.walk(apath):
        found = [_ for _ in files if _.startswith("SD") and _.endswith(".csv")]
        if found:
            record = found[0]
            record_name = os.path.join(root, record)
            # records.append(record_name)

            recorddate = record.strip("SD").strip(".csv").lower()
            for k, v in months.items():
                recorddate = recorddate.replace(k, v)
            d = time.strptime(recorddate, "%Y_%m_%d-%H_%M_%S")
            recorddate = "SD" + time.strftime("%Y_%m_%d-%H:%M:%S", d)
            dct[recorddate].append(record_name)
    return dct


def extract_record_day(monitor_file_name):
    """extract the date as 'YYYY_MM_DD' from a monitor_filename
    input:
        monitor file name (shortname)
    output:
        day : YYYY_MM_DD str
    """
    record_date = os.path.basename(monitor_file_name.lower())
    for st in ["sd", "m", ".csv", "wave"]:
        record_date = record_date.strip(st)
    d = time.strptime(record_date, "%Y_%m_%d-%H_%M_%S")
    day = time.strftime("%Y_%m_%d", d)
    return day


def choose_taph_record(monitorname=None):
    """select the taph recording:
    input:
        taphdico :  {date:path} builded from build_taph_decodedate_dico()'
        year = integer to place the pointer in pull down menu
        date = to be implemented (as year but to extract from monitor filename)
    output:
        filename (str) full path
    """
    print("{} > choose taph_record".format("-" * 20))
    taphdico = build_taph_decodedate_dico()
    recorddates = sorted(taphdico.keys(), reverse=True)

    global app
    question = "select the recording date"

    day_index = 0  # first key (<-> last date)
    if monitorname is not None:
        day = extract_record_day(monitorname)
        # index of the first record to be displayed based on year
        for i, v in enumerate(recorddates):
            if str(day) in v:
                day_index = i
                break
    #    app = QApplication(sys.argv)
    widg = QWidget()
    recorddate, ok_pressed = QInputDialog.getItem(
        widg, "select", question, recorddates, day_index, False
    )
    if ok_pressed and recorddate:
        filename = taphdico[recorddate][
            -1
        ]  # if bug : two dirs, the last should contain the data
        print("{} founded {}".format("-" * 10, os.path.basename(filename)))
    else:
        filename = None
        print("{} cancelled".format("-" * 10))
    return filename


def loadtaph_trenddata(filename):
    """load the taphoniusData trends data.

    :param str filename: fullname

    :returns: df = trends data
    :rtype: pandas.Dataframe
    """

    print("{} > loadtaph_datafile".format("-" * 20))
    if not os.path.isfile(filename):
        print("{} {}".format("!" * 10, "datafile not found"))
        print("{}".format(filename))
        print("{} {}".format("!" * 10, "datafile not found"))
        print()
        return pd.DataFrame()
    print("{} loading taph_datafile {}".format("-" * 10, os.path.basename(filename)))

    # check
    # filename = '/Users/cdesbois/enva/clinique/recordings/anesthRecords/onTaphRecorded/before2020/REDDY_A13-99999/Patients2013DEC16/Record08_19_11/SD2013DEC16-8_19_11.csv'

    try:
        df = pd.read_csv(filename, sep=",", header=1, skiprows=[2])
    except pd.errors.ParserError:
        print("corrupted file ({})".format(os.path.basename(filename)))
        return pd.DataFrame()

    corr_title = {
        "Date": "Date",
        "Time": "Time",
        "Events": "events",
        "CPAP/PEEP": "peep",
        "TV": "tv",
        "TVcc": "tvCc",
        "RR": "co2RR",
        "IT": "it",
        "IP": "ip",
        "MV": "minVol",
        "I Flow": "iFlow",
        "I:E Ratio": "IE",
        "Exp Time": "expTime",
        "TV.1": "tv1",
        "Insp Time": "inspTime",
        "Exp Time.1": "expTime",
        "RR.1": "rr1",
        "MV.1": "mv1",
        "I Flow.1": "iFlow1",
        "I:E Ratio.1": "IE1",
        "CPAP/PEEP.1": "peep1",
        "PIP": "pip",
        "Insp CO2": "co2insp",
        "Exp CO2": "co2exp",
        "Resp Rate": "rr",
        "Insp Agent": "aaInsp",
        "Exp Agent": "aaExp",
        "Insp O2": "o2insp",
        "Exp O2": "o2exp",
        "Atmospheric Pressure": "atmP",
        "SpO2 HR": "spo2Hr",
        "Saturation": "sat",
        "Mean": "ip1m",
        "Systolic": "ip1s",
        "Diastolic": "ip1d",
        "HR": "hr",
        "T1": "t1",
        "T2": "t2",
        "ECG HR": "ekgHR",
        "Batt1": "batt1",
        "Current1": "curr1",
        "Batt2": "batt2",
        "Current2": "curr2",
        "Piston Position": "pistPos",
        "Insp N2O": "n2oInsp",
        "Exp N2O": "n2oExp",
    }
    df.rename(columns=corr_title, inplace=True)
    df = pd.DataFrame(df)
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")
    df["datetime"] = pd.to_datetime(df.Date + ";" + df.Time)
    df["time"] = df.Date + "-" + df.Time
    df["time"] = pd.to_datetime(df["time"], dayfirst=True)
    sampling = (df.time[1] - df.time[0]).seconds
    df["eTime"] = df.index * sampling
    df["eTimeMin"] = df.eTime / 60
    # to remove the zero values :
    # OK for histograms, but induce a bug in plotting
    #    data.ip1m = data.ip1m.replace([0], [None])
    #    data = data.replace([0], [None])
    # CO2: from % to mmHg
    try:
        df[["co2exp", "co2insp"]] *= 760 / 100
    except KeyError:
        print("no capnographic recording")
    print(
        "{} < loaded taph_datafile ({}) -> pd.DataFrame".format(
            "-" * 20, os.path.basename(filename)
        )
    )
    return df


def loadtaph_patientfile(filename):
    """load the taphonius patient.csv file
    input:
        filename : (str) the full filename
            (the headername will be reconstructed inside the function)

    output:
        descr = dict of patient_data
    """
    headername = os.path.join(os.path.dirname(filename), "Patient.csv")

    print("{} > loading taph_patientfile".format("-" * 20))
    if not os.path.isfile(headername):
        print("{} {}".format("!" * 10, "patient_file not found"))
        print("{}".format(headername))
        print("{} {}".format("!" * 10, "patient_file not found"))
        print()
        return {}
    print("{} loading  {}".format("-" * 10, os.path.basename(headername)))

    df = pd.read_csv(headername, header=None, usecols=[0, 1], encoding="iso8859_15")
    # NB encoding needed for accentuated letters
    df[0] = df[0].str.replace(":", "")
    df = df.set_index(0).T
    # convert to num
    df["Body weight"] = df["Body weight"].astype(float)
    # convert to a dictionary
    descr = df.loc[1].to_dict()

    print(
        "{} < loaded taph_patientfile ({}) -> dict".format(
            "-" * 20, os.path.basename(headername)
        )
    )
    return descr


#%%
if __name__ == "__main__":
    from config.load_recordrc import build_paths

    paths = build_paths()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    monitor_name = "M2021_9_9-11_44_35.csv"
    file_name = choose_taph_record(monitor_name)
    tdata_df = loadtaph_trenddata(file_name)
    header_dico = loadtaph_patientfile(file_name)
