#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:09:29 2022

@author: cdesbois
"""


import os

import pandas as pd

exp = os.path.join(os.path.expanduser("~"), "toPlay", "export.hdf")

mtrends.data.to_hdf(exp, key="mtrend_data")
pd.DataFrame.from_dict({k: [str(v)] for k, v in mtrends.header.items()}).T.to_hdf(
    exp, key="mtrend_header"
)
pd.DataFrame.from_dict({k: [str(v)] for k, v in mtrends.param.items()}).T.to_hdf(
    exp, key="mtrend_param"
)
# filename

ttrends.data.to_hdf(exp, key="ttrend_data")
pd.DataFrame.from_dict({k: [str(v)] for k, v in mtrends.header.items()}).T.to_hdf(
    exp, key="trend_header"
)
pd.DataFrame.from_dict({k: [str(v)] for k, v in mtrends.param.items()}).T.to_hdf(
    exp, key="trend_param"
)

duplicates = {_ for _ in cols if cols.count(_) > 1}
print(f"{duplicates=}")
