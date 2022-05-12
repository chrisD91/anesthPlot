# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 16:05:29 2019

@author: cdesbois

rr to hrv ... to be continued (see Yann work)

"""


def build_hrv_limits(spec="horse"):
    """
    Return a dico containing HRV limits (VLF, LF, HF).

    Parameters
    ----------
    spec in ['horse', 'man']
    """
    dico = {}
    if spec == "man":
        # Guidelines. Circulation, 93(5):1043–65, mar 1996.
        vals = [0.001, 0.04, 0.15, 0.4]
    elif spec == "horse":
        # Ishii et al J. Auton. Nerv. Syst., 8(1):43–8, 1996.
        vals = [0.001, 0.01, 0.07, 0.6]
    else:
        print("spec should be man or horse")
        return dico
    for i, band in enumerate(["VLF", "LF", "HF"]):
        lims = (vals[i], vals[i + 1])
        dico[band] = lims
    return dico


# %%
if __name__ == "__main__":
    hrv_dico = build_hrv_limits("horse")
    if "ekg_df" not in dir():
        print("RR series are not extracted")
        print("run wave_to_hr to build one")
