#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 08:37:18 2022

@author: cdesbois
"""
import os

import matplotlib.pyplot as plt

import anesplot.record_main as rec
from anesplot.loadrec.export_reload import build_obj_from_hdf

paths = rec.paths
paths["save"] = "/Users/cdesbois/enva/clinique/recordings/casClin/220419"
name = "unknown_220419"
save_name = os.path.join(paths["save"], "data", name + ".hdf")
if not os.path.isfile(save_name):
    print(f"the file '{os.path.basename(save_name)}' doesn't exists")
    print(f"check the folder '{os.path.dirname(save_name)}'")
mtrends, ttrends, mwaves = build_obj_from_hdf(save_name)

mtrends.data.hr = mtrends.data.ihr

#%% find a sample to woro with

import anesplot.treatrec.ekg_to_hr as tohr

fig, *_ = mwaves.plot_wave(['wekg'])
lims = (19101.08725772946, 19101.087809159864)
ax = fig.get_axes()[0]
ax.set_xlim(lims)
ax.set_ylim(-2, 1)
# adjust the scale
mwaves.save_roi()

#%%
