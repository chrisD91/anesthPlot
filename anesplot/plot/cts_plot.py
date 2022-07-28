#!/usr/bin/env python3
"""
Created on Thu Jun 23 15:25:39 2022

@author: cdesbois
"""
from typing import Any

cts_dico: dict[str, dict[str, Any]] = {
    "default": dict(
        key="",
        label="",
        color="blue",
        edgecolor="blue",
        unit="",
        goals=[],
        traces=[],
        ylims=[None, None],
    ),
    "o2": dict(
        key="o2",
        label="oxygen (%)",
        color="tab:green",
        fillalpha=0.2,
        edgecolor="tab:green",
        unit="%",
        goals=[30, 50],
        traces=[],
        ylims=[20, 80],
    ),
    "co2": dict(
        key="co2",
        label="CO2 (mmHg)",
        color="tab:blue",
        fillalpha=0.2,
        edgecolor="tab:blue",
        unit="mmHg",
        goals=[35, 45],
        traces=[],
        ylims=[30, 150],
    ),
    "co2rr": dict(
        key="co2rr",
        label="CO2 respiratoryRate",
        color="tab:blue",
        fillalpha=0.2,
        edgecolor="tab:blue",
        unit="mmHg",
        goals=[5, 15],
        traces=[],
        ylims=[6, 10],
        style="--",
    ),
    "iso": dict(
        key="iso",
        label="isoflurane (%)",
        color="tab:purple",
        fillalpha=0.2,
        edgecolor="tab:purple",
        unit="%",
        goals=[1.2, 1.4],
        traces=[],
        ylims=[0, 2],
    ),
    "tvinsp": dict(
        # datex
        key="tvinsp",
        label="tidalVolume insp",
        color="tab:orange",
        fillalpha=0.2,
        style="-",
        edgecolor="tab:orange",
        unit="l",
        goals=[5, 6],
        traces=[],
        ylims=[0, 7],
        calib=187,
    ),
    "tvspont": dict(
        # taph
        key="tvspont",
        label="tidalVolume spont",
        color="tab:olive",
        fillalpha=0.2,
        style="-",
        edgecolor="tab:olive",
        unit="l",
        goals=[5, 6],
        traces=[],
        ylims=[0, 7],
    ),
    "tvcontrol": dict(
        # taph
        key="tvcontrol",
        label="tidalVolume control",
        color="tab:orange",
        fillalpha=0.2,
        style="-",
        edgecolor="tab:orange",
        unit="l",
        goals=[5, 6],
        traces=[],
        ylims=[0, 7],
    ),
    "minvol": dict(
        # taph
        key="minvol",
        label="minuteVolume",
        color="tab:olive",
        fillalpha=0.2,
        style="-",
        edgecolor="tab:olive",
        unit="uncalibrated",
        goals=[5, 6],
        traces=[],
        ylims=[0, 7],
    ),
    "pPeak": dict(
        # taph
        key="tvcontrol",
        label="tidalVolume control",
        color="tab:red",
        fillalpha=0.2,
        style="-",
        edgecolor="tab:red",
        unit="l",
        goals=[5, 6],
        traces=[],
        ylims=[0, 7],
    ),
    "peep": dict(
        # taph
        key="tvcontrol",
        label="tidalVolume control",
        color="tab:red",
        fillalpha=0.2,
        style="-",
        edgecolor="tab:red",
        unit="l",
        goals=[5, 6],
        traces=[],
        ylims=[0, 7],
    ),
    "pPlat": dict(
        # taph
        key="tvcontrol",
        label="tidalVolume control",
        color="tab:red",
        fillalpha=0.2,
        style="-",
        edgecolor="tab:red",
        unit="cmH20",
        goals=[10, 25],
        traces=[],
        ylims=[0, 30],
    ),
    "setrr": dict(
        # taph
        key="setrr",
        label="set_respiratoryRate",
        color="k",
        fillalpha=1,
        style=":",
        edgecolor="k",
        unit="rpm",
        goals=[5, 10],
        traces=[],
        ylims=[0, 15],
    ),
    "settv": dict(
        # taph
        key="settv",
        label="set_tidalVolume",
        color="k",
        fillalpha=1,
        style=":",
        edgecolor="tab:orange",
        unit="l",
        goals=[5, 6],
        traces=[],
        ylims=[0, 7],
    ),
    "setpeep": dict(
        # taph
        key="setpeep",
        label="set_peep",
        color="k",
        fillalpha=1,
        style=":",
        edgecolor="tab:red",
        unit="%H20",
        goals=[5, 6],
        traces=[],
        ylims=[0, 7],
    ),
    "sat": dict(
        key="sat",
        label="sp02",
        color="tab:red",
        tracealpha=0.8,
        edgecolor="tab:red",
        unit="%",
        goals=[90, 100],
        traces=[],
        ylims=[60, 100],
    ),
    "sathr": dict(
        key="sathr",
        label="spO2 heart rate",
        color="k",
        edgecolor="tab:gray",
        style=":",
        unit="bpm",
        goals=[30, 50],
        traces=[],
        ylims=[20, 100],
    ),
    "hr": dict(
        key="hr",
        label="heart rate",
        color="k",
        edgecolor="tab:gray",
        unit="bpm",
        goals=[30, 50],
        traces=[],
        ylims=[20, 100],
    ),
    "ip1": dict(
        key="ip1",
        label="arterial pressure",
        color="tab:red",
        edgecolor="red",
        unit="mmHg",
        goals=[70, 80],
        traces=["ip1" + _ for _ in ["m", "d", "s"]],
        ylims=[30, 150],
        fillalpha=0.5,
    ),
    "ip2": dict(
        key="ip2",
        label="venous pressure",
        color="tab:blue",
        edgecolor="blue",
        unit="mmHg",
        goals=[10, 20],
        traces=["ip2" + _ for _ in ["m", "d", "s"]],
        ylims=[0, 20],
        fillalpha=0.4,
    ),
}
