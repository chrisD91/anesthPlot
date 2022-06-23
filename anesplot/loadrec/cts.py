#!/usr/bin/env python3
"""
Created on Fri Jun 10 09:49:57 2022

constants to use in the loading process

@author: cdesbois
"""

mon_corr_title = {
    "AA  LB": "aaLabel",
    "AA_Insp": "aaInsp",
    "AA_Exp": "aaExp",
    "CO2 RR": "co2RR",
    "CO2_Insp": "co2insp",
    "CO2_Exp": "co2exp",
    "ECG HR": "ekgHR",
    "IP1_M": "ip1m",
    "IP1_S": "ip1s",
    "IP1_D": "ip1d",
    "IP1PR": "hr",
    "IP2_M": "ip2m",
    "IP2_S": "ip2s",
    "IP2_D": "ip2d",
    "IP2PR": "ip2PR",
    "O2_Insp": "o2insp",
    "O2_Exp": "o2exp",
    "Time": "dtime",
    "Resp": "resp",
    "PPeak": "pPeak",
    "Peep": "peep",
    "PPlat": "pPlat",
    "pmean": "pmean",
    "ipeep": "ipeep",
    "TV_Insp": "tvInsp",
    "TV_Exp": "tvExp",
    "Compli": "compli",
    "raw": "raw",
    "MinV_Insp": "minVinsp",
    "MinV_Exp": "minVexp",
    "epeep": "epeep",
    "peepe": "peepe",
    "peepi": "peepi",
    "I:E": "ieRat",
    "Inp_T": "inspT",
    "Exp_T": "expT",
    "eTime": "etimesec",
    "S_comp": "sCompl",
    "Spplat": "sPplat",
}


# set_ -> user settings
# calc_ -> calculated
# mes_ -> mesured

taph_corr_title = {
    "Date": "Date",
    "Time": "Time",
    "Events": "events",
    # settings
    "CPAP/PEEP": "set_peep",
    "TV": "set_tv",
    "TVcc": "tv_control",
    "RR": "set_rr",
    "IT": "set_it",
    "IP": "set_ip",
    "MV": "calc_minVol",
    "I Flow": "calc_iFlow",
    "I:E Ratio": "calc_IE",
    "Exp Time": "calc_expTime",
    # measured
    "TV.1": "tv_spont",
    "Insp Time": "inspTime",
    "Exp Time.1": "expTime",
    "RR.1": "rr_strange",
    "MV.1": "mv",
    "I Flow.1": "iFlow",
    "I:E Ratio.1": "IE",
    "CPAP/PEEP.1": "peep",
    "PIP": "pPeak",
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
